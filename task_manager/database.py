"""Database layer for Task Manager using SQLite."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from task_manager.config import DATE_FORMAT, SORT_COLUMN_MAP, get_db_path
from task_manager.logger import get_logger
from task_manager.models import Project, Task


log = get_logger(__name__)

_VALID_ORDER_BY = set(SORT_COLUMN_MAP.values())
_VALID_DIRECTIONS = {"ASC", "DESC"}


class TaskDB:
    """SQLite database interface for task management."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.task-manager/tasks.db
                     (overridable via TASK_MANAGER_DB env var).
        """
        if db_path is None:
            db_path = get_db_path()
        resolved = Path(db_path)
        resolved.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = str(resolved)
        self.create_tables()
        log.debug("TaskDB initialized at %s", self.db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Open a new SQLite connection with row factory + FK support."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create_tables(self) -> None:
        """Create tables and indices if they don't exist (idempotent)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    project TEXT DEFAULT 'General',
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    due_date TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    CONSTRAINT check_priority CHECK (priority IN ('high', 'medium', 'low')),
                    CONSTRAINT check_status CHECK (status IN ('pending', 'in_progress', 'done'))
                )
                """
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_project ON tasks(project)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_due_date ON tasks(due_date)")
            conn.commit()

    def add_task(self, task: Task) -> int:
        """Insert a task and return its new ID."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tasks
                (title, description, project, priority, status, due_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.title,
                    task.description,
                    task.project,
                    task.priority,
                    task.status,
                    task.due_date,
                    now,
                ),
            )
            task_id = cursor.lastrowid
            conn.commit()
        log.info("Task added id=%s project=%s", task_id, task.project)
        return task_id

    def get_task(self, task_id: int) -> Optional[Task]:
        """Return a task by ID, or None if missing."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_task(row)

    def list_tasks(
        self,
        project: Optional[str] = None,
        status: Optional[str] = None,
        order_by: str = "created_at",
        direction: str = "DESC",
        limit: int = 0,
        offset: int = 0,
    ) -> List[Task]:
        """List tasks with optional filters.

        Args:
            project: Filter by project name
            status: Filter by status (pending, in_progress, done)
            order_by: Column to order by (must be one of the allowed columns)
            direction: ASC or DESC
            limit: Maximum rows (0 = no limit)
            offset: Rows to skip

        Returns:
            List of Task objects
        """
        if order_by not in _VALID_ORDER_BY:
            raise ValueError(
                f"order_by must be one of {sorted(_VALID_ORDER_BY)}, got '{order_by}'"
            )
        direction_norm = direction.upper()
        if direction_norm not in _VALID_DIRECTIONS:
            raise ValueError(
                f"direction must be ASC or DESC, got '{direction}'"
            )

        query = "SELECT * FROM tasks WHERE 1=1"
        params: list = []

        if project:
            query += " AND project = ?"
            params.append(project)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += f" ORDER BY {order_by} {direction_norm}"
        if limit and limit > 0:
            query += " LIMIT ?"
            params.append(int(limit))
            if offset and offset > 0:
                query += " OFFSET ?"
                params.append(int(offset))

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        return [self._row_to_task(row) for row in rows]

    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update task fields. Returns True if the task exists, False otherwise."""
        task = self.get_task(task_id)
        if not task:
            return False

        allowed_fields = {
            "title",
            "description",
            "project",
            "priority",
            "status",
            "due_date",
            "completed_at",
        }
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_fields:
            return True

        if "status" in update_fields:
            if update_fields["status"] == "done" and not update_fields.get("completed_at"):
                update_fields["completed_at"] = datetime.now().isoformat()
            elif update_fields["status"] != "done":
                update_fields["completed_at"] = None

        set_clause = ", ".join(f"{k} = ?" for k in update_fields.keys())
        values = list(update_fields.values()) + [task_id]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
            conn.commit()

        log.info("Task updated id=%s fields=%s", task_id, list(update_fields.keys()))
        return True

    def delete_task(self, task_id: int) -> bool:
        """Delete a task. Returns True if a row was deleted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
        if deleted:
            log.info("Task deleted id=%s", task_id)
        return deleted

    def delete_tasks(self, task_ids: List[int]) -> int:
        """Delete multiple tasks in a single transaction. Returns deleted count."""
        if not task_ids:
            return 0
        placeholders = ",".join("?" for _ in task_ids)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM tasks WHERE id IN ({placeholders})", task_ids)
            count = cursor.rowcount
            conn.commit()
        log.info("Bulk delete count=%s", count)
        return count

    def mark_tasks_done(self, task_ids: List[int]) -> int:
        """Mark multiple tasks as done. Returns updated count."""
        if not task_ids:
            return 0
        now = datetime.now().isoformat()
        placeholders = ",".join("?" for _ in task_ids)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE tasks SET status = 'done', completed_at = ? "
                f"WHERE id IN ({placeholders})",
                [now, *task_ids],
            )
            count = cursor.rowcount
            conn.commit()
        log.info("Bulk done count=%s", count)
        return count

    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description (case-insensitive LIKE)."""
        if query is None:
            query = ""
        search_pattern = f"%{query}%"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM tasks
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY created_at DESC
                """,
                (search_pattern, search_pattern),
            )
            rows = cursor.fetchall()
        return [self._row_to_task(row) for row in rows]

    def list_projects(self) -> List[Project]:
        """Get all projects with task counts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    project,
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                    SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done
                FROM tasks
                GROUP BY project
                ORDER BY project
                """
            )
            rows = cursor.fetchall()

        return [
            Project(
                name=row["project"],
                total=row["total"],
                pending=row["pending"],
                in_progress=row["in_progress"],
                done=row["done"],
            )
            for row in rows
        ]

    def project_exists(self, name: str) -> bool:
        """Return True if the project has at least one task."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM tasks WHERE project = ? LIMIT 1", (name,))
            return cursor.fetchone() is not None

    def get_project_tasks(self, project: str) -> List[Task]:
        """Get all tasks in a project."""
        return self.list_tasks(project=project)

    def count_tasks(self) -> int:
        """Total number of tasks."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tasks")
            return cursor.fetchone()[0]

    def tasks_due_on(self, date_str: str) -> List[Task]:
        """Return tasks due exactly on `date_str` (YYYY-MM-DD) and not done."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE due_date = ? AND status != 'done' "
                "ORDER BY priority ASC",
                (date_str,),
            )
            rows = cursor.fetchall()
        return [self._row_to_task(row) for row in rows]

    def overdue_tasks(self, reference_date: Optional[str] = None) -> List[Task]:
        """Return tasks whose due_date is before reference_date and not done."""
        reference = reference_date or datetime.now().strftime(DATE_FORMAT)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks "
                "WHERE due_date IS NOT NULL AND due_date < ? AND status != 'done' "
                "ORDER BY due_date ASC",
                (reference,),
            )
            rows = cursor.fetchall()
        return [self._row_to_task(row) for row in rows]

    def clear_all(self) -> int:
        """Delete every task from the database. Returns the deleted count."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks")
            count = cursor.rowcount
            conn.commit()
        log.warning("Cleared all tasks (count=%s)", count)
        return count

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        """Convert database row to Task object."""
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            project=row["project"],
            priority=row["priority"],
            status=row["status"],
            due_date=row["due_date"],
            created_at=row["created_at"],
            completed_at=row["completed_at"],
        )
