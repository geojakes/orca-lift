"""Import fitness data commands."""

import click

from ..clients.google_fit import GoogleFitClient
from ..clients.health_connect import HealthConnectClient
from ..clients.manual import ManualInputClient
from ..db import FitnessDataRepository, UserProfileRepository, get_db_path
from .base import async_command, echo_error, echo_info, echo_success, ensure_initialized


@click.group(name="import")
@click.pass_context
def import_data(ctx):
    """Import fitness data from various sources.

    Available sources:
    - manual: Interactive questionnaire
    - health-connect: Health Connect SQLite backup (Android 14+)
    - google-fit: Google Fit Takeout export (legacy)
    """
    ensure_initialized(ctx)


@import_data.command()
@click.pass_context
@async_command
async def manual(ctx):
    """Collect fitness profile via interactive questionnaire.

    This will guide you through questions about your:
    - Training experience level
    - Fitness goals
    - Available equipment
    - Current strength levels
    - Any limitations or injuries
    """
    client = ManualInputClient()
    profile = await client.collect_profile()

    # Save to database
    db_path = get_db_path()
    repo = UserProfileRepository(db_path)
    profile_id = await repo.create(profile)

    echo_success(f"Profile saved with ID: {profile_id}")
    click.echo()
    click.echo("Profile Summary:")
    click.echo(profile.get_summary())


@import_data.command(name="health-connect")
@click.argument("path", type=click.Path(exists=True))
@click.option("--profile-id", "-p", type=int, help="Link to existing profile ID")
@click.pass_context
@async_command
async def health_connect(ctx, path: str, profile_id: int | None):
    """Import data from Health Connect backup.

    PATH should be the ZIP file exported from Health Connect
    (Settings > Health Connect > Manage data > Export).

    Example:
        orca-lift import health-connect "Health Connect.zip"
    """
    echo_info(f"Parsing Health Connect backup: {path}")

    client = HealthConnectClient()

    try:
        data = await client.parse(path)
    except Exception as e:
        echo_error(f"Failed to parse Health Connect data: {e}")
        ctx.exit(1)

    # Display summary
    click.echo()
    click.echo(client.get_workout_summary(data))

    # Save to database
    db_path = get_db_path()
    repo = FitnessDataRepository(db_path)

    # Store workouts
    for workout in data.workouts:
        await repo.create(
            source="health_connect",
            data_type="workout",
            data={
                "session_type": workout.session_type,
                "exercises": [
                    {
                        "name": ex.name,
                        "sets": [
                            {"reps": s.reps, "weight": s.weight}
                            for s in ex.sets
                        ],
                    }
                    for ex in workout.exercises
                ],
            },
            profile_id=profile_id,
            recorded_at=workout.start_time,
        )

    # Store body metrics
    for metric in data.body_metrics:
        await repo.create(
            source="health_connect",
            data_type="body_metric",
            data={
                "type": metric.metric_type,
                "value": metric.value,
                "unit": metric.unit,
            },
            profile_id=profile_id,
            recorded_at=metric.recorded_at,
        )

    echo_success(
        f"Imported {len(data.workouts)} workouts and {len(data.body_metrics)} body metrics"
    )


@import_data.command(name="google-fit")
@click.argument("path", type=click.Path(exists=True))
@click.option("--profile-id", "-p", type=int, help="Link to existing profile ID")
@click.pass_context
@async_command
async def google_fit(ctx, path: str, profile_id: int | None):
    """Import data from Google Fit Takeout export (legacy).

    PATH should be the ZIP file from Google Takeout containing
    your Fit data (https://takeout.google.com).

    Note: Google Fit API is being deprecated. Health Connect is
    the recommended source for new exports.

    Example:
        orca-lift import google-fit takeout-20240101.zip
    """
    echo_info(f"Parsing Google Fit Takeout: {path}")

    client = GoogleFitClient()

    try:
        data = await client.parse(path)
    except Exception as e:
        echo_error(f"Failed to parse Google Fit data: {e}")
        ctx.exit(1)

    # Display summary
    click.echo()
    click.echo(client.get_workout_summary(data))

    # Save to database
    db_path = get_db_path()
    repo = FitnessDataRepository(db_path)

    # Store workouts (Google Fit has weight data!)
    for workout in data.workouts:
        await repo.create(
            source="google_fit",
            data_type="workout",
            data={
                "session_type": workout.session_type,
                "exercises": [
                    {
                        "name": ex.name,
                        "sets": [
                            {
                                "reps": s.reps,
                                "weight": s.weight,  # Google Fit has this!
                                "duration": s.duration_seconds,
                            }
                            for s in ex.sets
                        ],
                    }
                    for ex in workout.exercises
                ],
            },
            profile_id=profile_id,
            recorded_at=workout.start_time,
        )

    # Store body metrics
    for metric in data.body_metrics:
        await repo.create(
            source="google_fit",
            data_type="body_metric",
            data={
                "type": metric.metric_type,
                "value": metric.value,
                "unit": metric.unit,
            },
            profile_id=profile_id,
            recorded_at=metric.recorded_at,
        )

    echo_success(
        f"Imported {len(data.workouts)} workouts and {len(data.body_metrics)} body metrics"
    )
