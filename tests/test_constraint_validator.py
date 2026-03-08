"""Tests for constraint validator."""

import pytest

from orca_lift.models.exercises import EquipmentType
from orca_lift.models.user_profile import (
    ExperienceLevel,
    FitnessGoal,
    Limitation,
    UserProfile,
)
from orca_lift.validators.constraint_validator import (
    ConstraintViolation,
    ValidationResult,
    ViolationSeverity,
    build_exercise_lookup,
    validate_program_constraints,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def minimal_equipment_profile():
    """Profile with only bodyweight + dumbbell."""
    return UserProfile(
        name="Minimal User",
        experience_level=ExperienceLevel.BEGINNER,
        goals=[FitnessGoal.GENERAL_FITNESS],
        available_equipment=[EquipmentType.BODYWEIGHT, EquipmentType.DUMBBELL],
        schedule_days=3,
        session_duration=45,
    )


@pytest.fixture
def profile_with_limitations():
    """Profile with injury limitations."""
    return UserProfile(
        name="Limited User",
        experience_level=ExperienceLevel.INTERMEDIATE,
        goals=[FitnessGoal.STRENGTH],
        available_equipment=[
            EquipmentType.BARBELL,
            EquipmentType.DUMBBELL,
            EquipmentType.BODYWEIGHT,
        ],
        schedule_days=4,
        session_duration=60,
        limitations=[
            Limitation(
                description="Shoulder impingement",
                affected_exercises=["Overhead Press", "Lateral Raise"],
                severity="severe",
            ),
            Limitation(
                description="Mild knee discomfort",
                affected_exercises=["Squat", "Leg Press"],
                severity="mild",
            ),
        ],
    )


@pytest.fixture
def sample_program_data():
    """A valid program dict with barbell + dumbbell exercises."""
    return {
        "program_name": "Test Program",
        "weeks": [
            {
                "week_number": 1,
                "is_deload": False,
                "days": [
                    {
                        "name": "Day 1",
                        "focus": "Push",
                        "exercises": [
                            {
                                "name": "Bench Press, Barbell",
                                "sets": 4,
                                "reps_min": 5,
                                "reps_max": 5,
                                "progression": "lp",
                                "increment": 5,
                            },
                            {
                                "name": "Shoulder Press, Dumbbell",
                                "sets": 3,
                                "reps_min": 8,
                                "reps_max": 10,
                                "progression": "dp",
                                "increment": 2.5,
                            },
                        ],
                    },
                    {
                        "name": "Day 2",
                        "focus": "Pull",
                        "exercises": [
                            {
                                "name": "Bent Over Row, Barbell",
                                "sets": 4,
                                "reps_min": 5,
                                "reps_max": 5,
                                "progression": "lp",
                                "increment": 5,
                            },
                        ],
                    },
                    {
                        "name": "Day 3",
                        "focus": "Legs",
                        "exercises": [
                            {
                                "name": "Squat, Barbell",
                                "sets": 4,
                                "reps_min": 5,
                                "reps_max": 5,
                                "progression": "lp",
                                "increment": 5,
                            },
                        ],
                    },
                    {
                        "name": "Day 4",
                        "focus": "Upper",
                        "exercises": [
                            {
                                "name": "Bench Press, Dumbbell",
                                "sets": 3,
                                "reps_min": 8,
                                "reps_max": 12,
                                "progression": "dp",
                                "increment": 5,
                            },
                        ],
                    },
                ],
            },
        ],
    }


# ---------------------------------------------------------------------------
# Exercise Lookup Tests
# ---------------------------------------------------------------------------


class TestBuildExerciseLookup:
    def test_lookup_by_full_name(self):
        lookup = build_exercise_lookup()
        assert "bench press, barbell" in lookup

    def test_lookup_by_base_name(self):
        lookup = build_exercise_lookup()
        # "Bench Press" (base name before comma) should resolve
        assert "bench press" in lookup

    def test_lookup_by_alias(self):
        lookup = build_exercise_lookup()
        assert "bb bench" in lookup
        assert "ohp" in lookup

    def test_case_insensitive(self):
        lookup = build_exercise_lookup()
        assert "BENCH PRESS, BARBELL".lower() in lookup
        assert "Squat".lower() in lookup


# ---------------------------------------------------------------------------
# Equipment Validation Tests
# ---------------------------------------------------------------------------


class TestEquipmentValidation:
    def test_valid_equipment(self, sample_user_profile, sample_program_data):
        """Program with barbell + dumbbell exercises passes for user with that equipment."""
        result = validate_program_constraints(sample_program_data, sample_user_profile)
        equipment_errors = [
            v
            for v in result.violations
            if v.constraint_type == "equipment"
            and v.severity == ViolationSeverity.ERROR
        ]
        assert len(equipment_errors) == 0

    def test_missing_equipment_detected(self, minimal_equipment_profile):
        """Barbell exercise flagged for bodyweight+dumbbell-only user."""
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {
                            "name": "Day 1",
                            "focus": "Push",
                            "exercises": [
                                {
                                    "name": "Bench Press, Barbell",
                                    "sets": 4,
                                    "reps_min": 5,
                                    "reps_max": 5,
                                },
                            ],
                        },
                    ],
                },
            ],
        }
        result = validate_program_constraints(program, minimal_equipment_profile)
        assert not result.is_valid
        assert any(
            v.constraint_type == "equipment" and v.severity == ViolationSeverity.ERROR
            for v in result.violations
        )

    def test_cable_exercise_without_cable(self, minimal_equipment_profile):
        """Cable exercise flagged for user without cable machine."""
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {
                            "name": "Day 1",
                            "focus": "Arms",
                            "exercises": [
                                {
                                    "name": "Triceps Pushdown, Cable",
                                    "sets": 3,
                                    "reps_min": 10,
                                    "reps_max": 12,
                                },
                            ],
                        },
                    ],
                },
            ],
        }
        result = validate_program_constraints(program, minimal_equipment_profile)
        assert any(
            v.constraint_type == "equipment"
            and v.severity == ViolationSeverity.ERROR
            and "cable" in v.message.lower()
            for v in result.violations
        )

    def test_unknown_exercise_is_warning(self, minimal_equipment_profile):
        """Exercise not in library produces WARNING, not ERROR."""
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {
                            "name": "Day 1",
                            "focus": "Misc",
                            "exercises": [
                                {
                                    "name": "Underwater Basket Weave",
                                    "sets": 3,
                                    "reps_min": 10,
                                    "reps_max": 10,
                                },
                            ],
                        },
                    ],
                },
            ],
        }
        result = validate_program_constraints(program, minimal_equipment_profile)
        equipment_violations = [
            v for v in result.violations if v.constraint_type == "equipment"
        ]
        assert len(equipment_violations) == 1
        assert equipment_violations[0].severity == ViolationSeverity.WARNING

    def test_bodyweight_exercise_always_valid(self, minimal_equipment_profile):
        """Bodyweight exercises pass for any profile with BODYWEIGHT equipment."""
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {
                            "name": "Day 1",
                            "focus": "Upper",
                            "exercises": [
                                {"name": "Push Up, Bodyweight", "sets": 3, "reps_min": 10, "reps_max": 15},
                                {"name": "Pull Up, Bodyweight", "sets": 3, "reps_min": 5, "reps_max": 8},
                            ],
                        },
                    ],
                },
            ],
        }
        result = validate_program_constraints(program, minimal_equipment_profile)
        equipment_errors = [
            v
            for v in result.violations
            if v.constraint_type == "equipment"
            and v.severity == ViolationSeverity.ERROR
        ]
        assert len(equipment_errors) == 0


