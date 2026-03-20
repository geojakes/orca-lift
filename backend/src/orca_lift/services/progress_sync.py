"""Progress sync service for Health Connect integration."""

import sqlite3
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ..models.program import Program
from ..models.progress import CompletedWorkout, ProgramProgress


# Health Connect exercise type mappings
# Maps Health Connect exercise segment types to common exercise names
HEALTH_CONNECT_EXERCISE_MAP = {
    "BENCH_PRESS": ["Bench Press", "Dumbbell Bench Press", "Incline Bench Press"],
    "SQUAT": ["Squat", "Front Squat", "Goblet Squat", "Leg Press"],
    "DEADLIFT": ["Deadlift", "Romanian Deadlift", "Trap Bar Deadlift"],
    "SHOULDER_PRESS": ["Overhead Press", "Dumbbell Shoulder Press", "Arnold Press"],
    "LAT_PULLDOWN": ["Lat Pulldown", "Pull Up", "Chin Up"],
    "ROWING": ["Barbell Row", "Dumbbell Row", "Cable Row", "T-Bar Row"],
    "BICEP_CURL": ["Barbell Curl", "Dumbbell Curl", "Hammer Curl", "EZ Bar Curl"],
    "TRICEP_EXTENSION": ["Tricep Pushdown", "Skull Crusher", "Overhead Tricep Extension"],
    "LEG_PRESS": ["Leg Press", "Hack Squat"],
    "LEG_CURL": ["Leg Curl", "Seated Leg Curl", "Nordic Hamstring Curl"],
    "LEG_EXTENSION": ["Leg Extension"],
    "CALF_RAISE": ["Standing Calf Raise", "Seated Calf Raise", "Dumbbell Calf Raise"],
    "CRUNCH": ["Crunch", "Cable Crunch", "Decline Crunch"],
    "PLANK": ["Plank", "Side Plank"],
    "LUNGE": ["Lunge", "Dumbbell Lunge", "Bulgarian Split Squat", "Step Up"],
    "HIP_THRUST": ["Hip Thrust", "Glute Bridge"],
    "DUMBBELL_FLY": ["Dumbbell Fly", "Cable Fly", "Pec Deck"],
    "LATERAL_RAISE": ["Lateral Raise", "Cable Lateral Raise", "Front Raise"],
    "FACE_PULL": ["Face Pull", "Rear Delt Fly"],
    "PULL_UP": ["Pull Up", "Chin Up", "Neutral Grip Pull Up"],
    "PUSH_UP": ["Push Up", "Diamond Push Up"],
    "DIP": ["Chest Dip", "Tricep Dip"],
    "SHRUG": ["Shrug", "Dumbbell Shrug"],
    "GOOD_MORNING": ["Good Morning", "Back Extension"],
    "CLEAN": ["Clean", "Hang Clean", "Power Clean"],
    "SNATCH": ["Snatch", "Hang Snatch", "Dumbbell Snatch"],
    "KETTLEBELL_SWING": ["Kettlebell Swing"],
}


@dataclass
class HealthConnectWorkout:
    """Parsed workout from Health Connect data."""

    session_id: str
    start_time: datetime
    end_time: datetime
    exercise_types: list[str]
    total_reps: int


