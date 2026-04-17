"""Reusable Rich renderers for CLI output."""

from datetime import datetime
from typing import Iterable, List

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from task_manager.models import Project, Task


def build_console() -> Console:
    """Build a default Rich console. Isolated for testability."""
    return Console()


def _format_created(task: Task) -> str:
    if not task.created_at:
        return ""
    try:
        return datetime.fromisoformat(task.created_at).strftime("%Y-%m-%d")
    except ValueError:
        return task.created_at


def _format_due(task: Task) -> str:
    due = task.due_date or ""
    if due and task.is_overdue:
        return f"[red]{due} ⚠️[/red]"
    return due


def render_task_table(
    tasks: Iterable[Task],
    *,
    title: str = "Tasks",
    show_description: bool = False,
) -> Table:
    """Build a Rich table for a collection of tasks."""
    table = Table(title=title, box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Title", style="white", no_wrap=False)
    table.add_column("Project", style="yellow")
    table.add_column("Priority", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Due", style="magenta")
    table.add_column("Created", style="dim")
    if show_description:
        table.add_column("Description", style="dim")

    for task in tasks:
        row = [
            str(task.id),
            task.title,
            task.project,
            task.priority_emoji,
            task.status_emoji,
            _format_due(task),
            _format_created(task),
        ]
        if show_description:
            row.append(task.description or "")
        table.add_row(*row)

    return table


def render_task_panel(task: Task) -> Panel:
    """Build a Rich panel with full task details."""
    content = (
        f"[bold cyan]{task.title}[/bold cyan]\n\n"
        f"[yellow]Project:[/yellow] {task.project}\n"
        f"[yellow]Priority:[/yellow] {task.priority_emoji} {task.priority.capitalize()}\n"
        f"[yellow]Status:[/yellow] {task.status_emoji} {task.status.capitalize()}\n\n"
        f"[yellow]ID:[/yellow] {task.id}\n"
        f"[yellow]Created:[/yellow] {task.created_at}"
    )
    if task.due_date:
        overdue_marker = " [red](OVERDUE)[/red]" if task.is_overdue else ""
        content += f"\n[yellow]Due:[/yellow] {task.due_date}{overdue_marker}"
    if task.description:
        content += f"\n\n[yellow]Description:[/yellow]\n{task.description}"
    if task.completed_at:
        content += f"\n[yellow]Completed:[/yellow] {task.completed_at}"

    return Panel(content, title=f"Task #{task.id}", expand=False, border_style="cyan")


def render_projects_table(projects: Iterable[Project]) -> Table:
    """Build a Rich table with project statistics."""
    table = Table(title="Projects", box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Project", style="yellow")
    table.add_column("Total", justify="center")
    table.add_column("Pending", justify="center", style="dim")
    table.add_column("In Progress", justify="center", style="blue")
    table.add_column("Done", justify="center", style="green")
    table.add_column("Completion", justify="center")

    for project in projects:
        completion_pct = f"{project.completion_rate:.0f}%"
        table.add_row(
            project.name,
            str(project.total),
            str(project.pending),
            str(project.in_progress),
            str(project.done),
            completion_pct,
        )

    return table


def render_stats_panel(tasks: List[Task], projects: List[Project]) -> Panel:
    """Build a Rich panel with aggregate statistics.

    Safe against empty task lists (avoids ZeroDivisionError).
    """
    total = len(tasks)
    pending = sum(1 for t in tasks if t.status == "pending")
    in_progress = sum(1 for t in tasks if t.status == "in_progress")
    done = sum(1 for t in tasks if t.status == "done")
    overdue = sum(1 for t in tasks if t.is_overdue)
    completion_rate = (done / total * 100) if total > 0 else 0.0

    body = (
        "[cyan]Overall Statistics[/cyan]\n\n"
        f"[yellow]Total Tasks:[/yellow] {total}\n"
        f"[yellow]Pending:[/yellow] {pending}\n"
        f"[yellow]In Progress:[/yellow] {in_progress}\n"
        f"[yellow]Completed:[/yellow] {done}\n"
        f"[yellow]Overdue:[/yellow] {overdue}\n\n"
        f"[yellow]Projects:[/yellow] {len(projects)}\n"
        f"[yellow]Completion Rate:[/yellow] {completion_rate:.1f}%"
    )
    return Panel(body, title="Task Statistics", border_style="cyan")


def summarize_status_counts(tasks: List[Task]) -> str:
    """One-line summary string used as footer below a list table."""
    total = len(tasks)
    pending = sum(1 for t in tasks if t.status == "pending")
    in_progress = sum(1 for t in tasks if t.status == "in_progress")
    done = sum(1 for t in tasks if t.status == "done")
    return f"Total: {total} | Pending: {pending} | In Progress: {in_progress} | Done: {done}"
