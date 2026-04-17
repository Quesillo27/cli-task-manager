"""CLI command groups.

Each module registers its subcommands on the root `cli` group via a
`register(cli)` function. Import :func:`register_all` to wire them up.
"""

from task_manager.commands import (
    bulk_cmds,
    export_cmds,
    filter_cmds,
    project_cmds,
    task_cmds,
)


def register_all(cli) -> None:
    """Attach every command module to the root CLI group."""
    task_cmds.register(cli)
    project_cmds.register(cli)
    filter_cmds.register(cli)
    bulk_cmds.register(cli)
    export_cmds.register(cli)


__all__ = ["register_all"]
