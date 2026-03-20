"""Health Connect SQLite backup client."""

import sqlite3
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from ..base import (
    BaseFitnessClient,
    BodyMetric,
    ExerciseRecord,
    FitnessData,
    SetRecord,
    SleepRecord,
    WorkoutSession,
)
from .exercise_mapping import map_segment_type_to_exercise
from .parsers import (
    parse_exercise_segments,
    parse_exercise_sessions,
    parse_heart_rate_records,
    parse_sleep_records,
    parse_weight_records,
)


class HealthConnectClient(BaseFitnessClient):
    """Client for parsing Health Connect SQLite backup files."""

    @property
    def source_name(self) -> str:
        return "health_connect"

    async def parse(self, path: str) -> FitnessData:
        """Parse Health Connect backup from ZIP file or SQLite database.

        Args:
            path: Path to ZIP file or SQLite database

        Returns:
            Parsed fitness data
        """
        path_obj = Path(path)

        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Handle ZIP file
        if path_obj.suffix.lower() == ".zip":
            db_path = await self._extract_db_from_zip(path_obj)
            try:
                return await self._parse_database(db_path)
            finally:
                # Clean up temp file
                db_path.unlink(missing_ok=True)
        else:
            # Assume it's a SQLite database
            return await self._parse_database(path_obj)

    async def _extract_db_from_zip(self, zip_path: Path) -> Path:
        """Extract SQLite database from Health Connect ZIP backup."""
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Look for SQLite database file
            db_files = [
                name
                for name in zf.namelist()
                if name.endswith(".db") or "health" in name.lower()
            ]

            if not db_files:
                # Try to find any file that might be a database
                for name in zf.namelist():
                    if not name.endswith("/"):  # Not a directory
                        # Check if it's a SQLite file by magic bytes
                        with zf.open(name) as f:
                            header = f.read(16)
                            if header.startswith(b"SQLite format 3"):
                                db_files.append(name)
                                break

            if not db_files:
                raise ValueError(
                    "No SQLite database found in ZIP file. "
                    "Make sure this is a Health Connect backup."
                )

            # Extract to temp file
            temp_dir = Path(tempfile.mkdtemp())
            db_name = db_files[0]
            zf.extract(db_name, temp_dir)
            return temp_dir / db_name

    async def _parse_database(self, db_path: Path) -> FitnessData:
        """Parse the Health Connect SQLite database."""
        workouts: list[WorkoutSession] = []
        body_metrics: list[BodyMetric] = []
        sleep_records: list[SleepRecord] = []
        raw_data: dict = {"tables": []}

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        try:
            # Get list of tables
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row["name"] for row in cursor.fetchall()]
            raw_data["tables"] = tables

            # Parse exercise sessions
            if "exercise_session_record" in tables or any(
                "exercise" in t.lower() for t in tables
            ):
                sessions = parse_exercise_sessions(conn, tables)
                segments = parse_exercise_segments(conn, tables)

                # Match segments to sessions and build workouts
                for session in sessions:
                    session_segments = [
                        s for s in segments if s.get("session_id") == session.get("id")
                    ]

                    exercises: list[ExerciseRecord] = []
                    for seg in session_segments:
                        exercise_name = map_segment_type_to_exercise(
                            seg.get("segment_type", "")
                        )
                        if exercise_name:
                            # Create sets from segment data
                            sets = []
                            reps = seg.get("repetitions", 0)
                            if reps > 0:
                                sets.append(
                                    SetRecord(
                                        reps=reps,
                                        weight=None,  # Health Connect doesn't have weight
                                    )
                                )

                            exercises.append(
                                ExerciseRecord(
                                    name=exercise_name,
                                    sets=sets,
                                    segment_type=seg.get("segment_type"),
                                )
                            )

                    if exercises or session.get("exercise_type"):
                        workouts.append(
                            WorkoutSession(
                                start_time=session.get(
                                    "start_time", datetime.now()
                                ),
                                end_time=session.get("end_time", datetime.now()),
                                session_type=session.get(
                                    "exercise_type", "strength_training"
                                ),
                                exercises=exercises,
                                notes=session.get("notes", ""),
                                source=self.source_name,
                            )
                        )

            # Parse weight records
            if "weight_record" in tables or any(
                "weight" in t.lower() for t in tables
            ):
                weight_records = parse_weight_records(conn, tables)
                for record in weight_records:
                    body_metrics.append(
                        BodyMetric(
                            metric_type="weight",
                            value=record.get("weight", 0),
                            unit="kg",
                            recorded_at=record.get("time", datetime.now()),
                        )
                    )

            # Parse sleep records
            if "sleep_session_record" in tables or any(
                "sleep" in t.lower() for t in tables
            ):
                sleep_data = parse_sleep_records(conn, tables)
                for record in sleep_data:
                    sleep_records.append(
                        SleepRecord(
                            start_time=record.get("start_time", datetime.now()),
                            end_time=record.get("end_time", datetime.now()),
                            stages=record.get("stages", {}),
                            quality_score=record.get("quality_score"),
                        )
                    )

            # Parse heart rate (for workout intensity analysis)
            if "heart_rate_record" in tables or any(
                "heart" in t.lower() for t in tables
            ):
                hr_records = parse_heart_rate_records(conn, tables)
                raw_data["heart_rate_samples"] = len(hr_records)

        finally:
            conn.close()

        return FitnessData(
            source=self.source_name,
            workouts=workouts,
            body_metrics=body_metrics,
            sleep_records=sleep_records,
            raw_data=raw_data,
        )
