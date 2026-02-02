"""Tests for data models."""

import pytest

from orca_lift.models.exercises import (
    COMMON_EXERCISES,
    EquipmentType,
    Exercise,
    MovementPattern,
    MuscleGroup,
)
from orca_lift.models.program import (
    Program,
    ProgramDay,
    ProgramExercise,
    ProgramWeek,
    ProgressionScheme,
    SetScheme,
)
from orca_lift.models.user_profile import (
    ExperienceLevel,
    FitnessGoal,
    Limitation,
    StrengthLevel,
    UserProfile,
)


class TestExercise:
    """Tests for Exercise model."""

    def test_exercise_to_dict(self):
        """Test exercise serialization."""
        exercise = Exercise(
            name="Bench Press",
            muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS],
            movement_pattern=MovementPattern.PUSH_HORIZONTAL,
            equipment=[EquipmentType.BARBELL],
            aliases=["BB Bench"],
        )
        data = exercise.to_dict()

        assert data["name"] == "Bench Press"
        assert "chest" in data["muscle_groups"]
        assert "triceps" in data["muscle_groups"]
        assert data["movement_pattern"] == "push_horizontal"
        assert "barbell" in data["equipment"]
        assert "BB Bench" in data["aliases"]

    def test_exercise_from_dict(self):
        """Test exercise deserialization."""
        data = {
            "name": "Squat",
            "muscle_groups": ["quads", "glutes"],
            "movement_pattern": "squat",
            "equipment": ["barbell"],
            "aliases": [],
        }
        exercise = Exercise.from_dict(data)

        assert exercise.name == "Squat"
        assert MuscleGroup.QUADS in exercise.muscle_groups
        assert exercise.movement_pattern == MovementPattern.SQUAT

    def test_common_exercises_populated(self):
        """Test that common exercises are populated."""
        assert len(COMMON_EXERCISES) > 0

        # Check some key exercises exist
        names = [e.name for e in COMMON_EXERCISES]
        assert "Bench Press" in names
        assert "Squat" in names
        assert "Deadlift" in names


class TestUserProfile:
    """Tests for UserProfile model."""

    def test_profile_to_dict(self):
        """Test profile serialization."""
        profile = UserProfile(
            name="Test User",
            experience_level=ExperienceLevel.INTERMEDIATE,
            goals=[FitnessGoal.STRENGTH, FitnessGoal.HYPERTROPHY],
            available_equipment=[EquipmentType.BARBELL, EquipmentType.DUMBBELL],
            schedule_days=4,
            strength_levels=[
                StrengthLevel(exercise="Squat", weight=100, reps=5),
            ],
        )
        data = profile.to_dict()

        assert data["name"] == "Test User"
        assert data["experience_level"] == "intermediate"
        assert "strength" in data["goals"]
        assert data["schedule_days"] == 4
        assert len(data["strength_levels"]) == 1

    def test_profile_from_dict(self):
        """Test profile deserialization."""
        data = {
            "name": "Test",
            "experience_level": "beginner",
            "goals": ["strength"],
            "available_equipment": ["barbell"],
            "schedule_days": 3,
            "session_duration": 60,
            "strength_levels": [],
            "limitations": [],
        }
        profile = UserProfile.from_dict(data)

        assert profile.name == "Test"
        assert profile.experience_level == ExperienceLevel.BEGINNER
        assert FitnessGoal.STRENGTH in profile.goals

    def test_strength_level_estimated_1rm(self):
        """Test 1RM estimation."""
        # 100kg x 5 reps
        sl = StrengthLevel(exercise="Squat", weight=100, reps=5)

        # Epley formula: weight * (1 + reps/30) = 100 * (1 + 5/30) = 116.67
        assert abs(sl.estimated_1rm - 116.67) < 0.1

    def test_strength_level_1rm_is_1rm(self):
        """Test 1RM when already a 1RM."""
        sl = StrengthLevel(exercise="Squat", weight=150, reps=1)
        assert sl.estimated_1rm == 150

    def test_profile_summary(self):
        """Test profile summary generation."""
        profile = UserProfile(
            name="Test User",
            experience_level=ExperienceLevel.INTERMEDIATE,
            goals=[FitnessGoal.STRENGTH],
            available_equipment=[EquipmentType.BARBELL],
            schedule_days=4,
            strength_levels=[
                StrengthLevel(exercise="Squat", weight=100, reps=5),
            ],
            limitations=[
                Limitation(description="Bad shoulder", severity="moderate"),
            ],
        )
        summary = profile.get_summary()

        assert "Test User" in summary
        assert "intermediate" in summary
        assert "4/week" in summary
        assert "Squat" in summary
        assert "Bad shoulder" in summary


