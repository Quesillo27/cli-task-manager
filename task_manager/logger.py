"""Structured logger used across modules.

Stays silent by default so the CLI UX isn't polluted. Set
`TASK_MANAGER_LOG_LEVEL=DEBUG` (or INFO/WARNING/ERROR) to enable output.
"""

import logging
import sys

from task_manager.config import get_log_level


_LOGGER_NAME = "task_manager"
_configured = False


def get_logger(name: str = _LOGGER_NAME) -> logging.Logger:
    """Return a configured logger. Idempotent — safe to call repeatedly."""
    global _configured
    logger = logging.getLogger(_LOGGER_NAME)
    if not _configured:
        level = getattr(logging, get_log_level(), logging.WARNING)
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.propagate = False
        _configured = True
    if name == _LOGGER_NAME:
        return logger
    return logger.getChild(name.replace(_LOGGER_NAME + ".", ""))
