"""Liftoscript DSL generator for Liftosaur programs.

Liftoscript is the domain-specific language used by Liftosaur for defining
workout programs. This module converts our Program models to valid Liftoscript
that can be imported into Liftosaur.

Liftoscript Format Reference:
- Programs consist of weeks and days
- Each day has exercises with sets, reps, and weight configurations
- Progression is defined using functions like lp(), dp(), sum()

Example:
```
# Week 1
## Day 1 - Push
Bench Press / 4x5 / 135lb / progress: lp(5lb)
Overhead Press / 3x8-10 / 85lb / progress: dp(2.5lb, 8, 10)
Tricep Pushdown / 3x12-15 / progress: dp(5lb, 12, 15)
```
"""

from dataclasses import dataclass, field
from typing import Callable

from ..models.equipment import EquipmentConfig
from ..models.program import Program, ProgramDay, ProgramExercise, ProgressionScheme


@dataclass
class GeneratorConfig:
    """Configuration for Liftoscript generation."""

    include_warmups: bool = False
    include_rest_times: bool = False
    weight_unit: str = "lb"  # "lb" or "kg"
    include_week_headers: bool = True
    include_comments: bool = False  # Liftosaur doesn't support // comments
    equipment_config: EquipmentConfig | None = None  # For weight rounding


