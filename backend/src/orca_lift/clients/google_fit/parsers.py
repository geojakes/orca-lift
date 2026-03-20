"""Parsers for Google Fit Takeout JSON/CSV data."""

from datetime import datetime


def _parse_timestamp(value: str | int | None) -> datetime:
    """Parse a timestamp value to datetime."""
    if value is None:
        return datetime.now()

    if isinstance(value, int):
        if value > 1e12:
            value = value / 1000
        return datetime.fromtimestamp(value)

    if isinstance(value, str):
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass

    return datetime.now()


# Google Fit exercise type codes
EXERCISE_TYPE_NAMES = {
    1: "Aerobics",
    2: "Badminton",
    3: "Baseball",
    4: "Basketball",
    5: "Biathlon",
    6: "Biking",
    7: "Handbiking",
    8: "Mountain Biking",
    9: "Road Biking",
    10: "Spinning",
    11: "Stationary Biking",
    12: "Utility Biking",
    13: "Boxing",
    14: "Calisthenics",
    15: "Circuit Training",
    16: "Cricket",
    17: "Crossfit",
    18: "Curling",
    19: "Dancing",
    20: "Diving",
    21: "Elliptical",
    22: "Ergometer",
    23: "Fencing",
    24: "Football (American)",
    25: "Football (Australian)",
    26: "Football (Soccer)",
    27: "Frisbee",
    28: "Gardening",
    29: "Golf",
    30: "Gymnastics",
    31: "Handball",
    32: "HIIT",
    33: "Hiking",
    34: "Hockey",
    35: "Horseback Riding",
    36: "Housework",
    37: "Ice Skating",
    38: "Interval Training",
    39: "Jumping Rope",
    40: "Kayaking",
    41: "Kettlebell Training",
    42: "Kickboxing",
    43: "Kitesurfing",
    44: "Martial Arts",
    45: "Meditation",
    46: "Mixed Martial Arts",
    47: "P90X",
    48: "Paragliding",
    49: "Pilates",
    50: "Polo",
    51: "Racquetball",
    52: "Rock Climbing",
    53: "Rowing",
    54: "Rowing Machine",
    55: "Rugby",
    56: "Running",
    57: "Running on Sand",
    58: "Running (Treadmill)",
    59: "Sailing",
    60: "Scuba Diving",
    61: "Skateboarding",
    62: "Skating",
    63: "Cross Skating",
    64: "Indoor Skating",
    65: "Inline Skating",
    66: "Skiing",
    67: "Back-Country Skiing",
    68: "Cross-Country Skiing",
    69: "Downhill Skiing",
    70: "Kite Skiing",
    71: "Roller Skiing",
    72: "Sledding",
    73: "Sleeping",
    74: "Snowboarding",
    75: "Snowmobile",
    76: "Snowshoeing",
    77: "Soccer",
    78: "Softball",
    79: "Squash",
    80: "Stair Climbing",
    81: "Stair-Climbing Machine",
    82: "Stand-Up Paddleboarding",
    83: "Strength Training",  # Generic strength
    84: "Surfing",
    85: "Swimming",
    86: "Swimming (Open Water)",
    87: "Swimming (Pool)",
    88: "Table Tennis",
    89: "Team Sports",
    90: "Tennis",
    91: "Treadmill (Walking/Running)",
    92: "Volleyball",
    93: "Volleyball (Beach)",
    94: "Volleyball (Indoor)",
    95: "Wakeboarding",
    96: "Walking",
    97: "Walking (Fitness)",
    98: "Water Polo",
    99: "Weightlifting",  # Explicit weightlifting
    100: "Wheelchair",
    101: "Windsurfing",
    102: "Yoga",
    103: "Zumba",
    104: "Other",
}

# Resistance type codes
RESISTANCE_TYPES = {
    0: "unknown",
    1: "barbell",
    2: "cable",
    3: "dumbbell",
    4: "kettlebell",
    5: "machine",
    6: "bodyweight",
}


def parse_fit_sessions(data: dict | list) -> list[dict]:
    """Parse Google Fit session data."""
    sessions = []

    # Handle both list and dict formats
    if isinstance(data, dict):
        data = data.get("sessions", []) or data.get("bucket", []) or [data]

    for item in data:
        session = {
            "start_time": _parse_timestamp(
                item.get("startTimeMillis") or item.get("startTime")
            ),
            "end_time": _parse_timestamp(
                item.get("endTimeMillis") or item.get("endTime")
            ),
            "activity_type": _get_activity_name(item.get("activityType")),
            "exercises": [],
            "notes": item.get("description", "") or item.get("name", ""),
        }

        # Parse exercise data if present
        if "point" in item:
            session["exercises"] = _parse_exercise_points(item["point"])
        elif "dataSet" in item:
            for dataset in item["dataSet"]:
                if "point" in dataset:
                    session["exercises"].extend(_parse_exercise_points(dataset["point"]))

        sessions.append(session)

    return sessions