class ProgressSyncService:
    """Service for syncing program progress with Health Connect data."""

    def __init__(self, match_threshold: float = 0.7):
        """Initialize the sync service.

        Args:
            match_threshold: Minimum percentage of exercises that must match
                to consider a workout day complete (0.0 - 1.0)
        """
        self.match_threshold = match_threshold

    async def sync_from_health_connect(
        self,
        program: Program,
        progress: ProgramProgress,
        health_connect_backup: Path,
    ) -> list[CompletedWorkout]:
        """Sync progress from Health Connect backup.

        Analyzes workout sessions from Health Connect to detect completed
        program days and returns a list of detected completed workouts.

        Args:
            program: The program to sync progress for
            progress: Current progress state
            health_connect_backup: Path to Health Connect backup (zip or sqlite)

        Returns:
            List of detected completed workouts
        """
        # Extract/open the database
        db_path = self._get_database_path(health_connect_backup)
        if not db_path:
            raise ValueError("Could not find Health Connect database in backup")

        # Parse workouts from database
        workouts = self._parse_workouts(db_path)

        # Filter to workouts after program start
        if progress.started_at:
            workouts = [w for w in workouts if w.start_time >= progress.started_at]

        # Match workouts to program days
        completed = self._match_workouts_to_program(program, progress, workouts)

        return completed

    def _get_database_path(self, backup_path: Path) -> Path | None:
        """Extract or locate the Health Connect SQLite database.

        Args:
            backup_path: Path to backup file (zip or sqlite)

        Returns:
            Path to SQLite database or None if not found
        """
        if backup_path.suffix == ".db" or backup_path.suffix == ".sqlite":
            return backup_path

        if backup_path.suffix == ".zip":
            # Extract from zip
            extract_dir = backup_path.parent / "hc_temp"
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(backup_path, "r") as zf:
                # Look for database files
                for name in zf.namelist():
                    if name.endswith(".db") or name.endswith(".sqlite"):
                        zf.extract(name, extract_dir)
                        return extract_dir / name

                    # Health Connect backup structure
                    if "health_connect" in name.lower() and name.endswith(".db"):
                        zf.extract(name, extract_dir)
                        return extract_dir / name

        return None

    def _parse_workouts(self, db_path: Path) -> list[HealthConnectWorkout]:
        """Parse workout sessions from Health Connect database.

        Args:
            db_path: Path to SQLite database

        Returns:
            List of parsed workouts
        """
        workouts = []

        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Query exercise sessions
            # Health Connect schema varies, try common table names
            tables = self._get_table_names(cursor)

            sessions_table = None
            segments_table = None

            for table in tables:
                lower = table.lower()
                if "exercise_session" in lower and "record" in lower:
                    sessions_table = table
                elif "exercise_segment" in lower:
                    segments_table = table

            if not sessions_table:
                # Fallback to generic query
                return self._parse_generic_workouts(cursor)

            # Query sessions
            cursor.execute(f"""
                SELECT * FROM {sessions_table}
                WHERE exercise_type IS NOT NULL
                ORDER BY start_time DESC
            """)

            session_rows = cursor.fetchall()

            for row in session_rows:
                try:
                    session_id = str(row["id"]) if "id" in row.keys() else str(row[0])
                    start_time = self._parse_timestamp(row["start_time"])
                    end_time = self._parse_timestamp(row["end_time"])

                    # Get exercise segments for this session
                    exercise_types = []
                    total_reps = 0

                    if segments_table:
                        cursor.execute(f"""
                            SELECT * FROM {segments_table}
                            WHERE session_id = ?
                        """, (session_id,))

                        for seg in cursor.fetchall():
                            if "exercise_type" in seg.keys():
                                exercise_types.append(seg["exercise_type"])
                            if "repetitions" in seg.keys():
                                total_reps += seg["repetitions"] or 0

                    workouts.append(HealthConnectWorkout(
                        session_id=session_id,
                        start_time=start_time,
                        end_time=end_time,
                        exercise_types=exercise_types,
                        total_reps=total_reps,
                    ))
                except Exception:
                    continue

            conn.close()

        except sqlite3.Error:
            pass

        return workouts

    def _parse_generic_workouts(self, cursor: sqlite3.Cursor) -> list[HealthConnectWorkout]:
        """Fallback workout parsing for non-standard databases."""
        # Try to find any workout-like data
        workouts = []

        tables = self._get_table_names(cursor)
        for table in tables:
            if "workout" in table.lower() or "exercise" in table.lower():
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                    rows = cursor.fetchall()
                    # Process rows if they look like workout data
                    for row in rows:
                        cols = row.keys() if hasattr(row, "keys") else []
                        if any("time" in c.lower() for c in cols):
                            # This might be workout data
                            pass
                except sqlite3.Error:
                    continue

        return workouts

    def _get_table_names(self, cursor: sqlite3.Cursor) -> list[str]:
        """Get all table names from database."""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]

    def _parse_timestamp(self, value: Any) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            # Unix timestamp (seconds or milliseconds)
            if value > 1e12:
                value = value / 1000
            return datetime.fromtimestamp(value)
        if isinstance(value, str):
            # ISO format
            for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                try:
                    return datetime.strptime(value[:19], fmt)
                except ValueError:
                    continue
        raise ValueError(f"Cannot parse timestamp: {value}")

    def _match_workouts_to_program(
        self,
        program: Program,
        progress: ProgramProgress,
        workouts: list[HealthConnectWorkout],
    ) -> list[CompletedWorkout]:
        """Match Health Connect workouts to program days.

        Args:
            program: The program
            progress: Current progress
            workouts: Parsed Health Connect workouts

        Returns:
            List of detected completed workouts
        """
        completed = []

        # Build lookup of program days
        program_days: list[tuple[int, int, list[str]]] = []
        for week_idx, week in enumerate(program.weeks):
            for day_idx, day in enumerate(week.days):
                exercise_names = [ex.name for ex in day.exercises]
                program_days.append((week_idx + 1, day_idx + 1, exercise_names))

        # Try to match each workout to a program day
        for workout in sorted(workouts, key=lambda w: w.start_time):
            best_match = None
            best_match_pct = 0.0
            best_exercises = []

            # Convert Health Connect exercise types to possible exercise names
            workout_exercises = set()
            for ex_type in workout.exercise_types:
                if ex_type in HEALTH_CONNECT_EXERCISE_MAP:
                    workout_exercises.update(HEALTH_CONNECT_EXERCISE_MAP[ex_type])

            for week, day, exercises in program_days:
                # Skip days before current progress
                if (week, day) < (progress.current_week, progress.current_day):
                    continue

                # Calculate match percentage
                matched = []
                for ex_name in exercises:
                    if ex_name in workout_exercises:
                        matched.append(ex_name)
                    else:
                        # Try fuzzy matching
                        for wex in workout_exercises:
                            if self._exercises_match(ex_name, wex):
                                matched.append(ex_name)
                                break

                match_pct = len(matched) / len(exercises) if exercises else 0

                if match_pct > best_match_pct and match_pct >= self.match_threshold:
                    best_match = (week, day)
                    best_match_pct = match_pct
                    best_exercises = matched

            if best_match:
                completed.append(CompletedWorkout(
                    program_id=program.id,
                    week=best_match[0],
                    day=best_match[1],
                    completed_at=workout.end_time,
                    exercises_matched=best_exercises,
                    match_percentage=best_match_pct,
                    source="health_connect",
                ))

        return completed

    def _exercises_match(self, program_ex: str, workout_ex: str) -> bool:
        """Check if two exercise names likely refer to the same exercise."""
        # Normalize names
        p = program_ex.lower().replace("-", " ").replace("_", " ")
        w = workout_ex.lower().replace("-", " ").replace("_", " ")

        # Exact match
        if p == w:
            return True

        # One contains the other
        if p in w or w in p:
            return True

        # Common words match
        p_words = set(p.split())
        w_words = set(w.split())
        common = p_words & w_words

        # At least 2 significant words in common
        significant = {"bench", "squat", "deadlift", "press", "curl", "row", "raise"}
        if len(common & significant) >= 1:
            return True

        return False
