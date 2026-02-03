"""Congregation tools for info requests during program deliberation.

These tools allow specialists to query for additional information about
the user, their equipment, and available exercises during deliberation.
"""

import asyncio
from typing import Awaitable, Callable
from uuid import uuid4

from orca import CongregationTool

from ..db.repositories import (
    EquipmentConfigRepository,
    ExerciseRepository,
    FitnessDataRepository,
    UserProfileRepository,
)
from ..models.exercises import EquipmentType, MuscleGroup, MovementPattern


# Global context - set before congregation runs
_profile_id: int | None = None

# Human interaction state
_pending_questions: dict[str, asyncio.Future] = {}
_question_callback: Callable[[str, str, str], Awaitable[None]] | None = None


def set_profile_context(profile_id: int) -> None:
    """Set the profile ID for the current congregation session."""
    global _profile_id
    _profile_id = profile_id


def set_question_callback(callback: Callable[[str, str, str], Awaitable[None]] | None) -> None:
    """Set the callback for sending questions to the user.

    The callback receives (question_id, specialist_name, question_text).
    """
    global _question_callback
    _question_callback = callback


def answer_question(question_id: str, answer: str) -> bool:
    """Provide an answer to a pending question.

    Returns True if the question was found and answered, False otherwise.
    """
    if question_id in _pending_questions:
        future = _pending_questions.pop(question_id)
        if not future.done():
            future.set_result(answer)
            return True
    return False


def get_pending_questions() -> list[str]:
    """Get list of pending question IDs."""
    return list(_pending_questions.keys())


async def get_user_profile() -> dict:
    """Get the full user profile including goals, experience level, and limitations.

    Returns a dictionary with all profile information that specialists
    can use to tailor their exercise recommendations.
    """
    if _profile_id is None:
        return {"error": "No profile context set"}

    repo = UserProfileRepository()
    profile = await repo.get(_profile_id)

    if not profile:
        return {"error": "Profile not found"}

    return {
        "name": profile.name,
        "experience_level": profile.experience_level.value,
        "goals": [g.value for g in profile.goals],
        "schedule_days": profile.schedule_days,
        "session_duration": profile.session_duration,
        "age": profile.age,
        "body_weight": profile.body_weight,
        "limitations": profile.limitations,
        "notes": profile.notes,
    }


async def get_strength_levels() -> dict:
    """Get the user's current strength levels for major lifts.

    Returns estimated or recorded strength levels that can inform
    exercise selection and progression recommendations.
    """
    if _profile_id is None:
        return {"error": "No profile context set"}

    repo = UserProfileRepository()
    profile = await repo.get(_profile_id)

    if not profile:
        return {"error": "Profile not found"}

    return {
        "experience_level": profile.experience_level.value,
        "strength_levels": profile.strength_levels,
        "body_weight": profile.body_weight,
    }


async def get_available_equipment() -> dict:
    """Get the user's available equipment and configuration.

    Returns equipment types available and optional plate inventory
    for weight rounding calculations.
    """
    if _profile_id is None:
        return {"error": "No profile context set"}

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get(_profile_id)

    if not profile:
        return {"error": "Profile not found"}

    result = {
        "equipment_types": [eq.value for eq in profile.available_equipment],
    }

    # Get equipment config if it exists
    config_repo = EquipmentConfigRepository()
    config = await config_repo.get_by_profile(_profile_id)

    if config:
        result["weight_unit"] = config.weight_unit
        result["barbell_weight"] = config.barbell_weight
        result["dumbbell_max"] = config.dumbbell_max
        if config.plate_inventory:
            result["plate_inventory"] = config.plate_inventory
            result["min_increment"] = config.min_increment()

    return result


async def get_available_exercises() -> dict:
    """Get all exercises available with the user's equipment.

    Returns a list of exercise names that can be performed with
    the user's available equipment.
    """
    if _profile_id is None:
        return {"error": "No profile context set"}

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get(_profile_id)

    if not profile:
        return {"error": "Profile not found"}

    exercise_repo = ExerciseRepository()
    exercises = await exercise_repo.get_by_equipment(profile.available_equipment)

    return {
        "count": len(exercises),
        "exercises": [
            {
                "name": ex.name,
                "movement_pattern": ex.movement_pattern.value,
                "is_compound": ex.is_compound,
            }
            for ex in exercises
        ],
    }


