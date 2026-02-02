"""Program revision service for partial regeneration."""

import json

from ..agents.congregation import run_congregation
from ..generators.liftoscript import LiftoscriptGenerator
from ..models.program import (
    Program,
    ProgramDay,
    ProgramExercise,
    ProgramWeek,
    ProgressionScheme,
    SetScheme,
)
from ..models.user_profile import UserProfile


class RevisionService:
    """Service for revising programs from a specific position.

    Keeps completed work unchanged and regenerates remaining weeks
    using the congregation of specialist agents.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.generator = LiftoscriptGenerator()

    async def revise_from_position(
        self,
        program: Program,
        from_week: int,
        from_day: int,
        user_profile: UserProfile,
        reason: str = "",
        available_exercises: list[str] | None = None,
    ) -> Program:
        """Revise a program from a specific position forward.

        Keeps completed weeks/days unchanged and regenerates the rest
        based on the user's feedback and current state.

        Args:
            program: The program to revise
            from_week: Week to start revision from (1-indexed)
            from_day: Day to start revision from (1-indexed)
            user_profile: User profile for context
            reason: User's reason for revision
            available_exercises: Optional filtered list of exercises

        Returns:
            Revised program with updated weeks and Liftoscript
        """
        total_weeks = len(program.weeks)

        if from_week < 1 or from_week > total_weeks:
            raise ValueError(f"Invalid week {from_week}. Program has {total_weeks} weeks.")

        # Split program into completed and to-revise
        completed_weeks = []
        for i in range(from_week - 1):
            completed_weeks.append(program.weeks[i])

        # If revising mid-week, keep completed days from that week
        completed_days_in_week = []
        if from_week <= len(program.weeks):
            current_week = program.weeks[from_week - 1]
            for j in range(from_day - 1):
                if j < len(current_week.days):
                    completed_days_in_week.append(current_week.days[j])

        # Summarize completed work for AI context
        completed_summary = self._summarize_completed_work(
            completed_weeks, completed_days_in_week
        )

        # Build user summary
        user_summary = user_profile.get_summary()

        # Build revision context
        remaining_weeks = total_weeks - from_week + 1
        weeks_to_generate = remaining_weeks

        # Get existing program framework info
        framework = self._extract_framework(program)

        # Add revision context
        revision_context = f"""
REVISION REQUEST:
Starting from Week {from_week}, Day {from_day}

Completed work summary:
{completed_summary}

User's revision reason: {reason or "User requested revision from this point"}

