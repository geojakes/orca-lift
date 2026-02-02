"""User profile data models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .exercises import EquipmentType


class ExperienceLevel(str, Enum):
    """Training experience level."""

    BEGINNER = "beginner"  # < 1 year consistent training
    INTERMEDIATE = "intermediate"  # 1-3 years
    ADVANCED = "advanced"  # 3+ years


class FitnessGoal(str, Enum):
    """Primary fitness goals."""

    STRENGTH = "strength"  # Max strength, 1RM focus
    HYPERTROPHY = "hypertrophy"  # Muscle size
    POWERLIFTING = "powerlifting"  # Squat, bench, deadlift
    ENDURANCE = "endurance"  # Muscular endurance
    GENERAL_FITNESS = "general_fitness"  # Overall health
    ATHLETIC = "athletic"  # Sport-specific performance
    FAT_LOSS = "fat_loss"  # Weight loss while preserving muscle


@dataclass
class StrengthLevel:
    """Current strength levels for major lifts."""

    exercise: str
    weight: float  # in kg
    reps: int
    is_estimated_1rm: bool = False

    @property
    def estimated_1rm(self) -> float:
        """Calculate estimated 1RM using Epley formula."""
        if self.is_estimated_1rm:
            return self.weight
        if self.reps == 1:
            return self.weight
        return self.weight * (1 + self.reps / 30)


@dataclass
class Limitation:
    """Injury or movement limitation."""

    description: str
    affected_exercises: list[str] = field(default_factory=list)
    severity: str = "moderate"  # mild, moderate, severe


@dataclass
class UserProfile:
    """Complete user fitness profile."""

    name: str
    experience_level: ExperienceLevel
    goals: list[FitnessGoal]
    available_equipment: list[EquipmentType]
    schedule_days: int  # Training days per week
    session_duration: int = 60  # Minutes per session
    strength_levels: list[StrengthLevel] = field(default_factory=list)
    limitations: list[Limitation] = field(default_factory=list)
    age: int | None = None
    body_weight: float | None = None  # in kg
    notes: str = ""
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "experience_level": self.experience_level.value,
            "goals": [g.value for g in self.goals],
            "available_equipment": [eq.value for eq in self.available_equipment],
            "schedule_days": self.schedule_days,
            "session_duration": self.session_duration,
            "strength_levels": [
                {
                    "exercise": sl.exercise,
                    "weight": sl.weight,
                    "reps": sl.reps,
                    "is_estimated_1rm": sl.is_estimated_1rm,
                }
                for sl in self.strength_levels
            ],
            "limitations": [
                {
                    "description": lim.description,
                    "affected_exercises": lim.affected_exercises,
                    "severity": lim.severity,
                }
                for lim in self.limitations
            ],
            "age": self.age,
            "body_weight": self.body_weight,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
        id: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> "UserProfile":
        """Create from dictionary."""
        return cls(
            id=id,
            name=data["name"],
            experience_level=ExperienceLevel(data["experience_level"]),
            goals=[FitnessGoal(g) for g in data["goals"]],
            available_equipment=[EquipmentType(eq) for eq in data["available_equipment"]],
            schedule_days=data["schedule_days"],
            session_duration=data.get("session_duration", 60),
            strength_levels=[
                StrengthLevel(
                    exercise=sl["exercise"],
                    weight=sl["weight"],
                    reps=sl["reps"],
                    is_estimated_1rm=sl.get("is_estimated_1rm", False),
                )
                for sl in data.get("strength_levels", [])
            ],
            limitations=[
                Limitation(
                    description=lim["description"],
                    affected_exercises=lim.get("affected_exercises", []),
                    severity=lim.get("severity", "moderate"),
                )
                for lim in data.get("limitations", [])
            ],
            age=data.get("age"),
            body_weight=data.get("body_weight"),
            notes=data.get("notes", ""),
            created_at=created_at,
            updated_at=updated_at,
        )

    def get_summary(self) -> str:
        """Generate a summary for AI context."""
        summary = f"User: {self.name}\n"
        summary += f"Experience: {self.experience_level.value}\n"
        summary += f"Goals: {', '.join(g.value for g in self.goals)}\n"
        summary += f"Training days: {self.schedule_days}/week, {self.session_duration} min/session\n"
        summary += f"Equipment: {', '.join(eq.value for eq in self.available_equipment)}\n"

        if self.strength_levels:
            summary += "Current strength:\n"
            for sl in self.strength_levels:
                summary += f"  - {sl.exercise}: {sl.weight}kg x {sl.reps} (est. 1RM: {sl.estimated_1rm:.1f}kg)\n"

        if self.limitations:
            summary += "Limitations:\n"
            for lim in self.limitations:
                summary += f"  - {lim.description} ({lim.severity})\n"

        if self.body_weight:
            summary += f"Body weight: {self.body_weight}kg\n"

        if self.notes:
            summary += f"Notes: {self.notes}\n"

        return summary
