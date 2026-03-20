"""Utilities for exercise name normalization and matching."""

import re
from difflib import SequenceMatcher

from ..models.exercises import COMMON_EXERCISES, Exercise


def normalize_exercise_name(name: str) -> str:
    """Normalize an exercise name for comparison.

    Converts to lowercase, removes extra whitespace, and standardizes common variations.
    """
    # Lowercase and strip
    normalized = name.lower().strip()

    # Remove extra whitespace
    normalized = re.sub(r"\s+", " ", normalized)

    # Common abbreviation expansions
    abbreviations = {
        "bb": "barbell",
        "db": "dumbbell",
        "kb": "kettlebell",
        "ohp": "overhead press",
        "rdl": "romanian deadlift",
        "bss": "bulgarian split squat",
        "rfess": "rear foot elevated split squat",
    }

    # Check if the entire name is an abbreviation
    if normalized in abbreviations:
        return abbreviations[normalized]

    # Replace abbreviations at word boundaries
    for abbrev, full in abbreviations.items():
        normalized = re.sub(rf"\b{abbrev}\b", full, normalized)

    return normalized


def find_matching_exercise(
    name: str,
    exercises: list[Exercise] | None = None,
    threshold: float = 0.8,
) -> Exercise | None:
    """Find the best matching exercise from the library.

    Args:
        name: The exercise name to match
        exercises: List of exercises to search (defaults to COMMON_EXERCISES)
        threshold: Minimum similarity ratio (0-1) to consider a match

    Returns:
        The best matching Exercise or None if no match above threshold
    """
    if exercises is None:
        exercises = COMMON_EXERCISES

    normalized_name = normalize_exercise_name(name)

    best_match: Exercise | None = None
    best_score = 0.0

    for exercise in exercises:
        # Check exact name match
        if normalize_exercise_name(exercise.name) == normalized_name:
            return exercise

        # Check aliases
        for alias in exercise.aliases:
            if normalize_exercise_name(alias) == normalized_name:
                return exercise

        # Calculate similarity to exercise name
        name_score = SequenceMatcher(
            None, normalized_name, normalize_exercise_name(exercise.name)
        ).ratio()

        if name_score > best_score:
            best_score = name_score
            best_match = exercise

        # Check similarity to aliases
        for alias in exercise.aliases:
            alias_score = SequenceMatcher(
                None, normalized_name, normalize_exercise_name(alias)
            ).ratio()
            if alias_score > best_score:
                best_score = alias_score
                best_match = exercise

    if best_score >= threshold:
        return best_match

    return None


def get_exercise_by_segment_type(segment_type: str | int | None) -> str | None:
    """Map Health Connect segment type to exercise name.

    Args:
        segment_type: Health Connect segment type constant (string or int)

    Returns:
        Exercise name or None if not recognized
    """
    # Numeric segment type codes (some Health Connect versions use integers)
    segment_type_codes = {
        1: "Bench Press",
        2: "Squat",
        3: "Deadlift",
        4: "Overhead Press",
        5: "Pull-up",
        6: "Push-up",
        7: "Dumbbell Curl",
        8: "Tricep Pushdown",
        9: "Lat Pulldown",
        10: "Cable Row",
        11: "Lunge",
        12: "Leg Press",
        13: "Leg Curl",
        14: "Leg Extension",
        15: "Calf Raise",
    }

    # Health Connect segment type mapping
    segment_mapping = {
        "EXERCISE_SEGMENT_TYPE_BENCH_PRESS": "Bench Press",
        "EXERCISE_SEGMENT_TYPE_SQUAT": "Squat",
        "EXERCISE_SEGMENT_TYPE_DEADLIFT": "Deadlift",
        "EXERCISE_SEGMENT_TYPE_SHOULDER_PRESS": "Overhead Press",
        "EXERCISE_SEGMENT_TYPE_BICEPS_CURL": "Dumbbell Curl",
        "EXERCISE_SEGMENT_TYPE_TRICEPS_EXTENSION": "Tricep Pushdown",
        "EXERCISE_SEGMENT_TYPE_LAT_PULLDOWN": "Lat Pulldown",
        "EXERCISE_SEGMENT_TYPE_ROWING_MACHINE": "Cable Row",
        "EXERCISE_SEGMENT_TYPE_LUNGES": "Lunge",
        "EXERCISE_SEGMENT_TYPE_LEG_PRESS": "Leg Press",
        "EXERCISE_SEGMENT_TYPE_LEG_CURL": "Leg Curl",
        "EXERCISE_SEGMENT_TYPE_LEG_EXTENSION": "Leg Extension",
        "EXERCISE_SEGMENT_TYPE_CALF_RAISE": "Calf Raise",
        "EXERCISE_SEGMENT_TYPE_PLANK": "Plank",
        "EXERCISE_SEGMENT_TYPE_PULL_UP": "Pull-up",
        "EXERCISE_SEGMENT_TYPE_PUSH_UP": "Push-up",
        "EXERCISE_SEGMENT_TYPE_CRUNCH": "Cable Crunch",
        "EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_LEFT_ARM": "Dumbbell Curl",
        "EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_RIGHT_ARM": "Dumbbell Curl",
        "EXERCISE_SEGMENT_TYPE_DUMBBELL_FRONT_RAISE": "Lateral Raise",
        "EXERCISE_SEGMENT_TYPE_DUMBBELL_LATERAL_RAISE": "Lateral Raise",
        "EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_LEFT_ARM": "Overhead Tricep Extension",
        "EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_RIGHT_ARM": "Overhead Tricep Extension",
        "EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_TWO_ARM": "Overhead Tricep Extension",
        "EXERCISE_SEGMENT_TYPE_FORWARD_TWIST": "Ab Wheel Rollout",
        "EXERCISE_SEGMENT_TYPE_HIP_THRUST": "Hip Thrust",
        "EXERCISE_SEGMENT_TYPE_SINGLE_ARM_TRICEPS_EXTENSION": "Overhead Tricep Extension",
        "EXERCISE_SEGMENT_TYPE_SPLIT_SQUAT": "Bulgarian Split Squat",
        "EXERCISE_SEGMENT_TYPE_WEIGHTED_ARM_CURL": "Barbell Curl",
    }

    # Handle None
    if segment_type is None:
        return None

    # Handle integer codes
    if isinstance(segment_type, int):
        return segment_type_codes.get(segment_type)

    # Convert to string for remaining checks
    segment_type = str(segment_type).upper().strip()

    # Try direct mapping
    if segment_type in segment_mapping:
        return segment_mapping[segment_type]

    # Try without prefix
    if segment_type.startswith("EXERCISE_SEGMENT_TYPE_"):
        short_name = segment_type[22:].replace("_", " ").title()
        # Try to find a match in our exercise library
        match = find_matching_exercise(short_name)
        if match:
            return match.name

    return None


def categorize_exercises_by_pattern(
    exercises: list[Exercise],
) -> dict[str, list[Exercise]]:
    """Group exercises by movement pattern.

    Returns a dictionary with movement patterns as keys and lists of exercises as values.
    """
    from ..models.exercises import MovementPattern

    result: dict[str, list[Exercise]] = {pattern.value: [] for pattern in MovementPattern}

    for exercise in exercises:
        result[exercise.movement_pattern.value].append(exercise)

    return result