def parse_workout_data(data: dict | list) -> list[dict]:
    """Parse workout-specific data with exercise details."""
    workouts = []

    # Handle both list and dict formats
    if isinstance(data, dict):
        items = data.get("workout", []) or data.get("point", []) or [data]
    else:
        items = data

    for item in items:
        workout = {
            "start_time": _parse_timestamp(
                item.get("startTimeNanos")
                or item.get("startTimeMillis")
                or item.get("startTime")
            ),
            "end_time": _parse_timestamp(
                item.get("endTimeNanos")
                or item.get("endTimeMillis")
                or item.get("endTime")
            ),
            "exercises": [],
        }

        # Extract exercise sets from value array
        if "value" in item:
            exercise_data = _parse_exercise_values(item["value"])
            if exercise_data:
                workout["exercises"].append(exercise_data)

        # Handle nested data
        if "dataset" in item or "dataSet" in item:
            datasets = item.get("dataset") or item.get("dataSet") or []
            for ds in datasets:
                if "point" in ds:
                    for point in ds["point"]:
                        if "value" in point:
                            ex = _parse_exercise_values(point["value"])
                            if ex:
                                workout["exercises"].append(ex)

        workouts.append(workout)

    return workouts


def _parse_exercise_points(points: list) -> list[dict]:
    """Parse exercise data from points array."""
    exercises = []

    for point in points:
        if "value" not in point:
            continue

        exercise = _parse_exercise_values(point["value"])
        if exercise:
            exercises.append(exercise)

    return exercises


def _parse_exercise_values(values: list) -> dict | None:
    """Parse exercise data from value array.

    Google Fit workout data format:
    - exercise_type: int (maps to exercise name)
    - repetitions: int
    - resistance_type: int (barbell, dumbbell, etc.)
    - resistance_weight: float (kg)
    - duration: int (milliseconds)
    """
    exercise = {
        "name": "Unknown Exercise",
        "sets": [],
    }

    set_data = {}

    for val in values:
        # Handle different value formats
        if isinstance(val, dict):
            # Format: {"intVal": 10} or {"fpVal": 50.0}
            if "intVal" in val:
                int_val = val["intVal"]
                # Try to determine what this value represents
                if int_val > 100:  # Likely duration in ms
                    set_data["duration"] = int_val / 1000
                elif int_val < 30:  # Likely reps or resistance type
                    if "reps" not in set_data:
                        set_data["reps"] = int_val
                    else:
                        # Might be resistance type
                        pass

            if "fpVal" in val:
                fp_val = val["fpVal"]
                # Float values are typically weight
                set_data["weight"] = fp_val

            if "stringVal" in val:
                # Might be exercise name
                exercise["name"] = val["stringVal"]

            # Named field format
            if "mapVal" in val:
                for entry in val.get("mapVal", []):
                    key = entry.get("key", "")
                    value = entry.get("value", {})

                    if "exercise" in key.lower():
                        exercise["name"] = value.get("stringVal", exercise["name"])
                    elif "repetition" in key.lower():
                        set_data["reps"] = value.get("intVal", 0)
                    elif "weight" in key.lower():
                        set_data["weight"] = value.get("fpVal")
                    elif "duration" in key.lower():
                        set_data["duration"] = value.get("intVal", 0) / 1000

    if set_data.get("reps", 0) > 0 or set_data.get("weight"):
        exercise["sets"].append(set_data)
        return exercise

    return None


def _get_activity_name(activity_type: int | None) -> str:
    """Get activity name from type code."""
    if activity_type is None:
        return "unknown"
    return EXERCISE_TYPE_NAMES.get(activity_type, "unknown")


def parse_daily_activity_metrics(rows: list[dict]) -> list[dict]:
    """Parse daily activity metrics from CSV."""
    metrics = []

    for row in rows:
        metric = {
            "date": row.get("Date") or row.get("date"),
            "steps": _safe_int(row.get("Steps") or row.get("steps")),
            "calories": _safe_float(row.get("Calories") or row.get("calories")),
            "distance": _safe_float(row.get("Distance") or row.get("distance")),
            "active_minutes": _safe_int(
                row.get("Move Minutes") or row.get("active_minutes")
            ),
        }
        metrics.append(metric)

    return metrics


def _safe_int(value: str | int | None) -> int:
    """Safely convert to int."""
    if value is None:
        return 0
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def _safe_float(value: str | float | None) -> float:
    """Safely convert to float."""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
