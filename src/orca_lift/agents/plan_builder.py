"""DAG plan builder for program generation workflow."""

from dataclasses import dataclass

from orca import Plan, PlanNode, ModelType

from .output_specs import (
    equipment_assessment_specs,
    program_framework_specs,
    user_analysis_specs,
)
from .prompts import (
    EQUIPMENT_ASSESSMENT_PROMPT,
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


def build_generation_plan(context: PlanContext) -> Plan:
    """Build the DAG plan for program generation.

    The plan has the following structure:

    Phase 1 (Parallel):
    ├── user_analysis (analyze user profile and data)
    ├── equipment_assessment (assess available equipment)
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

    # Phase 2: Program framework (depends on phase 1)
    # Use output references to inject results from previous nodes
    framework_prompt = PROGRAM_FRAMEWORK_PROMPT.format(
        user_analysis="{{user_analysis}}",  # Will be replaced with actual output
        equipment_assessment="{{equipment_assessment}}",
        user_goals=context.user_goals,
        days_per_week=context.days_per_week,
    )

    program_framework_node = PlanNode(
        name="program_framework",
        prompt=framework_prompt,
        output_specs=program_framework_specs,
        dependencies=[user_analysis_node, equipment_assessment_node],
        model_override=ModelType.SONNET,
    )

    return Plan(
        nodes=[
            user_analysis_node,
            equipment_assessment_node,
            program_framework_node,
        ],
        default_model=ModelType.SONNET,
    )


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
