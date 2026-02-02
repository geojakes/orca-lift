"""Exercise definitions and metadata."""

from dataclasses import dataclass, field
from enum import Enum


class MuscleGroup(str, Enum):
    """Major muscle groups."""

    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    FOREARMS = "forearms"
    QUADS = "quads"
    HAMSTRINGS = "hamstrings"
    GLUTES = "glutes"
    CALVES = "calves"
    ABS = "abs"
    OBLIQUES = "obliques"
    LOWER_BACK = "lower_back"
    TRAPS = "traps"
    LATS = "lats"


class MovementPattern(str, Enum):
    """Fundamental movement patterns."""

    PUSH_HORIZONTAL = "push_horizontal"
    PUSH_VERTICAL = "push_vertical"
    PULL_HORIZONTAL = "pull_horizontal"
    PULL_VERTICAL = "pull_vertical"
    SQUAT = "squat"
    HINGE = "hinge"
    LUNGE = "lunge"
    CARRY = "carry"
    ROTATION = "rotation"
    ISOLATION = "isolation"


class EquipmentType(str, Enum):
    """Equipment types for exercises."""

    BARBELL = "barbell"
    DUMBBELL = "dumbbell"
    KETTLEBELL = "kettlebell"
    CABLE = "cable"
    MACHINE = "machine"
    BODYWEIGHT = "bodyweight"
    BANDS = "bands"
    EZ_BAR = "ez_bar"
    TRAP_BAR = "trap_bar"
    SMITH_MACHINE = "smith_machine"


@dataclass
class Exercise:
    """Represents an exercise with metadata."""

    name: str
    muscle_groups: list[MuscleGroup]
    movement_pattern: MovementPattern
    equipment: list[EquipmentType]
    aliases: list[str] = field(default_factory=list)
    liftosaur_id: str | None = None  # Liftosaur's internal exercise ID
    is_compound: bool = False  # True for multi-joint movements
    id: int | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "muscle_groups": [mg.value for mg in self.muscle_groups],
            "movement_pattern": self.movement_pattern.value,
            "equipment": [eq.value for eq in self.equipment],
            "aliases": self.aliases,
            "liftosaur_id": self.liftosaur_id,
            "is_compound": self.is_compound,
        }

    @classmethod
    def from_dict(cls, data: dict, id: int | None = None) -> "Exercise":
        """Create from dictionary."""
        return cls(
            id=id,
            name=data["name"],
            muscle_groups=[MuscleGroup(mg) for mg in data["muscle_groups"]],
            movement_pattern=MovementPattern(data["movement_pattern"]),
            equipment=[EquipmentType(eq) for eq in data["equipment"]],
            aliases=data.get("aliases", []),
            liftosaur_id=data.get("liftosaur_id"),
            is_compound=data.get("is_compound", False),
        )


