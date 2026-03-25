"""Database layer for Task Manager using SQLite."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from task_manager.models import Task, Project


class TaskDB:
    """SQLite database interface for task management."""

    def __init__(self, db_path: str = None):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.task-manager/tasks.db
        """
        if db_path is None:
            db_dir = Path.home() / ".task-manager"
            db_dir.mkdir(exist_ok=True)
            db_path = db_dir / "tasks.db"
        else:
            db_path = Path(db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = str(db_path)
        self.create_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self) -> None:
        """Create tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
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
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_project ON tasks(project)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)
        """)

        conn.commit()
        conn.close()

    def add_task(self, task: Task) -> int:
        """Add a new task to the database.

        Args:
            task: Task object to add

        Returns:
            ID of the created task
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO tasks
            (title, description, project, priority, status, due_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            task.title,
            task.description,
            task.project,
            task.priority,
            task.status,
            task.due_date,
            now
        ))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return task_id

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID.

        Args:
            task_id: ID of the task

        Returns:
            Task object or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_task(row)

    def list_tasks(
        self,
        project: Optional[str] = None,
        status: Optional[str] = None,
        order_by: str = "created_at"
    ) -> List[Task]:
        """List tasks with optional filters.

        Args:
            project: Filter by project name
            status: Filter by status (pending, in_progress, done)
            order_by: Column to order by (default: created_at)

        Returns:
            List of Task objects
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if project:
            query += " AND project = ?"
            params.append(project)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += f" ORDER BY {order_by} DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_task(row) for row in rows]

    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update task fields.

        Args:
            task_id: ID of the task
            **kwargs: Fields to update (title, description, project, priority, status, due_date, etc.)

        Returns:
            True if task was updated, False if not found
        """
        # Get current task to validate
        task = self.get_task(task_id)
        if not task:
            return False

        # Build update query
        allowed_fields = {
            "title", "description", "project", "priority",
            "status", "due_date", "completed_at"
        }
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_fields:
            return True

        # Add completed_at if marking as done
        if update_fields.get("status") == "done" and not update_fields.get("completed_at"):
            update_fields["completed_at"] = datetime.now().isoformat()
        elif update_fields.get("status") != "done":
            update_fields["completed_at"] = None

        set_clause = ", ".join(f"{k} = ?" for k in update_fields.keys())
        values = list(update_fields.values()) + [task_id]

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()

        return True

    def delete_task(self, task_id: int) -> bool:
        """Delete a task.

        Args:
            task_id: ID of the task

        Returns:
            True if task was deleted, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted

    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description.

        Args:
            query: Search query

        Returns:
            List of matching Task objects
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT * FROM tasks
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY created_at DESC
        """, (search_pattern, search_pattern))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_task(row) for row in rows]

    def list_projects(self) -> List[Project]:
        """Get all projects with task counts.

        Returns:
            List of Project objects with statistics
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                project,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done
            FROM tasks
            GROUP BY project
            ORDER BY project
        """)

        rows = cursor.fetchall()
        conn.close()

        projects = []
        for row in rows:
            projects.append(Project(
                name=row["project"],
                total=row["total"],
                pending=row["pending"],
                in_progress=row["in_progress"],
                done=row["done"]
            ))

        return projects

    def get_project_tasks(self, project: str) -> List[Task]:
        """Get all tasks in a project.

        Args:
            project: Project name

        Returns:
            List of Task objects in the project
        """
        return self.list_tasks(project=project)

    def clear_all(self) -> None:
        """Clear all tasks from database (useful for testing)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()

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
            completed_at=row["completed_at"]
        )
