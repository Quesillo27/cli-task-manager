"""CLI entry point — wires every command group onto the root `cli` group."""

import click

from task_manager import __version__
from task_manager.commands import register_all


@click.group(
    help="CLI Task Manager - Manage your tasks from the command line.",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(__version__, "-V", "--version", prog_name="task")
def cli() -> None:
    """Root command group."""


register_all(cli)


if __name__ == "__main__":
    cli()
