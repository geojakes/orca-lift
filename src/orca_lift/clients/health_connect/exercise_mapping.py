"""Map Health Connect segment types to exercise names."""

# Mapping from Health Connect segment types to our exercise names
SEGMENT_TYPE_MAPPING = {
    # Compound lifts
    "EXERCISE_SEGMENT_TYPE_BENCH_PRESS": "Bench Press",
    "EXERCISE_SEGMENT_TYPE_SQUAT": "Squat",
    "EXERCISE_SEGMENT_TYPE_DEADLIFT": "Deadlift",
    "EXERCISE_SEGMENT_TYPE_SHOULDER_PRESS": "Overhead Press",
    "EXERCISE_SEGMENT_TYPE_BARBELL_SHOULDER_PRESS": "Overhead Press",
    # Upper body
    "EXERCISE_SEGMENT_TYPE_BICEPS_CURL": "Dumbbell Curl",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_LEFT_ARM": "Dumbbell Curl",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_CURL_RIGHT_ARM": "Dumbbell Curl",
    "EXERCISE_SEGMENT_TYPE_WEIGHTED_ARM_CURL": "Barbell Curl",
    "EXERCISE_SEGMENT_TYPE_HAMMER_CURL": "Hammer Curl",
    "EXERCISE_SEGMENT_TYPE_TRICEPS_EXTENSION": "Tricep Pushdown",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_LEFT_ARM": "Overhead Tricep Extension",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_RIGHT_ARM": "Overhead Tricep Extension",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_TRICEPS_EXTENSION_TWO_ARM": "Overhead Tricep Extension",
    "EXERCISE_SEGMENT_TYPE_SINGLE_ARM_TRICEPS_EXTENSION": "Overhead Tricep Extension",
    "EXERCISE_SEGMENT_TYPE_TRICEP_DIP": "Dip",
    # Back
    "EXERCISE_SEGMENT_TYPE_LAT_PULLDOWN": "Lat Pulldown",
    "EXERCISE_SEGMENT_TYPE_LAT_PULL_DOWN": "Lat Pulldown",
    "EXERCISE_SEGMENT_TYPE_PULL_UP": "Pull-up",
    "EXERCISE_SEGMENT_TYPE_CHIN_UP": "Chin-up",
    "EXERCISE_SEGMENT_TYPE_ROWING_MACHINE": "Cable Row",
    "EXERCISE_SEGMENT_TYPE_SEATED_ROW": "Cable Row",
    "EXERCISE_SEGMENT_TYPE_BENT_OVER_ROW": "Barbell Row",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_ROW": "Dumbbell Row",
    # Shoulders
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_FRONT_RAISE": "Lateral Raise",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_LATERAL_RAISE": "Lateral Raise",
    "EXERCISE_SEGMENT_TYPE_LATERAL_RAISE": "Lateral Raise",
    "EXERCISE_SEGMENT_TYPE_FRONT_RAISE": "Lateral Raise",
    "EXERCISE_SEGMENT_TYPE_REAR_DELT_FLY": "Face Pull",
    # Chest
    "EXERCISE_SEGMENT_TYPE_PUSH_UP": "Push-up",
    "EXERCISE_SEGMENT_TYPE_PUSHUP": "Push-up",
    "EXERCISE_SEGMENT_TYPE_CHEST_FLY": "Dumbbell Fly",
    "EXERCISE_SEGMENT_TYPE_INCLINE_BENCH_PRESS": "Incline Bench Press",
    "EXERCISE_SEGMENT_TYPE_DECLINE_BENCH_PRESS": "Bench Press",
    "EXERCISE_SEGMENT_TYPE_DUMBBELL_BENCH_PRESS": "Dumbbell Bench Press",
    # Legs
    "EXERCISE_SEGMENT_TYPE_LEG_PRESS": "Leg Press",
    "EXERCISE_SEGMENT_TYPE_LEG_CURL": "Leg Curl",
    "EXERCISE_SEGMENT_TYPE_LEG_EXTENSION": "Leg Extension",
    "EXERCISE_SEGMENT_TYPE_CALF_RAISE": "Calf Raise",
    "EXERCISE_SEGMENT_TYPE_LUNGES": "Lunge",
    "EXERCISE_SEGMENT_TYPE_LUNGE": "Lunge",
    "EXERCISE_SEGMENT_TYPE_SPLIT_SQUAT": "Bulgarian Split Squat",
    "EXERCISE_SEGMENT_TYPE_GOBLET_SQUAT": "Goblet Squat",
    "EXERCISE_SEGMENT_TYPE_FRONT_SQUAT": "Front Squat",
    "EXERCISE_SEGMENT_TYPE_HIP_THRUST": "Hip Thrust",
    "EXERCISE_SEGMENT_TYPE_GLUTE_BRIDGE": "Hip Thrust",
    "EXERCISE_SEGMENT_TYPE_ROMANIAN_DEADLIFT": "Romanian Deadlift",
    "EXERCISE_SEGMENT_TYPE_STIFF_LEG_DEADLIFT": "Romanian Deadlift",
    # Core
    "EXERCISE_SEGMENT_TYPE_PLANK": "Plank",
    "EXERCISE_SEGMENT_TYPE_CRUNCH": "Cable Crunch",
    "EXERCISE_SEGMENT_TYPE_SIT_UP": "Cable Crunch",
    "EXERCISE_SEGMENT_TYPE_LEG_RAISE": "Hanging Leg Raise",
    "EXERCISE_SEGMENT_TYPE_HANGING_LEG_RAISE": "Hanging Leg Raise",
    "EXERCISE_SEGMENT_TYPE_AB_WHEEL": "Ab Wheel Rollout",
    "EXERCISE_SEGMENT_TYPE_FORWARD_TWIST": "Ab Wheel Rollout",
    # Generic strength training (will be logged but may need manual categorization)
    "EXERCISE_SEGMENT_TYPE_WEIGHTLIFTING": None,
    "EXERCISE_SEGMENT_TYPE_STRENGTH_TRAINING": None,
    "EXERCISE_SEGMENT_TYPE_UNKNOWN": None,
}

