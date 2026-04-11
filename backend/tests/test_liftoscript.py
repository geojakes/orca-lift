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
        config = GeneratorConfig(include_comments=True)
        generator = LiftoscriptGenerator(config)
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


class TestCrossExerciseConsistency:
    """Tests for cross-exercise progress consistency validation."""

    def test_validate_same_progress_across_weeks(self):
        """Same exercise with same progress in multiple weeks is valid."""
        generator = LiftoscriptGenerator()
        script = """
# Week 1
## Day 1 - Push
Bench Press / 4x5 / progress: lp(5lb)

# Week 2
## Day 1 - Push
Bench Press / 4x5 / progress: lp(5lb)
"""
        is_valid, errors = generator.validate(script)
        assert is_valid
        assert len(errors) == 0

    def test_validate_different_progress_same_exercise_error(self):
        """Same exercise with different progress across weeks is an error."""
        generator = LiftoscriptGenerator()
        script = """
# Week 1
## Day 1 - Push
Bicep Curl / 3x10 / progress: dp(2.5lb, 8, 12)

# Week 2
## Day 1 - Push
Bicep Curl / 3x8 / progress: lp(5lb)
"""
        is_valid, errors = generator.validate(script)
        assert not is_valid
        assert any("Bicep Curl" in e for e in errors)
        assert any("progress" in e.lower() for e in errors)

    def test_validate_different_progress_with_labels_ok(self):
        """Same exercise with different progress but different labels is valid."""
        generator = LiftoscriptGenerator()
        script = """
# Week 1
## Day 1 - Push
heavy: Bench Press / 4x5 / progress: lp(5lb)

# Week 2
## Day 1 - Push
light: Bench Press / 3x10 / progress: dp(2.5lb, 8, 12)
"""
        is_valid, errors = generator.validate(script)
        assert is_valid
        assert len(errors) == 0

    def test_validate_same_label_different_progress_error(self):
        """Same exercise with same label but different progress is an error."""
        generator = LiftoscriptGenerator()
        script = """
# Week 1
## Day 1 - Push
heavy: Bench Press / 4x5 / progress: lp(5lb)

# Week 5
## Day 1 - Push
heavy: Bench Press / 4x3 / progress: lp(10lb)
"""
        is_valid, errors = generator.validate(script)
        assert not is_valid
        assert any("Bench Press" in e for e in errors)

    def test_validate_multiple_exercises_independent(self):
        """Different exercises with different progress are independent."""
        generator = LiftoscriptGenerator()
        script = """
# Week 1
## Day 1 - Push
Bench Press / 4x5 / progress: lp(5lb)
Overhead Press / 3x8-10 / progress: dp(2.5lb, 8, 10)

# Week 2
## Day 1 - Push
Bench Press / 4x5 / progress: lp(5lb)
Overhead Press / 3x8-10 / progress: dp(2.5lb, 8, 10)
"""
        is_valid, errors = generator.validate(script)
        assert is_valid

    def test_validate_exercise_without_progress_ignored(self):
        """Exercises without progress don't participate in consistency check."""
        generator = LiftoscriptGenerator()
        script = """
# Week 1
## Day 1
Bench Press / 4x5 / progress: lp(5lb)

# Week 2
## Day 1
Bench Press / 3x8
"""
        is_valid, errors = generator.validate(script)
        assert is_valid


