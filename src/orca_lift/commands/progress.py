"""Progress tracking commands."""

from datetime import datetime

import click

from ..db.repositories import ProgramProgressRepository, ProgramRepository
from ..models.progress import ProgramProgress, ProgramStatus
from .base import (
    async_command,
    echo_error,
    echo_info,
    echo_success,
    echo_warning,
    ensure_initialized,
    format_table,
)


@click.group()
def progress():
    """Track program progress.

    Mark workouts as complete, view current position, and sync with
    Health Connect data.
    """
    pass


@progress.command("status")
@click.argument("program_id", type=int)
@click.pass_context
@async_command
async def status(ctx: click.Context, program_id: int):
    """Show progress status for a program.

    Displays current week/day, overall progress percentage, and
    workout history.
    """
    ensure_initialized(ctx)

    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        echo_error(f"Program {program_id} not found.")
        ctx.exit(1)

    progress_repo = ProgramProgressRepository()
    prog = await progress_repo.get_by_program(program_id)

    click.echo()
    click.echo(click.style(f"Program: {program.name}", bold=True))
    click.echo("=" * 50)

    if not prog:
        echo_info("Program not started yet.")
        click.echo("Run 'orca-lift progress start " + str(program_id) + "' to begin.")
        return

    # Calculate progress
    total_weeks = len(program.weeks)
    total_days = sum(len(week.days) for week in program.weeks)
    current_week_days = len(program.weeks[prog.current_week - 1].days) if program.weeks else 0

    completed_days = 0
    for i, week in enumerate(program.weeks):
        if i < prog.current_week - 1:
            completed_days += len(week.days)
        elif i == prog.current_week - 1:
            completed_days += prog.current_day - 1

    progress_pct = (completed_days / total_days * 100) if total_days > 0 else 0

    # Status display
    click.echo()
    click.echo(f"Status: {prog.get_status_display()}")
    click.echo(f"Position: {prog.get_position_display()}")
    click.echo(f"Progress: {progress_pct:.1f}% ({completed_days}/{total_days} workouts)")

    if prog.started_at:
        click.echo(f"Started: {prog.started_at.strftime('%Y-%m-%d')}")
    if prog.last_workout_at:
        click.echo(f"Last workout: {prog.last_workout_at.strftime('%Y-%m-%d %H:%M')}")

    # Show current day details
    click.echo()
    click.echo(click.style("Next Workout:", bold=True))
    if prog.current_week <= total_weeks:
        week = program.weeks[prog.current_week - 1]
        if prog.current_day <= len(week.days):
            day = week.days[prog.current_day - 1]
            click.echo(f"  Week {prog.current_week}, Day {prog.current_day}: {day.name}")
            if day.focus:
                click.echo(f"  Focus: {day.focus}")
            click.echo(f"  Exercises: {len(day.exercises)}")
        else:
            echo_info("Week complete! Advance to next week.")
    else:
        echo_success("Program complete!")

    # Show week overview
    click.echo()
    click.echo(click.style("Week Overview:", bold=True))
    for i, week in enumerate(program.weeks):
        week_num = i + 1
        is_current = week_num == prog.current_week
        prefix = ">" if is_current else " "
        status_icon = ""

        if week_num < prog.current_week:
            status_icon = click.style(" [done]", fg="green")
        elif is_current:
            status_icon = click.style(" [in progress]", fg="yellow")

        deload = " (Deload)" if week.is_deload else ""
        click.echo(f"  {prefix} Week {week_num}{deload}: {len(week.days)} days{status_icon}")


@progress.command("start")
@click.argument("program_id", type=int)
@click.pass_context
@async_command
async def start(ctx: click.Context, program_id: int):
    """Start a program (set to week 1, day 1)."""
    ensure_initialized(ctx)

    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        echo_error(f"Program {program_id} not found.")
        ctx.exit(1)

    progress_repo = ProgramProgressRepository()
    existing = await progress_repo.get_by_program(program_id)

    if existing and existing.status == ProgramStatus.ACTIVE:
        echo_warning("Program already in progress.")
        if not click.confirm("Reset to week 1, day 1?"):
            return

    prog = ProgramProgress(program_id=program_id)
    prog.start()

    await progress_repo.upsert(prog)

    echo_success(f"Started program: {program.name}")
    click.echo(f"Position: Week 1, Day 1")

    # Show first day
    if program.weeks:
        day = program.weeks[0].days[0] if program.weeks[0].days else None
        if day:
            click.echo(f"First workout: {day.name}")


@progress.command("complete")
@click.argument("program_id", type=int)
@click.pass_context
@async_command
async def complete(ctx: click.Context, program_id: int):
    """Mark current workout day as complete and advance."""
    ensure_initialized(ctx)

    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        echo_error(f"Program {program_id} not found.")
        ctx.exit(1)

    progress_repo = ProgramProgressRepository()
    prog = await progress_repo.get_by_program(program_id)

    if not prog:
        echo_error("Program not started. Run 'orca-lift progress start' first.")
        ctx.exit(1)

    if prog.status == ProgramStatus.COMPLETED:
        echo_info("Program already completed!")
        return

    # Get current workout info before advancing
    current_week = prog.current_week
    current_day = prog.current_day
    week = program.weeks[current_week - 1]
    day = week.days[current_day - 1] if current_day <= len(week.days) else None

    # Calculate total days per week (may vary)
    total_weeks = len(program.weeks)

    # Advance
    days_this_week = len(week.days)
    advanced = prog.advance(days_this_week, total_weeks)

    await progress_repo.update(prog)

    if day:
        echo_success(f"Completed: Week {current_week}, Day {current_day} - {day.name}")

    if not advanced:
        click.echo()
        echo_success("Congratulations! Program complete!")
        click.echo("Consider starting a new program or revisiting this one.")
    else:
        click.echo(f"Next workout: {prog.get_position_display()}")
        if prog.current_week <= len(program.weeks):
            next_week = program.weeks[prog.current_week - 1]
            if prog.current_day <= len(next_week.days):
                next_day = next_week.days[prog.current_day - 1]
                click.echo(f"  {next_day.name}")


