"""Conversation-based program refinement service using congregation.

Mirrors the full generation pipeline: congregation → constraint validation →
AI Liftoscript conversion → duplicate progress fix → validation → fallback.
"""

import json
import re
from typing import Awaitable, Callable

from orca import CongregationEventType

from ..agents.congregation import (
    CongregationResult,
    run_congregation,
    run_congregation_stream,
)
from ..agents.liftoscript_converter import LiftoscriptConverter
from ..agents.liftoscript_spec import LIFTOSCRIPT_FULL_SPEC
from ..agents.prompts import format_constraint_checklist, format_equipment_constraints
from ..agents.tools import set_current_specialist, set_profile_context
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
from ..validators import validate_program_constraints

# Max number of AI correction attempts for constraint violations
MAX_CORRECTION_RETRIES = 2

# Type for progress callback: (event_type, message, data)
ProgressCallback = Callable[[str, str, dict | None], Awaitable[None]]


class RefinementService:
    """Service for refining programs through conversation using the congregation.

    Uses the same post-congregation sanitization pipeline as generation:
    1. Constraint validation with AI correction retries
    2. Robust program model construction (type coercion, cardio skip)
    3. AI-powered Liftoscript conversion (LiftoscriptConverter)
    4. Duplicate progress fix (auto-labeling)
    5. Syntax validation with Python fallback
    """

    def __init__(self):
        self.generator = LiftoscriptGenerator()
        self.converter = LiftoscriptConverter(
            liftoscript_spec=LIFTOSCRIPT_FULL_SPEC,
            verbose=False,
        )
        self.conversation_history: list[dict] = []

    async def refine(
        self,
        program: Program,
        request: str,
        user_profile: UserProfile | None = None,
        equipment_constraints: str | None = None,
        constraint_checklist: str = "",
        on_progress: ProgressCallback | None = None,
    ) -> Program:
        """Refine a program based on user request using the congregation.

        Args:
            program: The current program
            request: The user's refinement request
            user_profile: User profile for context
            equipment_constraints: Formatted equipment constraints string
            constraint_checklist: Formatted constraint checklist for the mediator
            on_progress: Optional callback for streaming progress events

        Returns:
            Updated program with changes applied
        """
        async def notify(event_type: str, message: str, data: dict | None = None):
            if on_progress:
                await on_progress(event_type, message, data)

        # Build the program framework from existing structure
        framework = self._extract_framework(program)

        # Build user context with refinement request
        program_summary = self._program_to_summary(program)
        conversation_context = self._build_conversation_context()

        user_summary = ""
        if user_profile:
            user_summary = user_profile.get_summary() + "\n\n"

        user_summary += f"""REFINEMENT REQUEST (this is a modification to an existing program, NOT a new program):

Current Program: {program.name}
{program_summary}

{conversation_context}

User's request: {request}

IMPORTANT: You are refining an EXISTING program. Only change what the user asked for.
Keep everything else the same. Return the COMPLETE updated program structure."""

        await notify("phase", "Consulting specialist coaches...")

        # Track conversation
        self.conversation_history.append({
            "role": "user",
            "content": request,
        })

        # Use streaming congregation if we have a progress callback
        if on_progress:
            congregation_result = await self._run_streaming_congregation(
                user_summary=user_summary,
                framework=framework,
                equipment_constraints=equipment_constraints,
                constraint_checklist=constraint_checklist,
                profile_id=user_profile.id if user_profile else None,
                notify=notify,
            )
        else:
            # Non-streaming fallback (CLI or no callback)
            congregation_result = await run_congregation(
                user_summary=user_summary,
                program_framework=framework,
                verbose=False,
                equipment_constraints=equipment_constraints,
                profile_id=user_profile.id if user_profile else None,
                constraint_checklist=constraint_checklist,
            )

        # Try to get structured program data
        final_program_data = congregation_result.final_program
        if not final_program_data or "weeks" not in final_program_data:
            # Try parsing from thesis as fallback
            if congregation_result.final_thesis:
                parsed = self._try_parse_from_thesis(congregation_result.final_thesis)
                if parsed and "weeks" in parsed:
                    final_program_data = parsed

        if not final_program_data or "weeks" not in final_program_data:
            program.congregation_log.append({
                "phase": "refinement",
                "request": request,
                "status": "no_output",
            })
            return program

        # === SANITIZATION PIPELINE (matches generation) ===

        # Step 1: Constraint validation with AI correction retries
        if user_profile:
            await notify("phase", "Validating program constraints...")
            final_program_data = await self._validate_and_correct(
                final_program_data, user_profile, notify
            )

        # Step 2: Build Program model with robust type coercion
        await notify("phase", "Building program structure...")
        new_weeks = self._build_weeks_from_congregation_data(
            final_program_data.get("weeks", [])
        )
        program.weeks = new_weeks

        # Update name if provided
        if "program_name" in final_program_data:
            program.name = final_program_data["program_name"]

        # Step 3: AI-powered Liftoscript conversion
        await notify("phase", "Converting to Liftoscript...")
        effective_weeks = len(program.weeks)
        try:
            conversion_result = await self.converter.convert(
                final_program=final_program_data,
                final_thesis=congregation_result.final_thesis or "",
                num_weeks=effective_weeks,
            )
            liftoscript = conversion_result.liftoscript
        except Exception:
            liftoscript = ""

        # Step 4: Fix duplicate progress conflicts (auto-add labels)
        if liftoscript.strip():
            liftoscript = self.generator.fix_duplicate_progress(liftoscript)

        # Step 5: Validate Liftoscript syntax
        if liftoscript.strip():
            is_valid, errors = self.generator.validate(liftoscript)
            # If validation found issues, they're logged but we still use
            # the AI-generated Liftoscript (it's usually better than fallback)

        # Step 6: Fallback to Python generator if AI returned empty
        if not liftoscript.strip():
            liftoscript = self.generator.generate(program)

        program.liftoscript = liftoscript

        # Log the refinement
        program.congregation_log.append({
            "phase": "refinement",
            "request": request,
            "converged": congregation_result.converged,
            "status": "success",
        })

        # Track AI response in conversation
        self.conversation_history.append({
            "role": "assistant",
            "content": f"Applied refinement: {request}",
        })

        return program

    async def _validate_and_correct(
        self,
        program_data: dict,
        user_profile: UserProfile,
        notify: Callable,
    ) -> dict:
        """Run constraint validation with AI correction retries.

        Same loop as executor.py: validate → correct → re-validate up to
        MAX_CORRECTION_RETRIES times.
        """
        for attempt in range(MAX_CORRECTION_RETRIES + 1):
            validation = validate_program_constraints(
                program_data, user_profile
            )

            if not validation.errors:
                break

            if attempt == MAX_CORRECTION_RETRIES:
                break

            await notify(
                "phase",
                f"Fixing {len(validation.errors)} constraint violation(s) "
                f"(attempt {attempt + 1})...",
            )

            program_data = await self._correct_violations(
                program_data, validation.errors, user_profile
            )

        return program_data

    async def _correct_violations(
        self,
        program_data: dict,
        violations: list,
        user_profile: UserProfile,
    ) -> dict:
        """Use AI to correct constraint violations in the program.

        Same approach as executor._correct_violations: sends program + violations
        to Sonnet with structured output and asks it to fix only the flagged issues.
        """
        violation_lines = []
        for v in violations:
            line = f"- [{v.constraint_type}] {v.message}"
            if v.location:
                line += f" (at {v.location})"
            if v.suggestion:
                line += f" — suggestion: {v.suggestion}"
            violation_lines.append(line)

        eq_list = ", ".join(eq.value for eq in user_profile.available_equipment)
        limitations_str = ""
        if user_profile.limitations:
            lim_lines = []
            for lim in user_profile.limitations:
                affected = ", ".join(lim.affected_exercises) if lim.affected_exercises else "N/A"
                lim_lines.append(f"  - {lim.description} ({lim.severity}): affects {affected}")
            limitations_str = "\n".join(lim_lines)

        correction_prompt = f"""The following generated training program has constraint violations that MUST be fixed.

Program (JSON):
```json
{json.dumps(program_data, indent=2)}
```

VIOLATIONS TO FIX:
{chr(10).join(violation_lines)}

USER CONSTRAINTS:
- Available equipment: {eq_list}
- Schedule: {user_profile.schedule_days} days/week, {user_profile.session_duration} min/session
- Experience: {user_profile.experience_level.value}
{f"- Limitations:{chr(10)}{limitations_str}" if limitations_str else ""}

INSTRUCTIONS:
1. Fix ONLY the violations listed above
2. Do NOT change anything else about the program
3. Replace violating exercises with appropriate alternatives that use the user's available equipment
4. Return the complete corrected program with the same JSON structure"""

        try:
            from orca import AgentChat, ModelType as OrcaModelType
            from ..agents.output_specs import final_program_specs

            chat = AgentChat(
                system_prompt="You are a program correction assistant. Fix the specified constraint violations in the training program.",
                model_type=OrcaModelType.SONNET,
                output_specs=final_program_specs,
            )

            result = await chat.send(correction_prompt)

            if result and isinstance(result, dict):
                return result
            if result and isinstance(result, str):
                try:
                    parsed = json.loads(result)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

        # Return original if correction failed
        return program_data

    async def _run_streaming_congregation(
        self,
        user_summary: str,
        framework: dict,
        equipment_constraints: str | None,
        constraint_checklist: str,
        profile_id: int | None,
        notify: Callable,
    ) -> CongregationResult:
        """Run congregation with streaming events."""
        deliberation_log = []
        captured_mediator_output = None

        if profile_id is not None:
            set_profile_context(profile_id)

        async for event in run_congregation_stream(
            user_summary=user_summary,
            program_framework=framework,
            equipment_constraints=equipment_constraints,
            profile_id=profile_id,
            constraint_checklist=constraint_checklist,
        ):
            if event.type == CongregationEventType.CLIENT_START:
                persona_name = event.data.get("persona_name", "Specialist")
                set_current_specialist(persona_name)

            elif event.type == CongregationEventType.CLIENT_RESPONSE:
                client_id = event.data.get("client_id", "")
                persona_name = event.data.get("persona_name", "")
                thoughts = event.data.get("thoughts", "")
                aligned = event.data.get("aligned")

                deliberation_log.append({
                    "client_id": client_id,
                    "content": thoughts,
                    "is_aligned": aligned,
                })

                if thoughts:
                    preview = thoughts[:200] + "..." if len(thoughts) > 200 else thoughts
                    await notify("specialist", persona_name, {
                        "preview": preview,
                        "full": thoughts,
                        "aligned": aligned,
                    })

            elif event.type == CongregationEventType.TURN_START:
                turn = event.data.get("turn", 0)
                await notify("phase", f"Deliberation round {turn}...")

            elif event.type == CongregationEventType.CLIENT_INFO_REQUEST:
                persona_name = event.data.get("persona_name", "Specialist")
                requests = event.data.get("requests", [])
                if requests:
                    func_names = [
                        r.get("identifier", "") for r in requests if r.get("identifier")
                    ]
                    if func_names:
                        await notify("info_request", persona_name, {
                            "functions": func_names,
                        })

            elif event.type == CongregationEventType.MEDIATOR_SYNTHESIS:
                await notify("phase", "Mediator synthesizing final program...")
                captured_mediator_output = event.data.get("output")

            elif event.type == CongregationEventType.COMPLETED:
                result = event.data.get("result")
                if result:
                    raw_output = result.final_output or captured_mediator_output or {}
                    final_program = raw_output
                    if isinstance(final_program, str):
                        try:
                            final_program = json.loads(final_program)
                        except json.JSONDecodeError:
                            final_program = {}

                    return CongregationResult(
                        final_program=final_program,
                        final_thesis=result.final_thesis,
                        deliberation_log=deliberation_log,
                        converged=result.converged,
                    )

        # If we get here without a COMPLETED event, return empty
        return CongregationResult(
            final_program={},
            final_thesis="",
            deliberation_log=deliberation_log,
            converged=False,
        )

    def _program_to_summary(self, program: Program) -> str:
        """Convert program to a readable summary for the congregation topic."""
        lines = []
        for week in program.weeks:
            deload = " (deload)" if week.deload else ""
            lines.append(f"Week {week.week_number}{deload}:")
            for day in week.days:
                focus = f" | {day.focus}" if day.focus else ""
                lines.append(f"  {day.name}{focus}:")
                for ex in day.exercises:
                    working_sets = [s for s in ex.sets if not s.is_warmup]
                    if working_sets:
                        first_set = working_sets[0]
                        sets_str = f"{len(working_sets)}x{first_set.reps}"
                    else:
                        sets_str = "3x10"
                    lines.append(
                        f"    - {ex.name}: {sets_str} ({ex.progression.value})"
                    )
        return "\n".join(lines)

    def _extract_framework(self, program: Program) -> dict:
        """Extract program framework information from existing program."""
        days_per_week = len(program.weeks[0].days) if program.weeks else 4
        day_focuses = []

        if program.weeks:
            for day in program.weeks[0].days:
                day_focuses.append(day.focus if day.focus else day.name)

        # Determine split type from day names
        split_type = "custom"
        if program.weeks and program.weeks[0].days:
            day_names = [d.name.lower() for d in program.weeks[0].days]
            if any("upper" in n for n in day_names) and any(
                "lower" in n for n in day_names
            ):
                split_type = "upper_lower"
            elif any("push" in n for n in day_names) and any(
                "pull" in n for n in day_names
            ):
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

    def _build_conversation_context(self) -> str:
        """Build conversation context from history."""
        if not self.conversation_history:
            return ""

        lines = ["Previous refinement requests in this session:"]
        for entry in self.conversation_history[-6:]:  # Last 6 messages
            role = "User" if entry["role"] == "user" else "Coach"
            lines.append(f"  {role}: {entry['content']}")
        return "\n".join(lines)

    def _try_parse_from_thesis(self, thesis: str) -> dict | None:
        """Try to parse structured program data from the mediator's thesis."""
        # Try JSON code block
        json_match = re.search(r"```json\s*(.*?)\s*```", thesis, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try raw JSON object
        json_match = re.search(r"\{[\s\S]*\"weeks\"[\s\S]*\}", thesis)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def _build_weeks_from_congregation_data(self, weeks_data: list) -> list[ProgramWeek]:
        """Build ProgramWeek objects from congregation output.

        Uses the same robust type coercion as executor._build_program:
        handles int/str sets, reps_min/reps_max, cardio skipping, etc.
        """
        new_weeks = []

        for week_data in weeks_data:
            if not isinstance(week_data, dict):
                continue

            new_days = []
            for day_data in week_data.get("days", []):
                if not isinstance(day_data, dict):
                    continue

                new_exercises = []
                for ex_data in day_data.get("exercises", []):
                    if not isinstance(ex_data, dict):
                        continue

                    # Skip cardio/duration-based exercises (can't express in Liftoscript)
                    if "duration_minutes" in ex_data and "reps_min" not in ex_data:
                        continue

                    # Build sets — handle both congregation format (sets/reps_min/reps_max)
                    # and simple format (sets: "4x8")
                    sets = self._parse_exercise_sets(ex_data)

                    # Map progression type
                    prog_str = ex_data.get("progression", "dp")
                    try:
                        progression = ProgressionScheme(prog_str)
                    except ValueError:
                        progression = ProgressionScheme.DOUBLE

                    # Coerce increment to a number
                    raw_increment = ex_data.get("increment", 5)
                    if not isinstance(raw_increment, (int, float)):
                        try:
                            raw_increment = float(raw_increment)
                        except (ValueError, TypeError):
                            raw_increment = 5

                    new_exercises.append(
                        ProgramExercise(
                            name=ex_data.get("name", "Unknown"),
                            sets=sets,
                            progression=progression,
                            progression_params={"increment": raw_increment},
                            notes=ex_data.get("notes", ""),
                        )
                    )

                new_days.append(
                    ProgramDay(
                        name=day_data.get("name", f"Day {len(new_days) + 1}"),
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

    def _parse_exercise_sets(self, ex_data: dict) -> list[SetScheme]:
        """Parse exercise set data handling both congregation and simple formats.

        Congregation format: {"sets": 4, "reps_min": 5, "reps_max": 8, "is_amrap_final_set": true}
        Simple format: {"sets": "4x8"} or {"sets": "3x8-12"}
        """
        raw_sets = ex_data.get("sets", 3)

        # If sets is a string like "4x8", parse it
        if isinstance(raw_sets, str) and "x" in raw_sets:
            return self._parse_sets_string(raw_sets)

        # Congregation format: numeric sets with reps_min/reps_max
        num_sets = raw_sets
        if not isinstance(num_sets, int):
            try:
                num_sets = int(num_sets)
            except (ValueError, TypeError):
                num_sets = 3

        reps_min = ex_data.get("reps_min", 5)
        if not isinstance(reps_min, int):
            try:
                reps_min = int(reps_min)
            except (ValueError, TypeError):
                reps_min = 5

        reps_max = ex_data.get("reps_max", reps_min)
        if not isinstance(reps_max, int):
            try:
                reps_max = int(reps_max)
            except (ValueError, TypeError):
                reps_max = reps_min

        is_amrap = ex_data.get("is_amrap_final_set", False)

        sets = []
        for i in range(num_sets):
            is_last = i == num_sets - 1
            reps = reps_min if reps_min == reps_max else f"{reps_min}-{reps_max}"
            sets.append(
                SetScheme(
                    reps=reps,
                    rpe=ex_data.get("rpe_target"),
                    is_amrap=is_last and is_amrap,
                )
            )

        return sets

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