# ---------------------------------------------------------------------------
# Schedule Validation Tests
# ---------------------------------------------------------------------------


class TestScheduleValidation:
    def test_matching_days(self, sample_user_profile, sample_program_data):
        """4-day program for 4-day profile passes."""
        result = validate_program_constraints(sample_program_data, sample_user_profile)
        schedule_errors = [
            v for v in result.violations if v.constraint_type == "schedule"
        ]
        assert len(schedule_errors) == 0

    def test_too_many_days(self, minimal_equipment_profile):
        """5-day program for 3-day profile is flagged."""
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {"name": f"Day {i}", "focus": "Full Body", "exercises": []}
                        for i in range(1, 6)
                    ],
                },
            ],
        }
        result = validate_program_constraints(program, minimal_equipment_profile)
        assert any(
            v.constraint_type == "schedule" and v.severity == ViolationSeverity.ERROR
            for v in result.violations
        )

    def test_fewer_days_is_ok(self, sample_user_profile):
        """2-day program for 4-day profile is NOT flagged."""
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {"name": "Day 1", "focus": "Upper", "exercises": []},
                        {"name": "Day 2", "focus": "Lower", "exercises": []},
                    ],
                },
            ],
        }
        result = validate_program_constraints(program, sample_user_profile)
        schedule_errors = [
            v for v in result.violations if v.constraint_type == "schedule"
        ]
        assert len(schedule_errors) == 0


