"""Filter-style commands: today, overdue, upcoming."""

from datetime import datetime, timedelta

import click

from task_manager.config import DATE_FORMAT
from task_manager.database import TaskDB
from task_manager.renderers import build_console, render_task_table


def register(cli: click.Group) -> None:
    cli.add_command(today)
    cli.add_command(overdue)
    cli.add_command(upcoming)


@click.command(name="today")
def today():
    """List tasks due today (non-completed)."""
    console = build_console()
    date_str = datetime.now().strftime(DATE_FORMAT)
    tasks = TaskDB().tasks_due_on(date_str)
    if not tasks:
        console.print(f"[yellow]No tasks due today ({date_str}).[/yellow]")
        return
    console.print(render_task_table(tasks, title=f"Due Today — {date_str}"))
    console.print(f"\n[dim]Found {len(tasks)} task(s)[/dim]")


@click.command(name="overdue")
def overdue():
    """List overdue tasks (due date in the past, not done)."""
    console = build_console()
    tasks = TaskDB().overdue_tasks()
    if not tasks:
        console.print("[green]No overdue tasks. 🎉[/green]")
        return
    console.print(render_task_table(tasks, title="Overdue Tasks"))
    console.print(f"\n[dim]Found {len(tasks)} overdue task(s)[/dim]")


@click.command(name="upcoming")
@click.option("--days", type=int, default=7, help="Window size in days (default: 7)")
def upcoming(days: int):
    """List non-completed tasks due within the next N days."""
    console = build_console()
    if days <= 0:
        console.print("[red]Error: --days must be positive[/red]")
        raise click.Abort()

    db = TaskDB()
    today_str = datetime.now().strftime(DATE_FORMAT)
    horizon = (datetime.now() + timedelta(days=days)).strftime(DATE_FORMAT)

    all_pending = [
        t for t in db.list_tasks()
        if t.status != "done" and t.due_date and today_str <= t.due_date <= horizon
    ]
    if not all_pending:
        console.print(f"[green]No tasks due in the next {days} day(s).[/green]")
        return
    all_pending.sort(key=lambda t: t.due_date or "")
    console.print(render_task_table(all_pending, title=f"Upcoming (next {days}d)"))
    console.print(f"\n[dim]Found {len(all_pending)} upcoming task(s)[/dim]")
