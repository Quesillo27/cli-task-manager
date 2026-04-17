"""Centralized configuration and constants for CLI Task Manager."""

import os
from pathlib import Path

# Valid domain values
VALID_PRIORITIES = ("high", "medium", "low")
VALID_STATUSES = ("pending", "in_progress", "done")
VALID_SORT_KEYS = ("created", "due_date", "priority", "title", "status")
VALID_ORDER = ("asc", "desc")
VALID_EXPORT_FORMATS = ("md", "json", "csv")

# Sort column mapping (CLI name -> DB column)
SORT_COLUMN_MAP = {
    "created": "created_at",
    "due_date": "due_date",
    "priority": "priority",
    "title": "title",
    "status": "status",
}

# Emoji mapping
PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}
STATUS_EMOJI = {"pending": "⭕", "in_progress": "🔄", "done": "✅"}

# Date format
DATE_FORMAT = "%Y-%m-%d"

# Defaults
DEFAULT_PROJECT = "General"
DEFAULT_PRIORITY = "medium"
DEFAULT_STATUS = "pending"
DEFAULT_LIST_LIMIT = 0  # 0 = no limit

# Database paths
DEFAULT_DB_DIR = Path.home() / ".task-manager"
DEFAULT_DB_FILE = DEFAULT_DB_DIR / "tasks.db"


def get_db_path() -> str:
    """Resolve database path from env or default."""
    env_path = os.environ.get("TASK_MANAGER_DB")
    if env_path:
        return env_path
    return str(DEFAULT_DB_FILE)


def get_log_level() -> str:
    """Resolve logger level from env (default WARNING so CLI stays quiet)."""
    return os.environ.get("TASK_MANAGER_LOG_LEVEL", "WARNING").upper()
