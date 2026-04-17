"""Project-level commands: projects, stats, version."""

import click

from task_manager import __version__
from task_manager.database import TaskDB
from task_manager.renderers import (
    build_console,
    render_projects_table,
    render_stats_panel,
)


def register(cli: click.Group) -> None:
    cli.add_command(projects)
    cli.add_command(stats)
    cli.add_command(version)


@click.command(name="projects")
def projects():
    """List all projects with task counts and completion rates."""
    console = build_console()
    projects_list = TaskDB().list_projects()
    if not projects_list:
        console.print("[yellow]No projects found. Create a task first![/yellow]")
        return
    console.print(render_projects_table(projects_list))


@click.command(name="stats")
def stats():
    """Show general statistics across all tasks."""
    console = build_console()
    db = TaskDB()
    tasks = db.list_tasks()
    projects_list = db.list_projects()
    console.print(render_stats_panel(tasks, projects_list))


@click.command(name="version")
def version():
    """Show the installed version."""
    console = build_console()
    console.print(f"[cyan]cli-task-manager[/cyan] [bold]{__version__}[/bold]")
