"""Database model definitions (for reference and type hints)."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class DBUserProfile:
    """Database representation of a user profile."""

    id: int
    name: str
    experience_level: str
    goals: str  # JSON string
    available_equipment: str  # JSON string
    schedule_days: int
    session_duration: int
    strength_levels: str  # JSON string
    limitations: str  # JSON string
    age: int | None
    body_weight: float | None
    notes: str
    created_at: datetime
    updated_at: datetime


@dataclass
class DBFitnessData:
    """Database representation of fitness data."""

    id: int
    profile_id: int | None
    source: str
    data_type: str
    data: str  # JSON string
    recorded_at: datetime | None
    imported_at: datetime


@dataclass
class DBProgram:
    """Database representation of a program."""

    id: int
    profile_id: int | None
    name: str
    description: str
    goals: str
    structure: str  # JSON string
    liftoscript: str
    congregation_log: str  # JSON string
    created_at: datetime


@dataclass
class DBExercise:
    """Database representation of an exercise."""

    id: int
    name: str
    aliases: str  # JSON string
    muscle_groups: str  # JSON string
    equipment: str  # JSON string
    movement_pattern: str
