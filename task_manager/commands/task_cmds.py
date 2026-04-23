"""CRUD commands for individual tasks: add, list, show, update, done, delete, search."""

from typing import Optional

import click

from task_manager import config
from task_manager.database import TaskDB
from task_manager.models import Task
from task_manager.renderers import (
    build_console,
    render_task_panel,
    render_task_table,
    summarize_status_counts,
)
from task_manager.validators import (
    ValidationError,
    validate_due_date,
    validate_order,
    validate_pagination,
    validate_priority,
    validate_sort_key,
    validate_status,
    validate_title,
)


def _db() -> TaskDB:
    return TaskDB()


def register(cli: click.Group) -> None:
    cli.add_command(add)
    cli.add_command(list_)
    cli.add_command(show)
    cli.add_command(done)
    cli.add_command(update)
    cli.add_command(delete)
    cli.add_command(search)


@click.command(name="add")
@click.argument("title")
@click.option("--project", "-p", default=config.DEFAULT_PROJECT, help="Project name")
@click.option(
    "--priority",
    type=click.Choice(list(config.VALID_PRIORITIES)),
    default=config.DEFAULT_PRIORITY,
    help="Task priority",
)
@click.option("--due", help="Due date (YYYY-MM-DD format)")
@click.option("--description", "-d", default="", help="Task description")
def add(title: str, project: str, priority: str, due: Optional[str], description: str):
    """Add a new task."""
    console = build_console()
    try:
        title = validate_title(title)
        validate_due_date(due)
        task = Task(
            title=title,
            project=project,
            priority=priority,
            due_date=due,
            description=description,
        )
        task_id = _db().add_task(task)
    except (ValidationError, ValueError) as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise click.Abort()

    console.print(f"[green]✓ Task created[/green] with ID: [cyan]{task_id}[/cyan]")
    console.print(f"  Title: [bold]{title}[/bold]")
    console.print(f"  Project: [yellow]{project}[/yellow]")
    console.print(f"  Priority: {task.priority_emoji} {priority.capitalize()}")
    if due:
        console.print(f"  Due: [magenta]{due}[/magenta]")


@click.command(name="list")
@click.option("--project", "-p", help="Filter by project")
@click.option(
    "--status",
    "-s",
    type=click.Choice(list(config.VALID_STATUSES)),
    help="Filter by status",
)
@click.option(
    "--sort",
    type=click.Choice(list(config.SORT_COLUMN_MAP.keys())),
    default="created",
    help="Sort by",
)
@click.option(
    "--order",
    type=click.Choice(["asc", "desc"]),
    default="desc",
    help="Sort direction",
)
@click.option("--limit", type=int, default=0, help="Maximum rows (0 = no limit)")
@click.option("--offset", type=int, default=0, help="Rows to skip")
def list_(
    project: Optional[str],
    status: Optional[str],
    sort: str,
    order: str,
    limit: int,
    offset: int,
):
    """List tasks with optional filters, sort, and pagination."""
    console = build_console()
    try:
        sort_column = validate_sort_key(sort)
        direction = validate_order(order)
        validate_status(status)
        limit, offset = validate_pagination(limit, offset)
    except ValidationError as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise click.Abort()

    tasks = _db().list_tasks(
        project=project,
        status=status,
        order_by=sort_column,
        direction=direction,
        limit=limit,
        offset=offset,
    )

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    console.print(render_task_table(tasks))
    console.print(f"\n[dim]{summarize_status_counts(tasks)}[/dim]")


@click.command(name="show")
@click.argument("task_id", type=int)
def show(task_id: int):
    """Show detailed information about a task."""
    console = build_console()
    task = _db().get_task(task_id)
    if not task:
        console.print(f"[red]Error: Task with ID {task_id} not found[/red]")
        raise click.Abort()
    console.print(render_task_panel(task))


@click.command(name="done")
@click.argument("task_id", type=int)
def done(task_id: int):
    """Mark a task as completed."""
    console = build_console()
    db = _db()
    task = db.get_task(task_id)
    if not task:
        console.print(f"[red]Error: Task with ID {task_id} not found[/red]")
        raise click.Abort()
    db.update_task(task_id, status="done")
    console.print(f"[green]✓ Task #{task_id} marked as done[/green]")
    console.print(f"  {task.title}")


@click.command(name="update")
@click.argument("task_id", type=int)
@click.option(
    "--status",
    "-s",
    type=click.Choice(list(config.VALID_STATUSES)),
    help="New status",
)
@click.option(
    "--priority",
    type=click.Choice(list(config.VALID_PRIORITIES)),
    help="New priority",
)
@click.option("--title", help="New title")
@click.option("--project", "-p", help="New project")
@click.option("--due", help="New due date (YYYY-MM-DD)")
@click.option("--description", "-d", help="New description")
def update(
    task_id: int,
    status: Optional[str],
    priority: Optional[str],
    title: Optional[str],
    project: Optional[str],
    due: Optional[str],
    description: Optional[str],
):
    """Update task fields."""
    console = build_console()
    db = _db()
    task = db.get_task(task_id)
    if not task:
        console.print(f"[red]Error: Task with ID {task_id} not found[/red]")
        raise click.Abort()

    try:
        validate_due_date(due)
        if title is not None:
            title = validate_title(title)
    except ValidationError as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise click.Abort()

    updates = {}
    if status:
        updates["status"] = status
    if priority:
        updates["priority"] = priority
    if title:
        updates["title"] = title
    if project:
        updates["project"] = project
    if due:
        updates["due_date"] = due
    if description is not None:
        updates["description"] = description

    if not updates:
        console.print("[yellow]No updates provided[/yellow]")
        return

    db.update_task(task_id, **updates)
    console.print(f"[green]✓ Task #{task_id} updated[/green]")
    for key, value in updates.items():
        console.print(f"  {key}: {value}")


@click.command(name="delete")
@click.argument("task_id", type=int)
@click.option(
    "--yes", "assume_yes", is_flag=True, default=False,
    help="Skip confirmation prompt (non-interactive mode).",
)
def delete(task_id: int, assume_yes: bool):
    """Delete a task."""
    console = build_console()
    db = _db()
    task = db.get_task(task_id)
    if not task:
        console.print(f"[red]Error: Task with ID {task_id} not found[/red]")
        raise click.Abort()

    if not assume_yes:
        if not click.confirm(f"Delete task #{task_id} '{task.title}'?"):
            console.print("[yellow]Aborted[/yellow]")
            return

    db.delete_task(task_id)
    console.print(f"[green]✓ Task #{task_id} deleted[/green]")
    console.print(f"  {task.title}")


@click.command(name="search")
@click.argument("query")
def search(query: str):
    """Search tasks by title or description."""
    console = build_console()
    tasks = _db().search_tasks(query)

    if not tasks:
        console.print(f"[yellow]No tasks found matching '{query}'[/yellow]")
        return

    console.print(render_task_table(tasks, title=f"Search Results for '{query}'"))
    console.print(f"\n[dim]Found {len(tasks)} task(s)[/dim]")
