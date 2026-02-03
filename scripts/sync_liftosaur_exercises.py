#!/usr/bin/env python3
"""Sync exercise list from Liftosaur's GitHub repository.

This script fetches the latest exercise definitions from Liftosaur's
open-source repo and outputs them in a format we can use.

Usage:
    uv run python scripts/sync_liftosaur_exercises.py

Source: https://github.com/astashov/liftosaur
"""

import json
import re
import urllib.request
from dataclasses import dataclass


LIFTOSAUR_EXERCISE_URL = (
    "https://raw.githubusercontent.com/astashov/liftosaur/master/src/models/exercise.ts"
)

# Map Liftosaur equipment names to display names (for Liftoscript format)
EQUIPMENT_DISPLAY = {
    "barbell": "Barbell",
    "dumbbell": "Dumbbell",
    "kettlebell": "Kettlebell",
    "cable": "Cable",
    "leverageMachine": "Leverage Machine",
    "bodyweight": "Bodyweight",
    "band": "Band",
    "ezbar": "EZ Bar",
    "trapbar": "Trap Bar",
    "smith": "Smith Machine",
    "medicineball": "Medicine Ball",
}

# Map Liftosaur equipment to our EquipmentType enum
EQUIPMENT_TO_ENUM = {
    "barbell": "barbell",
    "dumbbell": "dumbbell",
    "kettlebell": "kettlebell",
    "cable": "cable",
    "leverageMachine": "machine",
    "bodyweight": "bodyweight",
    "band": "bands",
    "ezbar": "ez_bar",
    "trapbar": "trap_bar",
    "smith": "smith_machine",
    "medicineball": "medicine_ball",
}


@dataclass
class LiftosaurExercise:
    """Exercise from Liftosaur."""

    id: str
    name: str
    equipment_types: list[str]
    target_muscles: list[str]
    synergist_muscles: list[str]
    body_parts: list[str]


def fetch_exercise_file() -> str:
    """Fetch the exercise.ts file from Liftosaur's GitHub."""
    print(f"Fetching exercises from: {LIFTOSAUR_EXERCISE_URL}")
    with urllib.request.urlopen(LIFTOSAUR_EXERCISE_URL) as response:
        return response.read().decode("utf-8")


def parse_exercises(content: str) -> list[LiftosaurExercise]:
    """Parse exercises from the TypeScript file.

    Parses both allExercisesList (for id and name) and metadata (for equipment).
    """
    exercises = []

    # Parse exercise list: id: { id: "...", name: "...", ... }
    exercise_pattern = r'(\w+):\s*\{\s*id:\s*"(\w+)",\s*name:\s*"([^"]+)"'
    exercise_matches = {
        m.group(1): {"id": m.group(2), "name": m.group(3)}
        for m in re.finditer(exercise_pattern, content)
    }

    # Parse metadata: exerciseId: { ..., sortedEquipment: [...], ... }
    metadata_start = content.find("export const metadata")
    if metadata_start < 0:
        print("Warning: Could not find metadata section")
        return exercises

    metadata_section = content[metadata_start:]

    # For each exercise in metadata, extract sortedEquipment
    # Pattern: exerciseId: { targetMuscles: [...], synergistMuscles: [...], bodyParts: [...], sortedEquipment: [...] }
    metadata_pattern = r'(\w+):\s*\{\s*targetMuscles:\s*\[([^\]]*)\],\s*synergistMuscles:\s*\[([^\]]*)\],\s*bodyParts:\s*\[([^\]]*)\],\s*sortedEquipment:\s*\[([^\]]*)\]'

    for match in re.finditer(metadata_pattern, metadata_section):
        exercise_id = match.group(1)
        target_muscles = [s.strip().strip('"') for s in match.group(2).split(",") if s.strip()]
        synergist_muscles = [s.strip().strip('"') for s in match.group(3).split(",") if s.strip()]
        body_parts = [s.strip().strip('"') for s in match.group(4).split(",") if s.strip()]
        equipment = [s.strip().strip('"') for s in match.group(5).split(",") if s.strip()]

        # Get exercise name from allExercisesList
        if exercise_id in exercise_matches:
            name = exercise_matches[exercise_id]["name"]
        else:
            # Convert camelCase to Title Case
            name = re.sub(r"([A-Z])", r" \1", exercise_id).strip().title()

        exercises.append(
            LiftosaurExercise(
                id=exercise_id,
                name=name,
                equipment_types=equipment,
                target_muscles=target_muscles,
                synergist_muscles=synergist_muscles,
                body_parts=body_parts,
            )
        )

    return exercises


def generate_liftosaur_names(exercises: list[LiftosaurExercise]) -> list[str]:
    """Generate all valid Liftosaur exercise names.

    Liftosaur format: "Exercise Name, Equipment Type"
    """
    names = []
    for ex in exercises:
        for equip in ex.equipment_types:
            display_equip = EQUIPMENT_DISPLAY.get(equip, equip.title())
            full_name = f"{ex.name}, {display_equip}"
            names.append(full_name)

    return sorted(set(names))


def main():
    """Main entry point."""
    content = fetch_exercise_file()
    exercises = parse_exercises(content)

    print(f"\nFound {len(exercises)} exercise definitions")

    # Generate all valid names
    all_names = generate_liftosaur_names(exercises)
    print(f"Generated {len(all_names)} exercise+equipment combinations")

    # Output as JSON for easy consumption
    output_file = "scripts/liftosaur_exercises.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "source": "https://github.com/astashov/liftosaur",
                "exercises": [
                    {
                        "id": ex.id,
                        "name": ex.name,
                        "equipment": ex.equipment_types,
                        "equipment_display": [
                            EQUIPMENT_DISPLAY.get(e, e) for e in ex.equipment_types
                        ],
                        "target_muscles": ex.target_muscles,
                        "body_parts": ex.body_parts,
                    }
                    for ex in exercises
                ],
                "valid_names": all_names,
                "equipment_mapping": EQUIPMENT_DISPLAY,
            },
            f,
            indent=2,
        )
    print(f"\nSaved to {output_file}")

    # Print sample
    print("\nSample valid exercise names:")
    for name in all_names[:20]:
        print(f"  - {name}")
    print(f"  ... and {len(all_names) - 20} more")

    # Print some stats
    equipment_counts = {}
    for ex in exercises:
        for eq in ex.equipment_types:
            equipment_counts[eq] = equipment_counts.get(eq, 0) + 1

    print("\nEquipment type distribution:")
    for eq, count in sorted(equipment_counts.items(), key=lambda x: -x[1]):
        display = EQUIPMENT_DISPLAY.get(eq, eq)
        print(f"  {display}: {count} exercises")


if __name__ == "__main__":
    main()
