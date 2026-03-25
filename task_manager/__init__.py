"""CLI Task Manager - A command-line task management tool."""

__version__ = "1.0.0"
__author__ = "Task Manager Team"

from task_manager.models import Task, Project
from task_manager.database import TaskDB

__all__ = ["Task", "Project", "TaskDB"]
