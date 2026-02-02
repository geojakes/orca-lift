"""Initialize project command."""

import click

from ..db import get_db_path, init_db, seed_exercises
from ..data.exercise_loader import seed_exercises_from_json, get_exercises_json_path
from .base import async_command, echo_info, echo_success, get_data_dir


@click.command()
@async_command
async def init():
    """Initialize the orca-lift project and database.

    This creates the data directory and initializes the SQLite database
    with the required schema and exercise library.
    """
    data_dir = get_data_dir()
    db_path = get_db_path(data_dir)

    echo_info(f"Initializing orca-lift in {data_dir}")

    # Create data directory
    data_dir.mkdir(parents=True, exist_ok=True)

    # Initialize database
    await init_db(db_path)
    echo_success("Database initialized")

    # Seed exercises from JSON (or fall back to COMMON_EXERCISES)
    json_path = get_exercises_json_path()
    if json_path.exists():
        count = await seed_exercises_from_json(db_path)
        echo_success(f"Exercise library populated ({count} exercises from Liftosaur library)")
    else:
        await seed_exercises(db_path)
        echo_success("Exercise library populated (basic exercises)")

    click.echo()
    click.echo("orca-lift is ready to use!")
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Import your fitness data:")
    click.echo("     orca-lift import manual         # Interactive questionnaire")
    click.echo("     orca-lift import health-connect <file.zip>")
    click.echo("     orca-lift import google-fit <takeout.zip>")
    click.echo()
    click.echo("  2. Generate a program:")
    click.echo('     orca-lift generate "Build strength, 4 days per week"')