Generate the remaining {weeks_to_generate} weeks of the program.
Keep the same overall structure and split type, but incorporate
the revision feedback into the remaining weeks.
"""

        if available_exercises:
            revision_context += f"\nAvailable exercises: {', '.join(available_exercises[:50])}"

        # Run congregation for remaining weeks
        result = await run_congregation(
            user_summary=user_summary + revision_context,
            program_framework=framework,
            verbose=self.verbose,
        )

        # Parse new weeks from congregation result
        new_weeks = self._parse_weeks_from_result(
            result.final_program,
            start_week=from_week,
            total_weeks=total_weeks,
        )

        # Merge completed and new content
        final_weeks = list(completed_weeks)

        # Handle partial week if applicable
        if completed_days_in_week and new_weeks:
            # Merge partial week
            first_new_week = new_weeks[0]
            merged_days = list(completed_days_in_week) + first_new_week.days
            merged_week = ProgramWeek(
                week_number=from_week,
                days=merged_days,
                deload=first_new_week.deload,
            )
            final_weeks.append(merged_week)
            new_weeks = new_weeks[1:]

        # Add remaining new weeks
        final_weeks.extend(new_weeks)

        # Update program
        program.weeks = final_weeks

        # Regenerate Liftoscript
        program.liftoscript = self.generator.generate(program)

        # Log the revision
        program.congregation_log.append({
            "phase": "revision",
            "from_week": from_week,
            "from_day": from_day,
            "reason": reason,
            "converged": result.converged,
        })

        return program

    def _summarize_completed_work(
        self,
        completed_weeks: list[ProgramWeek],
        completed_days: list[ProgramDay],
    ) -> str:
        """Summarize completed work for AI context."""
        lines = []

        if completed_weeks:
            lines.append(f"Completed {len(completed_weeks)} full weeks:")
            for week in completed_weeks:
                deload = " (deload)" if week.deload else ""
                days_summary = ", ".join(d.name for d in week.days)
                lines.append(f"  Week {week.week_number}{deload}: {days_summary}")

        if completed_days:
            lines.append(f"Partial week completed days:")
            for day in completed_days:
                exercises = ", ".join(ex.name for ex in day.exercises[:3])
                if len(day.exercises) > 3:
                    exercises += f", +{len(day.exercises) - 3} more"
                lines.append(f"  {day.name}: {exercises}")

        if not lines:
            return "No completed work (starting fresh)"

        return "\n".join(lines)

    def _extract_framework(self, program: Program) -> dict:
        """Extract program framework information."""
        # Analyze existing program structure
        days_per_week = len(program.weeks[0].days) if program.weeks else 4
        day_focuses = []

        if program.weeks:
            for day in program.weeks[0].days:
                if day.focus:
                    day_focuses.append(day.focus)
                else:
                    day_focuses.append(day.name)

        # Determine split type from day names
        split_type = "custom"
        if program.weeks and program.weeks[0].days:
            day_names = [d.name.lower() for d in program.weeks[0].days]
            if any("upper" in n for n in day_names) and any("lower" in n for n in day_names):
                split_type = "upper_lower"
            elif any("push" in n for n in day_names) and any("pull" in n for n in day_names):
                split_type = "push_pull_legs"
            elif any("full" in n for n in day_names):
                split_type = "full_body"

        return {
            "split_type": split_type,
            "days_per_week": days_per_week,
            "day_focuses": day_focuses,
            "periodization": "linear with deload",
            "progression_philosophy": "progressive overload",
        }

    def _parse_weeks_from_result(
        self,
        result: dict,
        start_week: int,
        total_weeks: int,
    ) -> list[ProgramWeek]:
        """Parse weeks from congregation result."""
        weeks = []
        weeks_data = result.get("weeks", [])

        for i, week_data in enumerate(weeks_data):
            week_number = start_week + i
            if week_number > total_weeks:
                break

            days = []
            for day_data in week_data.get("days", []):
                exercises = []
                for ex_data in day_data.get("exercises", []):
                    sets = self._parse_sets(ex_data.get("sets", "3x10"))
                    progression = self._parse_progression(
                        ex_data.get("progression", "dp")
                    )

                    exercises.append(ProgramExercise(
                        name=ex_data.get("name", "Unknown"),
                        sets=sets,
                        progression=progression,
                        notes=ex_data.get("notes", ""),
                    ))

                days.append(ProgramDay(
                    name=day_data.get("name", f"Day {len(days) + 1}"),
                    focus=day_data.get("focus", ""),
                    exercises=exercises,
                ))

            weeks.append(ProgramWeek(
                week_number=week_number,
                days=days,
                deload=week_data.get("is_deload", False),
            ))

        return weeks

    def _parse_sets(self, sets_str: str) -> list[SetScheme]:
        """Parse sets string into SetScheme objects."""
        import re

        sets = []
        match = re.match(r"(\d+)x(\d+)(?:-(\d+))?(\+)?", str(sets_str))

        if match:
            num_sets = int(match.group(1))
            reps_min = int(match.group(2))
            reps_max = int(match.group(3)) if match.group(3) else reps_min
            is_amrap = bool(match.group(4))

            for i in range(num_sets):
                is_last = i == num_sets - 1
                reps = reps_min if reps_min == reps_max else f"{reps_min}-{reps_max}"
                sets.append(SetScheme(
                    reps=reps,
                    is_amrap=is_last and is_amrap,
                ))
        else:
            for _ in range(3):
                sets.append(SetScheme(reps=10))

        return sets

    def _parse_progression(self, prog_str: str) -> ProgressionScheme:
        """Parse progression string to ProgressionScheme."""
        prog_map = {
            "lp": ProgressionScheme.LINEAR,
            "linear": ProgressionScheme.LINEAR,
            "dp": ProgressionScheme.DOUBLE,
            "double": ProgressionScheme.DOUBLE,
            "sum": ProgressionScheme.SUM,
            "custom": ProgressionScheme.CUSTOM,
        }
        return prog_map.get(prog_str.lower(), ProgressionScheme.DOUBLE)
