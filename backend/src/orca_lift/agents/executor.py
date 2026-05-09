"""Plan execution orchestration for program generation."""

import json as json_module
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
from ..validators import validate_program_constraints
from orca import CongregationEvent, CongregationEventType

from .congregation import CongregationResult, run_congregation, run_congregation_stream
from .liftoscript_converter import LiftoscriptConverter
from .liftoscript_spec import LIFTOSCRIPT_FULL_SPEC
from .plan_builder import PlanContext, build_enrichment_plan, build_generation_plan
from .prompts import format_constraint_checklist
from .tools import set_current_specialist, set_question_callback

# Max number of AI correction attempts for constraint violations
MAX_CORRECTION_RETRIES = 2

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
        self.converter = LiftoscriptConverter(
            liftoscript_spec=LIFTOSCRIPT_FULL_SPEC,
            verbose=verbose,
        )

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

        # Clamp to supported range so prompts and validators stay consistent.
        num_weeks = max(1, min(8, int(num_weeks)))

        # Echo the explicit length into goals so it shows up everywhere goals
        # is referenced (specialists, framework prompt, retry prompts).
        goals = f"{goals}. Program length: exactly {num_weeks} weeks."

        # Build context
        context = PlanContext(
            user_profile=user_profile.get_summary(),
            fitness_data=fitness_data_summary or "No fitness data imported.",
            user_goals=goals,
            equipment_list=[eq.value for eq in user_profile.available_equipment],
            days_per_week=user_profile.schedule_days,
            num_weeks=num_weeks,
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
        constraint_extraction = plan_result.get("constraint_extraction", {})

        phase_outputs["user_analysis"] = user_analysis
        phase_outputs["equipment_assessment"] = equipment_assessment
        phase_outputs["program_framework"] = program_framework
        phase_outputs["constraint_extraction"] = constraint_extraction

        # Build extracted constraints list and constraint checklist for mediator
        extracted_constraints = constraint_extraction.get("constraints", [])
        if not isinstance(extracted_constraints, list):
            extracted_constraints = []
        constraint_checklist = format_constraint_checklist(
            user_profile, extracted_constraints, num_weeks=num_weeks
        )

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
            captured_mediator_output = None  # Capture from MEDIATOR_SYNTHESIS event

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
                    constraint_checklist=constraint_checklist,
                    num_weeks=num_weeks,
                ):
                    if event.type == CongregationEventType.CLIENT_START:
                        # Track which specialist is currently active
                        persona_name = event.data.get("persona_name", "Specialist")
                        set_current_specialist(persona_name)
                        if self.verbose:
                            print(f"  [{persona_name}] thinking...")

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

                        if self.verbose:
                            status = "aligned" if aligned else "proposing changes"
                            preview = thoughts[:300] + "..." if len(thoughts) > 300 else thoughts
                            print(f"  [{persona_name}] ({status})")
                            print(f"    {preview}\n")

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
                        if self.verbose:
                            print(f"\n--- Deliberation round {turn} ---\n")
                        await notify("phase", f"Deliberation round {turn}...")

                    elif event.type == CongregationEventType.CLIENT_INFO_REQUEST:
                        persona_name = event.data.get("persona_name", "Specialist")
                        requests = event.data.get("requests", [])
                        if requests:
                            func_names = [r.get("identifier", "") for r in requests if r.get("identifier")]
                            if func_names:
                                if self.verbose:
                                    print(f"  [{persona_name}] querying: {', '.join(func_names)}")
                                await notify("info_request", persona_name, {
                                    "functions": func_names,
                                })

                    elif event.type == CongregationEventType.PEER_MESSAGE_SENT:
                        from_id = event.data.get("from", "")
                        from_name = specialist_names.get(from_id, from_id)
                        messages = event.data.get("messages", [])
                        for pm in messages:
                            to_label = pm.get("to", "")
                            if to_label == "all":
                                to_label = "everyone"
                            if self.verbose:
                                print(f"  [{from_name}] → {to_label}: {pm.get('content', '')}")
                            await notify("peer_message", from_name, {
                                "to": pm.get("to", ""),
                                "content": pm.get("content", ""),
                            })

                    elif event.type == CongregationEventType.CLIENT_INFO_RESULT:
                        pass

                    elif event.type == CongregationEventType.PEER_MESSAGE_DELIVERED:
                        delivered = event.data.get("delivered", [])
                        if self.verbose and delivered:
                            print(f"  ({len(delivered)} peer message(s) delivered to inboxes)")

                    elif event.type == CongregationEventType.CONVERGENCE:
                        if self.verbose:
                            print("  *** Convergence reached ***")

                    elif event.type == CongregationEventType.MEDIATOR_START:
                        if self.verbose:
                            print("\n  Mediator synthesizing final program...")

                    elif event.type == CongregationEventType.MEDIATOR_SYNTHESIS:
                        await notify("phase", "Mediator synthesizing final program...")
                        captured_mediator_output = event.data.get("output")
                        if self.verbose:
                            print("  Mediator synthesis complete.")

                    elif event.type == CongregationEventType.COMPLETED:
                        result = event.data.get("result")
                        if result:
                            if self.verbose:
                                print(f"\n  Deliberation complete: converged={result.converged}, "
                                      f"turns={result.turns_taken}, mediated={result.mediated}")

                            raw_output = result.final_output or captured_mediator_output or {}

                            # Handle case where final_output is a string (JSON) instead of dict
                            final_program = raw_output
                            if isinstance(final_program, str):
                                import json
                                try:
                                    final_program = json.loads(final_program)
                                except json.JSONDecodeError:
                                    final_program = {}

                            if self.verbose and isinstance(final_program, dict):
                                weeks = final_program.get("weeks", [])
                                print(f"  Program: {final_program.get('program_name', 'N/A')}, "
                                      f"{len(weeks)} weeks")

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
                constraint_checklist=constraint_checklist,
                num_weeks=num_weeks,
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

        # Enforce the requested program length: truncate if too long, pad by
        # cloning the last non-deload week (with re-numbering) if too short.
        self._enforce_program_length(
            congregation_result.final_program, num_weeks
        )

        phase_outputs["congregation"] = {
            "final_program": congregation_result.final_program,
            "converged": congregation_result.converged,
        }

        # === Constraint validation loop ===
        if self.verbose:
            print("\n=== Validating program against constraints ===\n")

        await notify("phase", "Validating program constraints...")

        for attempt in range(MAX_CORRECTION_RETRIES + 1):
            validation = validate_program_constraints(
                congregation_result.final_program,
                user_profile,
                extracted_constraints=extracted_constraints,
            )

            if validation.warnings and self.verbose:
                for w in validation.warnings:
                    print(f"  Warning: {w.message}")

            if not validation.errors:
                if self.verbose:
                    print("  All constraints satisfied!")
                break

            if attempt == MAX_CORRECTION_RETRIES:
                if self.verbose:
                    print(
                        f"  {len(validation.errors)} constraint violation(s) remain "
                        f"after {MAX_CORRECTION_RETRIES} correction attempts"
                    )
                    for err in validation.errors:
                        print(f"    - {err.message}")
                break

            if self.verbose:
                print(
                    f"  Found {len(validation.errors)} violation(s), "
                    f"requesting correction (attempt {attempt + 1}/{MAX_CORRECTION_RETRIES})..."
                )
            await notify(
                "phase",
                f"Fixing {len(validation.errors)} constraint violation(s) "
                f"(attempt {attempt + 1})...",
            )

            congregation_result.final_program = await self._correct_violations(
                congregation_result.final_program,
                validation.errors,
                user_profile,
            )

        if self.verbose:
            print("\n=== Phase 4: Enriching exercises with form notes + videos ===\n")

        await notify("phase", "Looking up form notes and demo videos...")

        await self._enrich_exercises(
            congregation_result.final_program,
            on_progress=on_progress,
        )

        if self.verbose:
            print("\n=== Phase 5: Generating Liftoscript ===\n")

        await notify("phase", "Converting to Liftoscript...")

        # Step 1: Build Program model (still needed for DB storage)
        program = self._build_program(
            congregation_result.final_program,
            congregation_result.final_thesis,
            goals,
            congregation_result.deliberation_log,
            user_profile.id,
        )

        # Step 2: AI-powered Liftoscript conversion
        # Use the requested length so Liftoscript output matches what the user asked for.
        conversion_result = await self.converter.convert(
            final_program=congregation_result.final_program,
            final_thesis=congregation_result.final_thesis or "",
            num_weeks=num_weeks,
        )
        liftoscript = conversion_result.liftoscript

        # Step 3: Fix duplicate progress conflicts (auto-add labels)
        liftoscript = self.generator.fix_duplicate_progress(liftoscript)

        # Step 4: Validate
        is_valid, errors = self.generator.validate(liftoscript)
        if not is_valid and self.verbose:
            print(f"  Liftoscript validation warnings: {errors}")

        # Step 5: Fallback to Python generator if AI returned empty
        if not liftoscript.strip():
            if self.verbose:
                print("  AI converter returned empty, falling back to Python generator")
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

    def _enforce_program_length(
        self,
        program_data: dict,
        num_weeks: int,
    ) -> None:
        """Force `program_data["weeks"]` to have exactly `num_weeks` entries.

        - Trims trailing weeks if the agents produced too many.
        - Pads by cloning the last non-deload week (re-numbered) if too few.
        - Re-numbers `week_number` 1..num_weeks so downstream code matches.

        Mutates `program_data` in place.
        """
        import copy

        if not isinstance(program_data, dict):
            return

        weeks = program_data.get("weeks")
        if not isinstance(weeks, list):
            program_data["weeks"] = []
            weeks = program_data["weeks"]

        if num_weeks < 1:
            return

        actual = len(weeks)

        if actual > num_weeks:
            if self.verbose:
                print(
                    f"  Program had {actual} weeks but {num_weeks} were requested — "
                    f"trimming trailing weeks."
                )
            weeks[:] = weeks[:num_weeks]
        elif actual < num_weeks:
            if actual == 0:
                if self.verbose:
                    print(
                        f"  Program had 0 weeks but {num_weeks} were requested — "
                        f"cannot pad without a template week."
                    )
                return

            template_source = next(
                (w for w in reversed(weeks) if isinstance(w, dict) and not w.get("is_deload")),
                weeks[-1] if isinstance(weeks[-1], dict) else None,
            )
            if not isinstance(template_source, dict):
                return

            if self.verbose:
                print(
                    f"  Program had {actual} weeks but {num_weeks} were requested — "
                    f"padding by cloning the last non-deload week."
                )
            while len(weeks) < num_weeks:
                clone = copy.deepcopy(template_source)
                clone["is_deload"] = False
                weeks.append(clone)

        # Re-number weeks 1..N regardless of what the agents produced.
        for idx, week in enumerate(weeks):
            if isinstance(week, dict):
                week["week_number"] = idx + 1

    async def _enrich_exercises(
        self,
        program_data: dict,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        """Run a parallel DAG that fetches form notes + a YouTube demo per exercise.

        Mutates `program_data` in place: each exercise dict gains `posture`,
        `position`, `cues`, and `video_url` keys derived from its enrichment node.
        Exercises sharing a name share enrichment results.
        """
        if not isinstance(program_data, dict):
            return

        # Collect unique exercises and remember every (week, day, exercise) slot
        # they appear in, so we can fan results back out.
        unique: dict[str, dict] = {}
        slots: dict[str, list[dict]] = {}

        for week in program_data.get("weeks", []) or []:
            if not isinstance(week, dict):
                continue
            for day in week.get("days", []) or []:
                if not isinstance(day, dict):
                    continue
                day_focus = day.get("focus", "") or day.get("name", "")
                for ex in day.get("exercises", []) or []:
                    if not isinstance(ex, dict):
                        continue
                    name = (ex.get("name") or "").strip()
                    if not name:
                        continue
                    if name not in unique:
                        unique[name] = {
                            "name": name,
                            "day_focus": day_focus,
                            "notes": ex.get("notes", "") or "",
                        }
                    slots.setdefault(name, []).append(ex)

        if not unique:
            if self.verbose:
                print("  No exercises to enrich.")
            return

        plan, name_map = build_enrichment_plan(list(unique.values()))

        if self.verbose:
            print(f"  Enriching {len(unique)} unique exercise(s) in parallel...")

        executor = PlanExecutor.from_plan(
            plan,
            verbose=self.verbose,
            permission_mode=PermissionMode.DEFAULT,
        )

        try:
            plan_result = await executor.execute(plan)
        except Exception as e:
            if self.verbose:
                print(f"  Enrichment phase failed: {e}")
            return

        async def notify(event_type: str, message: str, data: dict | None = None):
            if on_progress:
                await on_progress(event_type, message, data)

        for ex_name, node_name in name_map.items():
            result = plan_result.get(node_name) or {}
            if not isinstance(result, dict):
                continue

            posture = (result.get("posture") or "").strip()
            position = (result.get("position") or "").strip()
            video_url = (result.get("video_url") or "").strip()
            cues_raw = result.get("cues", [])
            cues = [str(c).strip() for c in cues_raw if c] if isinstance(cues_raw, list) else []

            if not (posture or position or video_url or cues):
                continue

            for ex in slots.get(ex_name, []):
                ex["posture"] = posture
                ex["position"] = position
                ex["cues"] = cues
                ex["video_url"] = video_url

            if self.verbose:
                video_label = video_url if video_url else "no video"
                print(f"  [{ex_name}] {video_label}")

            await notify("exercise_enrichment", ex_name, {
                "posture": posture,
                "position": position,
                "cues": cues,
                "video_url": video_url,
            })

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
            if self.verbose:
                print("  Warning: No weeks in program data, using fallback")
            weeks_data = self._parse_thesis_to_weeks(final_thesis)

        for week_data in weeks_data:
            if not isinstance(week_data, dict):
                continue

            days = []

            for day_data in week_data.get("days", []):
                if not isinstance(day_data, dict):
                    continue

                exercises = []

                for ex_data in day_data.get("exercises", []):
                    if not isinstance(ex_data, dict):
                        continue

                    # Skip cardio/duration-based exercises that can't be expressed in Liftoscript
                    if "duration_minutes" in ex_data and "reps_min" not in ex_data:
                        continue

                    # Build set schemes
                    sets = []
                    num_sets = ex_data.get("sets", 3)
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

                    # Per-set RPE from enriched data (e.g., [9, 10])
                    rpe_per_set = ex_data.get("rpe_per_set", [])
                    if not isinstance(rpe_per_set, list):
                        rpe_per_set = []

                    # Rest seconds from enriched data
                    rest_seconds = ex_data.get("rest_seconds")
                    if rest_seconds is not None:
                        try:
                            rest_seconds = int(rest_seconds)
                        except (ValueError, TypeError):
                            rest_seconds = None

                    for i in range(num_sets):
                        is_last = i == num_sets - 1
                        reps = reps_min if reps_min == reps_max else f"{reps_min}-{reps_max}"
                        # Use per-set RPE if available, else fall back to uniform rpe_target
                        set_rpe = None
                        if rpe_per_set and i < len(rpe_per_set):
                            try:
                                set_rpe = float(rpe_per_set[i])
                            except (ValueError, TypeError):
                                set_rpe = None
                        if set_rpe is None:
                            set_rpe = ex_data.get("rpe_target")

                        sets.append(
                            SetScheme(
                                reps=reps,
                                rpe=set_rpe,
                                is_amrap=is_last and is_amrap,
                                rest_seconds=rest_seconds,
                            )
                        )

                    # Map progression type
                    prog_type = ex_data.get("progression", "dp")
                    try:
                        progression = ProgressionScheme(prog_type)
                    except ValueError:
                        progression = ProgressionScheme.DOUBLE

                    # Coerce increment to a number
                    raw_increment = ex_data.get("increment", 5)
                    if not isinstance(raw_increment, (int, float)):
                        try:
                            raw_increment = float(raw_increment)
                        except (ValueError, TypeError):
                            raw_increment = 5

                    # Collect enriched metadata
                    substitutions = ex_data.get("substitutions", [])
                    if not isinstance(substitutions, list):
                        substitutions = []
                    techniques = ex_data.get("techniques", [])
                    if not isinstance(techniques, list):
                        techniques = []

                    cues = ex_data.get("cues", [])
                    if not isinstance(cues, list):
                        cues = []

                    exercises.append(
                        ProgramExercise(
                            name=ex_data.get("name", "Unknown"),
                            sets=sets,
                            progression=progression,
                            progression_params={
                                "increment": raw_increment,
                            },
                            notes=ex_data.get("notes", ""),
                            substitutions=substitutions,
                            techniques=techniques,
                            posture=ex_data.get("posture", "") or "",
                            position=ex_data.get("position", "") or "",
                            cues=[str(c) for c in cues if c],
                            video_url=ex_data.get("video_url", "") or "",
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
                    phase_name=week_data.get("phase_name", ""),
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

    async def _correct_violations(
        self,
        program_data: dict,
        violations: list,
        user_profile: UserProfile,
    ) -> dict:
        """Use AI to correct constraint violations in the program.

        Sends the program + violations to Sonnet and asks it to fix only the
        flagged issues, returning the corrected program dict.
        """
        from .liftoscript_converter import LiftoscriptConverter

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
{json_module.dumps(program_data, indent=2)}
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
            from .output_specs import final_program_specs

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
                    parsed = json_module.loads(result)
                    if isinstance(parsed, dict):
                        return parsed
                except json_module.JSONDecodeError:
                    pass
        except Exception as e:
            if self.verbose:
                print(f"  Correction attempt failed: {e}")

        # Return original if correction failed
        return program_data

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
