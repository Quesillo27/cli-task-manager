"""Bulk operation commands: bulk-done, bulk-delete, clear."""

import click

from task_manager.database import TaskDB
from task_manager.renderers import build_console
from task_manager.validators import ValidationError, validate_task_ids


def register(cli: click.Group) -> None:
    cli.add_command(bulk_done)
    cli.add_command(bulk_delete)
    cli.add_command(clear)


@click.command(name="bulk-done")
@click.argument("task_ids", nargs=-1, type=int)
def bulk_done(task_ids):
    """Mark multiple tasks as done in one transaction."""
    console = build_console()
    try:
        ids = validate_task_ids(task_ids)
    except ValidationError as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise click.Abort()

    count = TaskDB().mark_tasks_done(ids)
    console.print(f"[green]✓ Marked {count} task(s) as done[/green]")


@click.command(name="bulk-delete")
@click.argument("task_ids", nargs=-1, type=int)
@click.option("--yes", "assume_yes", is_flag=True, default=False, help="Skip confirmation")
def bulk_delete(task_ids, assume_yes: bool):
    """Delete multiple tasks in one transaction."""
    console = build_console()
    try:
        ids = validate_task_ids(task_ids)
    except ValidationError as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise click.Abort()

    if not assume_yes:
        if not click.confirm(f"Delete {len(ids)} task(s)?"):
            console.print("[yellow]Aborted[/yellow]")
            return

    count = TaskDB().delete_tasks(ids)
    console.print(f"[green]✓ Deleted {count} task(s)[/green]")


@click.command(name="clear")
@click.option("--yes", "assume_yes", is_flag=True, default=False, help="Skip confirmation")
def clear(assume_yes: bool):
    """Delete EVERY task from the database."""
    console = build_console()
    db = TaskDB()
    total = db.count_tasks()
    if total == 0:
        console.print("[yellow]Database already empty.[/yellow]")
        return

    if not assume_yes:
        if not click.confirm(
            f"This will permanently delete {total} task(s). Continue?"
        ):
            console.print("[yellow]Aborted[/yellow]")
            return

    count = db.clear_all()
    console.print(f"[red]✗ Cleared database — {count} task(s) removed[/red]")
