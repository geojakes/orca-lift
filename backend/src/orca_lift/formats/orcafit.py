"""OrcaFit JSON format — our native structured workout format."""

import json
import uuid
from datetime import datetime, timezone

from ..models.program import (
    Program,
    ProgramDay,
    ProgramExercise,
    ProgramWeek,
    ProgressionScheme,
    SetScheme,
)
from .base import ValidationResult


# OrcaFit progression types (superset of Liftosaur's)
VALID_PROGRESSION_TYPES = {
    "linear",        # Add weight each session (was "lp")
    "double",        # Increase reps then weight (was "dp")
    "undulating",    # Daily undulating periodization
    "rpe_based",     # Auto-regulate based on RPE
    "percentage",    # Percentage-based progression
    "custom",        # Custom logic
}

# OrcaFit set types
VALID_SET_TYPES = {"warmup", "working", "amrap", "drop", "backoff", "timed"}

# Map from our ProgressionScheme enum to OrcaFit type strings
_PROGRESSION_TO_ORCAFIT = {
    ProgressionScheme.LINEAR: "linear",
    ProgressionScheme.DOUBLE: "double",
    ProgressionScheme.SUM: "linear",  # Sum maps closest to linear
    ProgressionScheme.CUSTOM: "custom",
}

_ORCAFIT_TO_PROGRESSION = {
    "linear": ProgressionScheme.LINEAR,
    "double": ProgressionScheme.DOUBLE,
    "undulating": ProgressionScheme.CUSTOM,
    "rpe_based": ProgressionScheme.CUSTOM,
    "percentage": ProgressionScheme.LINEAR,
    "custom": ProgressionScheme.CUSTOM,
}


def _slugify(name: str) -> str:
    """Convert exercise name to slug ID."""
    import re
    slug = name.lower().strip()
    slug = re.sub(r"[,/]", "", slug)
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


