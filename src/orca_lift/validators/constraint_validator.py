"""Post-generation constraint validation for workout programs.

Checks a generated program dict against UserProfile constraints and
extracted prompt constraints. All validation functions are pure — no AI
or DB dependencies — making them easy to unit test.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum

from ..models.exercises import COMMON_EXERCISES, EquipmentType, Exercise
from ..models.user_profile import UserProfile


class ViolationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass
class ConstraintViolation:
    constraint_type: str  # equipment, schedule, limitation, duration, prompt_constraint
    severity: ViolationSeverity
    message: str
    location: str  # e.g. "Week 1, Day 2: Cable Crossover"
    suggestion: str = ""

    def __str__(self) -> str:
        parts = [f"[{self.severity.value.upper()}] {self.message}"]
        if self.location:
            parts.append(f"  at {self.location}")
        if self.suggestion:
            parts.append(f"  suggestion: {self.suggestion}")
        return "\n".join(parts)


@dataclass
class ValidationResult:
    violations: list[ConstraintViolation] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    @property
    def errors(self) -> list[ConstraintViolation]:
        return [v for v in self.violations if v.severity == ViolationSeverity.ERROR]

    @property
    def warnings(self) -> list[ConstraintViolation]:
        return [v for v in self.violations if v.severity == ViolationSeverity.WARNING]


# ---------------------------------------------------------------------------
# Exercise name lookup
# ---------------------------------------------------------------------------

def build_exercise_lookup(
    exercises: list[Exercise] | None = None,
) -> dict[str, Exercise]:
    """Build a case-insensitive lookup from exercise names + aliases."""
    if exercises is None:
        exercises = COMMON_EXERCISES

    lookup: dict[str, Exercise] = {}
    for ex in exercises:
        # Full name: "Bench Press, Barbell"
        lookup[ex.name.lower()] = ex
        # Base name (before comma): "Bench Press"
        if ", " in ex.name:
            base = ex.name.split(", ")[0].lower()
            # Only add base if not already mapped (avoids ambiguity)
            if base not in lookup:
                lookup[base] = ex
        # All aliases
        for alias in ex.aliases:
            lookup[alias.lower()] = ex
    return lookup


def _find_exercise(name: str, lookup: dict[str, Exercise]) -> Exercise | None:
    """Try to match an exercise name against the lookup."""
    key = name.strip().lower()
    if key in lookup:
        return lookup[key]
    # Try base name (before comma) of the input
    if ", " in key:
        base = key.split(", ")[0]
        if base in lookup:
            return lookup[base]
    return None


# ---------------------------------------------------------------------------
# Iterate exercises in program dict
# ---------------------------------------------------------------------------

def _iter_program_exercises(
    program_data: dict,
) -> Iterator[tuple[str, dict]]:
    """Yield (location_string, exercise_dict) for every exercise in the program."""
    for week_data in program_data.get("weeks", []):
        if not isinstance(week_data, dict):
            continue
        week_num = week_data.get("week_number", "?")
        for day_data in week_data.get("days", []):
            if not isinstance(day_data, dict):
                continue
            day_name = day_data.get("name", day_data.get("focus", "?"))
            for ex_data in day_data.get("exercises", []):
                if not isinstance(ex_data, dict):
                    continue
                ex_name = ex_data.get("name", "Unknown")
                location = f"Week {week_num}, {day_name}: {ex_name}"
                yield location, ex_data


def _iter_program_days(
    program_data: dict,
) -> Iterator[tuple[int, list[dict]]]:
    """Yield (week_number, days_list) for every week in the program."""
    for week_data in program_data.get("weeks", []):
        if not isinstance(week_data, dict):
            continue
        week_num = week_data.get("week_number", 0)
        days = [d for d in week_data.get("days", []) if isinstance(d, dict)]
        yield week_num, days


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_equipment(
    program_data: dict,
    available_equipment: list[EquipmentType],
    lookup: dict[str, Exercise],
) -> list[ConstraintViolation]:
    """Check that exercises only use available equipment."""
    violations: list[ConstraintViolation] = []
    eq_set = {eq.value.lower() for eq in available_equipment}

    for location, ex_data in _iter_program_exercises(program_data):
        ex_name = ex_data.get("name", "")
        matched = _find_exercise(ex_name, lookup)
        if matched is None:
            violations.append(ConstraintViolation(
                constraint_type="equipment",
                severity=ViolationSeverity.WARNING,
                message=f"Unknown exercise '{ex_name}' — cannot verify equipment",
                location=location,
            ))
            continue

        # Check if at least one required equipment type is available
        required = {eq.value.lower() for eq in matched.equipment}
        if required and not required.intersection(eq_set):
            available_str = ", ".join(eq.value for eq in available_equipment)
            needed_str = ", ".join(eq.value for eq in matched.equipment)
            violations.append(ConstraintViolation(
                constraint_type="equipment",
                severity=ViolationSeverity.ERROR,
                message=f"'{ex_name}' requires {needed_str}, but user only has: {available_str}",
                location=location,
                suggestion=f"Replace with an alternative using available equipment ({available_str})",
            ))

    return violations


def _check_schedule(
    program_data: dict,
    schedule_days: int,
) -> list[ConstraintViolation]:
    """Check that each week doesn't exceed the allowed training days."""
    violations: list[ConstraintViolation] = []

    for week_num, days in _iter_program_days(program_data):
        if len(days) > schedule_days:
            violations.append(ConstraintViolation(
                constraint_type="schedule",
                severity=ViolationSeverity.ERROR,
                message=f"Week {week_num} has {len(days)} days but user requested {schedule_days} days/week",
                location=f"Week {week_num}",
                suggestion=f"Remove {len(days) - schedule_days} day(s) from this week",
            ))

    return violations


