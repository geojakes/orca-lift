"""CLI entry point for orca-lift."""

import asyncio

import click

from .commands import export, generate, import_data, init, programs, refine
from .commands.equipment import equipment
from .commands.progress import progress
from .commands.revise_cmd import revise
from .commands.serve import serve


@click.group()
@click.version_option(version="0.1.0", prog_name="orca-lift")
def main():
    """orca-lift: AI-Powered Liftosaur Program Generator.

    Generate personalized weightlifting programs using multi-agent AI deliberation.
    Programs are output in Liftoscript format compatible with Liftosaur.

    Example usage:

        # Initialize the project
        orca-lift init

        # Import your fitness data
        orca-lift import manual

        # Generate a program
        orca-lift generate "Build strength, 4 days per week"

        # View and export programs
        orca-lift programs list
        orca-lift export 1 --clipboard
    """
    pass


# Register commands
main.add_command(init)
main.add_command(import_data)
main.add_command(generate)
main.add_command(refine)
main.add_command(export)
main.add_command(programs)
main.add_command(equipment)
main.add_command(progress)
main.add_command(revise)
main.add_command(serve)


def run():
    """Run the CLI (handles async event loop)."""
    main()


if __name__ == "__main__":
    run()