class TestProgram:
    """Tests for Program model."""

    def test_program_to_dict(self):
        """Test program serialization."""
        program = Program(
            name="Test Program",
            description="A test",
            goals="Build strength",
            weeks=[
                ProgramWeek(
                    week_number=1,
                    days=[
                        ProgramDay(
                            name="Day 1",
                            focus="Push",
                            exercises=[
                                ProgramExercise(
                                    name="Bench Press",
                                    sets=[SetScheme(reps=5)],
                                )
                            ],
                        )
                    ],
                )
            ],
        )
        data = program.to_dict()

        assert data["name"] == "Test Program"
        assert data["goals"] == "Build strength"
        assert len(data["weeks"]) == 1
        assert data["weeks"][0]["days"][0]["exercises"][0]["name"] == "Bench Press"

    def test_program_from_dict(self):
        """Test program deserialization."""
        data = {
            "name": "Test",
            "description": "A test",
            "goals": "Build muscle",
            "weeks": [
                {
                    "week_number": 1,
                    "days": [
                        {
                            "name": "Day 1",
                            "focus": "Push",
                            "exercises": [
                                {
                                    "name": "Bench Press",
                                    "sets": [{"reps": 8}],
                                    "progression": "dp",
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        program = Program.from_dict(data)

        assert program.name == "Test"
        assert program.days_per_week == 1
        assert program.total_weeks == 1

    def test_program_days_per_week(self):
        """Test days per week calculation."""
        program = Program(
            name="Test",
            description="",
            goals="",
            weeks=[
                ProgramWeek(
                    week_number=1,
                    days=[
                        ProgramDay(name="Day 1", exercises=[]),
                        ProgramDay(name="Day 2", exercises=[]),
                        ProgramDay(name="Day 3", exercises=[]),
                    ],
                )
            ],
        )
        assert program.days_per_week == 3

    def test_program_summary(self):
        """Test program summary generation."""
        program = Program(
            name="Strength Builder",
            description="4-day program",
            goals="Build strength",
            weeks=[
                ProgramWeek(
                    week_number=1,
                    days=[
                        ProgramDay(
                            name="Day 1",
                            focus="Push",
                            exercises=[
                                ProgramExercise(
                                    name="Bench Press",
                                    sets=[
                                        SetScheme(reps=5),
                                        SetScheme(reps=5),
                                        SetScheme(reps=5),
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
        )
        summary = program.get_summary()

        assert "Strength Builder" in summary
        assert "Day 1" in summary or "Push" in summary
        assert "Bench Press" in summary
        assert "3x5" in summary


class TestSetScheme:
    """Tests for SetScheme model."""

    def test_set_scheme_defaults(self):
        """Test SetScheme default values."""
        set_scheme = SetScheme(reps=10)

        assert set_scheme.reps == 10
        assert set_scheme.weight_percent is None
        assert set_scheme.rpe is None
        assert set_scheme.is_amrap is False
        assert set_scheme.is_warmup is False

    def test_set_scheme_with_all_fields(self):
        """Test SetScheme with all fields."""
        set_scheme = SetScheme(
            reps=5,
            weight_percent=0.85,
            rpe=8.5,
            is_amrap=True,
            rest_seconds=180,
        )

        assert set_scheme.reps == 5
        assert set_scheme.weight_percent == 0.85
        assert set_scheme.rpe == 8.5
        assert set_scheme.is_amrap is True
        assert set_scheme.rest_seconds == 180
