"""Program management commands."""

import click

from ..db import ProgramRepository, get_db_path
from .base import async_command, echo_error, echo_info, echo_success, ensure_initialized, format_table


@click.group()
@click.pass_context
def programs(ctx):
    """Manage generated programs.

    Commands for listing, viewing, and deleting programs.
    """
    ensure_initialized(ctx)


@programs.command(name="list")
@click.pass_context
@async_command
async def list_programs(ctx):
    """List all generated programs."""
    db_path = get_db_path()
    repo = ProgramRepository(db_path)

    all_programs = await repo.list_all()

    if not all_programs:
        echo_info("No programs found. Generate one with 'orca-lift generate'")
        return

    headers = ["ID", "Name", "Days", "Weeks", "Created"]
    rows = []

    for prog in all_programs:
        created = prog.created_at.strftime("%Y-%m-%d") if prog.created_at else "N/A"
        rows.append([
            str(prog.id),
            prog.name[:30] + "..." if len(prog.name) > 30 else prog.name,
            str(prog.days_per_week),
            str(prog.total_weeks),
            created,
        ])

    click.echo()
    click.echo(format_table(headers, rows))
    click.echo()
    click.echo(f"Total: {len(all_programs)} program(s)")


@programs.command()
@click.argument("program_id", type=int)
@click.option("--liftoscript", "-l", is_flag=True, help="Show Liftoscript code")
@click.option("--deliberation", "-d", is_flag=True, help="Show congregation deliberation log")
@click.pass_context
@async_command
async def show(ctx, program_id: int, liftoscript: bool, deliberation: bool):
    """Show details of a specific program."""
    db_path = get_db_path()
    repo = ProgramRepository(db_path)

    program = await repo.get(program_id)
    if not program:
        echo_error(f"Program ID {program_id} not found")
        ctx.exit(1)

    click.echo()
    click.echo("=" * 60)
    click.echo(f"Program: {program.name} (ID: {program.id})")
    click.echo("=" * 60)
    click.echo()
    click.echo(f"Description: {program.description}")
    click.echo(f"Goals: {program.goals}")
    click.echo(f"Created: {program.created_at}")
    click.echo()

    # Program structure
    click.echo("Structure:")
    click.echo("-" * 40)
    click.echo(program.get_summary())

    if liftoscript:
        click.echo()
        click.echo("Liftoscript:")
        click.echo("-" * 40)
        click.echo("```liftoscript")
        click.echo(program.liftoscript)
        click.echo("```")

    if deliberation and program.congregation_log:
        click.echo()
        click.echo("Congregation Deliberation:")
        click.echo("-" * 40)
        for entry in program.congregation_log:
            phase = entry.get("phase", "unknown")
            agent = entry.get("agent", "unknown")
            click.echo(f"\n[{phase.upper()}] {agent}:")

            output = entry.get("output", {})
            if isinstance(output, dict):
                if "key_principles" in output:
                    click.echo("  Key Principles:")
                    for p in output["key_principles"]:
                        click.echo(f"    - {p}")

                if "exercise_recommendations" in output:
                    click.echo("  Recommendations:")
                    for ex in output["exercise_recommendations"][:5]:
                        click.echo(f"    - {ex.get('exercise', 'N/A')}: {ex.get('rationale', '')[:50]}...")

                if "concerns" in output:
                    click.echo("  Concerns:")
                    for c in output["concerns"]:
                        click.echo(f"    - {c}")
            else:
                click.echo(f"  {str(output)[:200]}...")


@programs.command()
@click.argument("program_id", type=int)
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
@click.pass_context
@async_command
async def delete(ctx, program_id: int, force: bool):
    """Delete a program."""
    db_path = get_db_path()
    repo = ProgramRepository(db_path)

    program = await repo.get(program_id)
    if not program:
        echo_error(f"Program ID {program_id} not found")
        ctx.exit(1)

    if not force:
        click.echo(f"Program: {program.name}")
        if not click.confirm("Are you sure you want to delete this program?"):
            echo_info("Cancelled")
            return

    await repo.delete(program_id)
    echo_success(f"Program {program_id} deleted")
