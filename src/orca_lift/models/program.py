"""Training program data models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProgressionScheme(str, Enum):
    """Progression schemes supported by Liftosaur."""

    LINEAR = "lp"  # Linear progression
    DOUBLE = "dp"  # Double progression (weight after hitting top of rep range)
    SUM = "sum"  # Sum progression (total reps across sets)
    CUSTOM = "custom"  # Custom Liftoscript logic


@dataclass
class SetScheme:
    """Defines a set structure."""

    reps: int | str  # int or "5+" for AMRAP
    weight_percent: float | None = None  # Percentage of 1RM or working weight
    rpe: float | None = None  # Rate of perceived exertion
    is_amrap: bool = False
    is_warmup: bool = False
    rest_seconds: int | None = None


@dataclass
class ProgramExercise:
    """An exercise within a training day."""

    name: str
    sets: list[SetScheme]
    progression: ProgressionScheme = ProgressionScheme.DOUBLE
    progression_params: dict = field(default_factory=dict)
    notes: str = ""
    superset_with: str | None = None  # Name of exercise to superset with

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "sets": [
                {
                    "reps": s.reps,
                    "weight_percent": s.weight_percent,
                    "rpe": s.rpe,
                    "is_amrap": s.is_amrap,
                    "is_warmup": s.is_warmup,
                    "rest_seconds": s.rest_seconds,
                }
                for s in self.sets
            ],
            "progression": self.progression.value,
            "progression_params": self.progression_params,
            "notes": self.notes,
            "superset_with": self.superset_with,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProgramExercise":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            sets=[
                SetScheme(
                    reps=s["reps"],
                    weight_percent=s.get("weight_percent"),
                    rpe=s.get("rpe"),
                    is_amrap=s.get("is_amrap", False),
                    is_warmup=s.get("is_warmup", False),
                    rest_seconds=s.get("rest_seconds"),
                )
                for s in data["sets"]
            ],
            progression=ProgressionScheme(data.get("progression", "dp")),
            progression_params=data.get("progression_params", {}),
            notes=data.get("notes", ""),
            superset_with=data.get("superset_with"),
        )


@dataclass
class ProgramDay:
    """A single training day."""

    name: str
    exercises: list[ProgramExercise]
    focus: str = ""  # e.g., "Push", "Lower Body", "Full Body"
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "exercises": [ex.to_dict() for ex in self.exercises],
            "focus": self.focus,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProgramDay":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            exercises=[ProgramExercise.from_dict(ex) for ex in data["exercises"]],
            focus=data.get("focus", ""),
            notes=data.get("notes", ""),
        )


@dataclass
class ProgramWeek:
    """A week in the program (for periodization)."""

    week_number: int
    days: list[ProgramDay]
    deload: bool = False
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "week_number": self.week_number,
            "days": [day.to_dict() for day in self.days],
            "deload": self.deload,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProgramWeek":
        """Create from dictionary."""
        return cls(
            week_number=data["week_number"],
            days=[ProgramDay.from_dict(day) for day in data["days"]],
            deload=data.get("deload", False),
            notes=data.get("notes", ""),
        )


@dataclass
class Program:
    """A complete training program."""

    name: str
    description: str
    weeks: list[ProgramWeek]
    goals: str  # Original user request
    congregation_log: list[dict] = field(default_factory=list)  # Deliberation history
    liftoscript: str = ""  # Generated Liftoscript code
    id: int | None = None
    profile_id: int | None = None
    created_at: datetime | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "description": self.description,
            "weeks": [week.to_dict() for week in self.weeks],
            "goals": self.goals,
            "congregation_log": self.congregation_log,
            "liftoscript": self.liftoscript,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
        id: int | None = None,
        profile_id: int | None = None,
        created_at: datetime | None = None,
    ) -> "Program":
        """Create from dictionary."""
        return cls(
            id=id,
            profile_id=profile_id,
            name=data["name"],
            description=data["description"],
            weeks=[ProgramWeek.from_dict(week) for week in data["weeks"]],
            goals=data["goals"],
            congregation_log=data.get("congregation_log", []),
            liftoscript=data.get("liftoscript", ""),
            created_at=created_at,
        )

    @property
    def days_per_week(self) -> int:
        """Get the number of training days per week."""
        if not self.weeks:
            return 0
        return len(self.weeks[0].days)

    @property
    def total_weeks(self) -> int:
        """Get total number of weeks."""
        return len(self.weeks)

    def get_summary(self) -> str:
        """Generate a summary of the program."""
        summary = f"Program: {self.name}\n"
        summary += f"Description: {self.description}\n"
        summary += f"Duration: {self.total_weeks} weeks, {self.days_per_week} days/week\n\n"

        for week in self.weeks:
            week_label = f"Week {week.week_number}"
            if week.deload:
                week_label += " (Deload)"
            summary += f"{week_label}:\n"

            for day in week.days:
                summary += f"  {day.name}"
                if day.focus:
                    summary += f" - {day.focus}"
                summary += ":\n"

                for ex in day.exercises:
                    set_info = self._format_sets(ex.sets)
                    summary += f"    - {ex.name}: {set_info}\n"

            summary += "\n"

        return summary

    def _format_sets(self, sets: list[SetScheme]) -> str:
        """Format sets for display."""
        # Group similar sets
        working_sets = [s for s in sets if not s.is_warmup]
        if not working_sets:
            return "No working sets"

        # Check if all sets are identical
        first_set = working_sets[0]
        all_same = all(s.reps == first_set.reps for s in working_sets)

        if all_same:
            reps = first_set.reps
            if first_set.is_amrap:
                reps = f"{reps}+"
            return f"{len(working_sets)}x{reps}"
        else:
            return ", ".join(
                f"{s.reps}{'+'if s.is_amrap else ''}" for s in working_sets
            )
