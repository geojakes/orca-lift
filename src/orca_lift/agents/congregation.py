"""Multi-agent congregation for program design deliberation."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Callable, Awaitable

from orca import (
    Congregation,
    CongregationEvent,
    CongregationEventType,
    ConversationClient,
    MediatorConfig,
    ModelType,
    PermissionMode,
)
from orca.clients.claude_agent_client import ClaudeAgentClient

from .output_specs import final_program_specs
from .prompts import (
    DEFAULT_EQUIPMENT_CONSTRAINTS,
    HYPERTROPHY_EXPERT_SYSTEM,
    MEDIATOR_SYSTEM,
    PERIODIZATION_SPECIALIST_SYSTEM,
    RECOVERY_ANALYST_SYSTEM,
    STRENGTH_COACH_SYSTEM,
)

# Type for event callback
EventCallback = Callable[[CongregationEvent], Awaitable[None]] | None


@dataclass
class CongregationResult:
    """Result from congregation deliberation."""

    final_program: dict
    final_thesis: str
    deliberation_log: list[dict]
    converged: bool


def create_specialist_clients(
    equipment_constraints: str | None = None,
) -> list[ConversationClient]:
    """Create the specialist conversation clients for program design.

    Args:
        equipment_constraints: Formatted equipment constraints string
            to inject into each specialist's prompt
    """
    constraints = equipment_constraints or DEFAULT_EQUIPMENT_CONSTRAINTS

    specialists = [
        ("strength_coach", "Strength Coach", STRENGTH_COACH_SYSTEM),
        ("hypertrophy_expert", "Hypertrophy Expert", HYPERTROPHY_EXPERT_SYSTEM),
        ("periodization_specialist", "Periodization Specialist", PERIODIZATION_SPECIALIST_SYSTEM),
        ("recovery_analyst", "Recovery Analyst", RECOVERY_ANALYST_SYSTEM),
    ]

    clients = []
    for client_id, name, prompt_template in specialists:
        # Inject equipment constraints into prompt
        prompt = prompt_template.format(equipment_constraints=constraints)

        agent_client = ClaudeAgentClient(permission_mode=PermissionMode.DEFAULT)
        clients.append(
            ConversationClient(
                client_id=client_id,
                persona_name=name,
                persona_prompt=prompt,
                agent_client=agent_client,
                model_type=ModelType.SONNET,
            )
        )

    return clients


def create_mediator_config() -> MediatorConfig:
    """Create the mediator configuration."""
    return MediatorConfig(
        persona_prompt=MEDIATOR_SYSTEM,
        model_type=ModelType.OPUS,
        output_spec=final_program_specs,
    )


def create_congregation(
    verbose: bool = True,
    equipment_constraints: str | None = None,
) -> Congregation:
    """Create the full congregation for program generation.

    Args:
        verbose: Whether to show deliberation progress
        equipment_constraints: Formatted equipment constraints string
    """
    clients = create_specialist_clients(equipment_constraints=equipment_constraints)
    mediator_config = create_mediator_config()

    return Congregation(
        clients=clients,
        mediator_config=mediator_config,
        min_turns=2,
        max_turns=5,
        verbose=verbose,
    )


def _build_topic(user_summary: str, program_framework: dict) -> str:
    """Build the deliberation topic string."""
    return f"""Design a complete training program for the following user:

{user_summary}

Proposed Framework:
- Split: {program_framework.get('split_type', 'TBD')}
- Days/week: {program_framework.get('days_per_week', 'TBD')}
- Focus areas: {', '.join(program_framework.get('day_focuses', []))}
- Periodization: {program_framework.get('periodization', 'TBD')}
- Progression: {program_framework.get('progression_philosophy', 'TBD')}

Each specialist should provide their recommendations for:
1. Exercise selection and order
2. Sets and rep ranges
3. Progression schemes (lp = linear, dp = double progression, sum = total reps)
4. Any concerns or modifications needed

The mediator should synthesize all recommendations into a complete program structure."""


async def run_congregation_stream(
    user_summary: str,
    program_framework: dict,
    equipment_constraints: str | None = None,
) -> AsyncGenerator[CongregationEvent, None]:
    """Run the congregation with streaming events.

    Yields CongregationEvent objects as the deliberation progresses,
    allowing real-time observation of specialist responses.

    Args:
        user_summary: Summary of user profile and goals
        program_framework: The proposed program framework
        equipment_constraints: Formatted equipment constraints string

    Yields:
        CongregationEvent objects for each significant event
    """
    congregation = create_congregation(
        verbose=False,  # We're streaming instead
        equipment_constraints=equipment_constraints,
    )

    topic = _build_topic(user_summary, program_framework)

    async for event in congregation.deliberate_stream(topic):
        yield event


async def run_congregation(
    user_summary: str,
    program_framework: dict,
    verbose: bool = True,
    equipment_constraints: str | None = None,
) -> CongregationResult:
    """Run the congregation to design a program.

    Args:
        user_summary: Summary of user profile and goals
        program_framework: The proposed program framework
        verbose: Whether to show deliberation progress
        equipment_constraints: Formatted equipment constraints string

    Returns:
        CongregationResult with final program and deliberation log
    """
    congregation = create_congregation(
        verbose=verbose,
        equipment_constraints=equipment_constraints,
    )

    topic = _build_topic(user_summary, program_framework)

    # Run deliberation
    result = await congregation.deliberate(topic)

    # Build deliberation log from messages
    deliberation_log = []
    for msg in result.message_history:
        deliberation_log.append({
            "client_id": msg.client_id,
            "content": msg.thoughts,
            "is_aligned": msg.aligned,
        })

    # Parse final output if available
    final_program = {}
    if result.final_output:
        final_program = result.final_output

    return CongregationResult(
        final_program=final_program,
        final_thesis=result.final_thesis,
        deliberation_log=deliberation_log,
        converged=result.converged,
    )
