"""CLI entry point for orcafit."""

import asyncio

import click

from .commands import export, generate, import_data, init, programs, refine
from .commands.equipment import equipment
from .commands.progress import progress
from .commands.revise_cmd import revise
from .commands.serve import serve


@click.group()
@click.version_option(version="0.1.0", prog_name="orcafit")
def main():
    """orcafit: AI-Powered Fitness Program Generator & Workout Tracker.

    Generate personalized training programs using multi-agent AI deliberation.
    Programs are output in Liftoscript format compatible with Liftosaur or native OrcaFit JSON format.

    Example usage:

        # Initialize the project
        orcafit init

        # Import your fitness data
        orcafit import manual

        # Generate a program
        orcafit generate "Build strength, 4 days per week"

        # View and export programs
        orcafit programs list
        orcafit export 1 --clipboard
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
