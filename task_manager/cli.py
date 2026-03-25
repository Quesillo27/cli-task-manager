"""Command-line interface for Task Manager."""

from datetime import datetime
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from task_manager.database import TaskDB
from task_manager.models import Task
from task_manager.exporter import MarkdownExporter


console = Console()


def get_db() -> TaskDB:
    """Get or create database instance."""
    return TaskDB()


@click.group()
def cli():
    """CLI Task Manager - Manage your tasks from the command line."""
    pass


@cli.command()
@click.argument("title")
@click.option("--project", "-p", default="General", help="Project name")
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), default="medium", help="Task priority")
@click.option("--due", help="Due date (YYYY-MM-DD format)")
@click.option("--description", "-d", default="", help="Task description")
def add(title: str, project: str, priority: str, due: Optional[str], description: str):
    """Add a new task.

    Example: task add "Buy groceries" --project "Home" --priority high --due "2026-04-01"
    """
    try:
        # Validate due date format if provided
        if due:
            try:
                datetime.strptime(due, "%Y-%m-%d")
            except ValueError:
                console.print("[red]Error: Due date must be in YYYY-MM-DD format[/red]")
                raise click.Abort()

        task = Task(
            title=title,
            project=project,
            priority=priority,
            due_date=due,
            description=description
        )

        db = get_db()
        task_id = db.add_task(task)

        console.print(f"[green]✓ Task created[/green] with ID: [cyan]{task_id}[/cyan]")
        console.print(f"  Title: [bold]{title}[/bold]")
        console.print(f"  Project: [yellow]{project}[/yellow]")
        console.print(f"  Priority: {task.priority_emoji} {priority.capitalize()}")

        if due:
            console.print(f"  Due: [magenta]{due}[/magenta]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.option("--project", "-p", help="Filter by project")
@click.option("--status", "-s", type=click.Choice(["pending", "in_progress", "done"]), help="Filter by status")
@click.option("--sort", type=click.Choice(["created", "due_date", "priority"]), default="created", help="Sort by")
def list(project: Optional[str], status: Optional[str], sort: str):
    """List all tasks with optional filters.

    Examples:
        task list
        task list --project "Work"
        task list --status pending
        task list --status done
    """
    db = get_db()

    # Determine sort column
    sort_map = {
        "created": "created_at",
        "due_date": "due_date",
        "priority": "priority"
    }

    tasks = db.list_tasks(project=project, status=status, order_by=sort_map.get(sort, "created_at"))

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    # Create table
    table = Table(title="Tasks", box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Title", style="white", no_wrap=False)
    table.add_column("Project", style="yellow")
    table.add_column("Priority", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Due Date", style="magenta")
    table.add_column("Created", style="dim")

    for task in tasks:
        created_date = ""
        if task.created_at:
            created_date = datetime.fromisoformat(task.created_at).strftime("%Y-%m-%d")

        due_date_str = task.due_date if task.due_date else ""
        if task.is_overdue:
            due_date_str = f"[red]{due_date_str} ⚠️[/red]"

        table.add_row(
            str(task.id),
            task.title,
            task.project,
            task.priority_emoji,
            task.status_emoji,
            due_date_str,
            created_date
        )

    console.print(table)

    # Print summary
    total = len(tasks)
    pending = sum(1 for t in tasks if t.status == "pending")
    in_progress = sum(1 for t in tasks if t.status == "in_progress")
    done = sum(1 for t in tasks if t.status == "done")

    console.print(f"\n[dim]Total: {total} | Pending: {pending} | In Progress: {in_progress} | Done: {done}[/dim]")


@cli.command()
@click.argument("task_id", type=int)
def show(task_id: int):
    """Show detailed information about a task.

    Example: task show 1
    """
    db = get_db()
    task = db.get_task(task_id)

    if not task:
        console.print(f"[red]Error: Task with ID {task_id} not found[/red]")
        raise click.Abort()

    # Create panel with task details
    content = f"""[bold cyan]{task.title}[/bold cyan]

[yellow]Project:[/yellow] {task.project}
[yellow]Priority:[/yellow] {task.priority_emoji} {task.priority.capitalize()}
[yellow]Status:[/yellow] {task.status_emoji} {task.status.capitalize()}

[yellow]ID:[/yellow] {task.id}
[yellow]Created:[/yellow] {task.created_at}"""

    if task.due_date:
        overdue_marker = " [red](OVERDUE)[/red]" if task.is_overdue else ""
        content += f"\n[yellow]Due:[/yellow] {task.due_date}{overdue_marker}"

    if task.description:
        content += f"\n\n[yellow]Description:[/yellow]\n{task.description}"

    if task.completed_at:
        content += f"\n[yellow]Completed:[/yellow] {task.completed_at}"

    panel = Panel(content, title=f"Task #{task.id}", expand=False, border_style="cyan")
    console.print(panel)


@cli.command()
@click.argument("task_id", type=int)
def done(task_id: int):
    """Mark a task as completed.

    Example: task done 1
    """
    db = get_db()
    task = db.get_task(task_id)

    if not task:
        console.print(f"[red]Error: Task with ID {task_id} not found[/red]")
        raise click.Abort()

    db.update_task(task_id, status="done")
    console.print(f"[green]✓ Task #{task_id} marked as done[/green]")
    console.print(f"  {task.title}")


@cli.command()
@click.argument("task_id", type=int)
@click.option("--status", "-s", type=click.Choice(["pending", "in_progress", "done"]), help="New status")
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), help="New priority")
@click.option("--title", help="New title")
@click.option("--project", "-p", help="New project")
@click.option("--due", help="New due date (YYYY-MM-DD)")
@click.option("--description", "-d", help="New description")
def update(task_id: int, status: Optional[str], priority: Optional[str], title: Optional[str],
           project: Optional[str], due: Optional[str], description: Optional[str]):
    """Update task details.

    Example: task update 1 --status in_progress --priority high
    """
    db = get_db()
    task = db.get_task(task_id)

    if not task:
        console.print(f"[red]Error: Task with ID {task_id} not found[/red]")
        raise click.Abort()

    # Validate due date if provided
    if due:
        try:
            datetime.strptime(due, "%Y-%m-%d")
        except ValueError:
            console.print("[red]Error: Due date must be in YYYY-MM-DD format[/red]")
            raise click.Abort()

    # Build update dict with only provided values
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
    if description:
        updates["description"] = description

    if not updates:
        console.print("[yellow]No updates provided[/yellow]")
        return

    try:
        db.update_task(task_id, **updates)
        console.print(f"[green]✓ Task #{task_id} updated[/green]")

        # Show what was updated
        for key, value in updates.items():
            console.print(f"  {key}: {value}")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.argument("task_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
def delete(task_id: int):
    """Delete a task.

    Example: task delete 1
    """
    db = get_db()
    task = db.get_task(task_id)

    if not task:
        console.print(f"[red]Error: Task with ID {task_id} not found[/red]")
        raise click.Abort()

    db.delete_task(task_id)
    console.print(f"[green]✓ Task #{task_id} deleted[/green]")
    console.print(f"  {task.title}")


@cli.command()
@click.argument("query")
def search(query: str):
    """Search tasks by title or description.

    Example: task search "grocery"
    """
    db = get_db()
    tasks = db.search_tasks(query)

    if not tasks:
        console.print(f"[yellow]No tasks found matching '{query}'[/yellow]")
        return

    # Create table
    table = Table(title=f"Search Results for '{query}'", box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Title", style="white", no_wrap=False)
    table.add_column("Project", style="yellow")
    table.add_column("Status", justify="center")

    for task in tasks:
        table.add_row(
            str(task.id),
            task.title,
            task.project,
            task.status_emoji
        )

    console.print(table)
    console.print(f"\n[dim]Found {len(tasks)} task(s)[/dim]")


@cli.command()
def projects():
    """List all projects with task counts.

    Example: task projects
    """
    db = get_db()
    projects_list = db.list_projects()

    if not projects_list:
        console.print("[yellow]No projects found. Create a task first![/yellow]")
        return

    # Create table
    table = Table(title="Projects", box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Project", style="yellow")
    table.add_column("Total", justify="center")
    table.add_column("Pending", justify="center", style="dim")
    table.add_column("In Progress", justify="center", style="blue")
    table.add_column("Done", justify="center", style="green")
    table.add_column("Completion", justify="center")

    for project in projects_list:
        completion_pct = f"{project.completion_rate:.0f}%"
        table.add_row(
            project.name,
            str(project.total),
            str(project.pending),
            str(project.in_progress),
            str(project.done),
            completion_pct
        )

    console.print(table)


@cli.command()
@click.option("--project", "-p", help="Export specific project only")
@click.option("--status", "-s", type=click.Choice(["pending", "in_progress", "done"]), help="Export specific status")
@click.option("--output", "-o", required=True, help="Output markdown file path")
def export(project: Optional[str], status: Optional[str], output: str):
    """Export tasks to markdown file.

    Examples:
        task export --output tasks.md
        task export --project Work --output work.md
        task export --status done --output completed.md
    """
    db = get_db()
    exporter = MarkdownExporter(db)

    try:
        if project:
            # Check if project exists
            projects = db.list_projects()
            if not any(p.name == project for p in projects):
                console.print(f"[red]Error: Project '{project}' not found[/red]")
                raise click.Abort()

            file_path = exporter.export_project(project, output)
            console.print(f"[green]✓ Exported project '{project}' to[/green] [cyan]{file_path}[/cyan]")

        elif status:
            file_path = exporter.export_status(status, output)
            console.print(f"[green]✓ Exported {status} tasks to[/green] [cyan]{file_path}[/cyan]")

        else:
            file_path = exporter.export_all(output)
            console.print(f"[green]✓ Exported all tasks to[/green] [cyan]{file_path}[/cyan]")

        # Show file size
        import os
        size = os.path.getsize(file_path)
        console.print(f"  File size: {size} bytes")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command()
def stats():
    """Show general statistics.

    Example: task stats
    """
    db = get_db()

    all_tasks = db.list_tasks()
    projects = db.list_projects()

    total = len(all_tasks)
    pending = sum(1 for t in all_tasks if t.status == "pending")
    in_progress = sum(1 for t in all_tasks if t.status == "in_progress")
    done = sum(1 for t in all_tasks if t.status == "done")
    overdue = sum(1 for t in all_tasks if t.is_overdue)

    stats_text = f"""
[cyan]Overall Statistics[/cyan]

[yellow]Total Tasks:[/yellow] {total}
[yellow]Pending:[/yellow] {pending}
[yellow]In Progress:[/yellow] {in_progress}
[yellow]Completed:[/yellow] {done}
[yellow]Overdue:[/yellow] {overdue}

[yellow]Projects:[/yellow] {len(projects)}
[yellow]Completion Rate:[/yellow] {(done/total*100):.1f if total > 0 else 0}%
"""

    panel = Panel(stats_text.strip(), title="Task Statistics", border_style="cyan")
    console.print(panel)


@cli.command()
@click.argument("status", type=click.Choice(["pending", "in_progress", "done"]))
def status_filter(status: str):
    """List tasks by status (shortcut).

    Examples:
        task pending
        task in-progress
        task done
    """
    # Convert command-style naming to internal status
    status_map = {
        "pending": "pending",
        "in_progress": "in_progress",
        "in-progress": "in_progress",
        "done": "done"
    }

    actual_status = status_map.get(status, status)
    db = get_db()
    tasks = db.list_tasks(status=actual_status)

    if not tasks:
        console.print(f"[yellow]No tasks with status '{status}'[/yellow]")
        return

    # Create table
    table = Table(title=f"{status.capitalize()} Tasks", box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Title", style="white", no_wrap=False)
    table.add_column("Project", style="yellow")
    table.add_column("Priority", justify="center")
    table.add_column("Due", style="magenta")

    for task in tasks:
        due_date_str = task.due_date if task.due_date else ""
        if task.is_overdue:
            due_date_str = f"[red]{due_date_str} ⚠️[/red]"

        table.add_row(
            str(task.id),
            task.title,
            task.project,
            task.priority_emoji,
            due_date_str
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(tasks)} task(s)[/dim]")


if __name__ == "__main__":
    cli()