# ---------------------------------------------------------------------------
# Limitation Validation Tests
# ---------------------------------------------------------------------------


class TestLimitationValidation:
    def test_severe_limitation_is_error(self, profile_with_limitations):
        """Severe limitation exercise produces ERROR."""
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {
                            "name": "Day 1",
                            "focus": "Push",
                            "exercises": [
                                {
                                    "name": "Overhead Press, Barbell",
                                    "sets": 3,
                                    "reps_min": 8,
                                    "reps_max": 10,
                                },
                            ],
                        },
                    ],
                },
            ],
        }
        result = validate_program_constraints(program, profile_with_limitations)
        limitation_errors = [
            v
            for v in result.violations
            if v.constraint_type == "limitation"
            and v.severity == ViolationSeverity.ERROR
        ]
        assert len(limitation_errors) > 0

    def test_mild_limitation_is_warning(self, profile_with_limitations):
        """Mild limitation exercise produces WARNING."""
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {
                            "name": "Day 1",
                            "focus": "Legs",
                            "exercises": [
                                {
                                    "name": "Squat, Barbell",
                                    "sets": 4,
                                    "reps_min": 5,
                                    "reps_max": 5,
                                },
                            ],
                        },
                    ],
                },
            ],
        }
        result = validate_program_constraints(program, profile_with_limitations)
        limitation_warnings = [
            v
            for v in result.violations
            if v.constraint_type == "limitation"
            and v.severity == ViolationSeverity.WARNING
        ]
        assert len(limitation_warnings) > 0

    def test_no_limitations_passes(self, sample_user_profile, sample_program_data):
        """Profile without limitations has no limitation violations."""
        result = validate_program_constraints(sample_program_data, sample_user_profile)
        limitation_violations = [
            v for v in result.violations if v.constraint_type == "limitation"
        ]
        assert len(limitation_violations) == 0


# ---------------------------------------------------------------------------
# Session Duration Validation Tests
# ---------------------------------------------------------------------------


class TestSessionDurationValidation:
    def test_reasonable_session_passes(self, sample_user_profile):
        """Session with moderate exercises passes."""
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {
                            "name": "Day 1",
                            "focus": "Upper",
                            "exercises": [
                                {"name": "Bench Press, Barbell", "sets": 3, "reps_min": 5, "reps_max": 5},
                                {"name": "Bent Over Row, Barbell", "sets": 3, "reps_min": 5, "reps_max": 5},
                                {"name": "Bicep Curl, Dumbbell", "sets": 2, "reps_min": 10, "reps_max": 12},
                            ],
                        },
                    ],
                },
            ],
        }
        result = validate_program_constraints(program, sample_user_profile)
        duration_warnings = [
            v for v in result.violations if v.constraint_type == "duration"
        ]
        assert len(duration_warnings) == 0

    def test_excessive_volume_warns(self, minimal_equipment_profile):
        """Day with many exercises warns about duration (45 min limit)."""
        exercises = [
            {"name": f"Exercise {i}", "sets": 4, "reps_min": 8, "reps_max": 12}
            for i in range(12)
        ]
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {
                            "name": "Day 1",
                            "focus": "Full Body",
                            "exercises": exercises,
                        },
                    ],
                },
            ],
        }
        result = validate_program_constraints(program, minimal_equipment_profile)
        duration_warnings = [
            v for v in result.violations if v.constraint_type == "duration"
        ]
        assert len(duration_warnings) > 0


# ---------------------------------------------------------------------------
# Prompt Constraint Validation Tests
# ---------------------------------------------------------------------------


