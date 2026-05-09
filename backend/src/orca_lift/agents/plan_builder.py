"""DAG plan builder for program generation workflow."""

from dataclasses import dataclass

from orca import Plan, PlanNode, ModelType

from .output_specs import (
    constraint_extraction_specs,
    equipment_assessment_specs,
    exercise_enrichment_specs,
    program_framework_specs,
    user_analysis_specs,
)
from .prompts import (
    CONSTRAINT_EXTRACTION_PROMPT,
    EQUIPMENT_ASSESSMENT_PROMPT,
    EXERCISE_ENRICHMENT_PROMPT,
    PROGRAM_FRAMEWORK_PROMPT,
    USER_ANALYSIS_PROMPT,
)


@dataclass
class PlanContext:
    """Context data passed through the plan execution."""

    user_profile: str
    fitness_data: str
    user_goals: str
    equipment_list: list[str]
    days_per_week: int
    num_weeks: int = 4


def build_generation_plan(context: PlanContext) -> Plan:
    """Build the DAG plan for program generation.

    The plan has the following structure:

    Phase 1 (Parallel):
    ├── user_analysis (analyze user profile and data)
    ├── equipment_assessment (assess available equipment)
    ├── constraint_extraction (extract constraints from goals and profile)
            ↓
    Phase 2:
    ├── program_framework (design high-level structure)

    Note: congregation and liftoscript generation are handled separately.
    """
    # Phase 1: Parallel analysis tasks
    user_analysis_node = PlanNode(
        name="user_analysis",
        prompt=USER_ANALYSIS_PROMPT.format(
            user_profile=context.user_profile,
            fitness_data=context.fitness_data,
        ),
        output_specs=user_analysis_specs,
        model_override=ModelType.SONNET,
    )

    equipment_assessment_node = PlanNode(
        name="equipment_assessment",
        prompt=EQUIPMENT_ASSESSMENT_PROMPT.format(
            equipment_list=", ".join(context.equipment_list),
        ),
        output_specs=equipment_assessment_specs,
        model_override=ModelType.SONNET,
    )

    constraint_extraction_node = PlanNode(
        name="constraint_extraction",
        prompt=CONSTRAINT_EXTRACTION_PROMPT.format(
            user_goals=context.user_goals,
            user_profile=context.user_profile,
        ),
        output_specs=constraint_extraction_specs,
        model_override=ModelType.SONNET,
    )

    # Phase 2: Program framework (depends on phase 1)
    # Use output references to inject results from previous nodes
    framework_prompt = PROGRAM_FRAMEWORK_PROMPT.format(
        user_analysis="{{user_analysis}}",  # Will be replaced with actual output
        equipment_assessment="{{equipment_assessment}}",
        user_goals=context.user_goals,
        days_per_week=context.days_per_week,
        num_weeks=context.num_weeks,
    )

    program_framework_node = PlanNode(
        name="program_framework",
        prompt=framework_prompt,
        output_specs=program_framework_specs,
        dependencies=[
            user_analysis_node,
            equipment_assessment_node,
            constraint_extraction_node,
        ],
        model_override=ModelType.SONNET,
    )

    return Plan(
        nodes=[
            user_analysis_node,
            equipment_assessment_node,
            constraint_extraction_node,
            program_framework_node,
        ],
        default_model=ModelType.SONNET,
    )


def _enrichment_node_name(exercise_name: str) -> str:
    """Derive a stable, plan-safe node name from an exercise name."""
    import re

    slug = re.sub(r"[^a-z0-9]+", "_", exercise_name.lower()).strip("_")
    return f"enrich_{slug or 'exercise'}"


def build_enrichment_plan(
    exercises: list[dict],
) -> tuple[Plan, dict[str, str]]:
    """Build a parallel DAG that fetches form notes + a demo video per exercise.

    Each exercise gets one PlanNode with web access (WebSearch + WebFetch) so
    Claude can locate a YouTube demonstration link and write posture/position
    cues. Nodes have no dependencies, so the executor runs them all in parallel.

    Args:
        exercises: Deduplicated list of {"name": str, "day_focus": str, "notes": str}.

    Returns:
        (plan, name_to_node_map) — `name_to_node_map` maps exercise name to the
        plan node name so callers can look up results.
    """
    nodes: list[PlanNode] = []
    name_map: dict[str, str] = {}
    seen_node_names: set[str] = set()

    for ex in exercises:
        ex_name = (ex.get("name") or "").strip()
        if not ex_name:
            continue

        node_name = _enrichment_node_name(ex_name)
        # Disambiguate collisions (e.g., two exercises slugifying to the same thing)
        base = node_name
        suffix = 2
        while node_name in seen_node_names:
            node_name = f"{base}_{suffix}"
            suffix += 1
        seen_node_names.add(node_name)
        name_map[ex_name] = node_name

        prompt = EXERCISE_ENRICHMENT_PROMPT.format(
            exercise_name=ex_name,
            day_focus=ex.get("day_focus", "") or "(unspecified)",
            existing_notes=ex.get("notes", "") or "(none)",
        )

        nodes.append(
            PlanNode(
                name=node_name,
                prompt=prompt,
                output_specs=exercise_enrichment_specs,
                model_override=ModelType.SONNET,
                web=True,
            )
        )

    return Plan(nodes=nodes, default_model=ModelType.SONNET), name_map


def build_refinement_plan(
    program_structure: dict,
    refinement_request: str,
) -> Plan:
    """Build a plan for refining an existing program."""
    import json

    refinement_node = PlanNode(
        name="refine_program",
        prompt=f"""Refine the following program based on the user's request:

Current Program:
```json
{json.dumps(program_structure, indent=2)}
```

User Request: {refinement_request}

Provide the updated program structure as JSON with the same schema.
Explain what was changed and why.""",
        output_specs=[],  # Free-form response
        model_override=ModelType.SONNET,
    )

    return Plan(nodes=[refinement_node])