# Common exercise library
COMMON_EXERCISES: list[Exercise] = [
    # Chest - Horizontal Push
    Exercise(
        name="Bench Press",
        muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.PUSH_HORIZONTAL,
        equipment=[EquipmentType.BARBELL],
        aliases=["Flat Bench Press", "Barbell Bench Press", "BB Bench"],
    ),
    Exercise(
        name="Incline Bench Press",
        muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.PUSH_HORIZONTAL,
        equipment=[EquipmentType.BARBELL],
        aliases=["Incline Press", "Incline BB Press"],
    ),
    Exercise(
        name="Dumbbell Bench Press",
        muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.PUSH_HORIZONTAL,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Bench Press", "Flat DB Press"],
    ),
    Exercise(
        name="Dumbbell Fly",
        muscle_groups=[MuscleGroup.CHEST],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["Chest Fly", "DB Fly", "Pec Fly"],
    ),
    Exercise(
        name="Push-up",
        muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.PUSH_HORIZONTAL,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Pushup", "Press-up"],
    ),
    Exercise(
        name="Dip",
        muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.PUSH_HORIZONTAL,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Chest Dip", "Parallel Bar Dip"],
    ),
    # Shoulders - Vertical Push
    Exercise(
        name="Overhead Press",
        muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.PUSH_VERTICAL,
        equipment=[EquipmentType.BARBELL],
        aliases=["OHP", "Shoulder Press", "Military Press", "Standing Press"],
    ),
    Exercise(
        name="Dumbbell Shoulder Press",
        muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.PUSH_VERTICAL,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Shoulder Press", "Seated DB Press"],
    ),
    Exercise(
        name="Lateral Raise",
        muscle_groups=[MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["Side Raise", "DB Lateral Raise", "Side Lateral Raise"],
    ),
    Exercise(
        name="Face Pull",
        muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.TRAPS],
        movement_pattern=MovementPattern.PULL_HORIZONTAL,
        equipment=[EquipmentType.CABLE],
        aliases=["Cable Face Pull", "Rear Delt Face Pull"],
    ),
    # Back - Horizontal Pull
    Exercise(
        name="Barbell Row",
        muscle_groups=[MuscleGroup.BACK, MuscleGroup.BICEPS, MuscleGroup.LATS],
        movement_pattern=MovementPattern.PULL_HORIZONTAL,
        equipment=[EquipmentType.BARBELL],
        aliases=["Bent Over Row", "BB Row", "Pendlay Row"],
    ),
    Exercise(
        name="Dumbbell Row",
        muscle_groups=[MuscleGroup.BACK, MuscleGroup.BICEPS, MuscleGroup.LATS],
        movement_pattern=MovementPattern.PULL_HORIZONTAL,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Row", "One Arm Row", "Single Arm DB Row"],
    ),
    Exercise(
        name="Cable Row",
        muscle_groups=[MuscleGroup.BACK, MuscleGroup.BICEPS, MuscleGroup.LATS],
        movement_pattern=MovementPattern.PULL_HORIZONTAL,
        equipment=[EquipmentType.CABLE],
        aliases=["Seated Cable Row", "Low Row"],
    ),
    # Back - Vertical Pull
    Exercise(
        name="Pull-up",
        muscle_groups=[MuscleGroup.LATS, MuscleGroup.BICEPS, MuscleGroup.BACK],
        movement_pattern=MovementPattern.PULL_VERTICAL,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Pullup", "Wide Grip Pull-up"],
    ),
    Exercise(
        name="Chin-up",
        muscle_groups=[MuscleGroup.LATS, MuscleGroup.BICEPS, MuscleGroup.BACK],
        movement_pattern=MovementPattern.PULL_VERTICAL,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Chinup", "Underhand Pull-up"],
    ),
    Exercise(
        name="Lat Pulldown",
        muscle_groups=[MuscleGroup.LATS, MuscleGroup.BICEPS, MuscleGroup.BACK],
        movement_pattern=MovementPattern.PULL_VERTICAL,
        equipment=[EquipmentType.CABLE],
        aliases=["Cable Pulldown", "Wide Grip Pulldown"],
    ),
    # Legs - Squat Pattern
    Exercise(
        name="Squat",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS],
        movement_pattern=MovementPattern.SQUAT,
        equipment=[EquipmentType.BARBELL],
        aliases=["Back Squat", "Barbell Squat", "BB Squat"],
    ),
    Exercise(
        name="Front Squat",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.ABS],
        movement_pattern=MovementPattern.SQUAT,
        equipment=[EquipmentType.BARBELL],
        aliases=["Barbell Front Squat"],
    ),
    Exercise(
        name="Goblet Squat",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.SQUAT,
        equipment=[EquipmentType.DUMBBELL, EquipmentType.KETTLEBELL],
        aliases=["DB Goblet Squat", "KB Goblet Squat"],
    ),
    Exercise(
        name="Leg Press",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.SQUAT,
        equipment=[EquipmentType.MACHINE],
        aliases=["Machine Leg Press", "45 Degree Leg Press"],
    ),
    # Legs - Hinge Pattern
    Exercise(
        name="Deadlift",
        muscle_groups=[
            MuscleGroup.HAMSTRINGS,
            MuscleGroup.GLUTES,
            MuscleGroup.LOWER_BACK,
            MuscleGroup.BACK,
        ],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.BARBELL],
        aliases=["Conventional Deadlift", "BB Deadlift"],
    ),
    Exercise(
        name="Romanian Deadlift",
        muscle_groups=[MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES, MuscleGroup.LOWER_BACK],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.BARBELL],
        aliases=["RDL", "Stiff Leg Deadlift", "Romanian DL"],
    ),
    Exercise(
        name="Dumbbell Romanian Deadlift",
        muscle_groups=[MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB RDL", "Dumbbell RDL"],
    ),
    Exercise(
        name="Hip Thrust",
        muscle_groups=[MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.BARBELL],
        aliases=["Barbell Hip Thrust", "Glute Bridge"],
    ),
    # Legs - Lunge Pattern
    Exercise(
        name="Lunge",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.LUNGE,
        equipment=[EquipmentType.BODYWEIGHT, EquipmentType.DUMBBELL],
        aliases=["Walking Lunge", "Forward Lunge", "DB Lunge"],
    ),
    Exercise(
        name="Bulgarian Split Squat",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.LUNGE,
        equipment=[EquipmentType.DUMBBELL, EquipmentType.BODYWEIGHT],
        aliases=["BSS", "Rear Foot Elevated Split Squat", "RFESS"],
    ),
    # Legs - Isolation
    Exercise(
        name="Leg Curl",
        muscle_groups=[MuscleGroup.HAMSTRINGS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.MACHINE],
        aliases=["Hamstring Curl", "Lying Leg Curl", "Seated Leg Curl"],
    ),
    Exercise(
        name="Leg Extension",
        muscle_groups=[MuscleGroup.QUADS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.MACHINE],
        aliases=["Quad Extension", "Machine Leg Extension"],
    ),
    Exercise(
        name="Calf Raise",
        muscle_groups=[MuscleGroup.CALVES],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.MACHINE, EquipmentType.BODYWEIGHT],
        aliases=["Standing Calf Raise", "Seated Calf Raise"],
    ),
    # Arms
    Exercise(
        name="Barbell Curl",
        muscle_groups=[MuscleGroup.BICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BARBELL],
        aliases=["BB Curl", "Standing Barbell Curl"],
    ),
    Exercise(
        name="Dumbbell Curl",
        muscle_groups=[MuscleGroup.BICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Curl", "Bicep Curl", "Standing DB Curl"],
    ),
    Exercise(
        name="Hammer Curl",
        muscle_groups=[MuscleGroup.BICEPS, MuscleGroup.FOREARMS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Hammer Curl", "Neutral Grip Curl"],
    ),
    Exercise(
        name="Tricep Pushdown",
        muscle_groups=[MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.CABLE],
        aliases=["Cable Pushdown", "Rope Pushdown", "Tricep Extension"],
    ),
    Exercise(
        name="Skull Crusher",
        muscle_groups=[MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BARBELL, EquipmentType.EZ_BAR],
        aliases=["Lying Tricep Extension", "French Press"],
    ),
    Exercise(
        name="Overhead Tricep Extension",
        muscle_groups=[MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL, EquipmentType.CABLE],
        aliases=["Tricep Overhead Extension", "DB Overhead Extension"],
    ),
    # Core
    Exercise(
        name="Plank",
        muscle_groups=[MuscleGroup.ABS, MuscleGroup.OBLIQUES],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Front Plank", "Forearm Plank"],
    ),
    Exercise(
        name="Hanging Leg Raise",
        muscle_groups=[MuscleGroup.ABS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Leg Raise", "Hanging Knee Raise"],
    ),
    Exercise(
        name="Cable Crunch",
        muscle_groups=[MuscleGroup.ABS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.CABLE],
        aliases=["Kneeling Cable Crunch", "Rope Crunch"],
    ),
    Exercise(
        name="Ab Wheel Rollout",
        muscle_groups=[MuscleGroup.ABS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Ab Rollout", "Wheel Rollout"],
    ),
]