class LiftoscriptGenerator:
    """Generates Liftoscript code from Program models."""

    def __init__(self, config: GeneratorConfig | None = None):
        self.config = config or GeneratorConfig()

    def generate(self, program: Program) -> str:
        """Generate complete Liftoscript for a program.

        Args:
            program: The program to convert

        Returns:
            Valid Liftoscript code string
        """
        lines: list[str] = []

        # Program header comment
        if self.config.include_comments:
            lines.append(f"// {program.name}")
            if program.description:
                lines.append(f"// {program.description}")
            lines.append("")

        # Generate each week
        for week in program.weeks:
            if self.config.include_week_headers:
                week_label = f"# Week {week.week_number}"
                if week.deload:
                    week_label += " (Deload)"
                lines.append(week_label)
                lines.append("")

            # Generate each day
            for i, day in enumerate(week.days, 1):
                lines.extend(self._generate_day(day, i))
                lines.append("")

        return "\n".join(lines).strip()

    def _generate_day(self, day: ProgramDay, day_num: int) -> list[str]:
        """Generate Liftoscript for a single day."""
        lines: list[str] = []

        # Day header
        day_header = f"## Day {day_num}"
        if day.name:
            day_header = f"## {day.name}"
        if day.focus:
            day_header += f" - {day.focus}"

        lines.append(day_header)

        # Day notes as comment
        if self.config.include_comments and day.notes:
            lines.append(f"// {day.notes}")

        # Generate exercises
        for exercise in day.exercises:
            exercise_line = self._generate_exercise(exercise)
            lines.append(exercise_line)

        return lines

    def _generate_exercise(self, exercise: ProgramExercise) -> str:
        """Generate Liftoscript line for an exercise.

        Format: Exercise Name / SetsxReps / Weight / progress: progression()
        """
        parts: list[str] = []

        # Exercise name
        parts.append(exercise.name)

        # Sets and reps
        sets_reps = self._format_sets_reps(exercise)
        parts.append(sets_reps)

        # Progression (if not custom)
        if exercise.progression != ProgressionScheme.CUSTOM:
            progression = self._format_progression(exercise)
            if progression:
                parts.append(f"progress: {progression}")

        # Notes as inline comment
        line = " / ".join(parts)

        if self.config.include_comments and exercise.notes:
            line += f"  // {exercise.notes}"

        return line

    def _format_sets_reps(self, exercise: ProgramExercise) -> str:
        """Format the sets x reps portion.

        Examples:
        - 4x5 (4 sets of 5)
        - 3x8-10 (3 sets of 8-10)
        - 5x5, 1x5+ (5 sets of 5, then 1 AMRAP set)
        - 3x10 @RPE8
        """
        working_sets = [s for s in exercise.sets if not s.is_warmup]

        if not working_sets:
            return "3x10"  # Default

        # Check if all sets are the same
        first_set = working_sets[0]
        all_same = all(
            s.reps == first_set.reps and s.is_amrap == first_set.is_amrap
            for s in working_sets
        )

        if all_same:
            reps = first_set.reps
            if isinstance(reps, int):
                rep_str = str(reps)
            else:
                rep_str = str(reps)  # Already formatted like "8-10"

            if first_set.is_amrap:
                rep_str += "+"

            result = f"{len(working_sets)}x{rep_str}"

            # Add RPE if specified
            if first_set.rpe:
                result += f" @RPE{first_set.rpe}"

            return result
        else:
            # Different sets - format each
            set_strs = []
            for s in working_sets:
                reps = s.reps
                if isinstance(reps, int):
                    rep_str = str(reps)
                else:
                    rep_str = str(reps)

                if s.is_amrap:
                    rep_str += "+"

                set_strs.append(f"1x{rep_str}")

            return ", ".join(set_strs)

    def _format_progression(self, exercise: ProgramExercise) -> str:
        """Format the progression function.

        Liftosaur progression functions:
        - lp(increment) - Linear progression: add weight each session
        - dp(increment, minReps, maxReps) - Double progression: increase reps then weight
        - sum(increment, targetReps) - Sum progression: total reps across sets
        """
        params = exercise.progression_params
        increment = params.get("increment", 5)
        unit = self.config.weight_unit

        # Round increment to achievable value if equipment config available
        increment = self._round_increment(increment)

        if exercise.progression == ProgressionScheme.LINEAR:
            return f"lp({increment}{unit})"

        elif exercise.progression == ProgressionScheme.DOUBLE:
            # Extract rep range from sets
            working_sets = [s for s in exercise.sets if not s.is_warmup]
            if working_sets:
                first_reps = working_sets[0].reps
                if isinstance(first_reps, str) and "-" in first_reps:
                    min_reps, max_reps = first_reps.split("-")
                    return f"dp({increment}{unit}, {min_reps}, {max_reps})"
                else:
                    # Default rep range
                    return f"dp({increment}{unit}, {first_reps}, {int(first_reps) + 2})"
            return f"dp({increment}{unit}, 8, 12)"

        elif exercise.progression == ProgressionScheme.SUM:
            target_reps = params.get("target_reps", 25)
            return f"sum({increment}{unit}, {target_reps})"

        return ""

    def _round_increment(self, increment: float) -> float:
        """Round increment to achievable value based on plate inventory.

        If equipment config is available, rounds to the minimum achievable
        increment. Otherwise, returns the original value.
        """
        # Ensure increment is numeric
        if not isinstance(increment, (int, float)):
            try:
                increment = float(increment)
            except (ValueError, TypeError):
                increment = 5.0

        if not self.config.equipment_config:
            return increment

        min_inc = self.config.equipment_config.min_increment()

        # Round to nearest achievable increment
        # e.g., if min_inc is 5lb, round 7.5 to either 5 or 10
        if increment < min_inc:
            return min_inc

        # Round to nearest multiple of min_inc
        return round(increment / min_inc) * min_inc

    def round_weight(self, target: float) -> float:
        """Round a target weight to an achievable weight.

        Uses equipment config plate inventory if available.
        Otherwise rounds to standard increments.

        Args:
            target: Target weight

        Returns:
            Achievable weight based on plate inventory
        """
        if self.config.equipment_config:
            return self.config.equipment_config.round_weight(target)

        # Default rounding to 5lb or 2.5kg
        increment = 5.0 if self.config.weight_unit == "lb" else 2.5
        return round(target / increment) * increment

    def generate_single_day(self, day: ProgramDay) -> str:
        """Generate Liftoscript for a single day (for refinement preview)."""
        lines = self._generate_day(day, 1)
        return "\n".join(lines)

    def validate(self, liftoscript: str) -> tuple[bool, list[str]]:
        """Validate Liftoscript syntax including advanced features.

        Handles: labels, repeat syntax [1-N], reuse (...Name), templates
        (/ used: none), line continuations (\\), and custom() progress scripts.

        Args:
            liftoscript: The Liftoscript code to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        import re

        errors: list[str] = []
        raw_lines = liftoscript.strip().split("\n")

        # Join line continuations (backslash at end of line)
        lines: list[str] = []
        buffer = ""
        for raw in raw_lines:
            stripped = raw.rstrip()
            if stripped.endswith("\\"):
                buffer += stripped[:-1] + " "
            else:
                buffer += stripped
                lines.append(buffer)
                buffer = ""
        if buffer:
            lines.append(buffer)

        in_script_block = False

        for i, line in enumerate(lines, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("//"):
                continue

            # Track multi-line script blocks (progress: custom() ... ~)
            if in_script_block:
                if line == "~":
                    in_script_block = False
                continue

            # Week headers — may include repeat syntax like # Week 1[1-4]
            if re.match(r"^#\s+", line) and not line.startswith("## "):
                continue

            # Day headers — may include repeat syntax like ## Day 1[1-4]
            if line.startswith("## "):
                continue

            # Reuse syntax: ...ExerciseName or ...TemplateName
            if line.startswith("..."):
                continue

            # Exercise / template lines must contain /
            if "/" in line:
                parts = [p.strip() for p in line.split("/")]

                if len(parts) < 2:
                    errors.append(f"Line {i}: Exercise needs at least name and sets")
                    continue

                # Exercise name — may have label prefix (e.g. "heavy: Bench Press")
                # and/or repeat suffix (e.g. "Bench Press[1-4]")
                name = parts[0]
                # Strip label prefix
                if ":" in name:
                    name = name.split(":", 1)[1].strip()
                # Strip repeat suffix like [1-4] or [1,3-5,8]
                name = re.sub(r"\[[\d,\-]+\]$", "", name).strip()

                if not name or name.startswith("//"):
                    errors.append(f"Line {i}: Missing exercise name")

                # Second part could be sets OR "used: none" (template marker)
                second = parts[1]
                if second.strip() == "used: none":
                    # Template definition — remaining parts are valid
                    pass
                else:
                    # Validate sets format
                    if not self._validate_sets_format(second):
                        errors.append(f"Line {i}: Invalid sets format: {second}")

                # Check remaining parts for progress/update/weight
                for part in parts[2:]:
                    part = part.strip()
                    if part.startswith("progress:"):
                        prog = part[9:].strip()
                        if prog.startswith("custom("):
                            # custom() opens a multi-line script block
                            in_script_block = True
                        elif not self._validate_progression_format(prog):
                            errors.append(f"Line {i}: Invalid progression: {prog}")
                    elif part.startswith("update:"):
                        update = part[7:].strip()
                        if update.startswith("custom("):
                            in_script_block = True
                    # Weight, timer, warmup, etc. are free-form — skip

            else:
                if line and not line.startswith("#"):
                    errors.append(f"Line {i}: Invalid line format (missing /)")

        return len(errors) == 0, errors

    def _validate_sets_format(self, sets_str: str) -> bool:
        """Validate sets x reps format including advanced notations."""
        import re

        sets_str = sets_str.strip()

        # Remove RPE annotation
        sets_str = re.sub(r"@RPE\d+\.?\d*", "", sets_str).strip()

        # Remove weight suffix like "/ 135lb" that may be merged
        # Handle comma-separated sets (e.g. "5x5, 1x5+")
        if "," in sets_str:
            parts = [p.strip() for p in sets_str.split(",")]
            return all(self._validate_single_set(p) for p in parts)

        return self._validate_single_set(sets_str)

    def _validate_single_set(self, set_str: str) -> bool:
        """Validate a single set notation.

        Supports: 4x5, 3x8-10, 1x5+, 3x60s, 3x8+, expressions like 3x(state.reps)
        """
        import re

        set_str = set_str.strip()
        if not set_str:
            return False

        # Standard: NxM, NxM-P, NxM+, NxMs (time-based)
        if re.match(r"^\d+x\d+(-\d+)?(\+)?(s)?$", set_str):
            return True

        # Expression-based reps like Nx(state.reps) or Nx(state.weight)
        if re.match(r"^\d+x\(.+\)(\+)?$", set_str):
            return True

        # Weight included like "4x5 135lb" or "3x8 80%"
        if re.match(r"^\d+x\d+(-\d+)?(\+)?\s+[\d.]+(%|lb|kg)$", set_str):
            return True

        return False

    def _validate_progression_format(self, prog_str: str) -> bool:
        """Validate progression function format."""
        import re

        prog_str = prog_str.strip()

        # Built-in functions: lp, dp, sum, custom
        if re.match(r"^(lp|dp|sum|custom)\([^)]*\)$", prog_str):
            return True

        return False


def generate_liftoscript(program: Program, config: GeneratorConfig | None = None) -> str:
    """Convenience function to generate Liftoscript from a program."""
    generator = LiftoscriptGenerator(config)
    return generator.generate(program)
