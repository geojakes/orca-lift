"""Refine program command (conversation mode)."""

import click

from ..db import ProgramRepository, get_db_path
from ..services.refine import RefinementService
from .base import async_command, echo_error, echo_info, echo_success, ensure_initialized


@click.command()
@click.argument("program_id", type=int)
@click.pass_context
@async_command
async def refine(ctx, program_id: int):
    """Refine a program through conversation.

    Enter interactive mode to iteratively modify your program.
    Type your changes in natural language, and the AI will update
    the program accordingly.

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

    echo_info(f"Refining program: {program.name}")
    click.echo()
    click.echo("Enter your refinement requests. Commands:")
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
        echo_info("Processing refinement...")

        try:
            program = await service.refine(program, request)
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
