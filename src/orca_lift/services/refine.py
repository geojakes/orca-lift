"""Conversation-based program refinement service."""

import json
import re

from orca import PlanExecutor, PermissionMode

from ..generators.liftoscript import LiftoscriptGenerator
from ..models.program import (
    Program,
    ProgramDay,
    ProgramExercise,
    ProgramWeek,
    ProgressionScheme,
    SetScheme,
)
from ..agents.plan_builder import build_refinement_plan


class RefinementService:
    """Service for refining programs through conversation."""

    def __init__(self):
        self.generator = LiftoscriptGenerator()
        self.conversation_history: list[dict] = []

    async def refine(self, program: Program, request: str) -> Program:
        """Refine a program based on user request.

        Args:
            program: The current program
            request: The user's refinement request

        Returns:
            Updated program with changes applied
        """
        # Build and execute refinement plan
        plan = build_refinement_plan(
            program_structure=self._program_to_dict(program),
            refinement_request=request,
        )

        executor = PlanExecutor.from_plan(
            plan,
            verbose=False,
            permission_mode=PermissionMode.DEFAULT,
        )
        result = await executor.execute(plan)

        # Get the refinement response
        refined_data = result.get("refine_program", {})

        # Apply refinements
        if isinstance(refined_data, dict):
            refined_program = self._apply_refinement(program, refined_data, request)
        else:
            # Try to parse from string response
            refined_program = self._apply_refinement_from_text(program, str(refined_data), request)

        return refined_program

    def _program_to_dict(self, program: Program) -> dict:
        """Convert program to a simplified dict for the prompt."""
        simplified = {
            "name": program.name,
            "weeks": []
        }

        for week in program.weeks:
            week_data = {
                "week_number": week.week_number,
                "is_deload": week.deload,
                "days": []
            }

            for day in week.days:
                day_data = {
                    "name": day.name,
                    "focus": day.focus,
                    "exercises": []
                }

                for ex in day.exercises:
                    # Simplify sets representation
                    working_sets = [s for s in ex.sets if not s.is_warmup]
                    if working_sets:
                        first_set = working_sets[0]
                        sets_str = f"{len(working_sets)}x{first_set.reps}"
                    else:
                        sets_str = "3x10"

                    day_data["exercises"].append({
                        "name": ex.name,
                        "sets": sets_str,
                        "progression": ex.progression.value,
                    })

                week_data["days"].append(day_data)

            simplified["weeks"].append(week_data)

        return simplified

    def _apply_refinement(
        self, program: Program, ai_response: dict, request: str
    ) -> Program:
        """Apply AI refinement response to the program."""
        # Try to extract JSON from response if it's nested
        refined_data = ai_response

        if "weeks" in refined_data:
            new_weeks = self._build_weeks_from_data(refined_data["weeks"])
            program.weeks = new_weeks

        # Update name if provided
        if "name" in refined_data:
            program.name = refined_data["name"]

        # Regenerate Liftoscript
        program.liftoscript = self.generator.generate(program)

        # Log the refinement
        program.congregation_log.append({
            "phase": "refinement",
            "request": request,
            "status": "success",
        })

        return program

    def _apply_refinement_from_text(
        self, program: Program, text: str, request: str
    ) -> Program:
        """Try to parse refinement from free-form text response."""
        # Try to extract JSON from the response
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r"\{[\s\S]*\"weeks\"[\s\S]*\}", text)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Can't parse, return original with log
                program.congregation_log.append({
                    "phase": "refinement",
                    "request": request,
                    "response": text[:500],
                    "status": "parse_error",
                })
                return program

        try:
            refined_data = json.loads(json_str)
            return self._apply_refinement(program, refined_data, request)
        except json.JSONDecodeError:
            program.congregation_log.append({
                "phase": "refinement",
                "request": request,
                "status": "json_error",
            })
            return program

    def _build_weeks_from_data(self, weeks_data: list) -> list[ProgramWeek]:
        """Build ProgramWeek objects from data."""
        new_weeks = []

        for week_data in weeks_data:
            new_days = []
            for day_data in week_data.get("days", []):
                new_exercises = []
                for ex_data in day_data.get("exercises", []):
                    # Parse sets string like "4x8" or "3x8-12"
                    sets_str = ex_data.get("sets", "3x10")
                    sets = self._parse_sets_string(sets_str)

                    # Get progression
                    prog_str = ex_data.get("progression", "dp")
                    try:
                        progression = ProgressionScheme(prog_str)
                    except ValueError:
                        progression = ProgressionScheme.DOUBLE

                    new_exercises.append(
                        ProgramExercise(
                            name=ex_data.get("name", "Unknown"),
                            sets=sets,
                            progression=progression,
                            notes=ex_data.get("notes", ""),
                        )
                    )

                new_days.append(
                    ProgramDay(
                        name=day_data.get("name", ""),
                        focus=day_data.get("focus", ""),
                        exercises=new_exercises,
                    )
                )

            new_weeks.append(
                ProgramWeek(
                    week_number=week_data.get("week_number", len(new_weeks) + 1),
                    days=new_days,
                    deload=week_data.get("is_deload", False),
                )
            )

        return new_weeks

    def _parse_sets_string(self, sets_str: str) -> list[SetScheme]:
        """Parse a sets string like '4x8' or '3x8-12' into SetScheme list."""
        sets = []

        # Handle formats: 4x8, 3x8-12, 5x5+
        match = re.match(r"(\d+)x(\d+)(?:-(\d+))?(\+)?", str(sets_str))
        if match:
            num_sets = int(match.group(1))
            reps_min = int(match.group(2))
            reps_max = int(match.group(3)) if match.group(3) else reps_min
            is_amrap = bool(match.group(4))

            for i in range(num_sets):
                is_last = i == num_sets - 1
                reps = reps_min if reps_min == reps_max else f"{reps_min}-{reps_max}"
                sets.append(
                    SetScheme(
                        reps=reps,
                        is_amrap=is_last and is_amrap,
                    )
                )
        else:
            # Default fallback
            for _ in range(3):
                sets.append(SetScheme(reps=10))

        return sets

    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
