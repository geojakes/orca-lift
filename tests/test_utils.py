"""Tests for utility functions."""

import pytest

from orca_lift.models.exercises import COMMON_EXERCISES
from orca_lift.utils.exercise_utils import (
    categorize_exercises_by_pattern,
    find_matching_exercise,
    get_exercise_by_segment_type,
    normalize_exercise_name,
)


class TestNormalizeExerciseName:
    """Tests for normalize_exercise_name function."""

    def test_lowercase_and_strip(self):
        """Test basic normalization."""
        assert normalize_exercise_name("  Bench Press  ") == "bench press"

    def test_abbreviation_expansion(self):
        """Test abbreviation expansion."""
        assert normalize_exercise_name("BB") == "barbell"
        assert normalize_exercise_name("DB") == "dumbbell"
        assert normalize_exercise_name("OHP") == "overhead press"
        assert normalize_exercise_name("RDL") == "romanian deadlift"

    def test_inline_abbreviation(self):
        """Test abbreviation expansion within name."""
        assert normalize_exercise_name("BB Curl") == "barbell curl"
        assert normalize_exercise_name("DB Row") == "dumbbell row"

    def test_extra_whitespace(self):
        """Test extra whitespace removal."""
        assert normalize_exercise_name("Bench   Press") == "bench press"


class TestFindMatchingExercise:
    """Tests for find_matching_exercise function."""

    def test_exact_match(self):
        """Test exact name matching."""
        result = find_matching_exercise("Bench Press")
        assert result is not None
        assert result.name == "Bench Press"

    def test_case_insensitive(self):
        """Test case insensitive matching."""
        result = find_matching_exercise("bench press")
        assert result is not None
        assert result.name == "Bench Press"

    def test_alias_match(self):
        """Test alias matching."""
        result = find_matching_exercise("BB Bench")
        assert result is not None
        assert result.name == "Bench Press"

    def test_abbreviation_match(self):
        """Test abbreviation matching."""
        result = find_matching_exercise("OHP")
        assert result is not None
        assert result.name == "Overhead Press"

    def test_fuzzy_match(self):
        """Test fuzzy matching."""
        result = find_matching_exercise("Bench Pres")  # Missing 's'
        assert result is not None
        assert result.name == "Bench Press"

    def test_no_match_below_threshold(self):
        """Test no match returned for low similarity."""
        result = find_matching_exercise("xyzabc123")
        assert result is None

    def test_custom_threshold(self):
        """Test custom threshold."""
        # With very high threshold, slight misspelling shouldn't match
        result = find_matching_exercise("Bench Pres", threshold=0.99)
        assert result is None


class TestGetExerciseBySegmentType:
    """Tests for get_exercise_by_segment_type function."""

    def test_known_segment_type(self):
        """Test mapping of known segment type."""
        result = get_exercise_by_segment_type("EXERCISE_SEGMENT_TYPE_BENCH_PRESS")
        assert result == "Bench Press"

    def test_squat_segment(self):
        """Test squat segment mapping."""
        result = get_exercise_by_segment_type("EXERCISE_SEGMENT_TYPE_SQUAT")
        assert result == "Squat"

    def test_numeric_segment_type(self):
        """Test numeric segment type mapping."""
        result = get_exercise_by_segment_type(1)
        assert result == "Bench Press"

    def test_unknown_segment_type(self):
        """Test unknown segment type returns None."""
        result = get_exercise_by_segment_type("EXERCISE_SEGMENT_TYPE_UNKNOWN_XYZ")
        assert result is None

    def test_none_input(self):
        """Test None input returns None."""
        result = get_exercise_by_segment_type(None)
        assert result is None


class TestCategorizeExercisesByPattern:
    """Tests for categorize_exercises_by_pattern function."""

    def test_categorization(self):
        """Test exercise categorization."""
        result = categorize_exercises_by_pattern(COMMON_EXERCISES)

        # Check that categories exist
        assert "push_horizontal" in result
        assert "push_vertical" in result
        assert "pull_horizontal" in result
        assert "pull_vertical" in result
        assert "squat" in result
        assert "hinge" in result

        # Check some exercises are in correct categories
        push_h_names = [e.name for e in result["push_horizontal"]]
        assert "Bench Press" in push_h_names
        assert "Push-up" in push_h_names

        squat_names = [e.name for e in result["squat"]]
        assert "Squat" in squat_names

    def test_empty_input(self):
        """Test with empty input."""
        result = categorize_exercises_by_pattern([])

        # All categories should be empty
        for category in result.values():
            assert len(category) == 0
