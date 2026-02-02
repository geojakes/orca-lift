"""Integration tests for the full pipeline.

These tests require API access and are meant to verify the full flow works.
Mark as slow/integration tests to skip in regular test runs.
"""

import pytest

from orca_lift.generators.liftoscript import LiftoscriptGenerator
from orca_lift.models.exercises import EquipmentType
from orca_lift.models.program import (
    Program,
    ProgramDay,
    ProgramExercise,
    ProgramWeek,
    ProgressionScheme,
    SetScheme,
)
from orca_lift.models.user_profile import (
    ExperienceLevel,
    FitnessGoal,
    StrengthLevel,
    UserProfile,
)


@pytest.fixture
def sample_user_profile():
    """Create a sample user profile for testing."""
    return UserProfile(
        name="Test User",
        experience_level=ExperienceLevel.INTERMEDIATE,
        goals=[FitnessGoal.STRENGTH, FitnessGoal.HYPERTROPHY],
        available_equipment=[
            EquipmentType.BARBELL,
            EquipmentType.DUMBBELL,
            EquipmentType.CABLE,
            EquipmentType.MACHINE,
        ],
        schedule_days=4,
        session_duration=60,
        strength_levels=[
            StrengthLevel(exercise="Squat", weight=100, reps=5),
            StrengthLevel(exercise="Bench Press", weight=80, reps=5),
            StrengthLevel(exercise="Deadlift", weight=120, reps=5),
        ],
    )


class TestPipelineIntegration:
    """Integration tests for the full generation pipeline."""

    def test_profile_to_liftoscript_flow(self, sample_user_profile):
        """Test that we can create a program and generate valid Liftoscript."""
        # Create a mock program (simulating AI output)
        program = Program(
            name="Test Generated Program",
            description="An automatically generated program",
            goals="Build strength and muscle",
            weeks=[
                ProgramWeek(
                    week_number=1,
                    days=[
                        ProgramDay(
                            name="Day 1",
                            focus="Upper A",
                            exercises=[
                                ProgramExercise(
                                    name="Bench Press",
                                    sets=[
                                        SetScheme(reps=5) for _ in range(4)
                                    ],
                                    progression=ProgressionScheme.LINEAR,
                                    progression_params={"increment": 5},
                                ),
                                ProgramExercise(
                                    name="Barbell Row",
                                    sets=[
                                        SetScheme(reps=5) for _ in range(4)
                                    ],
                                    progression=ProgressionScheme.LINEAR,
                                    progression_params={"increment": 5},
                                ),
                                ProgramExercise(
                                    name="Overhead Press",
                                    sets=[
                                        SetScheme(reps="8-10") for _ in range(3)
                                    ],
                                    progression=ProgressionScheme.DOUBLE,
                                    progression_params={"increment": 2.5},
                                ),
                            ],
                        ),
                        ProgramDay(
                            name="Day 2",
                            focus="Lower A",
                            exercises=[
                                ProgramExercise(
                                    name="Squat",
                                    sets=[
                                        SetScheme(reps=5) for _ in range(4)
                                    ],
                                    progression=ProgressionScheme.LINEAR,
                                    progression_params={"increment": 5},
                                ),
                                ProgramExercise(
                                    name="Romanian Deadlift",
                                    sets=[
                                        SetScheme(reps="8-10") for _ in range(3)
                                    ],
                                    progression=ProgressionScheme.DOUBLE,
                                    progression_params={"increment": 5},
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

        # Generate Liftoscript
        generator = LiftoscriptGenerator()
        liftoscript = generator.generate(program)

        # Validate the output
        is_valid, errors = generator.validate(liftoscript)

        assert is_valid, f"Liftoscript validation failed: {errors}"
        assert "Bench Press" in liftoscript
        assert "Squat" in liftoscript
        assert "progress:" in liftoscript
        assert "lp(" in liftoscript
        assert "dp(" in liftoscript

    def test_program_roundtrip(self):
        """Test that program can be serialized and deserialized."""
        original = Program(
            name="Roundtrip Test",
            description="Testing serialization",
            goals="Test goals",
            weeks=[
                ProgramWeek(
                    week_number=1,
                    days=[
                        ProgramDay(
                            name="Day 1",
                            exercises=[
                                ProgramExercise(
                                    name="Squat",
                                    sets=[SetScheme(reps=5, rpe=8)],
                                    progression=ProgressionScheme.LINEAR,
                                )
                            ],
                        )
                    ],
                )
            ],
            congregation_log=[{"phase": "test", "output": "test data"}],
        )

        # Serialize
        data = original.to_dict()

        # Deserialize
        restored = Program.from_dict(data)

        assert restored.name == original.name
        assert restored.goals == original.goals
        assert len(restored.weeks) == len(original.weeks)
        assert restored.weeks[0].days[0].exercises[0].name == "Squat"


@pytest.mark.skip(reason="Requires API access")
class TestAIPipeline:
    """Tests that require actual API calls."""

    async def test_full_generation(self, sample_user_profile):
        """Test full program generation with AI."""
        from orca_lift.agents import ProgramExecutor

        executor = ProgramExecutor(verbose=False)
        result = await executor.execute(
            user_profile=sample_user_profile,
            goals="Build strength, 4 days per week",
        )

        assert result.program is not None
        assert len(result.program.weeks) > 0
        assert result.liftoscript is not None
        assert len(result.liftoscript) > 0

    async def test_refinement(self, sample_user_profile):
        """Test program refinement."""
        from orca_lift.services.refine import RefinementService

        # Create a simple program
        program = Program(
            name="Test",
            description="",
            goals="",
            weeks=[
                ProgramWeek(
                    week_number=1,
                    days=[
                        ProgramDay(
                            name="Day 1",
                            focus="Push",
                            exercises=[
                                ProgramExercise(
                                    name="Bench Press",
                                    sets=[SetScheme(reps=5) for _ in range(4)],
                                )
                            ],
                        )
                    ],
                )
            ],
        )

        service = RefinementService()
        refined = await service.refine(program, "Add tricep work")

        # Check that something changed
        assert refined is not None
        # The exact change depends on AI response
