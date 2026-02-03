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


# Common exercise library - names must match Liftosaur format exactly
# Format: "Exercise Name, Equipment Type"
COMMON_EXERCISES: list[Exercise] = [
    # Chest - Horizontal Push
    Exercise(
        name="Bench Press, Barbell",
        muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.PUSH_HORIZONTAL,
        equipment=[EquipmentType.BARBELL],
        aliases=["Flat Bench Press", "Barbell Bench Press", "BB Bench"],
        is_compound=True,
    ),
    Exercise(
        name="Incline Bench Press, Barbell",
        muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.PUSH_HORIZONTAL,
        equipment=[EquipmentType.BARBELL],
        aliases=["Incline Press", "Incline BB Press"],
        is_compound=True,
    ),
    Exercise(
        name="Bench Press, Dumbbell",
        muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.PUSH_HORIZONTAL,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Bench Press", "Flat DB Press", "Dumbbell Bench Press"],
        is_compound=True,
    ),
    Exercise(
        name="Chest Fly, Dumbbell",
        muscle_groups=[MuscleGroup.CHEST],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["Dumbbell Fly", "DB Fly", "Pec Fly"],
    ),
    Exercise(
        name="Push Up, Bodyweight",
        muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.PUSH_HORIZONTAL,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Pushup", "Press-up", "Push-up"],
        is_compound=True,
    ),
    Exercise(
        name="Chest Dip, Bodyweight",
        muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.PUSH_HORIZONTAL,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Dip", "Parallel Bar Dip"],
        is_compound=True,
    ),
    # Shoulders - Vertical Push
    Exercise(
        name="Overhead Press, Barbell",
        muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.PUSH_VERTICAL,
        equipment=[EquipmentType.BARBELL],
        aliases=["OHP", "Shoulder Press", "Military Press", "Standing Press"],
        is_compound=True,
    ),
    Exercise(
        name="Shoulder Press, Dumbbell",
        muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.PUSH_VERTICAL,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Shoulder Press", "Seated DB Press", "Dumbbell Shoulder Press"],
        is_compound=True,
    ),
    Exercise(
        name="Lateral Raise, Dumbbell",
        muscle_groups=[MuscleGroup.SHOULDERS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["Side Raise", "DB Lateral Raise", "Side Lateral Raise"],
    ),
    Exercise(
        name="Face Pull, Band",
        muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.TRAPS],
        movement_pattern=MovementPattern.PULL_HORIZONTAL,
        equipment=[EquipmentType.BANDS],
        aliases=["Face Pull", "Rear Delt Face Pull"],
    ),
    # Back - Horizontal Pull
    Exercise(
        name="Bent Over Row, Barbell",
        muscle_groups=[MuscleGroup.BACK, MuscleGroup.BICEPS, MuscleGroup.LATS],
        movement_pattern=MovementPattern.PULL_HORIZONTAL,
        equipment=[EquipmentType.BARBELL],
        aliases=["Barbell Row", "BB Row"],
        is_compound=True,
    ),
    Exercise(
        name="Pendlay Row, Barbell",
        muscle_groups=[MuscleGroup.BACK, MuscleGroup.BICEPS, MuscleGroup.LATS],
        movement_pattern=MovementPattern.PULL_HORIZONTAL,
        equipment=[EquipmentType.BARBELL],
        aliases=["Pendlay Row"],
        is_compound=True,
    ),
    Exercise(
        name="Bent Over One Arm Row, Dumbbell",
        muscle_groups=[MuscleGroup.BACK, MuscleGroup.BICEPS, MuscleGroup.LATS],
        movement_pattern=MovementPattern.PULL_HORIZONTAL,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Row", "One Arm Row", "Single Arm DB Row", "Dumbbell Row"],
        is_compound=True,
    ),
    Exercise(
        name="Seated Row, Cable",
        muscle_groups=[MuscleGroup.BACK, MuscleGroup.BICEPS, MuscleGroup.LATS],
        movement_pattern=MovementPattern.PULL_HORIZONTAL,
        equipment=[EquipmentType.CABLE],
        aliases=["Cable Row", "Seated Cable Row", "Low Row"],
        is_compound=True,
    ),
    # Back - Vertical Pull
    Exercise(
        name="Pull Up, Bodyweight",
        muscle_groups=[MuscleGroup.LATS, MuscleGroup.BICEPS, MuscleGroup.BACK],
        movement_pattern=MovementPattern.PULL_VERTICAL,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Pullup", "Wide Grip Pull-up", "Pull-up"],
        is_compound=True,
    ),
    Exercise(
        name="Chin Up, Bodyweight",
        muscle_groups=[MuscleGroup.LATS, MuscleGroup.BICEPS, MuscleGroup.BACK],
        movement_pattern=MovementPattern.PULL_VERTICAL,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Chinup", "Underhand Pull-up", "Chin-up"],
        is_compound=True,
    ),
    Exercise(
        name="Lat Pulldown, Cable",
        muscle_groups=[MuscleGroup.LATS, MuscleGroup.BICEPS, MuscleGroup.BACK],
        movement_pattern=MovementPattern.PULL_VERTICAL,
        equipment=[EquipmentType.CABLE],
        aliases=["Cable Pulldown", "Wide Grip Pulldown", "Lat Pulldown"],
        is_compound=True,
    ),
    # Legs - Squat Pattern
    Exercise(
        name="Squat, Barbell",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS],
        movement_pattern=MovementPattern.SQUAT,
        equipment=[EquipmentType.BARBELL],
        aliases=["Back Squat", "Barbell Squat", "BB Squat", "Squat"],
        is_compound=True,
    ),
    Exercise(
        name="Front Squat, Barbell",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.ABS],
        movement_pattern=MovementPattern.SQUAT,
        equipment=[EquipmentType.BARBELL],
        aliases=["Front Squat", "Barbell Front Squat"],
        is_compound=True,
    ),
    Exercise(
        name="Goblet Squat, Dumbbell",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.SQUAT,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Goblet Squat", "Goblet Squat"],
        is_compound=True,
    ),
    Exercise(
        name="Goblet Squat, Kettlebell",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.SQUAT,
        equipment=[EquipmentType.KETTLEBELL],
        aliases=["KB Goblet Squat"],
        is_compound=True,
    ),
    Exercise(
        name="Leg Press, Leverage Machine",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.SQUAT,
        equipment=[EquipmentType.MACHINE],
        aliases=["Leg Press", "Machine Leg Press", "45 Degree Leg Press"],
        is_compound=True,
    ),
    # Legs - Hinge Pattern
    Exercise(
        name="Deadlift, Barbell",
        muscle_groups=[
            MuscleGroup.HAMSTRINGS,
            MuscleGroup.GLUTES,
            MuscleGroup.LOWER_BACK,
            MuscleGroup.BACK,
        ],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.BARBELL],
        aliases=["Conventional Deadlift", "BB Deadlift", "Deadlift"],
        is_compound=True,
    ),
    Exercise(
        name="Romanian Deadlift, Barbell",
        muscle_groups=[MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES, MuscleGroup.LOWER_BACK],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.BARBELL],
        aliases=["RDL", "Romanian DL", "Romanian Deadlift"],
        is_compound=True,
    ),
    Exercise(
        name="Romanian Deadlift, Dumbbell",
        muscle_groups=[MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB RDL", "Dumbbell RDL", "Dumbbell Romanian Deadlift"],
        is_compound=True,
    ),
    Exercise(
        name="Stiff Leg Deadlift, Barbell",
        muscle_groups=[MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES, MuscleGroup.LOWER_BACK],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.BARBELL],
        aliases=["Stiff Leg Deadlift", "SLDL"],
        is_compound=True,
    ),
    Exercise(
        name="Hip Thrust, Barbell",
        muscle_groups=[MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.BARBELL],
        aliases=["Barbell Hip Thrust", "Hip Thrust"],
        is_compound=True,
    ),
    Exercise(
        name="Glute Bridge, Barbell",
        muscle_groups=[MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.BARBELL],
        aliases=["Glute Bridge", "Barbell Glute Bridge"],
        is_compound=True,
    ),
    # Legs - Lunge Pattern
    Exercise(
        name="Lunge, Bodyweight",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.LUNGE,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Walking Lunge", "Forward Lunge", "Lunge"],
        is_compound=True,
    ),
    Exercise(
        name="Lunge, Dumbbell",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.LUNGE,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Lunge", "Dumbbell Lunge"],
        is_compound=True,
    ),
    Exercise(
        name="Bulgarian Split Squat, Dumbbell",
        muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.LUNGE,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["BSS", "Rear Foot Elevated Split Squat", "RFESS", "Bulgarian Split Squat"],
        is_compound=True,
    ),
    # Legs - Isolation
    Exercise(
        name="Lying Leg Curl, Leverage Machine",
        muscle_groups=[MuscleGroup.HAMSTRINGS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.MACHINE],
        aliases=["Leg Curl", "Hamstring Curl", "Lying Leg Curl"],
    ),
    Exercise(
        name="Seated Leg Curl, Leverage Machine",
        muscle_groups=[MuscleGroup.HAMSTRINGS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.MACHINE],
        aliases=["Seated Leg Curl"],
    ),
    Exercise(
        name="Leg Extension, Leverage Machine",
        muscle_groups=[MuscleGroup.QUADS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.MACHINE],
        aliases=["Leg Extension", "Quad Extension", "Machine Leg Extension"],
    ),
    Exercise(
        name="Standing Calf Raise, Leverage Machine",
        muscle_groups=[MuscleGroup.CALVES],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.MACHINE],
        aliases=["Calf Raise", "Standing Calf Raise"],
    ),
    Exercise(
        name="Seated Calf Raise, Leverage Machine",
        muscle_groups=[MuscleGroup.CALVES],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.MACHINE],
        aliases=["Seated Calf Raise"],
    ),
    # Arms - Biceps
    Exercise(
        name="Bicep Curl, Barbell",
        muscle_groups=[MuscleGroup.BICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BARBELL],
        aliases=["BB Curl", "Standing Barbell Curl", "Barbell Curl"],
    ),
    Exercise(
        name="Bicep Curl, Dumbbell",
        muscle_groups=[MuscleGroup.BICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Curl", "Bicep Curl", "Standing DB Curl", "Dumbbell Curl"],
    ),
    Exercise(
        name="Hammer Curl, Dumbbell",
        muscle_groups=[MuscleGroup.BICEPS, MuscleGroup.FOREARMS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["DB Hammer Curl", "Neutral Grip Curl", "Hammer Curl"],
    ),
    Exercise(
        name="Preacher Curl, Barbell",
        muscle_groups=[MuscleGroup.BICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BARBELL],
        aliases=["Preacher Curl"],
    ),
    Exercise(
        name="Preacher Curl, EZ Bar",
        muscle_groups=[MuscleGroup.BICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.EZ_BAR],
        aliases=["EZ Bar Preacher Curl"],
    ),
    # Arms - Triceps
    Exercise(
        name="Triceps Pushdown, Cable",
        muscle_groups=[MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.CABLE],
        aliases=["Cable Pushdown", "Rope Pushdown", "Tricep Pushdown"],
    ),
    Exercise(
        name="Skullcrusher, Barbell",
        muscle_groups=[MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BARBELL],
        aliases=["Skull Crusher", "Lying Tricep Extension"],
    ),
    Exercise(
        name="Skullcrusher, EZ Bar",
        muscle_groups=[MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.EZ_BAR],
        aliases=["EZ Bar Skull Crusher", "French Press"],
    ),
    Exercise(
        name="Triceps Extension, Dumbbell",
        muscle_groups=[MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["Overhead Tricep Extension", "DB Overhead Extension"],
    ),
    Exercise(
        name="Triceps Extension, Cable",
        muscle_groups=[MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.CABLE],
        aliases=["Cable Tricep Extension", "Overhead Cable Extension"],
    ),
    Exercise(
        name="Triceps Dip, Bodyweight",
        muscle_groups=[MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Tricep Dip", "Bench Dip"],
    ),
    # Core
    Exercise(
        name="Plank, Bodyweight",
        muscle_groups=[MuscleGroup.ABS, MuscleGroup.OBLIQUES],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Front Plank", "Forearm Plank", "Plank"],
    ),
    Exercise(
        name="Hanging Leg Raise, Bodyweight",
        muscle_groups=[MuscleGroup.ABS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Leg Raise", "Hanging Knee Raise", "Hanging Leg Raise"],
    ),
    Exercise(
        name="Crunch, Cable",
        muscle_groups=[MuscleGroup.ABS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.CABLE],
        aliases=["Cable Crunch", "Kneeling Cable Crunch", "Rope Crunch"],
    ),
    Exercise(
        name="Ab Wheel, Bodyweight",
        muscle_groups=[MuscleGroup.ABS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Ab Rollout", "Wheel Rollout", "Ab Wheel Rollout"],
    ),
    # Additional exercises
    Exercise(
        name="Shrug, Barbell",
        muscle_groups=[MuscleGroup.TRAPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.BARBELL],
        aliases=["Barbell Shrug", "Shrug"],
    ),
    Exercise(
        name="Shrug, Dumbbell",
        muscle_groups=[MuscleGroup.TRAPS],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["Dumbbell Shrug", "DB Shrug"],
    ),
    Exercise(
        name="Reverse Fly, Dumbbell",
        muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.BACK],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["Rear Delt Fly", "DB Reverse Fly"],
    ),
    Exercise(
        name="Good Morning, Barbell",
        muscle_groups=[MuscleGroup.HAMSTRINGS, MuscleGroup.LOWER_BACK, MuscleGroup.GLUTES],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.BARBELL],
        aliases=["Good Morning"],
        is_compound=True,
    ),
    Exercise(
        name="Sumo Deadlift, Barbell",
        muscle_groups=[MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES, MuscleGroup.QUADS],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.BARBELL],
        aliases=["Sumo Deadlift"],
        is_compound=True,
    ),
    Exercise(
        name="Trap Bar Deadlift, Trap Bar",
        muscle_groups=[MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES, MuscleGroup.QUADS],
        movement_pattern=MovementPattern.HINGE,
        equipment=[EquipmentType.TRAP_BAR],
        aliases=["Hex Bar Deadlift", "Trap Bar Deadlift"],
        is_compound=True,
    ),
    Exercise(
        name="T Bar Row, Leverage Machine",
        muscle_groups=[MuscleGroup.BACK, MuscleGroup.LATS, MuscleGroup.BICEPS],
        movement_pattern=MovementPattern.PULL_HORIZONTAL,
        equipment=[EquipmentType.MACHINE],
        aliases=["T-Bar Row", "T Bar Row"],
        is_compound=True,
    ),
    Exercise(
        name="Inverted Row, Bodyweight",
        muscle_groups=[MuscleGroup.BACK, MuscleGroup.BICEPS],
        movement_pattern=MovementPattern.PULL_HORIZONTAL,
        equipment=[EquipmentType.BODYWEIGHT],
        aliases=["Inverted Row", "Australian Pull-up", "Body Row"],
        is_compound=True,
    ),
    Exercise(
        name="Cable Crossover, Cable",
        muscle_groups=[MuscleGroup.CHEST],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.CABLE],
        aliases=["Cable Crossover", "Cable Fly"],
    ),
    Exercise(
        name="Incline Chest Fly, Dumbbell",
        muscle_groups=[MuscleGroup.CHEST],
        movement_pattern=MovementPattern.ISOLATION,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["Incline Fly", "Incline DB Fly"],
    ),
    Exercise(
        name="Arnold Press, Dumbbell",
        muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
        movement_pattern=MovementPattern.PUSH_VERTICAL,
        equipment=[EquipmentType.DUMBBELL],
        aliases=["Arnold Press"],
        is_compound=True,
    ),
    Exercise(
        name="Upright Row, Barbell",
        muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.TRAPS],
        movement_pattern=MovementPattern.PULL_VERTICAL,
        equipment=[EquipmentType.BARBELL],
        aliases=["Upright Row"],
        is_compound=True,
    ),
]
