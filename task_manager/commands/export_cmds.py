"""Export / import commands."""

import os
from typing import Optional

import click

from task_manager import config
from task_manager.database import TaskDB
from task_manager.exporter import (
    Exporter,
    ExporterError,
    import_tasks_from_csv,
    import_tasks_from_json,
)
from task_manager.renderers import build_console
from task_manager.validators import ValidationError, validate_export_format, validate_status


def register(cli: click.Group) -> None:
    cli.add_command(export)
    cli.add_command(import_)


@click.command(name="export")
@click.option("--project", "-p", help="Export only tasks from this project")
@click.option(
    "--status", "-s",
    type=click.Choice(list(config.VALID_STATUSES)),
    help="Export only tasks with this status",
)
@click.option("--output", "-o", required=True, help="Output file path")
@click.option(
    "--format", "fmt",
    type=click.Choice(list(config.VALID_EXPORT_FORMATS)),
    default="md",
    help="Export format (md, json, csv)",
)
def export(project: Optional[str], status: Optional[str], output: str, fmt: str):
    """Export tasks to a file (Markdown, JSON, or CSV)."""
    console = build_console()
    try:
        fmt = validate_export_format(fmt)
        validate_status(status)
    except ValidationError as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise click.Abort()

    db = TaskDB()
    exporter = Exporter(db)

    try:
        if project:
            if not db.project_exists(project):
                console.print(f"[red]Error: Project '{project}' not found[/red]")
                raise click.Abort()
            path = exporter.export_project(project, output, fmt=fmt)
            label = f"project '{project}'"
        elif status:
            path = exporter.export_status(status, output, fmt=fmt)
            label = f"{status} tasks"
        else:
            path = exporter.export_all(output, fmt=fmt)
            label = "all tasks"
    except ExporterError as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise click.Abort()

    console.print(f"[green]✓ Exported {label}[/green] to [cyan]{path}[/cyan] ({fmt})")
    try:
        size = os.path.getsize(path)
        console.print(f"  File size: {size} bytes")
    except OSError:
        pass


@click.command(name="import")
@click.option(
    "--input", "input_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Input JSON or CSV file",
)
@click.option(
    "--format", "fmt",
    type=click.Choice(["json", "csv"]),
    default=None,
    help="Force input format (default: detect from extension)",
)
def import_(input_path: str, fmt: Optional[str]):
    """Import tasks from a JSON or CSV file."""
    console = build_console()
    db = TaskDB()

    if fmt is None:
        lower = input_path.lower()
        if lower.endswith(".json"):
            fmt = "json"
        elif lower.endswith(".csv"):
            fmt = "csv"
        else:
            console.print(
                "[red]Error: Unable to detect format. Use --format json or --format csv.[/red]"
            )
            raise click.Abort()

    try:
        if fmt == "json":
            count = import_tasks_from_json(db, input_path)
        else:
            count = import_tasks_from_csv(db, input_path)
    except ExporterError as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise click.Abort()
    except (ValueError, KeyError) as exc:
        console.print(f"[red]Error: Malformed import file — {exc}[/red]")
        raise click.Abort()

    console.print(f"[green]✓ Imported {count} task(s) from[/green] [cyan]{input_path}[/cyan]")
