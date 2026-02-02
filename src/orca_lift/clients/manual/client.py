"""Manual user profile input via interactive questionnaire."""

import questionary
from questionary import Style

from ...models.exercises import EquipmentType
from ...models.user_profile import (
    ExperienceLevel,
    FitnessGoal,
    Limitation,
    StrengthLevel,
    UserProfile,
)

# Custom style for questionnaire
custom_style = Style(
    [
        ("qmark", "fg:#673ab7 bold"),
        ("question", "bold"),
        ("answer", "fg:#f44336 bold"),
        ("pointer", "fg:#673ab7 bold"),
        ("highlighted", "fg:#673ab7 bold"),
        ("selected", "fg:#cc5454"),
        ("separator", "fg:#cc5454"),
        ("instruction", ""),
        ("text", ""),
    ]
)


class ManualInputClient:
    """Interactive questionnaire for collecting user fitness profile."""

    async def collect_profile(self) -> UserProfile:
        """Run interactive questionnaire to collect user profile."""
        print("\n=== Fitness Profile Questionnaire ===\n")

        # Basic info
        name = await questionary.text(
            "What's your name?",
            style=custom_style,
        ).ask_async()

        # Experience level
        experience = await questionary.select(
            "What's your training experience level?",
            choices=[
                questionary.Choice("Beginner (less than 1 year)", ExperienceLevel.BEGINNER),
                questionary.Choice("Intermediate (1-3 years)", ExperienceLevel.INTERMEDIATE),
                questionary.Choice("Advanced (3+ years)", ExperienceLevel.ADVANCED),
            ],
            style=custom_style,
        ).ask_async()

        # Goals
        goals = await questionary.checkbox(
            "What are your primary fitness goals? (Select all that apply)",
            choices=[
                questionary.Choice("Build strength", FitnessGoal.STRENGTH),
                questionary.Choice("Build muscle (hypertrophy)", FitnessGoal.HYPERTROPHY),
                questionary.Choice("Powerlifting (squat/bench/deadlift)", FitnessGoal.POWERLIFTING),
                questionary.Choice("Muscular endurance", FitnessGoal.ENDURANCE),
                questionary.Choice("General fitness", FitnessGoal.GENERAL_FITNESS),
                questionary.Choice("Athletic performance", FitnessGoal.ATHLETIC),
                questionary.Choice("Fat loss", FitnessGoal.FAT_LOSS),
            ],
            style=custom_style,
        ).ask_async()

        if not goals:
            goals = [FitnessGoal.GENERAL_FITNESS]

        # Equipment
        equipment = await questionary.checkbox(
            "What equipment do you have access to?",
            choices=[
                questionary.Choice("Barbell", EquipmentType.BARBELL),
                questionary.Choice("Dumbbells", EquipmentType.DUMBBELL),
                questionary.Choice("Kettlebells", EquipmentType.KETTLEBELL),
                questionary.Choice("Cable machines", EquipmentType.CABLE),
                questionary.Choice("Weight machines", EquipmentType.MACHINE),
                questionary.Choice("Bodyweight only", EquipmentType.BODYWEIGHT),
                questionary.Choice("Resistance bands", EquipmentType.BANDS),
                questionary.Choice("EZ Bar", EquipmentType.EZ_BAR),
                questionary.Choice("Trap Bar", EquipmentType.TRAP_BAR),
                questionary.Choice("Smith Machine", EquipmentType.SMITH_MACHINE),
            ],
            style=custom_style,
        ).ask_async()

        if not equipment:
            equipment = [EquipmentType.BODYWEIGHT]

        # Schedule
        schedule_days = await questionary.select(
            "How many days per week can you train?",
            choices=["2", "3", "4", "5", "6"],
            style=custom_style,
        ).ask_async()
        schedule_days = int(schedule_days)

        session_duration = await questionary.select(
            "How long are your typical training sessions?",
            choices=[
                questionary.Choice("30 minutes", 30),
                questionary.Choice("45 minutes", 45),
                questionary.Choice("60 minutes", 60),
                questionary.Choice("75 minutes", 75),
                questionary.Choice("90 minutes", 90),
                questionary.Choice("120 minutes", 120),
            ],
            style=custom_style,
        ).ask_async()

        # Optional: Age and body weight
        age = None
        body_weight = None

        collect_optional = await questionary.confirm(
            "Would you like to provide age and body weight? (optional)",
            default=False,
            style=custom_style,
        ).ask_async()

        if collect_optional:
            age_str = await questionary.text(
                "Your age:",
                style=custom_style,
            ).ask_async()
            try:
                age = int(age_str)
            except (ValueError, TypeError):
                age = None

            weight_str = await questionary.text(
                "Your body weight (in kg):",
                style=custom_style,
            ).ask_async()
            try:
                body_weight = float(weight_str)
            except (ValueError, TypeError):
                body_weight = None

        # Strength levels
        strength_levels: list[StrengthLevel] = []

        collect_strength = await questionary.confirm(
            "Would you like to enter your current strength levels for major lifts?",
            default=True,
            style=custom_style,
        ).ask_async()

        if collect_strength:
            strength_levels = await self._collect_strength_levels()

        # Limitations
        limitations: list[Limitation] = []

        has_limitations = await questionary.confirm(
            "Do you have any injuries or movement limitations?",
            default=False,
            style=custom_style,
        ).ask_async()

        if has_limitations:
            limitations = await self._collect_limitations()

        # Additional notes
        notes = await questionary.text(
            "Any additional notes or preferences? (optional)",
            default="",
            style=custom_style,
        ).ask_async()

        return UserProfile(
            name=name or "User",
            experience_level=experience,
            goals=goals,
            available_equipment=equipment,
            schedule_days=schedule_days,
            session_duration=session_duration,
            strength_levels=strength_levels,
            limitations=limitations,
            age=age,
            body_weight=body_weight,
            notes=notes or "",
        )

    async def _collect_strength_levels(self) -> list[StrengthLevel]:
        """Collect strength levels for major lifts."""
        strength_levels = []
        main_lifts = ["Squat", "Bench Press", "Deadlift", "Overhead Press"]

        print("\nEnter your current working weight (the weight you use for sets of 5-8).")
        print("Leave blank to skip an exercise.\n")

        for lift in main_lifts:
            weight_str = await questionary.text(
                f"{lift} - weight in kg:",
                default="",
                style=custom_style,
            ).ask_async()

            if weight_str:
                try:
                    weight = float(weight_str)
                    reps = await questionary.text(
                        f"{lift} - how many reps at that weight?",
                        default="5",
                        style=custom_style,
                    ).ask_async()
                    reps = int(reps) if reps else 5

                    strength_levels.append(
                        StrengthLevel(
                            exercise=lift,
                            weight=weight,
                            reps=reps,
                        )
                    )
                except (ValueError, TypeError):
                    continue

        # Option to add more exercises
        add_more = await questionary.confirm(
            "Would you like to add strength levels for other exercises?",
            default=False,
            style=custom_style,
        ).ask_async()

        while add_more:
            exercise = await questionary.text(
                "Exercise name:",
                style=custom_style,
            ).ask_async()

            weight_str = await questionary.text(
                "Weight in kg:",
                style=custom_style,
            ).ask_async()

            reps_str = await questionary.text(
                "Reps:",
                default="5",
                style=custom_style,
            ).ask_async()

            try:
                weight = float(weight_str)
                reps = int(reps_str) if reps_str else 5

                strength_levels.append(
                    StrengthLevel(
                        exercise=exercise,
                        weight=weight,
                        reps=reps,
                    )
                )
            except (ValueError, TypeError):
                pass

            add_more = await questionary.confirm(
                "Add another exercise?",
                default=False,
                style=custom_style,
            ).ask_async()

        return strength_levels

    async def _collect_limitations(self) -> list[Limitation]:
        """Collect injury and movement limitations."""
        limitations = []

        while True:
            description = await questionary.text(
                "Describe the limitation/injury:",
                style=custom_style,
            ).ask_async()

            if not description:
                break

            severity = await questionary.select(
                "How severe is this limitation?",
                choices=[
                    questionary.Choice("Mild (can work around it)", "mild"),
                    questionary.Choice("Moderate (need to modify exercises)", "moderate"),
                    questionary.Choice("Severe (must avoid certain movements)", "severe"),
                ],
                style=custom_style,
            ).ask_async()

            affected = await questionary.text(
                "Which exercises should be avoided or modified? (comma-separated, or leave blank)",
                default="",
                style=custom_style,
            ).ask_async()

            affected_exercises = [
                ex.strip() for ex in affected.split(",") if ex.strip()
            ]

            limitations.append(
                Limitation(
                    description=description,
                    affected_exercises=affected_exercises,
                    severity=severity,
                )
            )

            add_more = await questionary.confirm(
                "Add another limitation?",
                default=False,
                style=custom_style,
            ).ask_async()

            if not add_more:
                break

        return limitations
