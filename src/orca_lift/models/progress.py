"""Program progress tracking model."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ProgramStatus(str, Enum):
    """Program execution status."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


@dataclass
class ProgramProgress:
    """Tracks user's position and progress in a program.

    Stores the current week and day, along with timestamps
    for program start and last workout.
    """

    program_id: int
    current_week: int = 1
    current_day: int = 1
    started_at: datetime | None = None
    last_workout_at: datetime | None = None
    status: ProgramStatus = ProgramStatus.ACTIVE
    id: int | None = None

    def advance(self, total_days_per_week: int, total_weeks: int) -> bool:
        """Advance to the next workout day.

        Args:
            total_days_per_week: Number of training days per week
            total_weeks: Total weeks in the program

        Returns:
            True if advanced successfully, False if program is complete
        """
        self.last_workout_at = datetime.now()

        if self.current_day < total_days_per_week:
            self.current_day += 1
            return True

        if self.current_week < total_weeks:
            self.current_week += 1
            self.current_day = 1
            return True

        # Program complete
        self.status = ProgramStatus.COMPLETED
        return False

    def set_position(self, week: int, day: int) -> None:
        """Set position to a specific week and day."""
        self.current_week = week
        self.current_day = day

    def start(self) -> None:
        """Mark the program as started."""
        self.started_at = datetime.now()
        self.current_week = 1
        self.current_day = 1
        self.status = ProgramStatus.ACTIVE

    def pause(self) -> None:
        """Pause the program."""
        self.status = ProgramStatus.PAUSED

    def resume(self) -> None:
        """Resume a paused program."""
        self.status = ProgramStatus.ACTIVE

    def get_progress_percentage(
        self, total_days_per_week: int, total_weeks: int
    ) -> float:
        """Calculate overall progress percentage.

        Args:
            total_days_per_week: Number of training days per week
            total_weeks: Total weeks in the program

        Returns:
            Progress as a percentage (0-100)
        """
        total_workouts = total_days_per_week * total_weeks
        completed_workouts = (self.current_week - 1) * total_days_per_week + (
            self.current_day - 1
        )
        return (completed_workouts / total_workouts) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "program_id": self.program_id,
            "current_week": self.current_week,
            "current_day": self.current_day,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_workout_at": (
                self.last_workout_at.isoformat() if self.last_workout_at else None
            ),
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict, id: int | None = None) -> "ProgramProgress":
        """Create from dictionary."""
        started_at = None
        if data.get("started_at"):
            started_at = datetime.fromisoformat(data["started_at"])

        last_workout_at = None
        if data.get("last_workout_at"):
            last_workout_at = datetime.fromisoformat(data["last_workout_at"])

        return cls(
            id=id,
            program_id=data["program_id"],
            current_week=data.get("current_week", 1),
            current_day=data.get("current_day", 1),
            started_at=started_at,
            last_workout_at=last_workout_at,
            status=ProgramStatus(data.get("status", "active")),
        )

    def get_status_display(self) -> str:
        """Get a human-readable status string."""
        status_map = {
            ProgramStatus.ACTIVE: "In Progress",
            ProgramStatus.PAUSED: "Paused",
            ProgramStatus.COMPLETED: "Completed",
            ProgramStatus.ABANDONED: "Abandoned",
        }
        return status_map.get(self.status, self.status.value)

    def get_position_display(self) -> str:
        """Get a human-readable position string."""
        return f"Week {self.current_week}, Day {self.current_day}"


@dataclass
class CompletedWorkout:
    """Represents a detected completed workout from Health Connect sync."""

    program_id: int
    week: int
    day: int
    completed_at: datetime
    exercises_matched: list[str]
    match_percentage: float
    source: str = "health_connect"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "program_id": self.program_id,
            "week": self.week,
            "day": self.day,
            "completed_at": self.completed_at.isoformat(),
            "exercises_matched": self.exercises_matched,
            "match_percentage": self.match_percentage,
            "source": self.source,
        }