async def get_exercise_details(name: str) -> dict:
    """Get detailed information about a specific exercise.

    Args:
        name: The exercise name to look up

    Returns information about muscle groups, equipment options,
    and movement pattern.
    """
    repo = ExerciseRepository()
    exercise = await repo.get_by_name(name)

    if not exercise:
        # Try searching
        results = await repo.search(name)
        if results:
            exercise = results[0]
        else:
            return {"error": f"Exercise '{name}' not found"}

    return {
        "name": exercise.name,
        "aliases": exercise.aliases,
        "muscle_groups": [mg.value for mg in exercise.muscle_groups],
        "equipment": [eq.value for eq in exercise.equipment],
        "movement_pattern": exercise.movement_pattern.value,
        "is_compound": exercise.is_compound,
    }


async def search_exercises(query: str) -> dict:
    """Search for exercises by name or alias.

    Args:
        query: Search term to match against exercise names

    Returns matching exercises with their details.
    """
    repo = ExerciseRepository()
    exercises = await repo.search(query)

    return {
        "count": len(exercises),
        "exercises": [
            {
                "name": ex.name,
                "muscle_groups": [mg.value for mg in ex.muscle_groups],
                "movement_pattern": ex.movement_pattern.value,
            }
            for ex in exercises[:10]  # Limit to 10 results
        ],
    }


async def get_exercises_by_muscle_group(muscle_group: str) -> dict:
    """Get exercises targeting a specific muscle group.

    Args:
        muscle_group: One of: chest, back, shoulders, biceps, triceps,
            forearms, quads, hamstrings, glutes, calves, abs, obliques

    Returns exercises that target the specified muscle group.
    """
    try:
        mg = MuscleGroup(muscle_group.lower())
    except ValueError:
        valid = [m.value for m in MuscleGroup]
        return {"error": f"Invalid muscle group. Valid options: {valid}"}

    if _profile_id is None:
        return {"error": "No profile context set"}

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get(_profile_id)

    if not profile:
        return {"error": "Profile not found"}

    exercise_repo = ExerciseRepository()
    all_exercises = await exercise_repo.get_by_muscle_group(mg)

    # Filter by user's equipment
    exercises = [
        ex for ex in all_exercises
        if any(eq in profile.available_equipment for eq in ex.equipment)
    ]

    return {
        "muscle_group": muscle_group,
        "count": len(exercises),
        "exercises": [
            {
                "name": ex.name,
                "equipment": [eq.value for eq in ex.equipment],
                "is_compound": ex.is_compound,
            }
            for ex in exercises
        ],
    }


async def get_compound_exercises() -> dict:
    """Get all compound exercises available with the user's equipment.

    Compound exercises work multiple muscle groups and are typically
    prioritized in strength-focused programs.
    """
    if _profile_id is None:
        return {"error": "No profile context set"}

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get(_profile_id)

    if not profile:
        return {"error": "Profile not found"}

    exercise_repo = ExerciseRepository()
    all_compound = await exercise_repo.get_compound_exercises()

    # Filter by user's equipment
    exercises = [
        ex for ex in all_compound
        if any(eq in profile.available_equipment for eq in ex.equipment)
    ]

    return {
        "count": len(exercises),
        "exercises": [
            {
                "name": ex.name,
                "muscle_groups": [mg.value for mg in ex.muscle_groups],
                "movement_pattern": ex.movement_pattern.value,
            }
            for ex in exercises
        ],
    }


# Track which specialist is currently active (set by executor)
_current_specialist: str = "Specialist"


def set_current_specialist(name: str) -> None:
    """Set the name of the currently active specialist."""
    global _current_specialist
    _current_specialist = name


async def ask_human(question: str) -> dict:
    """Ask the user a question and wait for their response.

    Use this when you need clarification from the user about their
    preferences, goals, or constraints that aren't clear from the profile.

    Args:
        question: The question to ask the user. Be specific and concise.

    Returns:
        A dict with the user's answer, or an error if no callback is set.

    Examples:
        - "Do you prefer training in the morning or evening?"
        - "Are you training for a specific event or competition?"
        - "Do you have any exercises you particularly enjoy or want to avoid?"
    """
    global _question_callback, _current_specialist

    if _question_callback is None:
        return {
            "error": "Human interaction not available in this context",
            "answer": None,
        }

    # Create a unique ID for this question
    question_id = str(uuid4())[:8]

    # Create a future to wait for the answer
    loop = asyncio.get_event_loop()
    future: asyncio.Future = loop.create_future()
    _pending_questions[question_id] = future

    try:
        # Send the question to the frontend
        await _question_callback(question_id, _current_specialist, question)

        # Wait for the answer (with timeout)
        answer = await asyncio.wait_for(future, timeout=300.0)  # 5 minute timeout

        return {
            "question": question,
            "answer": answer,
        }
    except asyncio.TimeoutError:
        _pending_questions.pop(question_id, None)
        return {
            "error": "User did not respond in time",
            "answer": None,
        }
    except Exception as e:
        _pending_questions.pop(question_id, None)
        return {
            "error": str(e),
            "answer": None,
        }


