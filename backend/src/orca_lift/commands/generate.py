"""Generate program command."""

import click

from ..agents import ProgramExecutor
from ..db import FitnessDataRepository, ProgramRepository, UserProfileRepository, get_db_path
from ..models.exercises import EquipmentType
from ..models.user_profile import ExperienceLevel, FitnessGoal, UserProfile
from .base import async_command, echo_error, echo_info, echo_success, ensure_initialized


@click.command()
@click.argument("goals", required=False)
@click.option(
    "--from-profile",
    is_flag=True,
    help="Generate using the most recent user profile",
)
@click.option(
    "--profile-id",
    "-p",
    type=int,
    help="Use a specific profile ID",
)
@click.option(
    "--weeks",
    "-w",
    type=click.IntRange(1, 6),
    default=4,
    help="Program length in weeks (1-6, default: 4)",
)
@click.option(
    "--verbose/--quiet",
    "-v/-q",
    default=True,
    help="Show detailed deliberation output",
)
@click.pass_context
@async_command
async def generate(
    ctx,
    goals: str | None,
    from_profile: bool,
    profile_id: int | None,
    weeks: int,
    verbose: bool,
):
    """Generate a personalized training program.

    GOALS is a natural language description of your training goals.
    You can also use --from-profile to generate based on imported profile data.

    Examples:

        # Generate with explicit goals
        orca-lift generate "Build strength for powerlifting, 4 days per week"

        # Generate from imported profile
        orca-lift generate --from-profile

        # Combine profile with additional goals
        orca-lift generate --from-profile "Add more arm work"

        # Generate a 6-week program
        orca-lift generate "4 day upper/lower" --weeks 6
    """
    ensure_initialized(ctx)

    db_path = get_db_path()
    profile_repo = UserProfileRepository(db_path)
    fitness_repo = FitnessDataRepository(db_path)
    program_repo = ProgramRepository(db_path)

    # Get user profile
    if profile_id:
        profile = await profile_repo.get(profile_id)
        if not profile:
            echo_error(f"Profile ID {profile_id} not found")
            ctx.exit(1)
    elif from_profile:
        profile = await profile_repo.get_latest()
        if not profile:
            echo_error(
                "No profile found. Run 'orca-lift import manual' first."
            )
            ctx.exit(1)
    else:
        profile = await profile_repo.get_latest()

    if not profile and not goals:
        echo_error(
            "No profile or goals provided. Either:\n"
            "  - Run 'orca-lift import manual' to create a profile\n"
            "  - Provide goals: orca-lift generate 'Your goals here'"
        )
        ctx.exit(1)

    # Create a default profile if none exists but goals are provided
    if not profile and goals:
        echo_info("No profile found. Creating default profile from goals...")
        profile = _create_default_profile_from_goals(goals)

    # Build goals string
    if not goals:
        goals = f"Goals: {', '.join(g.value for g in profile.goals)}"
    elif profile and profile.id is not None:
        # Combine profile goals with additional request (only for saved profiles)
        profile_goals = ", ".join(g.value for g in profile.goals)
        goals = f"Profile goals: {profile_goals}. Additional request: {goals}"

    # Get fitness data summary if available
    fitness_summary = ""
    if profile and profile.id:
        fitness_data = await fitness_repo.get_by_type("workout", profile.id)
        if fitness_data:
            fitness_summary = f"Found {len(fitness_data)} workout records in history."

    echo_info("Generating program...")
    if profile:
        echo_info(f"Using profile: {profile.name} (ID: {profile.id})")
    echo_info(f"Goals: {goals}")
    echo_info(f"Program length: {weeks} weeks")
    click.echo()

    # Execute program generation
    executor = ProgramExecutor(verbose=verbose)

    try:
        result = await executor.execute(
            user_profile=profile,
            goals=goals,
            fitness_data_summary=fitness_summary,
            num_weeks=weeks,
        )
    except Exception as e:
        echo_error(f"Failed to generate program: {e}")
        ctx.exit(1)

    # Save program
    program_id = await program_repo.create(result.program)

    click.echo()
    echo_success(f"Program generated successfully! (ID: {program_id})")
    click.echo()

    # Display program summary
    click.echo("=" * 60)
    click.echo(result.program.get_summary())
    click.echo("=" * 60)

    click.echo()
    click.echo("Next steps:")
    click.echo(f"  - View full program: orca-lift programs show {program_id}")
    click.echo(f"  - Refine program: orca-lift refine {program_id}")
    click.echo(f"  - Export Liftoscript: orca-lift export {program_id}")
    click.echo(f"  - Copy to clipboard: orca-lift export {program_id} --clipboard")


def _create_default_profile_from_goals(goals: str) -> UserProfile:
    """Create a default profile based on goals text.

    Parses common patterns from the goals to infer settings.
    """
    goals_lower = goals.lower()

    # Infer training days from goals
    schedule_days = 4  # default
    for pattern in ["2 day", "2x", "twice"]:
        if pattern in goals_lower:
            schedule_days = 2
            break
    for pattern in ["3 day", "3x", "three day"]:
        if pattern in goals_lower:
            schedule_days = 3
            break
    for pattern in ["4 day", "4x", "four day"]:
        if pattern in goals_lower:
            schedule_days = 4
            break
    for pattern in ["5 day", "5x", "five day"]:
        if pattern in goals_lower:
            schedule_days = 5
            break
    for pattern in ["6 day", "6x", "six day"]:
        if pattern in goals_lower:
            schedule_days = 6
            break

    # Infer fitness goals
    fitness_goals = []
    if any(w in goals_lower for w in ["strength", "strong", "power"]):
        fitness_goals.append(FitnessGoal.STRENGTH)
    if any(w in goals_lower for w in ["muscle", "hypertrophy", "size", "mass"]):
        fitness_goals.append(FitnessGoal.HYPERTROPHY)
    if any(w in goals_lower for w in ["powerlifting", "squat", "bench", "deadlift"]):
        fitness_goals.append(FitnessGoal.POWERLIFTING)
    if any(w in goals_lower for w in ["lose weight", "fat loss", "weight loss", "cut", "lean"]):
        fitness_goals.append(FitnessGoal.FAT_LOSS)
    if any(w in goals_lower for w in ["general", "fitness", "health"]):
        fitness_goals.append(FitnessGoal.GENERAL_FITNESS)

    if not fitness_goals:
        fitness_goals = [FitnessGoal.GENERAL_FITNESS]

    # Infer experience level
    experience = ExperienceLevel.INTERMEDIATE  # default
    if any(w in goals_lower for w in ["beginner", "new to", "starting", "never"]):
        experience = ExperienceLevel.BEGINNER
    elif any(w in goals_lower for w in ["advanced", "experienced", "years"]):
        experience = ExperienceLevel.ADVANCED

    # Default to full gym equipment
    equipment = [
        EquipmentType.BARBELL,
        EquipmentType.DUMBBELL,
        EquipmentType.CABLE,
        EquipmentType.MACHINE,
        EquipmentType.BODYWEIGHT,
    ]

    return UserProfile(
        name="User",
        experience_level=experience,
        goals=fitness_goals,
        available_equipment=equipment,
        schedule_days=schedule_days,
        session_duration=60,
        notes=f"Generated from goals: {goals}",
    )
