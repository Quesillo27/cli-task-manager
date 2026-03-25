"""Data models for Task Manager."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Represents a task in the system."""

    title: str
    project: str = "General"
    priority: str = "medium"  # high, medium, low
    status: str = "pending"   # pending, in_progress, done
    description: str = ""
    due_date: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

    def __post_init__(self):
        """Validate priority and status."""
        valid_priorities = {"high", "medium", "low"}
        valid_statuses = {"pending", "in_progress", "done"}

        if self.priority not in valid_priorities:
            raise ValueError(f"Priority must be one of {valid_priorities}")
        if self.status not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.status == "done" or not self.due_date:
            return False
        try:
            due = datetime.strptime(self.due_date, "%Y-%m-%d")
            return due < datetime.now()
        except ValueError:
            return False

    @property
    def priority_emoji(self) -> str:
        """Get emoji for priority."""
        return {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(self.priority, "⚪")

    @property
    def status_emoji(self) -> str:
        """Get emoji for status."""
        return {"pending": "⭕", "in_progress": "🔄", "done": "✅"}.get(self.status, "❓")


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
        """Calculate completion rate."""
        if self.total == 0:
            return 0.0
        return (self.done / self.total) * 100

    @property
    def active(self) -> int:
        """Get number of active tasks."""
        return self.pending + self.in_progress