class TestFixDuplicateProgress:
    """Tests for fix_duplicate_progress auto-label method."""

    def test_fix_adds_labels_to_conflicting_exercises(self):
        """Conflicting progress should get v1, v2 labels."""
        generator = LiftoscriptGenerator()
        script = """# Week 1
## Day 1 - Push
Bicep Curl / 3x10 / progress: dp(2.5lb, 8, 12)

# Week 5
## Day 1 - Push
Bicep Curl / 3x8 / progress: lp(5lb)"""

        fixed = generator.fix_duplicate_progress(script)

        # Both occurrences should now have labels
        assert "v1: Bicep Curl" in fixed
        assert "v2: Bicep Curl" in fixed
        # Original unlabeled version should not remain
        lines = [l.strip() for l in fixed.split("\n") if "Bicep Curl" in l]
        for line in lines:
            assert line.startswith("v1:") or line.startswith("v2:")

    def test_fix_no_change_when_no_conflicts(self):
        """No modification when all exercises have consistent progress."""
        generator = LiftoscriptGenerator()
        script = """# Week 1
## Day 1
Bench Press / 4x5 / progress: lp(5lb)

# Week 2
## Day 1
Bench Press / 4x5 / progress: lp(5lb)"""

        fixed = generator.fix_duplicate_progress(script)
        assert fixed == script

    def test_fix_skips_already_labeled_exercises(self):
        """Already-labeled exercises should not be double-labeled."""
        generator = LiftoscriptGenerator()
        script = """# Week 1
## Day 1
heavy: Bench Press / 4x5 / progress: lp(5lb)

# Week 2
## Day 1
light: Bench Press / 3x10 / progress: dp(2.5lb, 8, 12)"""

        fixed = generator.fix_duplicate_progress(script)
        # Should remain unchanged since exercises are already labeled
        assert "heavy: Bench Press" in fixed
        assert "light: Bench Press" in fixed
        assert "v1:" not in fixed
        assert "v2:" not in fixed

    def test_fix_only_affects_conflicting_exercises(self):
        """Non-conflicting exercises should not be modified."""
        generator = LiftoscriptGenerator()
        script = """# Week 1
## Day 1
Bench Press / 4x5 / progress: lp(5lb)
Bicep Curl / 3x10 / progress: dp(2.5lb, 8, 12)

# Week 2
## Day 1
Bench Press / 4x5 / progress: lp(5lb)
Bicep Curl / 3x8 / progress: lp(5lb)"""

        fixed = generator.fix_duplicate_progress(script)

        # Bench Press should remain unlabeled (consistent progress)
        bench_lines = [l.strip() for l in fixed.split("\n") if "Bench Press" in l]
        for line in bench_lines:
            assert not line.startswith("v1:") and not line.startswith("v2:")

        # Bicep Curl should get labels (conflicting progress)
        curl_lines = [l.strip() for l in fixed.split("\n") if "Bicep Curl" in l]
        for line in curl_lines:
            assert line.startswith("v1:") or line.startswith("v2:")

    def test_fix_produces_valid_liftoscript(self):
        """After fixing, the result should pass validation."""
        generator = LiftoscriptGenerator()
        script = """# Week 1
## Day 1 - Push
Bicep Curl / 3x10 / progress: dp(2.5lb, 8, 12)

# Week 5
## Day 1 - Push
Bicep Curl / 3x8 / progress: lp(5lb)"""

        # Original should fail validation
        is_valid, errors = generator.validate(script)
        assert not is_valid

        # Fixed version should pass
        fixed = generator.fix_duplicate_progress(script)
        is_valid, errors = generator.validate(fixed)
        assert is_valid, f"Fixed script still has errors: {errors}"

    def test_fix_handles_three_variants(self):
        """Three different progress variants get v1, v2, v3 labels."""
        generator = LiftoscriptGenerator()
        script = """# Week 1
## Day 1
Squat / 4x5 / progress: lp(5lb)

# Week 4
## Day 1
Squat / 3x8-10 / progress: dp(5lb, 8, 10)

# Week 8
## Day 1
Squat / 5x3 / progress: lp(10lb)"""

        fixed = generator.fix_duplicate_progress(script)
        assert "v1: Squat" in fixed
        assert "v2: Squat" in fixed
        assert "v3: Squat" in fixed

    def test_fix_preserves_non_exercise_lines(self):
        """Week headers, day headers, and blank lines are preserved."""
        generator = LiftoscriptGenerator()
        script = """# Week 1
## Day 1 - Push
Bicep Curl / 3x10 / progress: dp(2.5lb, 8, 12)

# Week 5
## Day 1 - Push
Bicep Curl / 3x8 / progress: lp(5lb)"""

        fixed = generator.fix_duplicate_progress(script)
        assert "# Week 1" in fixed
        assert "# Week 5" in fixed
        assert "## Day 1 - Push" in fixed


def test_generate_liftoscript_convenience_function(sample_program):
    """Test the convenience function."""
    result = generate_liftoscript(sample_program)
    assert "Bench Press" in result
    assert "progress:" in result