class TestPromptConstraintValidation:
    def test_treadmill_only_flags_elliptical(self, sample_user_profile):
        """Extracted 'only treadmill' constraint flags elliptical exercise."""
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {
                            "name": "Day 1",
                            "focus": "Cardio",
                            "exercises": [
                                {"name": "Elliptical Trainer", "sets": 1, "reps_min": 1, "reps_max": 1},
                            ],
                        },
                    ],
                },
            ],
        }
        extracted = [
            {
                "type": "cardio",
                "rule": "Only treadmill for cardio exercises",
                "violations": ["elliptical", "bike", "rowing machine"],
            },
        ]
        result = validate_program_constraints(
            program, sample_user_profile, extracted_constraints=extracted
        )
        prompt_errors = [
            v
            for v in result.violations
            if v.constraint_type == "prompt_constraint"
        ]
        assert len(prompt_errors) > 0
        assert any("elliptical" in v.message.lower() for v in prompt_errors)

    def test_no_violations_when_compliant(self, sample_user_profile):
        """Program with treadmill passes the 'only treadmill' constraint."""
        program = {
            "weeks": [
                {
                    "week_number": 1,
                    "is_deload": False,
                    "days": [
                        {
                            "name": "Day 1",
                            "focus": "Cardio",
                            "exercises": [
                                {"name": "Treadmill Walk", "sets": 1, "reps_min": 1, "reps_max": 1},
                            ],
                        },
                    ],
                },
            ],
        }
        extracted = [
            {
                "type": "cardio",
                "rule": "Only treadmill for cardio exercises",
                "violations": ["elliptical", "bike", "rowing machine"],
            },
        ]
        result = validate_program_constraints(
            program, sample_user_profile, extracted_constraints=extracted
        )
        prompt_errors = [
            v
            for v in result.violations
            if v.constraint_type == "prompt_constraint"
        ]
        assert len(prompt_errors) == 0

    def test_no_extracted_constraints(self, sample_user_profile, sample_program_data):
        """No prompt constraint violations when no constraints extracted."""
        result = validate_program_constraints(
            sample_program_data, sample_user_profile, extracted_constraints=None
        )
        prompt_violations = [
            v for v in result.violations if v.constraint_type == "prompt_constraint"
        ]
        assert len(prompt_violations) == 0


# ---------------------------------------------------------------------------
# ValidationResult Tests
# ---------------------------------------------------------------------------


class TestValidationResult:
    def test_valid_when_no_errors(self):
        """is_valid is True when only warnings exist."""
        result = ValidationResult(
            violations=[
                ConstraintViolation(
                    constraint_type="equipment",
                    severity=ViolationSeverity.WARNING,
                    message="Unknown exercise",
                    location="Week 1, Day 1",
                ),
            ]
        )
        assert result.is_valid
        assert len(result.warnings) == 1
        assert len(result.errors) == 0

    def test_invalid_when_errors_exist(self):
        """is_valid is False when errors exist."""
        result = ValidationResult(
            violations=[
                ConstraintViolation(
                    constraint_type="equipment",
                    severity=ViolationSeverity.ERROR,
                    message="Missing barbell",
                    location="Week 1, Day 1",
                ),
            ]
        )
        assert not result.is_valid
        assert len(result.errors) == 1

    def test_empty_result_is_valid(self):
        """Empty validation result is valid."""
        result = ValidationResult()
        assert result.is_valid
        assert len(result.violations) == 0


# ---------------------------------------------------------------------------
# Integration: Full validation
# ---------------------------------------------------------------------------


class TestFullValidation:
    def test_valid_program_passes(self, sample_user_profile, sample_program_data):
        """A well-formed program matching the profile passes cleanly."""
        result = validate_program_constraints(sample_program_data, sample_user_profile)
        assert len(result.errors) == 0

    def test_empty_program(self, sample_user_profile):
        """Empty program data doesn't crash."""
        result = validate_program_constraints({}, sample_user_profile)
        assert result.is_valid

    def test_malformed_program_data(self, sample_user_profile):
        """Non-dict entries in program data are skipped gracefully."""
        program = {
            "weeks": [
                "not a dict",
                {
                    "week_number": 1,
                    "days": [
                        "also not a dict",
                        {
                            "name": "Day 1",
                            "exercises": [
                                "still not a dict",
                                {"name": "Bench Press, Barbell", "sets": 3, "reps_min": 5, "reps_max": 5},
                            ],
                        },
                    ],
                },
            ],
        }
        # Should not raise
        result = validate_program_constraints(program, sample_user_profile)
        assert isinstance(result, ValidationResult)
