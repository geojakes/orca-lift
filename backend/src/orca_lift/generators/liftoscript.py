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

        Also checks cross-exercise consistency: the same exercise name must
        have the same progress arguments everywhere it appears, unless
        differentiated by labels.

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
        # Track exercise progress for cross-exercise consistency
        # Key: exercise name (with label if present), Value: (progress_str, first_line, location)
        exercise_progress: dict[str, tuple[str, int, str]] = {}
        current_week = ""
        current_day = ""

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
                current_week = line
                continue

            # Day headers — may include repeat syntax like ## Day 1[1-4]
            if line.startswith("## "):
                current_day = line
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
                raw_name = parts[0]
                label = ""
                name = raw_name
                if ":" in name:
                    label, name = name.split(":", 1)
                    label = label.strip()
                    name = name.strip()
                # Strip repeat suffix like [1-4] or [1,3-5,8]
                name = re.sub(r"\[[\d,\-]+\]$", "", name).strip()

                if not name or name.startswith("//"):
                    errors.append(f"Line {i}: Missing exercise name")

                # Second part could be sets OR "used: none" (template marker)
                second = parts[1]
                is_template = second.strip() == "used: none"
                if not is_template:
                    # Validate sets format
                    if not self._validate_sets_format(second):
                        errors.append(f"Line {i}: Invalid sets format: {second}")

                # Check remaining parts for progress/update/weight
                progress_str = None
                for part in parts[2:]:
                    part = part.strip()
                    if part.startswith("progress:"):
                        prog = part[9:].strip()
                        progress_str = prog
                        if prog.startswith("custom("):
                            # Inline template reuse like custom() { ...progression }
                            # does NOT open a multi-line script block
                            if re.match(r"^custom\([^)]*\)\s*\{\s*\.\.\.\w+\s*\}$", prog):
                                pass  # Single-line, no script block
                            else:
                                # custom() opens a multi-line script block
                                in_script_block = True
                        elif not self._validate_progression_format(prog):
                            errors.append(f"Line {i}: Invalid progression: {prog}")
                    elif part.startswith("update:"):
                        update = part[7:].strip()
                        if update.startswith("custom("):
                            # Inline template reuse like custom() { ...dropsets }
                            if re.match(r"^custom\([^)]*\)\s*\{\s*\.\.\.\w+\s*\}$", update):
                                pass  # Single-line, no script block
                            else:
                                in_script_block = True
                    # Weight, timer, warmup, etc. are free-form — skip

                # Cross-exercise consistency check
                # The key includes the label so "heavy: Bench Press" and
                # "light: Bench Press" are tracked separately.
                # Skip "none" (deload weeks) — it doesn't conflict with other progressions
                if progress_str and progress_str != "none" and not is_template:
                    exercise_key = f"{label}: {name}" if label else name
                    location = f"{current_week}, {current_day}"
                    if exercise_key in exercise_progress:
                        prev_prog, prev_line, prev_loc = exercise_progress[exercise_key]
                        if prev_prog != progress_str:
                            errors.append(
                                f"Line {i}: Exercise '{name}' has progress '{progress_str}' "
                                f"but previously had '{prev_prog}' at line {prev_line} "
                                f"({prev_loc}). Use labels (e.g., 'phase1: {name}') to "
                                f"differentiate."
                            )
                    else:
                        exercise_progress[exercise_key] = (progress_str, i, location)

            else:
                if line and not line.startswith("#"):
                    errors.append(f"Line {i}: Invalid line format (missing /)")

        return len(errors) == 0, errors

    def fix_duplicate_progress(self, liftoscript: str) -> str:
        """Fix 'same progress with different arguments' errors by adding labels.

        When the same exercise appears with different progress arguments across
        weeks/days, Liftosaur rejects it. This method auto-adds labels like
        'v1:', 'v2:' to differentiate them.

        Args:
            liftoscript: The Liftoscript code that may have conflicts

        Returns:
            Fixed Liftoscript with labels added where needed
        """
        import re

        raw_lines = liftoscript.strip().split("\n")

        # First pass: find exercises with conflicting progress
        # Key: bare exercise name, Value: list of distinct progress strings
        exercise_variants: dict[str, list[str]] = {}
        for line in raw_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("..."):
                continue
            if "/" not in stripped:
                continue

            parts = [p.strip() for p in stripped.split("/")]
            if len(parts) < 2:
                continue

            raw_name = parts[0]
            name = raw_name
            # Skip if already labeled
            if ":" in name:
                continue
            name = re.sub(r"\[[\d,\-]+\]$", "", name).strip()

            # Find progress
            progress_str = None
            for part in parts[2:]:
                part = part.strip()
                if part.startswith("progress:"):
                    progress_str = part[9:].strip()
                    break

            if progress_str and name:
                if name not in exercise_variants:
                    exercise_variants[name] = []
                if progress_str not in exercise_variants[name]:
                    exercise_variants[name].append(progress_str)

        # Find which exercises have conflicts
        conflicting = {
            name: variants
            for name, variants in exercise_variants.items()
            if len(variants) > 1
        }

        if not conflicting:
            return liftoscript

        # Second pass: add labels to conflicting exercises
        result_lines = []
        for line in raw_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("..."):
                result_lines.append(line)
                continue
            if "/" not in stripped:
                result_lines.append(line)
                continue

            parts = [p.strip() for p in stripped.split("/")]
            if len(parts) < 2:
                result_lines.append(line)
                continue

            raw_name = parts[0]
            # Skip if already labeled
            if ":" in raw_name:
                result_lines.append(line)
                continue

            name = re.sub(r"\[[\d,\-]+\]$", "", raw_name).strip()

            if name not in conflicting:
                result_lines.append(line)
                continue

            # Find this line's progress
            progress_str = None
            for part in parts[2:]:
                part = part.strip()
                if part.startswith("progress:"):
                    progress_str = part[9:].strip()
                    break

            if not progress_str:
                result_lines.append(line)
                continue

            # Determine label based on variant index
            variant_idx = conflicting[name].index(progress_str)
            label = f"v{variant_idx + 1}"

            # Preserve leading whitespace
            leading_ws = line[: len(line) - len(line.lstrip())]
            new_line = f"{leading_ws}{label}: {stripped}"
            result_lines.append(new_line)

        return "\n".join(result_lines)

    def _validate_sets_format(self, sets_str: str) -> bool:
        """Validate sets x reps format including advanced notations."""
        import re

        sets_str = sets_str.strip()

        # Remove RPE annotation (both @RPE8 and bare @8 formats)
        sets_str = re.sub(r"@RPE\d+\.?\d*\+?", "", sets_str).strip()
        sets_str = re.sub(r"@\d+\.?\d*\+?", "", sets_str).strip()

        # Remove set labels in parentheses like (Full ROM), (Partial), (Dropset)
        sets_str = re.sub(r"\([^)]*\)", "", sets_str).strip()

        # Remove weight suffix like "/ 135lb" that may be merged
        # Handle comma-separated sets (e.g. "5x5, 1x5+")
        if "," in sets_str:
            parts = [p.strip() for p in sets_str.split(",")]
            return all(self._validate_single_set(p) for p in parts)

        return self._validate_single_set(sets_str)

    def _validate_single_set(self, set_str: str) -> bool:
        """Validate a single set notation.

        Supports: 4x5, 3x8-10, 1x5+, 3x60s, 3x8+, expressions like 3x(state.reps)
        Also handles set labels (Full ROM), (Partial), RPE @8, and rest times.
        """
        import re

        set_str = set_str.strip()
        if not set_str:
            return False

        # Strip set labels in parentheses like (Full ROM), (Partial)
        set_str = re.sub(r"\([^)]*\)", "", set_str).strip()

        # Strip RPE annotations (both @RPE8 and bare @8 formats)
        set_str = re.sub(r"@RPE\d+\.?\d*\+?", "", set_str).strip()
        set_str = re.sub(r"@\d+\.?\d*\+?", "", set_str).strip()

        # Strip rest time suffix like "60s" that may be attached
        set_str = re.sub(r"\s+\d+s$", "", set_str).strip()

        if not set_str:
            return False

        # Standard: NxM, NxM-P, NxM+, NxMs (time-based)
        if re.match(r"^\d+x\d+(-\d+)?(\+)?(s)?$", set_str):
            return True

        # Expression-based reps like Nx(state.reps) or Nx(state.weight)
        if re.match(r"^\d+x\(.+\)(\+)?$", set_str):
            return True

        # Weight included like "4x5 135lb" or "3x8 80%"
        if re.match(r"^\d+x\d+(-\d+)?(\+)?\s+[\d.]+(%|lb|kg)\+?$", set_str):
            return True

        return False

    def _validate_progression_format(self, prog_str: str) -> bool:
        """Validate progression function format."""
        import re

        prog_str = prog_str.strip()

        # "none" for deload weeks
        if prog_str == "none":
            return True

        # Built-in functions: lp, dp, sum, custom
        if re.match(r"^(lp|dp|sum|custom)\([^)]*\)$", prog_str):
            return True

        # Template reuse: custom() { ...templateName }
        if re.match(r"^custom\([^)]*\)\s*\{\s*\.\.\.\w+\s*\}$", prog_str):
            return True

        return False


def generate_liftoscript(program: Program, config: GeneratorConfig | None = None) -> str:
    """Convenience function to generate Liftoscript from a program."""
    generator = LiftoscriptGenerator(config)
    return generator.generate(program)
