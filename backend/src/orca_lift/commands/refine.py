"""Refine program command (conversation mode)."""

import click

from ..agents.prompts import format_constraint_checklist, format_equipment_constraints
from ..db import ProgramRepository, get_db_path
from ..db.repositories import EquipmentConfigRepository, ExerciseRepository, UserProfileRepository
from ..services.refine import RefinementService
from .base import async_command, echo_error, echo_info, echo_success, ensure_initialized


@click.command()
@click.argument("program_id", type=int)
@click.pass_context
@async_command
async def refine(ctx, program_id: int):
    """Refine a program through conversation with specialist coaches.

    Enter interactive mode to iteratively modify your program.
    The AI coaches (Strength Coach, Hypertrophy Expert, Periodization
    Specialist, Recovery Analyst) will deliberate on your changes.

    Commands during refinement:
        - Type your change request
        - 'show' - Display current program
        - 'preview' - Show Liftoscript preview
        - 'done' or 'exit' - Save and exit
        - 'cancel' - Exit without saving

    Example:
        orca-lift refine 1
        > Add more tricep work to push day
        > Make Friday a lighter day
        > done
    """
    ensure_initialized(ctx)

    db_path = get_db_path()
    repo = ProgramRepository(db_path)

    # Load program
    program = await repo.get(program_id)
    if not program:
        echo_error(f"Program ID {program_id} not found")
        ctx.exit(1)

    # Load user profile for context
    profile = None
    equipment_constraints = None
    constraint_checklist = ""

    if program.profile_id:
        profile_repo = UserProfileRepository(db_path)
        profile = await profile_repo.get(program.profile_id)

        if profile:
            config_repo = EquipmentConfigRepository(db_path)
            config = await config_repo.get_by_profile(profile.id)

            if config:
                exercise_repo = ExerciseRepository(db_path)
                exercises = await exercise_repo.get_by_equipment(
                    profile.available_equipment
                )
                exercise_names = [ex.name for ex in exercises]

                equipment_constraints = format_equipment_constraints(
                    equipment_types=profile.available_equipment,
                    available_exercises=exercise_names,
                    min_increment=config.min_increment(),
                    weight_unit=config.weight_unit,
                )

            constraint_checklist = format_constraint_checklist(profile)

    echo_info(f"Refining program: {program.name}")
    if profile:
        echo_info(f"Using profile: {profile.name}")
    click.echo()
    click.echo("Enter your refinement requests. Specialist coaches will deliberate on changes.")
    click.echo("Commands:")
    click.echo("  'show'    - Display current program")
    click.echo("  'preview' - Show Liftoscript preview")
    click.echo("  'done'    - Save and exit")
    click.echo("  'cancel'  - Exit without saving")
    click.echo()

    service = RefinementService()
    modified = False

    while True:
        try:
            request = click.prompt(
                click.style(">", fg="green"),
                prompt_suffix=" ",
            )
        except (KeyboardInterrupt, EOFError):
            click.echo()
            if modified:
                if click.confirm("Save changes before exiting?"):
                    await repo.update(program)
                    echo_success("Changes saved")
            break

        request = request.strip()

        if not request:
            continue

        # Handle commands
        if request.lower() == "done" or request.lower() == "exit":
            if modified:
                await repo.update(program)
                echo_success("Changes saved")
            else:
                echo_info("No changes made")
            break

        elif request.lower() == "cancel":
            if modified:
                if click.confirm("Discard changes?"):
                    echo_info("Changes discarded")
                    break
            else:
                break

        elif request.lower() == "show":
            click.echo()
            click.echo(program.get_summary())
            continue

        elif request.lower() == "preview":
            click.echo()
            click.echo("```liftoscript")
            click.echo(program.liftoscript)
            click.echo("```")
            continue

        # Process refinement request
        echo_info("Consulting specialist coaches...")

        try:
            program = await service.refine(
                program=program,
                request=request,
                user_profile=profile,
                equipment_constraints=equipment_constraints,
                constraint_checklist=constraint_checklist,
            )
            modified = True

            click.echo()
            echo_success("Program updated!")
            click.echo()

            # Show what changed (simplified)
            click.echo("Updated program summary:")
            click.echo(program.get_summary())

        except Exception as e:
            echo_error(f"Refinement failed: {e}")
            click.echo("Please try a different request.")