def _check_limitations(
    program_data: dict,
    limitations: list,
    lookup: dict[str, Exercise],
) -> list[ConstraintViolation]:
    """Check exercises against user's injury/movement limitations."""
    violations: list[ConstraintViolation] = []

    if not limitations:
        return violations

    for location, ex_data in _iter_program_exercises(program_data):
        ex_name = ex_data.get("name", "").lower()
        matched = _find_exercise(ex_name, lookup)
        # Check against each limitation
        for lim in limitations:
            for affected in lim.affected_exercises:
                affected_lower = affected.lower()
                # Match by exercise name or alias
                name_match = affected_lower in ex_name
                alias_match = False
                if matched:
                    alias_match = any(
                        affected_lower in alias.lower() for alias in matched.aliases
                    ) or affected_lower in matched.name.lower()

                if name_match or alias_match:
                    severity = (
                        ViolationSeverity.ERROR
                        if lim.severity == "severe"
                        else ViolationSeverity.WARNING
                    )
                    violations.append(ConstraintViolation(
                        constraint_type="limitation",
                        severity=severity,
                        message=f"'{ex_data.get('name', '')}' conflicts with limitation: {lim.description} ({lim.severity})",
                        location=location,
                        suggestion=f"Replace with an exercise that avoids {lim.description}",
                    ))

    return violations


def _check_session_duration(
    program_data: dict,
    session_duration: int,
    lookup: dict[str, Exercise],
) -> list[ConstraintViolation]:
    """Estimate session duration and warn if it exceeds target."""
    violations: list[ConstraintViolation] = []

    if not session_duration or session_duration <= 0:
        return violations

    for week_num, days in _iter_program_days(program_data):
        for day_data in days:
            day_name = day_data.get("name", day_data.get("focus", "?"))
            exercises = [e for e in day_data.get("exercises", []) if isinstance(e, dict)]

            # Estimate duration: warmup (2 min/exercise) + sets
            total_minutes = 0.0
            for ex in exercises:
                num_sets = ex.get("sets", 3)
                if not isinstance(num_sets, (int, float)):
                    try:
                        num_sets = int(num_sets)
                    except (ValueError, TypeError):
                        num_sets = 3
                matched = _find_exercise(ex.get("name", ""), lookup)
                is_compound = matched.is_compound if matched else False
                minutes_per_set = 3.0 if is_compound else 2.0
                total_minutes += 2.0 + (num_sets * minutes_per_set)  # warmup + working sets

            threshold = session_duration * 1.2  # 20% buffer
            if total_minutes > threshold:
                violations.append(ConstraintViolation(
                    constraint_type="duration",
                    severity=ViolationSeverity.WARNING,
                    message=(
                        f"Week {week_num}, {day_name}: estimated {total_minutes:.0f} min "
                        f"exceeds {session_duration} min target"
                    ),
                    location=f"Week {week_num}, {day_name}",
                    suggestion="Reduce exercise count or sets to fit within time limit",
                ))

    return violations


def _check_prompt_constraints(
    program_data: dict,
    extracted_constraints: list[dict],
) -> list[ConstraintViolation]:
    """Check program against constraints extracted from the user's goals prompt."""
    violations: list[ConstraintViolation] = []

    if not extracted_constraints:
        return violations

    for constraint in extracted_constraints:
        if not isinstance(constraint, dict):
            continue
        violation_keywords = constraint.get("violations", [])
        if not violation_keywords:
            continue

        rule = constraint.get("rule", "")
        constraint_type = constraint.get("type", "other")

        # Check each exercise name against violation keywords
        for location, ex_data in _iter_program_exercises(program_data):
            ex_name = ex_data.get("name", "").lower()
            for keyword in violation_keywords:
                if not isinstance(keyword, str):
                    continue
                if keyword.lower() in ex_name:
                    violations.append(ConstraintViolation(
                        constraint_type="prompt_constraint",
                        severity=ViolationSeverity.ERROR,
                        message=f"'{ex_data.get('name', '')}' violates constraint: {rule}",
                        location=location,
                        suggestion=f"Remove or replace this exercise per user's request ({constraint_type}: {rule})",
                    ))

    return violations


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def validate_program_constraints(
    program_data: dict,
    user_profile: UserProfile,
    extracted_constraints: list[dict] | None = None,
) -> ValidationResult:
    """Validate a generated program against user constraints.

    Args:
        program_data: The final program dict from the congregation mediator.
        user_profile: The user's fitness profile with equipment, schedule, etc.
        extracted_constraints: Structured constraints extracted from the goals
            prompt (from the constraint_extraction DAG node).

    Returns:
        ValidationResult with any violations found.
    """
    lookup = build_exercise_lookup()
    all_violations: list[ConstraintViolation] = []

    all_violations.extend(
        _check_equipment(program_data, user_profile.available_equipment, lookup)
    )
    all_violations.extend(
        _check_schedule(program_data, user_profile.schedule_days)
    )
    all_violations.extend(
        _check_limitations(program_data, user_profile.limitations, lookup)
    )
    all_violations.extend(
        _check_session_duration(program_data, user_profile.session_duration, lookup)
    )
    all_violations.extend(
        _check_prompt_constraints(program_data, extracted_constraints or [])
    )

    return ValidationResult(violations=all_violations)
