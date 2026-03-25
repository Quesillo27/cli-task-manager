"""Unit tests for Task Manager database."""

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from task_manager.database import TaskDB
from task_manager.models import Task


class TestTaskDB(unittest.TestCase):
    """Test cases for TaskDB class."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.db = TaskDB(str(self.db_path))

    def tearDown(self):
        """Clean up test database."""
        self.temp_dir.cleanup()

    def test_create_tables(self):
        """Test that tables are created correctly."""
        self.assertTrue(self.db_path.exists())

    def test_add_task(self):
        """Test adding a task."""
        task = Task(
            title="Test Task",
            project="Test",
            priority="high",
            description="A test task"
        )

        task_id = self.db.add_task(task)

        self.assertIsNotNone(task_id)
        self.assertGreater(task_id, 0)

    def test_get_task(self):
        """Test retrieving a task by ID."""
        task = Task(
            title="Test Task",
            project="Test",
            priority="medium"
        )

        task_id = self.db.add_task(task)
        retrieved_task = self.db.get_task(task_id)

        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task.title, "Test Task")
        self.assertEqual(retrieved_task.project, "Test")
        self.assertEqual(retrieved_task.priority, "medium")

    def test_get_nonexistent_task(self):
        """Test retrieving a non-existent task returns None."""
        task = self.db.get_task(99999)
        self.assertIsNone(task)

    def test_list_tasks(self):
        """Test listing all tasks."""
        task1 = Task(title="Task 1", project="Project A")
        task2 = Task(title="Task 2", project="Project B")

        self.db.add_task(task1)
        self.db.add_task(task2)

        tasks = self.db.list_tasks()

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].title, "Task 2")  # Most recent first
        self.assertEqual(tasks[1].title, "Task 1")

    def test_list_tasks_by_project(self):
        """Test filtering tasks by project."""
        task1 = Task(title="Task 1", project="Project A")
        task2 = Task(title="Task 2", project="Project A")
        task3 = Task(title="Task 3", project="Project B")

        self.db.add_task(task1)
        self.db.add_task(task2)
        self.db.add_task(task3)

        project_a_tasks = self.db.list_tasks(project="Project A")

        self.assertEqual(len(project_a_tasks), 2)
        self.assertTrue(all(t.project == "Project A" for t in project_a_tasks))

    def test_list_tasks_by_status(self):
        """Test filtering tasks by status."""
        task1 = Task(title="Task 1", status="pending")
        task2 = Task(title="Task 2", status="done")
        task3 = Task(title="Task 3", status="pending")

        self.db.add_task(task1)
        self.db.add_task(task2)
        self.db.add_task(task3)

        pending_tasks = self.db.list_tasks(status="pending")

        self.assertEqual(len(pending_tasks), 2)
        self.assertTrue(all(t.status == "pending" for t in pending_tasks))

    def test_update_task(self):
        """Test updating a task."""
        task = Task(title="Original Title", priority="low")
        task_id = self.db.add_task(task)

        self.db.update_task(task_id, title="Updated Title", priority="high")

        updated_task = self.db.get_task(task_id)

        self.assertEqual(updated_task.title, "Updated Title")
        self.assertEqual(updated_task.priority, "high")

    def test_update_nonexistent_task(self):
        """Test updating non-existent task returns False."""
        result = self.db.update_task(99999, title="New Title")
        self.assertFalse(result)

    def test_delete_task(self):
        """Test deleting a task."""
        task = Task(title="Task to Delete")
        task_id = self.db.add_task(task)

        result = self.db.delete_task(task_id)

        self.assertTrue(result)
        self.assertIsNone(self.db.get_task(task_id))

    def test_delete_nonexistent_task(self):
        """Test deleting non-existent task returns False."""
        result = self.db.delete_task(99999)
        self.assertFalse(result)

    def test_search_tasks(self):
        """Test searching tasks by title."""
        task1 = Task(title="Buy groceries", description="Milk, eggs, bread")
        task2 = Task(title="Call the doctor", description="Schedule appointment")
        task3 = Task(title="Fix kitchen sink", description="Water leak")

        self.db.add_task(task1)
        self.db.add_task(task2)
        self.db.add_task(task3)

        results = self.db.search_tasks("kitchen")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Fix kitchen sink")

    def test_search_in_description(self):
        """Test searching in task description."""
        task1 = Task(title="Task A", description="This is urgent")
        task2 = Task(title="Task B", description="Normal task")

        self.db.add_task(task1)
        self.db.add_task(task2)

        results = self.db.search_tasks("urgent")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Task A")

    def test_list_projects(self):
        """Test listing projects with statistics."""
        task1 = Task(title="Task 1", project="Work", status="pending")
        task2 = Task(title="Task 2", project="Work", status="done")
        task3 = Task(title="Task 3", project="Home", status="pending")

        self.db.add_task(task1)
        self.db.add_task(task2)
        self.db.add_task(task3)

        projects = self.db.list_projects()

        self.assertEqual(len(projects), 2)

        work_project = next((p for p in projects if p.name == "Work"), None)
        self.assertIsNotNone(work_project)
        self.assertEqual(work_project.total, 2)
        self.assertEqual(work_project.pending, 1)
        self.assertEqual(work_project.done, 1)

    def test_mark_task_as_done(self):
        """Test marking a task as done."""
        task = Task(title="Task to complete")
        task_id = self.db.add_task(task)

        self.db.update_task(task_id, status="done")

        updated_task = self.db.get_task(task_id)

        self.assertEqual(updated_task.status, "done")
        self.assertIsNotNone(updated_task.completed_at)

    def test_task_validation(self):
        """Test task validation."""
        with self.assertRaises(ValueError):
            Task(title="Invalid", priority="invalid_priority")

        with self.assertRaises(ValueError):
            Task(title="Invalid", status="invalid_status")

    def test_due_date_validation(self):
        """Test task with valid due date."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        task = Task(
            title="Task with due date",
            due_date=tomorrow
        )

        task_id = self.db.add_task(task)
        retrieved = self.db.get_task(task_id)

        self.assertEqual(retrieved.due_date, tomorrow)

    def test_is_overdue_property(self):
        """Test checking if task is overdue."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        overdue_task = Task(title="Overdue", due_date=yesterday)
        future_task = Task(title="Future", due_date=tomorrow)

        self.assertTrue(overdue_task.is_overdue)
        self.assertFalse(future_task.is_overdue)

    def test_clear_all(self):
        """Test clearing all tasks."""
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")

        self.db.add_task(task1)
        self.db.add_task(task2)

        self.db.clear_all()

        tasks = self.db.list_tasks()

        self.assertEqual(len(tasks), 0)


if __name__ == "__main__":
    unittest.main()