class OrcaFitFormat:
    """OrcaFit JSON workout format — our native structured format.
    
    Supports both resistance and cardio exercises with full tracking metadata.
    """
    
    @property
    def name(self) -> str:
        return "orcafit"
    
    @property
    def file_extension(self) -> str:
        return ".json"
    
    def generate(self, program: Program) -> dict:
        """Convert Program model to OrcaFit JSON structure."""
        return {
            "format": "orcafit",
            "version": "1.0",
            "program": {
                "id": str(uuid.uuid4()),
                "name": program.name,
                "description": program.description,
                "goals": program.goals,
                "created_at": (
                    program.created_at.isoformat()
                    if program.created_at
                    else datetime.now(timezone.utc).isoformat()
                ),
                "duration_weeks": program.total_weeks,
                "days_per_week": program.days_per_week,
                "weeks": [
                    self._generate_week(week) for week in program.weeks
                ],
            },
        }
    
    def _generate_week(self, week: ProgramWeek) -> dict:
        return {
            "week_number": week.week_number,
            "is_deload": week.deload,
            "notes": week.notes,
            "days": [
                self._generate_day(day, i + 1)
                for i, day in enumerate(week.days)
            ],
        }
    
    def _generate_day(self, day: ProgramDay, day_number: int) -> dict:
        return {
            "day_number": day_number,
            "name": day.name,
            "focus": day.focus,
            "notes": day.notes,
            "exercises": [
                self._generate_exercise(ex, i + 1)
                for i, ex in enumerate(day.exercises)
            ],
        }
    
    def _generate_exercise(self, exercise: ProgramExercise, order: int) -> dict:
        progression_type = _PROGRESSION_TO_ORCAFIT.get(
            exercise.progression, "double"
        )
        
        return {
            "exercise_id": _slugify(exercise.name),
            "exercise_name": exercise.name,
            "order": order,
            "sets": [
                self._generate_set(s, i + 1)
                for i, s in enumerate(exercise.sets)
            ],
            "progression": {
                "type": progression_type,
                "params": exercise.progression_params,
            },
            "superset_group": exercise.superset_with,
            "notes": exercise.notes,
        }
    
    def _generate_set(self, set_scheme: SetScheme, set_number: int) -> dict:
        set_type = "warmup" if set_scheme.is_warmup else ("amrap" if set_scheme.is_amrap else "working")
        
        reps = set_scheme.reps
        target_reps = None
        target_reps_max = None
        
        if isinstance(reps, str):
            if "-" in reps:
                parts = reps.split("-")
                target_reps = int(parts[0])
                target_reps_max = int(parts[1])
            elif reps.endswith("+"):
                target_reps = int(reps[:-1])
                set_type = "amrap"
            else:
                try:
                    target_reps = int(reps)
                except ValueError:
                    target_reps = 10
        else:
            target_reps = reps
        
        result = {
            "set_number": set_number,
            "type": set_type,
            "target_reps": target_reps,
        }
        
        if target_reps_max is not None:
            result["target_reps_max"] = target_reps_max
        
        if set_scheme.weight_percent is not None:
            result["target_weight_percent"] = set_scheme.weight_percent
        
        if set_scheme.rpe is not None:
            result["target_rpe"] = set_scheme.rpe
        
        if set_scheme.rest_seconds is not None:
            result["rest_seconds"] = set_scheme.rest_seconds
        
        return result
    
    def validate(self, output: str | dict) -> ValidationResult:
        """Validate OrcaFit JSON structure."""
        errors = []
        warnings = []
        
        if isinstance(output, str):
            try:
                output = json.loads(output)
            except json.JSONDecodeError as e:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Invalid JSON: {e}"]
                )
        
        if not isinstance(output, dict):
            return ValidationResult(
                is_valid=False,
                errors=["Output must be a JSON object"]
            )
        
        # Check top-level structure
        if output.get("format") != "orcafit":
            errors.append("Missing or invalid 'format' field (expected 'orcafit')")
        
        if "version" not in output:
            warnings.append("Missing 'version' field")
        
        program = output.get("program", {})
        if not program:
            errors.append("Missing 'program' object")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Required program fields
        for field in ["name", "weeks"]:
            if field not in program:
                errors.append(f"Missing required program field: '{field}'")
        
        # Validate weeks structure
        weeks = program.get("weeks", [])
        if not isinstance(weeks, list):
            errors.append("'weeks' must be an array")
        else:
            for wi, week in enumerate(weeks):
                days = week.get("days", [])
                if not isinstance(days, list) or not days:
                    errors.append(f"Week {wi + 1}: must have at least one day")
                    continue
                
                for di, day in enumerate(days):
                    exercises = day.get("exercises", [])
                    if not isinstance(exercises, list):
                        errors.append(
                            f"Week {wi + 1}, Day {di + 1}: 'exercises' must be an array"
                        )
                        continue
                    
                    for ei, ex in enumerate(exercises):
                        if "exercise_id" not in ex and "exercise_name" not in ex:
                            errors.append(
                                f"Week {wi+1}, Day {di+1}, Exercise {ei+1}: "
                                "needs 'exercise_id' or 'exercise_name'"
                            )
                        
                        sets = ex.get("sets", [])
                        if not sets:
                            warnings.append(
                                f"Week {wi+1}, Day {di+1}, Exercise {ei+1}: no sets defined"
                            )
                        
                        # Validate progression type
                        progression = ex.get("progression", {})
                        prog_type = progression.get("type", "")
                        if prog_type and prog_type not in VALID_PROGRESSION_TYPES:
                            errors.append(
                                f"Week {wi+1}, Day {di+1}, Exercise {ei+1}: "
                                f"invalid progression type '{prog_type}'"
                            )
                        
                        # Validate set types
                        for si, s in enumerate(sets):
                            st = s.get("type", "working")
                            if st not in VALID_SET_TYPES:
                                errors.append(
                                    f"Week {wi+1}, Day {di+1}, Ex {ei+1}, "
                                    f"Set {si+1}: invalid type '{st}'"
                                )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    def parse(self, raw: str | dict) -> Program:
        """Parse OrcaFit JSON back into a Program model."""
        if isinstance(raw, str):
            raw = json.loads(raw)
        
        program_data = raw.get("program", raw)
        
        weeks = []
        for week_data in program_data.get("weeks", []):
            days = []
            for day_data in week_data.get("days", []):
                exercises = []
                for ex_data in day_data.get("exercises", []):
                    sets = []
                    for s_data in ex_data.get("sets", []):
                        reps: int | str = s_data.get("target_reps", 10)
                        reps_max = s_data.get("target_reps_max")
                        if reps_max:
                            reps = f"{reps}-{reps_max}"
                        
                        sets.append(SetScheme(
                            reps=reps,
                            weight_percent=s_data.get("target_weight_percent"),
                            rpe=s_data.get("target_rpe"),
                            is_amrap=s_data.get("type") == "amrap",
                            is_warmup=s_data.get("type") == "warmup",
                            rest_seconds=s_data.get("rest_seconds"),
                        ))
                    
                    # Parse progression
                    prog_data = ex_data.get("progression", {})
                    prog_type = prog_data.get("type", "double")
                    progression = _ORCAFIT_TO_PROGRESSION.get(
                        prog_type, ProgressionScheme.DOUBLE
                    )
                    
                    exercises.append(ProgramExercise(
                        name=ex_data.get("exercise_name", ex_data.get("exercise_id", "")),
                        sets=sets,
                        progression=progression,
                        progression_params=prog_data.get("params", {}),
                        notes=ex_data.get("notes", ""),
                        superset_with=ex_data.get("superset_group"),
                    ))
                
                days.append(ProgramDay(
                    name=day_data.get("name", f"Day {day_data.get('day_number', 1)}"),
                    exercises=exercises,
                    focus=day_data.get("focus", ""),
                    notes=day_data.get("notes", ""),
                ))
            
            weeks.append(ProgramWeek(
                week_number=week_data.get("week_number", len(weeks) + 1),
                days=days,
                deload=week_data.get("is_deload", False),
                notes=week_data.get("notes", ""),
            ))
        
        return Program(
            name=program_data.get("name", "Imported Program"),
            description=program_data.get("description", ""),
            weeks=weeks,
            goals=program_data.get("goals", ""),
        )
    
    def to_json_string(self, program: Program, indent: int = 2) -> str:
        """Convenience: generate and serialize to JSON string."""
        data = self.generate(program)
        return json.dumps(data, indent=indent)
