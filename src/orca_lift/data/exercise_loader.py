"""Exercise library loader from JSON."""

import json
from pathlib import Path

import aiosqlite

from ..db.engine import get_db_path
from ..models.exercises import (
    EquipmentType,
    Exercise,
    MuscleGroup,
    MovementPattern,
)


def get_exercises_json_path() -> Path:
    """Get the path to the Liftosaur exercises JSON file."""
    return Path(__file__).parent.parent.parent.parent / "data" / "liftosaur_exercises.json"


def load_liftosaur_exercises() -> list[Exercise]:
    """Load exercises from the Liftosaur exercises JSON file.

    Returns:
        List of Exercise objects loaded from JSON
    """
    json_path = get_exercises_json_path()
    if not json_path.exists():
        return []

    with open(json_path) as f:
        data = json.load(f)

    exercises = []
    for ex_data in data.get("exercises", []):
        try:
            exercise = Exercise(
                name=ex_data["name"],
                muscle_groups=[MuscleGroup(mg) for mg in ex_data.get("muscle_groups", [])],
                movement_pattern=MovementPattern(ex_data.get("movement_pattern", "isolation")),
                equipment=[EquipmentType(eq) for eq in ex_data.get("equipment", [])],
                aliases=ex_data.get("aliases", []),
                liftosaur_id=ex_data.get("liftosaur_id"),
                is_compound=ex_data.get("is_compound", False),
            )
            exercises.append(exercise)
        except (ValueError, KeyError) as e:
            # Skip invalid exercises but log the error
            print(f"Warning: Skipping invalid exercise {ex_data.get('name', 'unknown')}: {e}")
            continue

    return exercises


async def seed_exercises_from_json(db_path: Path | None = None) -> int:
    """Seed the database with exercises from the JSON file.

    This replaces the existing exercises with the full Liftosaur library.

    Args:
        db_path: Optional database path. Uses default if not provided.

    Returns:
        Number of exercises seeded
    """
    if db_path is None:
        db_path = get_db_path()

    exercises = load_liftosaur_exercises()
    if not exercises:
        # Fall back to COMMON_EXERCISES if JSON not found
        from ..models.exercises import COMMON_EXERCISES
        exercises = COMMON_EXERCISES

    async with aiosqlite.connect(db_path) as db:
        count = 0
        for exercise in exercises:
            try:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO exercises
                    (name, aliases, muscle_groups, equipment, movement_pattern, liftosaur_id, is_compound)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        exercise.name,
                        json.dumps(exercise.aliases),
                        json.dumps([mg.value for mg in exercise.muscle_groups]),
                        json.dumps([eq.value for eq in exercise.equipment]),
                        exercise.movement_pattern.value,
                        exercise.liftosaur_id,
                        1 if exercise.is_compound else 0,
                    ),
                )
                count += 1
            except aiosqlite.Error as e:
                print(f"Warning: Failed to seed exercise {exercise.name}: {e}")
                continue

        await db.commit()

    return count


def get_exercises_by_equipment(
    exercises: list[Exercise],
    available_equipment: list[EquipmentType],
) -> list[Exercise]:
    """Filter exercises to only those the user can perform.

    Args:
        exercises: Full list of exercises
        available_equipment: Equipment types the user has

    Returns:
        Filtered list of exercises matching available equipment
    """
    filtered = []
    for exercise in exercises:
        # Exercise is available if ANY of its equipment options is available
        if any(eq in available_equipment for eq in exercise.equipment):
            filtered.append(exercise)
    return filtered
