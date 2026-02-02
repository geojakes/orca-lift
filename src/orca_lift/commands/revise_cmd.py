"""Revise program command."""

import click

from ..db.repositories import (
    EquipmentConfigRepository,
    ExerciseRepository,
    ProgramProgressRepository,
    ProgramRepository,
    UserProfileRepository,
)
from ..services.revision import RevisionService
from .base import (
    async_command,
    echo_error,
    echo_info,
    echo_success,
    echo_warning,
    ensure_initialized,
)


@click.command("revise")
@click.argument("program_id", type=int)
@click.option("-w", "--from-week", type=int, help="Week to start revision from")
@click.option("-d", "--from-day", type=int, default=1, help="Day to start revision from (default: 1)")
@click.option("-r", "--reason", type=str, default="", help="Reason for revision")
@click.option("--verbose/--quiet", default=True, help="Show congregation deliberation")
@click.pass_context
@async_command
async def revise(
    ctx: click.Context,
    program_id: int,
    from_week: int | None,
    from_day: int,
    reason: str,
    verbose: bool,
):
    """Revise a program from a specific position.

    Regenerates the program from the specified week/day forward,
    keeping all completed work unchanged. Useful when you want to:

    - Adjust the program based on how the first weeks went
    - Add more variety to later weeks
    - Modify intensity or volume for remaining weeks
    - Incorporate user feedback

    If --from-week is not specified, uses the current progress position
    or prompts interactively.

    Examples:

        # Revise from week 3 onward (interactive)
        orca-lift revise 1 --from-week 3

        # Revise with specific reason
        orca-lift revise 1 -w 3 -d 1 -r "Need more volume on back exercises"

        # Revise from current progress position
        orca-lift revise 1
    """
    ensure_initialized(ctx)

    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        echo_error(f"Program {program_id} not found.")
        ctx.exit(1)

    # Get user profile
    profile_repo = UserProfileRepository()
    profile = await profile_repo.get_latest()

    if not profile:
        echo_error("No user profile found. Run 'orca-lift init' first.")
        ctx.exit(1)

    # Determine revision position
    if from_week is None:
        # Try to get from progress
        progress_repo = ProgramProgressRepository()
        progress = await progress_repo.get_by_program(program_id)

        if progress:
            from_week = progress.current_week
            from_day = progress.current_day
            click.echo(f"Using current progress position: Week {from_week}, Day {from_day}")
        else:
            # Interactive prompt
            click.echo(f"\nProgram has {len(program.weeks)} weeks:")
            for i, week in enumerate(program.weeks):
                deload = " (deload)" if week.deload else ""
                click.echo(f"  Week {i + 1}{deload}: {len(week.days)} days")

            from_week = click.prompt(
                "Start revision from which week",
                type=int,
                default=1,
            )

    # Validate position
    if from_week < 1 or from_week > len(program.weeks):
        echo_error(f"Invalid week {from_week}. Program has {len(program.weeks)} weeks.")
        ctx.exit(1)

    week = program.weeks[from_week - 1]
    if from_day < 1 or from_day > len(week.days):
        echo_error(f"Invalid day {from_day}. Week {from_week} has {len(week.days)} days.")
        ctx.exit(1)

    # Prompt for reason if not provided
    if not reason:
        reason = click.prompt(
            "Reason for revision (optional)",
            default="",
            show_default=False,
        )

    # Get available exercises based on equipment
    available_exercises = None
    exercise_repo = ExerciseRepository()
    equipment_repo = EquipmentConfigRepository()

    equipment_config = await equipment_repo.get_by_profile(profile.id)
    if equipment_config and profile.available_equipment:
        exercises = await exercise_repo.get_by_equipment(profile.available_equipment)
        available_exercises = [ex.name for ex in exercises]

    # Confirm revision
    click.echo()
    click.echo(click.style("Revision Summary:", bold=True))
    click.echo(f"  Program: {program.name}")
    click.echo(f"  Starting from: Week {from_week}, Day {from_day}")
    click.echo(f"  Weeks to regenerate: {len(program.weeks) - from_week + 1}")
    if reason:
        click.echo(f"  Reason: {reason}")

    if not click.confirm("\nProceed with revision?"):
        echo_info("Revision cancelled.")
        return

    # Run revision
    click.echo()
    echo_info("Running congregation to revise program...")
    click.echo()

    service = RevisionService(verbose=verbose)

    try:
        revised_program = await service.revise_from_position(
            program=program,
            from_week=from_week,
            from_day=from_day,
            user_profile=profile,
            reason=reason,
            available_exercises=available_exercises,
        )
    except Exception as e:
        echo_error(f"Revision failed: {e}")
        ctx.exit(1)

    # Save revised program
    await program_repo.update(revised_program)

    click.echo()
    echo_success("Program revised successfully!")
    click.echo()

    # Show summary of changes
    click.echo(click.style("Revised Program:", bold=True))
    click.echo(revised_program.get_summary())

    click.echo()
    echo_info("Use 'orca-lift export " + str(program_id) + "' to export Liftoscript")
    echo_info("Use 'orca-lift refine " + str(program_id) + "' for further refinements")
