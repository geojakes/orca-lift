"""Plan execution orchestration for program generation."""

from dataclasses import dataclass
from typing import Awaitable, Callable

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
from ..models.user_profile import UserProfile
from orca import CongregationEvent, CongregationEventType

from .congregation import CongregationResult, run_congregation, run_congregation_stream
from .plan_builder import PlanContext, build_generation_plan
from .tools import set_current_specialist, set_question_callback

# Type for progress callback: (event_type, message, data)
ProgressCallback = Callable[[str, str, dict | None], Awaitable[None]]


@dataclass
class ExecutionResult:
    """Result from plan execution."""

    program: Program
    phase_outputs: dict[str, dict]
    congregation_result: CongregationResult | None
    liftoscript: str


class ProgramGenerator:
    """Orchestrates the full program generation pipeline."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.generator = LiftoscriptGenerator()

    async def execute(
        self,
        user_profile: UserProfile,
        goals: str,
        fitness_data_summary: str = "",
        num_weeks: int = 4,
        equipment_constraints: str | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> ExecutionResult:
        """Execute the full program generation pipeline.

        Args:
            user_profile: User's fitness profile
            goals: Natural language description of goals
            fitness_data_summary: Summary of imported fitness data
            num_weeks: Number of weeks for the program (1-6)
            equipment_constraints: Formatted equipment constraints for agents
            on_progress: Optional callback for progress updates

        Returns:
            ExecutionResult with the generated program
        """
        phase_outputs: dict[str, dict] = {}

        async def notify(event_type: str, message: str, data: dict | None = None):
            if on_progress:
                await on_progress(event_type, message, data)

        # Add weeks to goals for context
        if num_weeks != 4:
            goals = f"{goals}. Generate a {num_weeks}-week program."

        # Build context
        context = PlanContext(
            user_profile=user_profile.get_summary(),
            fitness_data=fitness_data_summary or "No fitness data imported.",
            user_goals=goals,
            equipment_list=[eq.value for eq in user_profile.available_equipment],
            days_per_week=user_profile.schedule_days,
        )

        if self.verbose:
            print("=== Phase 1: Analyzing user profile and equipment ===\n")

        await notify("phase", "Analyzing user profile...")

        # Execute Phase 1 & 2: DAG plan
        plan = build_generation_plan(context)
        executor = PlanExecutor.from_plan(
            plan,
            verbose=self.verbose,
            permission_mode=PermissionMode.DEFAULT,
        )

        await notify("phase", "Assessing available equipment...")
        plan_result = await executor.execute(plan)

        # Extract outputs
        user_analysis = plan_result.get("user_analysis", {})
        equipment_assessment = plan_result.get("equipment_assessment", {})
        program_framework = plan_result.get("program_framework", {})

        phase_outputs["user_analysis"] = user_analysis
        phase_outputs["equipment_assessment"] = equipment_assessment
        phase_outputs["program_framework"] = program_framework

        if self.verbose:
            print("\n=== Phase 2: Program framework designed ===")
            print(f"Split: {program_framework.get('split_type', 'N/A')}")
            print(f"Days: {program_framework.get('days_per_week', 'N/A')}/week")
            print(f"Periodization: {program_framework.get('periodization', 'N/A')}")

        await notify("phase", "Building program framework...", {
            "split": program_framework.get("split_type", "N/A"),
            "days": program_framework.get("days_per_week", "N/A"),
        })

        if self.verbose:
            print("\n=== Phase 3: Multi-agent congregation ===\n")

        await notify("phase", "Specialists are deliberating...")

        # Map client_id to friendly name
        specialist_names = {
            "strength_coach": "Strength Coach",
            "hypertrophy_expert": "Hypertrophy Expert",
            "periodization_specialist": "Periodization Specialist",
            "recovery_analyst": "Recovery Analyst",
            "mediator": "Mediator",
        }

        # Execute Phase 3: Congregation with streaming if callback provided
        if on_progress:
            # Use streaming to emit real-time specialist events
            congregation_result = None
            deliberation_log = []

            # Set up question callback for ask_human tool
            async def question_callback(question_id: str, specialist: str, question: str):
                await notify("human_question", specialist, {
                    "question_id": question_id,
                    "question": question,
                })

            set_question_callback(question_callback)

            try:
                async for event in run_congregation_stream(
                    user_summary=context.user_profile,
                    program_framework=program_framework,
                    equipment_constraints=equipment_constraints,
                    profile_id=user_profile.id,
                ):
                    if event.type == CongregationEventType.CLIENT_START:
                        # Track which specialist is currently active
                        persona_name = event.data.get("persona_name", "Specialist")
                        set_current_specialist(persona_name)

                    elif event.type == CongregationEventType.CLIENT_RESPONSE:
                        client_id = event.data.get("client_id", "")
                        persona_name = event.data.get("persona_name", "")
                        thoughts = event.data.get("thoughts", "")
                        aligned = event.data.get("aligned")

                        # Record for deliberation log
                        deliberation_log.append({
                            "client_id": client_id,
                            "content": thoughts,
                            "is_aligned": aligned,
                        })

                        # Emit specialist event with both preview and full content
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
                            func_names = [r.get("identifier", "") for r in requests if r.get("identifier")]
                            if func_names:
                                await notify("info_request", persona_name, {
                                    "functions": func_names,
                                })

                    elif event.type == CongregationEventType.CLIENT_INFO_RESULT:
                        # Results are returned to specialists - could show them if desired
                        pass

                    elif event.type == CongregationEventType.MEDIATOR_SYNTHESIS:
                        await notify("phase", "Mediator synthesizing final program...")

                    elif event.type == CongregationEventType.COMPLETED:
                        result = event.data.get("result")
                        if result:
                            # Build our CongregationResult from orca's result
                            # Handle case where final_output is a string (JSON) instead of dict
                            final_program = result.final_output if result.final_output else {}
                            if isinstance(final_program, str):
                                import json
                                try:
                                    final_program = json.loads(final_program)
                                except json.JSONDecodeError:
                                    final_program = {}
                            congregation_result = CongregationResult(
                                final_program=final_program,
                                final_thesis=result.final_thesis,
                                deliberation_log=deliberation_log,
                                converged=result.converged,
                            )
            finally:
                # Clean up question callback
                set_question_callback(None)
        else:
            # Use non-streaming version
            congregation_result = await run_congregation(
                user_summary=context.user_profile,
                program_framework=program_framework,
                verbose=self.verbose,
                equipment_constraints=equipment_constraints,
                profile_id=user_profile.id,
            )

            # Stream specialist contributions after the fact (for backward compat)
            for entry in congregation_result.deliberation_log:
                client_id = entry.get("client_id", "")
                content = entry.get("content", "")
                aligned = entry.get("is_aligned")
                name = specialist_names.get(client_id, client_id)

                if content and name:
                    # Send both preview and full content
                    preview = content[:200] + "..." if len(content) > 200 else content
                    await notify("specialist", name, {
                        "preview": preview,
                        "full": content,
                        "aligned": aligned,
                    })

        phase_outputs["congregation"] = {
            "final_program": congregation_result.final_program,
            "converged": congregation_result.converged,
        }

        if self.verbose:
            print("\n=== Phase 4: Generating Liftoscript ===\n")

        await notify("phase", "Generating Liftoscript...")

        # Execute Phase 4: Convert to Program model and generate Liftoscript
        program = self._build_program(
            congregation_result.final_program,
            congregation_result.final_thesis,
            goals,
            congregation_result.deliberation_log,
            user_profile.id,
        )

        liftoscript = self.generator.generate(program)
        program.liftoscript = liftoscript

        if self.verbose:
            print("Program generated successfully!")
            print(f"Name: {program.name}")
            print(f"Weeks: {program.total_weeks}")
            print(f"Days/week: {program.days_per_week}")

        return ExecutionResult(
            program=program,
            phase_outputs=phase_outputs,
            congregation_result=congregation_result,
            liftoscript=liftoscript,
        )

    def _build_program(
        self,
        program_data: dict,
        final_thesis: str,
        goals: str,
        congregation_log: list[dict],
        profile_id: int | None,
    ) -> Program:
        """Convert AI output to Program model."""
        weeks = []

        # Ensure program_data is a dict
        if not isinstance(program_data, dict):
            program_data = {}

        # Handle case where program_data might be empty or missing weeks
        weeks_data = program_data.get("weeks", [])
        if not weeks_data:
            # Create a default structure from final_thesis if structured output failed
            weeks_data = self._parse_thesis_to_weeks(final_thesis)

        for week_data in weeks_data:
            days = []

            for day_data in week_data.get("days", []):
                exercises = []

                for ex_data in day_data.get("exercises", []):
                    # Build set schemes
                    sets = []
                    num_sets = ex_data.get("sets", 3)
                    reps_min = ex_data.get("reps_min", 5)
                    reps_max = ex_data.get("reps_max", reps_min)
                    is_amrap = ex_data.get("is_amrap_final_set", False)

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

                    # Map progression type
                    prog_type = ex_data.get("progression", "dp")
                    try:
                        progression = ProgressionScheme(prog_type)
                    except ValueError:
                        progression = ProgressionScheme.DOUBLE

                    exercises.append(
                        ProgramExercise(
                            name=ex_data.get("name", "Unknown"),
                            sets=sets,
                            progression=progression,
                            progression_params={
                                "increment": ex_data.get("increment", 5),
                            },
                            notes=ex_data.get("notes", ""),
                        )
                    )

                days.append(
                    ProgramDay(
                        name=day_data.get("name", f"Day {len(days) + 1}"),
                        focus=day_data.get("focus", ""),
                        exercises=exercises,
                    )
                )

            weeks.append(
                ProgramWeek(
                    week_number=week_data.get("week_number", len(weeks) + 1),
                    days=days,
                    deload=week_data.get("is_deload", False),
                )
            )

        return Program(
            name=program_data.get("program_name", "Generated Program"),
            description=program_data.get("program_description", final_thesis[:200] if final_thesis else ""),
            weeks=weeks,
            goals=goals,
            congregation_log=congregation_log,
            profile_id=profile_id,
        )

    def _parse_thesis_to_weeks(self, thesis: str) -> list[dict]:
        """Attempt to parse a free-form thesis into week structure.

        This is a fallback when structured output parsing fails.
        """
        # Default 4-week program structure
        return [
            {
                "week_number": 1,
                "is_deload": False,
                "days": [
                    {
                        "name": "Day 1",
                        "focus": "Full Body",
                        "exercises": [
                            {"name": "Squat", "sets": 3, "reps_min": 5, "reps_max": 5, "progression": "lp", "increment": 5},
                            {"name": "Bench Press", "sets": 3, "reps_min": 5, "reps_max": 5, "progression": "lp", "increment": 5},
                            {"name": "Barbell Row", "sets": 3, "reps_min": 5, "reps_max": 5, "progression": "lp", "increment": 5},
                        ],
                    },
                ],
            },
        ]


# Alias for backwards compatibility
ProgramExecutor = ProgramGenerator