# Numeric segment type codes (some Health Connect versions use integers)
SEGMENT_TYPE_CODES = {
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
    # Add more as discovered
}


def map_segment_type_to_exercise(segment_type: str | int | None) -> str | None:
    """Map a Health Connect segment type to our exercise name.

    Args:
        segment_type: The segment type from Health Connect (string or int)

    Returns:
        The exercise name or None if not recognized
    """
    if segment_type is None:
        return None

    # Handle integer codes
    if isinstance(segment_type, int):
        return SEGMENT_TYPE_CODES.get(segment_type)

    # Handle string types
    segment_type = str(segment_type).upper().strip()

    # Direct lookup
    if segment_type in SEGMENT_TYPE_MAPPING:
        return SEGMENT_TYPE_MAPPING[segment_type]

    # Try with prefix
    prefixed = f"EXERCISE_SEGMENT_TYPE_{segment_type}"
    if prefixed in SEGMENT_TYPE_MAPPING:
        return SEGMENT_TYPE_MAPPING[prefixed]

    # Try to extract exercise name from type
    if segment_type.startswith("EXERCISE_SEGMENT_TYPE_"):
        # Convert EXERCISE_SEGMENT_TYPE_BENCH_PRESS -> Bench Press
        name = segment_type[22:].replace("_", " ").title()

        # Check if it matches any known exercise
        from ...utils.exercise_utils import find_matching_exercise

        match = find_matching_exercise(name)
        if match:
            return match.name

    return None


def get_all_known_segment_types() -> list[str]:
    """Get a list of all known segment type names."""
    return [k for k in SEGMENT_TYPE_MAPPING.keys() if SEGMENT_TYPE_MAPPING[k] is not None]
