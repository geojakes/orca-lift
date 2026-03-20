"""Liftoscript format implementation for Liftosaur compatibility."""

from ..generators.liftoscript import GeneratorConfig, LiftoscriptGenerator
from ..models.program import (
    Program,
    ProgramDay,
    ProgramExercise,
    ProgramWeek,
    ProgressionScheme,
    SetScheme,
)
from .base import ValidationResult


class LiftoscriptFormat:
    """Liftoscript workout format for Liftosaur app.
    
    Generates the Liftoscript DSL used by Liftosaur for defining workout programs.
    """
    
    def __init__(self, config: GeneratorConfig | None = None):
        self._generator = LiftoscriptGenerator(config)
    
    @property
    def name(self) -> str:
        return "liftoscript"
    
    @property
    def file_extension(self) -> str:
        return ".txt"
    
    def generate(self, program: Program) -> str:
        """Convert Program to Liftoscript DSL string."""
        return self._generator.generate(program)
    
    def validate(self, output: str | dict) -> ValidationResult:
        """Validate Liftoscript syntax."""
        if isinstance(output, dict):
            return ValidationResult(
                is_valid=False,
                errors=["Liftoscript format expects a string, not a dict"]
            )
        is_valid, errors = self._generator.validate(output)
        return ValidationResult(is_valid=is_valid, errors=errors)
    
    def parse(self, raw: str | dict) -> Program:
        """Parse Liftoscript back into a Program model.
        
        This is a best-effort parser for the Liftoscript DSL.
        """
        if isinstance(raw, dict):
            raise ValueError("Liftoscript format expects a string input")
        
        import re
        
        lines = raw.strip().split("\n")
        weeks: list[ProgramWeek] = []
        current_week_num = 1
        current_days: list[ProgramDay] = []
        current_exercises: list[ProgramExercise] = []
        current_day_name = ""
        current_day_focus = ""
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            
            # Week header
            if re.match(r"^#\s+", line) and not line.startswith("## "):
                # Save previous week
                if current_days or current_exercises:
                    if current_exercises:
                        current_days.append(ProgramDay(
                            name=current_day_name,
                            exercises=current_exercises,
                            focus=current_day_focus,
                        ))
                        current_exercises = []
                    if current_days:
                        weeks.append(ProgramWeek(
                            week_number=current_week_num,
                            days=current_days,
                            deload="deload" in line.lower(),
                        ))
                        current_days = []
                
                # Parse week number
                match = re.search(r"Week\s+(\d+)", line)
                current_week_num = int(match.group(1)) if match else len(weeks) + 1
                continue
            
            # Day header
            if line.startswith("## "):
                if current_exercises:
                    current_days.append(ProgramDay(
                        name=current_day_name,
                        exercises=current_exercises,
                        focus=current_day_focus,
                    ))
                    current_exercises = []
                
                header = line[3:].strip()
                if " - " in header:
                    current_day_name, current_day_focus = header.split(" - ", 1)
                else:
                    current_day_name = header
                    current_day_focus = ""
                continue
            
            # Exercise line
            if "/" in line:
                parts = [p.strip() for p in line.split("/")]
                if len(parts) >= 2:
                    name = parts[0]
                    # Remove label prefix
                    if ":" in name and not name.endswith(":"):
                        label_part, name = name.split(":", 1)
                        name = name.strip()
                    
                    sets = self._parse_sets(parts[1])
                    progression = ProgressionScheme.DOUBLE
                    progression_params = {}
                    
                    for part in parts[2:]:
                        part = part.strip()
                        if part.startswith("progress:"):
                            prog_str = part[9:].strip()
                            progression, progression_params = self._parse_progression(prog_str)
                    
                    current_exercises.append(ProgramExercise(
                        name=name,
                        sets=sets,
                        progression=progression,
                        progression_params=progression_params,
                    ))
        
        # Save final day/week
        if current_exercises:
            current_days.append(ProgramDay(
                name=current_day_name,
                exercises=current_exercises,
                focus=current_day_focus,
            ))
        if current_days:
            weeks.append(ProgramWeek(
                week_number=current_week_num,
                days=current_days,
            ))
        
        return Program(
            name="Imported Program",
            description="Imported from Liftoscript",
            weeks=weeks,
            goals="",
            liftoscript=raw,
        )
    
    def _parse_sets(self, sets_str: str) -> list[SetScheme]:
        """Parse a sets string like '4x5' or '3x8-10' into SetScheme list."""
        import re
        sets_str = sets_str.strip()
        
        # Handle comma-separated sets
        if "," in sets_str:
            result = []
            for part in sets_str.split(","):
                result.extend(self._parse_sets(part.strip()))
            return result
        
        match = re.match(r"(\d+)x(\d+)(?:-(\d+))?(\+)?", sets_str)
        if not match:
            return [SetScheme(reps=10)]
        
        num_sets = int(match.group(1))
        reps_low = int(match.group(2))
        reps_high = match.group(3)
        is_amrap = match.group(4) == "+"
        
        if reps_high:
            reps: int | str = f"{reps_low}-{reps_high}"
        else:
            reps = reps_low
        
        return [
            SetScheme(reps=reps, is_amrap=is_amrap)
            for _ in range(num_sets)
        ]
    
    def _parse_progression(self, prog_str: str) -> tuple[ProgressionScheme, dict]:
        """Parse a progression string like 'lp(5lb)' into scheme and params."""
        import re
        
        match = re.match(r"(lp|dp|sum|custom)\(([^)]*)\)", prog_str)
        if not match:
            return ProgressionScheme.DOUBLE, {}
        
        func = match.group(1)
        args_str = match.group(2)
        
        # Parse increment from first arg
        inc_match = re.match(r"([\d.]+)", args_str)
        increment = float(inc_match.group(1)) if inc_match else 5.0
        
        scheme_map = {
            "lp": ProgressionScheme.LINEAR,
            "dp": ProgressionScheme.DOUBLE,
            "sum": ProgressionScheme.SUM,
            "custom": ProgressionScheme.CUSTOM,
        }
        
        return scheme_map.get(func, ProgressionScheme.DOUBLE), {"increment": increment}
