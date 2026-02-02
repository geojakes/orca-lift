"""Shared CLI utilities."""

import asyncio
from functools import wraps
from pathlib import Path

import click

from ..db import get_db_path


def async_command(f):
    """Decorator to run async Click commands."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


def get_data_dir() -> Path:
    """Get the data directory path."""
    return Path(__file__).parent.parent.parent.parent / "data"


def ensure_initialized(ctx: click.Context) -> None:
    """Ensure the database is initialized."""
    db_path = get_db_path()
    if not db_path.exists():
        click.echo(
            click.style("Error: ", fg="red")
            + "Project not initialized. Run 'orca-lift init' first."
        )
        ctx.exit(1)


def echo_success(message: str) -> None:
    """Print a success message."""
    click.echo(click.style("[OK] ", fg="green") + message)


def echo_error(message: str) -> None:
    """Print an error message."""
    click.echo(click.style("[ERROR] ", fg="red") + message)


def echo_info(message: str) -> None:
    """Print an info message."""
    click.echo(click.style("[INFO] ", fg="blue") + message)


def echo_warning(message: str) -> None:
    """Print a warning message."""
    click.echo(click.style("[WARN] ", fg="yellow") + message)


def format_table(headers: list[str], rows: list[list[str]], padding: int = 2) -> str:
    """Format data as a simple table."""
    if not rows:
        return ""

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Build table
    lines = []

    # Header
    header_line = ""
    for i, h in enumerate(headers):
        header_line += h.ljust(widths[i] + padding)
    lines.append(header_line)

    # Separator
    sep_line = ""
    for w in widths:
        sep_line += "-" * w + " " * padding
    lines.append(sep_line)

    # Rows
    for row in rows:
        row_line = ""
        for i, cell in enumerate(row):
            row_line += str(cell).ljust(widths[i] + padding)
        lines.append(row_line)

    return "\n".join(lines)
