"""Data models for Task Manager."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional

from task_manager.config import (
    DATE_FORMAT,
    DEFAULT_PRIORITY,
    DEFAULT_PROJECT,
    DEFAULT_STATUS,
    PRIORITY_EMOJI,
    STATUS_EMOJI,
    VALID_PRIORITIES,
    VALID_STATUSES,
)


@dataclass
class Task:
    """Represents a task in the system."""

    title: str
    project: str = DEFAULT_PROJECT
    priority: str = DEFAULT_PRIORITY
    status: str = DEFAULT_STATUS
    description: str = ""
    due_date: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

    def __post_init__(self):
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Priority must be one of {VALID_PRIORITIES}, got '{self.priority}'"
            )
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"Status must be one of {VALID_STATUSES}, got '{self.status}'"
            )
        if self.title is None or not str(self.title).strip():
            raise ValueError("Title cannot be empty")

    @property
    def is_overdue(self) -> bool:
        if self.status == "done" or not self.due_date:
            return False
        try:
            due = datetime.strptime(self.due_date, DATE_FORMAT)
            return due.date() < datetime.now().date()
        except ValueError:
            return False

    @property
    def is_due_today(self) -> bool:
        if self.status == "done" or not self.due_date:
            return False
        try:
            due = datetime.strptime(self.due_date, DATE_FORMAT)
            return due.date() == datetime.now().date()
        except ValueError:
            return False

    @property
    def priority_emoji(self) -> str:
        return PRIORITY_EMOJI.get(self.priority, "⚪")

    @property
    def status_emoji(self) -> str:
        return STATUS_EMOJI.get(self.status, "❓")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to plain dict (JSON-ready)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Build a Task from a dict produced by to_dict or external input."""
        allowed = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in allowed}
        return cls(**filtered)


@dataclass
class Project:
    """Represents a project containing multiple tasks."""

    name: str
    total: int = 0
    pending: int = 0
    in_progress: int = 0
    done: int = 0

    @property
    def completion_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.done / self.total) * 100

    @property
    def active(self) -> int:
        return self.pending + self.in_progress

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to plain dict (JSON-ready)."""
        return {
            "name": self.name,
            "total": self.total,
            "pending": self.pending,
            "in_progress": self.in_progress,
            "done": self.done,
            "completion_rate": self.completion_rate,
            "active": self.active,
        }
