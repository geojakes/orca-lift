"""Tests for Liftoscript generator."""

import pytest

from orca_lift.generators.liftoscript import (
    GeneratorConfig,
    LiftoscriptGenerator,
    generate_liftoscript,
)
from orca_lift.models.program import (
    Program,
    ProgramDay,
    ProgramExercise,
    ProgramWeek,
    ProgressionScheme,
    SetScheme,
)


@pytest.fixture
def sample_program():
    """Create a sample program for testing."""
    return Program(
        name="Test Program",
        description="A test program for unit tests",
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
                                    SetScheme(reps=5),
                                ],
                                progression=ProgressionScheme.LINEAR,
                                progression_params={"increment": 5},
                            ),
                            ProgramExercise(
                                name="Overhead Press",
                                sets=[
                                    SetScheme(reps="8-10"),
                                    SetScheme(reps="8-10"),
                                    SetScheme(reps="8-10"),
                                ],
                                progression=ProgressionScheme.DOUBLE,
                                progression_params={"increment": 2.5},
                            ),
                        ],
                    ),
                    ProgramDay(
                        name="Day 2",
                        focus="Pull",
                        exercises=[
                            ProgramExercise(
                                name="Deadlift",
                                sets=[
                                    SetScheme(reps=5),
                                    SetScheme(reps=5),
                                    SetScheme(reps=5, is_amrap=True),
                                ],
                                progression=ProgressionScheme.LINEAR,
                                progression_params={"increment": 10},
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


class TestLiftoscriptGenerator:
    """Tests for LiftoscriptGenerator class."""

    def test_generate_basic_program(self, sample_program):
        """Test basic program generation."""
        generator = LiftoscriptGenerator()
        result = generator.generate(sample_program)

        assert "Test Program" in result
        assert "Day 1" in result
        assert "Push" in result
        assert "Bench Press" in result
        assert "4x5" in result
        assert "lp(5lb)" in result

    def test_generate_with_rep_range(self, sample_program):
        """Test generation with rep ranges."""
        generator = LiftoscriptGenerator()
        result = generator.generate(sample_program)

        # Should have rep range for OHP
        assert "Overhead Press" in result
        assert "3x8-10" in result
        assert "dp(" in result

    def test_generate_with_amrap(self, sample_program):
        """Test generation with AMRAP sets."""
        generator = LiftoscriptGenerator()
        result = generator.generate(sample_program)

        # Deadlift has AMRAP final set
        assert "Deadlift" in result
        # Format should be like "1x5, 1x5, 1x5+"
        assert "5+" in result

    def test_generate_with_kg_unit(self, sample_program):
        """Test generation with kg unit."""
        config = GeneratorConfig(weight_unit="kg")
        generator = LiftoscriptGenerator(config)
        result = generator.generate(sample_program)

        assert "kg" in result
        assert "lb" not in result

    def test_generate_without_comments(self, sample_program):
        """Test generation without comments."""
        config = GeneratorConfig(include_comments=False)
        generator = LiftoscriptGenerator(config)
        result = generator.generate(sample_program)

        assert "//" not in result


class TestLiftoscriptValidation:
    """Tests for Liftoscript validation."""

    def test_validate_valid_script(self):
        """Test validation of valid Liftoscript."""
        generator = LiftoscriptGenerator()
        valid_script = """
# Week 1
## Day 1 - Push
Bench Press / 4x5 / progress: lp(5lb)
Overhead Press / 3x8-10 / progress: dp(2.5lb, 8, 10)
"""
        is_valid, errors = generator.validate(valid_script)
        assert is_valid
        assert len(errors) == 0

    def test_validate_invalid_sets_format(self):
        """Test validation catches invalid sets format."""
        generator = LiftoscriptGenerator()
        invalid_script = """
## Day 1
Bench Press / invalid / progress: lp(5lb)
"""
        is_valid, errors = generator.validate(invalid_script)
        assert not is_valid
        assert any("Invalid sets format" in e for e in errors)

    def test_validate_missing_parts(self):
        """Test validation catches missing parts."""
        generator = LiftoscriptGenerator()
        invalid_script = """
## Day 1
Just an exercise name without slash
"""
        is_valid, errors = generator.validate(invalid_script)
        assert not is_valid


class TestSetSchemeFormatting:
    """Tests for set scheme formatting."""

    def test_format_uniform_sets(self):
        """Test formatting when all sets are the same."""
        generator = LiftoscriptGenerator()
        exercise = ProgramExercise(
            name="Test",
            sets=[
                SetScheme(reps=8),
                SetScheme(reps=8),
                SetScheme(reps=8),
            ],
        )
        result = generator._format_sets_reps(exercise)
        assert result == "3x8"

    def test_format_amrap_set(self):
        """Test formatting with AMRAP final set."""
        generator = LiftoscriptGenerator()
        exercise = ProgramExercise(
            name="Test",
            sets=[
                SetScheme(reps=5),
                SetScheme(reps=5),
                SetScheme(reps=5, is_amrap=True),
            ],
        )
        result = generator._format_sets_reps(exercise)
        # When all sets have same base reps but last is AMRAP, should show as "1x5, 1x5, 1x5+"
        assert "5+" in result

    def test_format_with_rpe(self):
        """Test formatting with RPE."""
        generator = LiftoscriptGenerator()
        exercise = ProgramExercise(
            name="Test",
            sets=[
                SetScheme(reps=5, rpe=8),
                SetScheme(reps=5, rpe=8),
            ],
        )
        result = generator._format_sets_reps(exercise)
        assert "@RPE8" in result


class TestProgressionFormatting:
    """Tests for progression formatting."""

    def test_format_linear_progression(self):
        """Test linear progression formatting."""
        generator = LiftoscriptGenerator()
        exercise = ProgramExercise(
            name="Test",
            sets=[SetScheme(reps=5)],
            progression=ProgressionScheme.LINEAR,
            progression_params={"increment": 5},
        )
        result = generator._format_progression(exercise)
        assert result == "lp(5lb)"

    def test_format_double_progression(self):
        """Test double progression formatting."""
        generator = LiftoscriptGenerator()
        exercise = ProgramExercise(
            name="Test",
            sets=[SetScheme(reps="8-12")],
            progression=ProgressionScheme.DOUBLE,
            progression_params={"increment": 5},
        )
        result = generator._format_progression(exercise)
        assert "dp(5lb, 8, 12)" in result

    def test_format_sum_progression(self):
        """Test sum progression formatting."""
        generator = LiftoscriptGenerator()
        exercise = ProgramExercise(
            name="Test",
            sets=[SetScheme(reps=10)],
            progression=ProgressionScheme.SUM,
            progression_params={"increment": 5, "target_reps": 30},
        )
        result = generator._format_progression(exercise)
        assert "sum(5lb, 30)" in result


def test_generate_liftoscript_convenience_function(sample_program):
    """Test the convenience function."""
    result = generate_liftoscript(sample_program)
    assert "Bench Press" in result
    assert "progress:" in result
