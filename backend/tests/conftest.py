"""Pytest configuration and fixtures."""

import pytest
import tempfile
from pathlib import Path

from orca_lift.models.exercises import EquipmentType
from orca_lift.models.user_profile import (
    ExperienceLevel,
    FitnessGoal,
    StrengthLevel,
    UserProfile,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test.db"


@pytest.fixture
def sample_user_profile():
    """Create a sample user profile for testing."""
    return UserProfile(
        name="Test User",
        experience_level=ExperienceLevel.INTERMEDIATE,
        goals=[FitnessGoal.STRENGTH, FitnessGoal.HYPERTROPHY],
        available_equipment=[
            EquipmentType.BARBELL,
            EquipmentType.DUMBBELL,
            EquipmentType.CABLE,
            EquipmentType.MACHINE,
        ],
        schedule_days=4,
        session_duration=60,
        strength_levels=[
            StrengthLevel(exercise="Squat", weight=100, reps=5),
            StrengthLevel(exercise="Bench Press", weight=80, reps=5),
            StrengthLevel(exercise="Deadlift", weight=120, reps=5),
        ],
    )