async def get_fitness_history() -> dict:
    """Get the user's fitness history from Health Connect or other sources.

    Returns workout history, exercise records, and any tracked metrics
    that can help inform program design.
    """
    if _profile_id is None:
        return {"error": "No profile context set"}

    repo = FitnessDataRepository()

    # Get all fitness data for this profile
    workout_data = await repo.get_by_type("workout", _profile_id)
    exercise_data = await repo.get_by_type("exercise", _profile_id)
    weight_data = await repo.get_by_type("weight", _profile_id)

    # Summarize the data
    summary = {
        "workouts": {
            "count": len(workout_data),
            "recent": workout_data[:10] if workout_data else [],
        },
        "exercises": {
            "count": len(exercise_data),
            "recent": exercise_data[:20] if exercise_data else [],
        },
        "body_weight": {
            "count": len(weight_data),
            "recent": weight_data[:5] if weight_data else [],
        },
    }

    # Add summary stats if we have data
    if exercise_data:
        # Count exercise frequency
        exercise_counts: dict[str, int] = {}
        for record in exercise_data:
            name = record.get("data", {}).get("exercise_name", "Unknown")
            exercise_counts[name] = exercise_counts.get(name, 0) + 1

        summary["most_frequent_exercises"] = sorted(
            exercise_counts.items(), key=lambda x: -x[1]
        )[:10]

    return summary


async def get_valid_exercise_names() -> dict:
    """Get the list of valid Liftosaur exercise names.

    Returns all exercise names that are valid in Liftosaur format.
    Use these exact names when recommending exercises.
    """
    import json
    from pathlib import Path

    # Try to load from the sync file
    sync_file = Path(__file__).parent.parent.parent.parent / "scripts" / "liftosaur_exercises.json"

    if sync_file.exists():
        with open(sync_file) as f:
            data = json.load(f)
            return {
                "total_exercises": len(data.get("exercises", [])),
                "valid_names": data.get("valid_names", []),
                "equipment_types": list(data.get("equipment_mapping", {}).values()),
            }

    # Fallback to our exercise repository
    if _profile_id is None:
        return {"error": "No profile context set"}

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get(_profile_id)

    if not profile:
        return {"error": "Profile not found"}

    exercise_repo = ExerciseRepository()
    exercises = await exercise_repo.get_by_equipment(profile.available_equipment)

    return {
        "total_exercises": len(exercises),
        "valid_names": [ex.name for ex in exercises],
        "note": "Use these exact exercise names in your recommendations",
    }


# Define congregation tools for export
CONGREGATION_TOOLS = [
    CongregationTool(
        get_user_profile,
        "Get the full user profile: name, experience level, goals, schedule, "
        "session duration, age, body weight, limitations, and notes.",
    ),
    CongregationTool(
        get_strength_levels,
        "Get the user's current strength levels for major lifts and body weight.",
    ),
    CongregationTool(
        get_available_equipment,
        "Get the user's equipment types, weight unit, barbell weight, "
        "plate inventory, and minimum weight increment.",
    ),
    CongregationTool(
        get_available_exercises,
        "Get all exercises the user can perform with their equipment. "
        "Returns name, movement pattern, and whether each is compound.",
    ),
    CongregationTool(
        get_exercise_details,
        "Get detailed info about a specific exercise: muscle groups, "
        "equipment options, movement pattern, and aliases.",
    ),
    CongregationTool(
        search_exercises,
        "Search for exercises by name or alias. Returns up to 10 matches.",
    ),
    CongregationTool(
        get_exercises_by_muscle_group,
        "Get exercises targeting a muscle group (chest, back, shoulders, "
        "biceps, triceps, quads, hamstrings, glutes, calves, abs, etc.).",
    ),
    CongregationTool(
        get_compound_exercises,
        "Get all compound exercises available with the user's equipment.",
    ),
    CongregationTool(
        get_fitness_history,
        "Get the user's workout history from Health Connect or other sources. "
        "Returns recent workouts, exercises performed, and body weight records.",
    ),
    CongregationTool(
        get_valid_exercise_names,
        "Get the list of valid Liftosaur exercise names. IMPORTANT: Use these "
        "exact names when recommending exercises to ensure compatibility.",
    ),
    CongregationTool(
        ask_human,
        "Ask the user a question when you need clarification about their "
        "preferences, goals, or constraints. Use sparingly - only when the "
        "answer would significantly impact your recommendations.",
    ),
]
