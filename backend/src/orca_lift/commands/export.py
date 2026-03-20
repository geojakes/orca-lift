"""Export program commands."""

import json

import click

from ..db import ProgramRepository, get_db_path
from ..generators.liftoscript import GeneratorConfig, LiftoscriptGenerator
from .base import async_command, echo_error, echo_info, echo_success, ensure_initialized


@click.command()
@click.argument("program_id", type=int)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["liftoscript", "json"]),
    default="liftoscript",
    help="Output format",
)
@click.option(
    "--clipboard",
    "-c",
    is_flag=True,
    help="Copy to clipboard instead of printing",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Write to file instead of stdout",
)
@click.option(
    "--unit",
    type=click.Choice(["lb", "kg"]),
    default="lb",
    help="Weight unit for Liftoscript",
)
@click.pass_context
@async_command
async def export(
    ctx,
    program_id: int,
    format: str,
    clipboard: bool,
    output: str | None,
    unit: str,
):
    """Export a program to various formats.

    By default, exports as Liftoscript to stdout. You can:
    - Copy directly to clipboard for pasting into Liftosaur
    - Save to a file
    - Export as JSON for programmatic use

    Examples:
        # Print Liftoscript
        orca-lift export 1

        # Copy to clipboard
        orca-lift export 1 --clipboard

        # Save to file
        orca-lift export 1 -o my_program.txt

        # Export as JSON
        orca-lift export 1 --format json

        # Use kg instead of lb
        orca-lift export 1 --unit kg
    """
    ensure_initialized(ctx)

    db_path = get_db_path()
    repo = ProgramRepository(db_path)

    # Load program
    program = await repo.get(program_id)
    if not program:
        echo_error(f"Program ID {program_id} not found")
        ctx.exit(1)

    # Generate output
    if format == "liftoscript":
        if not program.liftoscript or unit != "lb":
            # Regenerate with correct unit
            config = GeneratorConfig(weight_unit=unit)
            generator = LiftoscriptGenerator(config)
            content = generator.generate(program)
        else:
            content = program.liftoscript

    elif format == "json":
        content = json.dumps(program.to_dict(), indent=2)

    # Output
    if clipboard:
        try:
            import pyperclip

            pyperclip.copy(content)
            echo_success("Copied to clipboard!")
            echo_info(
                "Paste into Liftosaur: App > Programs > Import > Paste Liftoscript"
            )
        except ImportError:
            echo_error(
                "pyperclip not installed. Install with: pip install pyperclip"
            )
            ctx.exit(1)

    elif output:
        with open(output, "w") as f:
            f.write(content)
        echo_success(f"Exported to {output}")

    else:
        click.echo(content)
