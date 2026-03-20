"""Workout session tracking models for OrcaFit."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class WorkoutStatus(str, Enum):
    """Status of a workout session."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    PAUSED = "paused"


@dataclass
class LoggedSet:
    """A single logged set during a workout.
    
    Supports both resistance (weight/reps) and cardio (duration/distance/HR) tracking.
    """
    set_number: int
    # Resistance tracking
    weight_kg: float | None = None
    reps: int | None = None
    rpe: float | None = None  # 1-10 scale
    # Cardio tracking
    duration_seconds: int | None = None
    distance_meters: float | None = None
    heart_rate_avg: int | None = None
    heart_rate_max: int | None = None
    pace_per_km_seconds: int | None = None
    calories: int | None = None
    # Timing
    rest_seconds: int | None = None
    completed_at: datetime | None = None
    # Meta
    notes: str | None = None
    is_pr: bool = False  # Auto-detected personal record
    is_warmup: bool = False
    id: int | None = None

    def to_dict(self) -> dict:
        return {
            "set_number": self.set_number,
            "weight_kg": self.weight_kg,
            "reps": self.reps,
            "rpe": self.rpe,
            "duration_seconds": self.duration_seconds,
            "distance_meters": self.distance_meters,
            "heart_rate_avg": self.heart_rate_avg,
            "heart_rate_max": self.heart_rate_max,
            "pace_per_km_seconds": self.pace_per_km_seconds,
            "calories": self.calories,
            "rest_seconds": self.rest_seconds,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
            "is_pr": self.is_pr,
            "is_warmup": self.is_warmup,
        }

    @classmethod
    def from_dict(cls, data: dict, id: int | None = None) -> "LoggedSet":
        return cls(
            id=id,
            set_number=data["set_number"],
            weight_kg=data.get("weight_kg"),
            reps=data.get("reps"),
            rpe=data.get("rpe"),
            duration_seconds=data.get("duration_seconds"),
            distance_meters=data.get("distance_meters"),
            heart_rate_avg=data.get("heart_rate_avg"),
            heart_rate_max=data.get("heart_rate_max"),
            pace_per_km_seconds=data.get("pace_per_km_seconds"),
            calories=data.get("calories"),
            rest_seconds=data.get("rest_seconds"),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data.get("completed_at") else None
            ),
            notes=data.get("notes"),
            is_pr=data.get("is_pr", False),
            is_warmup=data.get("is_warmup", False),
        )


@dataclass
class WorkoutExercise:
    """An exercise within a workout session, with logged sets."""
    exercise_id: str  # References the exercise slug/name
    exercise_name: str
    order: int
    target_sets: int = 0  # How many sets were prescribed
    logged_sets: list[LoggedSet] = field(default_factory=list)
    skipped: bool = False
    notes: str = ""
    id: int | None = None

    def to_dict(self) -> dict:
        return {
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise_name,
            "order": self.order,
            "target_sets": self.target_sets,
            "logged_sets": [s.to_dict() for s in self.logged_sets],
            "skipped": self.skipped,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict, id: int | None = None) -> "WorkoutExercise":
        return cls(
            id=id,
            exercise_id=data["exercise_id"],
            exercise_name=data.get("exercise_name", data["exercise_id"]),
            order=data.get("order", 0),
            target_sets=data.get("target_sets", 0),
            logged_sets=[LoggedSet.from_dict(s) for s in data.get("logged_sets", [])],
            skipped=data.get("skipped", False),
            notes=data.get("notes", ""),
        )

    @property
    def completed_sets(self) -> int:
        """Number of non-warmup sets completed."""
        return sum(1 for s in self.logged_sets if not s.is_warmup)

    @property
    def total_volume_kg(self) -> float:
        """Total volume (weight x reps) for resistance exercises."""
        return sum(
            (s.weight_kg or 0) * (s.reps or 0)
            for s in self.logged_sets
            if not s.is_warmup
        )


@dataclass
class Workout:
    """A complete workout session."""
    program_id: int
    week_number: int
    day_number: int
    day_name: str = ""
    status: WorkoutStatus = WorkoutStatus.PLANNED
    exercises: list[WorkoutExercise] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str = ""
    total_duration_seconds: int | None = None
    user_id: int | None = None
    id: int | None = None

    def to_dict(self) -> dict:
        return {
            "program_id": self.program_id,
            "week_number": self.week_number,
            "day_number": self.day_number,
            "day_name": self.day_name,
            "status": self.status.value,
            "exercises": [ex.to_dict() for ex in self.exercises],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
            "total_duration_seconds": self.total_duration_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict, id: int | None = None, user_id: int | None = None) -> "Workout":
        started = data.get("started_at")
        completed = data.get("completed_at")
        return cls(
            id=id,
            user_id=user_id,
            program_id=data["program_id"],
            week_number=data["week_number"],
            day_number=data["day_number"],
            day_name=data.get("day_name", ""),
            status=WorkoutStatus(data.get("status", "planned")),
            exercises=[WorkoutExercise.from_dict(ex) for ex in data.get("exercises", [])],
            started_at=datetime.fromisoformat(started) if started else None,
            completed_at=datetime.fromisoformat(completed) if completed else None,
            notes=data.get("notes", ""),
            total_duration_seconds=data.get("total_duration_seconds"),
        )

    @property
    def total_volume_kg(self) -> float:
        """Total workout volume in kg."""
        return sum(ex.total_volume_kg for ex in self.exercises)

    @property
    def exercises_completed(self) -> int:
        """Number of exercises with at least one logged set."""
        return sum(1 for ex in self.exercises if ex.completed_sets > 0)

    @property
    def is_active(self) -> bool:
        return self.status in (WorkoutStatus.IN_PROGRESS, WorkoutStatus.PAUSED)


@dataclass
class PersonalRecord:
    """A personal record for an exercise."""
    exercise_id: str
    exercise_name: str
    record_type: str  # "1rm", "max_reps", "max_weight", "max_volume", "max_distance", "best_pace"
    value: float
    unit: str  # "kg", "reps", "kg*reps", "meters", "seconds"
    achieved_at: datetime | None = None
    workout_id: int | None = None
    previous_value: float | None = None
    id: int | None = None

    def to_dict(self) -> dict:
        return {
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise_name,
            "record_type": self.record_type,
            "value": self.value,
            "unit": self.unit,
            "achieved_at": self.achieved_at.isoformat() if self.achieved_at else None,
            "workout_id": self.workout_id,
            "previous_value": self.previous_value,
        }
