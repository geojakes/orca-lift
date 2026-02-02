"""Google Fit Takeout client (legacy fallback)."""

import csv
import json
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
from .parsers import (
    parse_daily_activity_metrics,
    parse_fit_sessions,
    parse_workout_data,
)


class GoogleFitClient(BaseFitnessClient):
    """Client for parsing Google Fit Takeout data."""

    @property
    def source_name(self) -> str:
        return "google_fit"

    async def parse(self, path: str) -> FitnessData:
        """Parse Google Fit data from Takeout ZIP file or extracted directory.

        Args:
            path: Path to ZIP file or extracted Takeout directory

        Returns:
            Parsed fitness data
        """
        path_obj = Path(path)

        if not path_obj.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        # Handle ZIP file
        if path_obj.suffix.lower() == ".zip":
            return await self._parse_zip(path_obj)
        elif path_obj.is_dir():
            return await self._parse_directory(path_obj)
        else:
            raise ValueError(f"Expected ZIP file or directory, got: {path}")

    async def _parse_zip(self, zip_path: Path) -> FitnessData:
        """Parse Google Fit data from a Takeout ZIP file."""
        workouts: list[WorkoutSession] = []
        body_metrics: list[BodyMetric] = []
        sleep_records: list[SleepRecord] = []
        raw_data: dict = {"files_processed": []}

        with zipfile.ZipFile(zip_path, "r") as zf:
            # Find Fit folder
            fit_files = [
                name
                for name in zf.namelist()
                if "Fit/" in name or "fit/" in name.lower()
            ]

            for file_path in fit_files:
                if file_path.endswith("/"):
                    continue

                raw_data["files_processed"].append(file_path)

                try:
                    with zf.open(file_path) as f:
                        content = f.read()

                        if file_path.endswith(".json"):
                            data = json.loads(content.decode("utf-8"))
                            self._process_json_file(
                                file_path,
                                data,
                                workouts,
                                body_metrics,
                                sleep_records,
                            )

                        elif file_path.endswith(".csv"):
                            lines = content.decode("utf-8").splitlines()
                            reader = csv.DictReader(lines)
                            rows = list(reader)
                            self._process_csv_file(
                                file_path,
                                rows,
                                workouts,
                                body_metrics,
                            )

                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

        return FitnessData(
            source=self.source_name,
            workouts=workouts,
            body_metrics=body_metrics,
            sleep_records=sleep_records,
            raw_data=raw_data,
        )

    async def _parse_directory(self, dir_path: Path) -> FitnessData:
        """Parse Google Fit data from an extracted Takeout directory."""
        workouts: list[WorkoutSession] = []
        body_metrics: list[BodyMetric] = []
        sleep_records: list[SleepRecord] = []
        raw_data: dict = {"files_processed": []}

        # Find Fit folder
        fit_dir = dir_path / "Takeout" / "Fit"
        if not fit_dir.exists():
            fit_dir = dir_path / "Fit"
        if not fit_dir.exists():
            # Try to find it recursively
            for subdir in dir_path.rglob("Fit"):
                if subdir.is_dir():
                    fit_dir = subdir
                    break

        if not fit_dir.exists():
            raise ValueError(
                "Could not find Fit folder in Takeout data. "
                "Make sure Google Fit was included in the export."
            )

        # Process all JSON and CSV files
        for file_path in fit_dir.rglob("*"):
            if file_path.is_dir():
                continue

            raw_data["files_processed"].append(str(file_path))

            try:
                if file_path.suffix == ".json":
                    with open(file_path) as f:
                        data = json.load(f)
                        self._process_json_file(
                            str(file_path),
                            data,
                            workouts,
                            body_metrics,
                            sleep_records,
                        )

                elif file_path.suffix == ".csv":
                    with open(file_path, newline="") as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                        self._process_csv_file(
                            str(file_path),
                            rows,
                            workouts,
                            body_metrics,
                        )

            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

        return FitnessData(
            source=self.source_name,
            workouts=workouts,
            body_metrics=body_metrics,
            sleep_records=sleep_records,
            raw_data=raw_data,
        )

    def _process_json_file(
        self,
        file_path: str,
        data: dict | list,
        workouts: list[WorkoutSession],
        body_metrics: list[BodyMetric],
        sleep_records: list[SleepRecord],
    ) -> None:
        """Process a JSON file from Google Fit Takeout."""
        file_name = Path(file_path).name.lower()

        # Activity/workout sessions
        if "sessions" in file_name or "activity" in file_name:
            sessions = parse_fit_sessions(data)
            for session in sessions:
                exercises = []
                for ex_data in session.get("exercises", []):
                    sets = []
                    for set_data in ex_data.get("sets", []):
                        sets.append(
                            SetRecord(
                                reps=set_data.get("reps", 0),
                                weight=set_data.get("weight"),
                                duration_seconds=set_data.get("duration"),
                            )
                        )
                    exercises.append(
                        ExerciseRecord(
                            name=ex_data.get("name", "Unknown"),
                            sets=sets,
                        )
                    )

                workouts.append(
                    WorkoutSession(
                        start_time=session.get("start_time", datetime.now()),
                        end_time=session.get("end_time", datetime.now()),
                        session_type=session.get("activity_type", "strength_training"),
                        exercises=exercises,
                        notes=session.get("notes", ""),
                        source=self.source_name,
                    )
                )

        # Workout-specific data with weight information
        elif "workout" in file_name or "exercise" in file_name:
            workout_data = parse_workout_data(data)
            for workout in workout_data:
                exercises = []
                for ex_data in workout.get("exercises", []):
                    sets = []
                    for set_data in ex_data.get("sets", []):
                        sets.append(
                            SetRecord(
                                reps=set_data.get("reps", 0),
                                weight=set_data.get("weight"),  # Google Fit has this!
                                duration_seconds=set_data.get("duration"),
                            )
                        )
                    exercises.append(
                        ExerciseRecord(
                            name=ex_data.get("name", "Unknown"),
                            sets=sets,
                        )
                    )

                workouts.append(
                    WorkoutSession(
                        start_time=workout.get("start_time", datetime.now()),
                        end_time=workout.get("end_time", datetime.now()),
                        session_type="strength_training",
                        exercises=exercises,
                        source=self.source_name,
                    )
                )

        # Body weight data
        elif "weight" in file_name:
            if isinstance(data, list):
                for record in data:
                    weight = record.get("value") or record.get("weight")
                    if weight:
                        body_metrics.append(
                            BodyMetric(
                                metric_type="weight",
                                value=float(weight),
                                unit="kg",
                                recorded_at=self._parse_timestamp(
                                    record.get("date") or record.get("startTime")
                                ),
                            )
                        )

        # Sleep data
        elif "sleep" in file_name:
            if isinstance(data, list):
                for record in data:
                    sleep_records.append(
                        SleepRecord(
                            start_time=self._parse_timestamp(record.get("startTime")),
                            end_time=self._parse_timestamp(record.get("endTime")),
                            stages={},
                        )
                    )

    def _process_csv_file(
        self,
        file_path: str,
        rows: list[dict],
        workouts: list[WorkoutSession],
        body_metrics: list[BodyMetric],
    ) -> None:
        """Process a CSV file from Google Fit Takeout."""
        file_name = Path(file_path).name.lower()

        # Daily activity metrics
        if "daily" in file_name:
            metrics = parse_daily_activity_metrics(rows)
            # These are general activity metrics, not directly used for programs
            pass

        # Body weight CSV
        elif "weight" in file_name:
            for row in rows:
                weight = row.get("Weight") or row.get("value") or row.get("weight")
                date = row.get("Date") or row.get("date") or row.get("startTime")
                if weight and date:
                    try:
                        body_metrics.append(
                            BodyMetric(
                                metric_type="weight",
                                value=float(weight),
                                unit="kg",
                                recorded_at=self._parse_timestamp(date),
                            )
                        )
                    except (ValueError, TypeError):
                        continue

    def _parse_timestamp(self, value: str | int | None) -> datetime:
        """Parse a timestamp value to datetime."""
        if value is None:
            return datetime.now()

        if isinstance(value, int):
            # Milliseconds since epoch
            if value > 1e12:
                value = value / 1000
            return datetime.fromtimestamp(value)

        if isinstance(value, str):
            # Try various formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue

            # Try ISO format
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass

        return datetime.now()