@progress.command("set")
@click.argument("program_id", type=int)
@click.option("-w", "--week", type=int, required=True, help="Week number")
@click.option("-d", "--day", type=int, required=True, help="Day number")
@click.pass_context
@async_command
async def set_position(
    ctx: click.Context,
    program_id: int,
    week: int,
    day: int,
):
    """Set position to a specific week and day.

    Useful for jumping ahead, going back, or syncing with actual progress.
    """
    ensure_initialized(ctx)

    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        echo_error(f"Program {program_id} not found.")
        ctx.exit(1)

    # Validate position
    if week < 1 or week > len(program.weeks):
        echo_error(f"Invalid week {week}. Program has {len(program.weeks)} weeks.")
        ctx.exit(1)

    week_obj = program.weeks[week - 1]
    if day < 1 or day > len(week_obj.days):
        echo_error(f"Invalid day {day}. Week {week} has {len(week_obj.days)} days.")
        ctx.exit(1)

    progress_repo = ProgramProgressRepository()
    prog = await progress_repo.get_by_program(program_id)

    if not prog:
        prog = ProgramProgress(program_id=program_id)
        prog.start()

    prog.set_position(week, day)
    prog.status = ProgramStatus.ACTIVE

    await progress_repo.upsert(prog)

    day_obj = week_obj.days[day - 1]
    echo_success(f"Position set to Week {week}, Day {day}")
    click.echo(f"Current workout: {day_obj.name}")


@progress.command("pause")
@click.argument("program_id", type=int)
@click.pass_context
@async_command
async def pause(ctx: click.Context, program_id: int):
    """Pause program progress."""
    ensure_initialized(ctx)

    progress_repo = ProgramProgressRepository()
    prog = await progress_repo.get_by_program(program_id)

    if not prog:
        echo_error("Program not started.")
        ctx.exit(1)

    prog.pause()
    await progress_repo.update(prog)

    echo_success(f"Program paused at {prog.get_position_display()}")


@progress.command("resume")
@click.argument("program_id", type=int)
@click.pass_context
@async_command
async def resume(ctx: click.Context, program_id: int):
    """Resume a paused program."""
    ensure_initialized(ctx)

    progress_repo = ProgramProgressRepository()
    prog = await progress_repo.get_by_program(program_id)

    if not prog:
        echo_error("Program not started.")
        ctx.exit(1)

    prog.resume()
    await progress_repo.update(prog)

    echo_success(f"Program resumed at {prog.get_position_display()}")


@progress.command("sync")
@click.argument("program_id", type=int)
@click.argument("backup_path", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Show what would be synced without making changes")
@click.pass_context
@async_command
async def sync(
    ctx: click.Context,
    program_id: int,
    backup_path: str,
    dry_run: bool,
):
    """Sync progress from Health Connect backup.

    Analyzes workout sessions from a Health Connect SQLite backup to
    automatically detect completed workouts and advance program position.

    The backup should be a .zip file from Android's Health Connect export
    or the raw SQLite database file.
    """
    ensure_initialized(ctx)

    from pathlib import Path
    from ..services.progress_sync import ProgressSyncService

    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        echo_error(f"Program {program_id} not found.")
        ctx.exit(1)

    progress_repo = ProgramProgressRepository()
    prog = await progress_repo.get_by_program(program_id)

    if not prog:
        echo_error("Program not started. Run 'orca-lift progress start' first.")
        ctx.exit(1)

    sync_service = ProgressSyncService()

    try:
        completed = await sync_service.sync_from_health_connect(
            program=program,
            progress=prog,
            health_connect_backup=Path(backup_path),
        )
    except Exception as e:
        echo_error(f"Sync failed: {e}")
        ctx.exit(1)

    if not completed:
        echo_info("No completed workouts detected.")
        return

    click.echo()
    click.echo(click.style("Detected Completed Workouts:", bold=True))
    for workout in completed:
        match_pct = workout.match_percentage * 100
        click.echo(
            f"  Week {workout.week}, Day {workout.day}: "
            f"{len(workout.exercises_matched)} exercises matched ({match_pct:.0f}%)"
        )

    if dry_run:
        echo_info("Dry run - no changes made.")
        return

    # Update progress to the furthest completed point
    if completed:
        last = completed[-1]
        prog.set_position(last.week, last.day)

        # Try to advance past the completed day
        total_weeks = len(program.weeks)
        days_this_week = len(program.weeks[last.week - 1].days)
        prog.advance(days_this_week, total_weeks)

        await progress_repo.update(prog)

        echo_success(f"Progress updated to {prog.get_position_display()}")


@progress.command("list")
@click.pass_context
@async_command
async def list_active(ctx: click.Context):
    """List all active program progress."""
    ensure_initialized(ctx)

    progress_repo = ProgramProgressRepository()
    program_repo = ProgramRepository()

    active = await progress_repo.list_active()

    if not active:
        echo_info("No active programs.")
        return

    rows = []
    for prog in active:
        program = await program_repo.get(prog.program_id)
        if program:
            rows.append([
                str(prog.program_id),
                program.name[:30],
                prog.get_position_display(),
                prog.last_workout_at.strftime("%Y-%m-%d") if prog.last_workout_at else "-",
            ])

    click.echo()
    table = format_table(
        headers=["ID", "Program", "Position", "Last Workout"],
        rows=rows,
    )
    click.echo(table)
