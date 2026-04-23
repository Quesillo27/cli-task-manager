"""Unit tests for Task Manager database layer."""

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from task_manager.database import TaskDB
from task_manager.models import Task


class TestTaskDB(unittest.TestCase):
    """Test cases for TaskDB class."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.db = TaskDB(str(self.db_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    # ---- Table lifecycle --------------------------------------------------

    def test_create_tables(self):
        self.assertTrue(self.db_path.exists())

    def test_create_tables_is_idempotent(self):
        self.db.create_tables()
        self.db.create_tables()
        self.assertTrue(self.db_path.exists())

    # ---- CRUD -------------------------------------------------------------

    def test_add_task(self):
        task = Task(title="Test Task", project="Test", priority="high")
        task_id = self.db.add_task(task)
        self.assertIsNotNone(task_id)
        self.assertGreater(task_id, 0)

    def test_get_task(self):
        task = Task(title="Test Task", project="Test", priority="medium")
        task_id = self.db.add_task(task)
        retrieved = self.db.get_task(task_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Test Task")
        self.assertEqual(retrieved.project, "Test")
        self.assertEqual(retrieved.priority, "medium")

    def test_get_nonexistent_task(self):
        self.assertIsNone(self.db.get_task(99999))

    def test_update_task(self):
        task_id = self.db.add_task(Task(title="Original", priority="low"))
        self.db.update_task(task_id, title="Updated", priority="high")
        updated = self.db.get_task(task_id)
        self.assertEqual(updated.title, "Updated")
        self.assertEqual(updated.priority, "high")

    def test_update_nonexistent_task(self):
        self.assertFalse(self.db.update_task(99999, title="x"))

    def test_update_ignores_unknown_fields(self):
        task_id = self.db.add_task(Task(title="A"))
        self.assertTrue(self.db.update_task(task_id, nope="ignored", title="B"))
        self.assertEqual(self.db.get_task(task_id).title, "B")

    def test_delete_task(self):
        task_id = self.db.add_task(Task(title="Delete me"))
        self.assertTrue(self.db.delete_task(task_id))
        self.assertIsNone(self.db.get_task(task_id))

    def test_delete_nonexistent_task(self):
        self.assertFalse(self.db.delete_task(99999))

    # ---- Listing + filters ------------------------------------------------

    def test_list_tasks_default_order(self):
        self.db.add_task(Task(title="Task 1"))
        self.db.add_task(Task(title="Task 2"))
        tasks = self.db.list_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].title, "Task 2")

    def test_list_tasks_by_project(self):
        self.db.add_task(Task(title="A", project="P1"))
        self.db.add_task(Task(title="B", project="P1"))
        self.db.add_task(Task(title="C", project="P2"))
        p1 = self.db.list_tasks(project="P1")
        self.assertEqual(len(p1), 2)
        self.assertTrue(all(t.project == "P1" for t in p1))

    def test_list_tasks_by_status(self):
        self.db.add_task(Task(title="1", status="pending"))
        self.db.add_task(Task(title="2", status="done"))
        self.db.add_task(Task(title="3", status="pending"))
        self.assertEqual(len(self.db.list_tasks(status="pending")), 2)

    def test_list_tasks_sort_ascending(self):
        self.db.add_task(Task(title="Alpha"))
        self.db.add_task(Task(title="Beta"))
        ascending = self.db.list_tasks(order_by="title", direction="ASC")
        self.assertEqual(ascending[0].title, "Alpha")
        self.assertEqual(ascending[1].title, "Beta")

    def test_list_tasks_with_limit(self):
        for i in range(5):
            self.db.add_task(Task(title=f"Task {i}"))
        self.assertEqual(len(self.db.list_tasks(limit=2)), 2)

    def test_list_tasks_with_limit_and_offset(self):
        for i in range(5):
            self.db.add_task(Task(title=f"Task {i}"))
        page = self.db.list_tasks(limit=2, offset=2)
        self.assertEqual(len(page), 2)

    def test_list_tasks_with_offset_without_limit(self):
        for i in range(5):
            self.db.add_task(Task(title=f"Task {i}"))
        page = self.db.list_tasks(offset=2)
        self.assertEqual(len(page), 3)
        self.assertEqual(page[0].title, "Task 2")

    def test_list_tasks_rejects_invalid_order_by(self):
        with self.assertRaises(ValueError):
            self.db.list_tasks(order_by="DROP TABLE tasks")

    def test_list_tasks_rejects_invalid_direction(self):
        with self.assertRaises(ValueError):
            self.db.list_tasks(direction="EVIL")

    def test_list_tasks_rejects_negative_limit(self):
        with self.assertRaises(ValueError):
            self.db.list_tasks(limit=-1)

    def test_list_tasks_rejects_negative_offset(self):
        with self.assertRaises(ValueError):
            self.db.list_tasks(offset=-1)

    # ---- Search -----------------------------------------------------------

    def test_search_tasks_by_title(self):
        self.db.add_task(Task(title="Buy groceries"))
        self.db.add_task(Task(title="Call the doctor"))
        self.db.add_task(Task(title="Fix kitchen sink"))
        results = self.db.search_tasks("kitchen")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Fix kitchen sink")

    def test_search_in_description(self):
        self.db.add_task(Task(title="Task A", description="This is urgent"))
        self.db.add_task(Task(title="Task B", description="Normal task"))
        results = self.db.search_tasks("urgent")
        self.assertEqual(len(results), 1)

    def test_search_empty_query_matches_all(self):
        self.db.add_task(Task(title="Something"))
        self.db.add_task(Task(title="Other"))
        self.assertEqual(len(self.db.search_tasks("")), 2)

    def test_search_no_match(self):
        self.db.add_task(Task(title="Unrelated"))
        self.assertEqual(self.db.search_tasks("zzzz"), [])

    # ---- Projects ---------------------------------------------------------

    def test_list_projects(self):
        self.db.add_task(Task(title="1", project="Work", status="pending"))
        self.db.add_task(Task(title="2", project="Work", status="done"))
        self.db.add_task(Task(title="3", project="Home", status="pending"))
        projects = self.db.list_projects()
        self.assertEqual(len(projects), 2)
        work = next(p for p in projects if p.name == "Work")
        self.assertEqual(work.total, 2)
        self.assertEqual(work.pending, 1)
        self.assertEqual(work.done, 1)

    def test_project_exists(self):
        self.db.add_task(Task(title="A", project="Real"))
        self.assertTrue(self.db.project_exists("Real"))
        self.assertFalse(self.db.project_exists("Ghost"))

    def test_count_tasks(self):
        self.assertEqual(self.db.count_tasks(), 0)
        self.db.add_task(Task(title="A"))
        self.db.add_task(Task(title="B"))
        self.assertEqual(self.db.count_tasks(), 2)

    # ---- Bulk operations --------------------------------------------------

    def test_mark_tasks_done_bulk(self):
        ids = [self.db.add_task(Task(title=f"T{i}")) for i in range(3)]
        count = self.db.mark_tasks_done(ids)
        self.assertEqual(count, 3)
        for tid in ids:
            self.assertEqual(self.db.get_task(tid).status, "done")
            self.assertIsNotNone(self.db.get_task(tid).completed_at)

    def test_mark_tasks_done_empty(self):
        self.assertEqual(self.db.mark_tasks_done([]), 0)

    def test_delete_tasks_bulk(self):
        ids = [self.db.add_task(Task(title=f"T{i}")) for i in range(3)]
        count = self.db.delete_tasks(ids)
        self.assertEqual(count, 3)
        self.assertEqual(self.db.count_tasks(), 0)

    def test_delete_tasks_empty(self):
        self.assertEqual(self.db.delete_tasks([]), 0)

    # ---- Due date filters -------------------------------------------------

    def test_tasks_due_on(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.db.add_task(Task(title="Today", due_date=today))
        self.db.add_task(Task(title="Tomorrow",
                              due_date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")))
        due = self.db.tasks_due_on(today)
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0].title, "Today")

    def test_tasks_due_on_excludes_done(self):
        today = datetime.now().strftime("%Y-%m-%d")
        tid = self.db.add_task(Task(title="Done today", due_date=today))
        self.db.update_task(tid, status="done")
        self.assertEqual(self.db.tasks_due_on(today), [])

    def test_overdue_tasks(self):
        past = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        self.db.add_task(Task(title="Late", due_date=past))
        self.db.add_task(Task(title="Future", due_date=future))
        overdue = self.db.overdue_tasks()
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0].title, "Late")

    def test_overdue_tasks_excludes_done(self):
        past = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        tid = self.db.add_task(Task(title="Late and done", due_date=past))
        self.db.update_task(tid, status="done")
        self.assertEqual(self.db.overdue_tasks(), [])

    # ---- Status transitions ----------------------------------------------

    def test_mark_task_as_done_sets_completed_at(self):
        tid = self.db.add_task(Task(title="Task"))
        self.db.update_task(tid, status="done")
        t = self.db.get_task(tid)
        self.assertEqual(t.status, "done")
        self.assertIsNotNone(t.completed_at)

    def test_revert_done_clears_completed_at(self):
        tid = self.db.add_task(Task(title="Task"))
        self.db.update_task(tid, status="done")
        self.db.update_task(tid, status="pending")
        t = self.db.get_task(tid)
        self.assertEqual(t.status, "pending")
        self.assertIsNone(t.completed_at)

    # ---- Misc -------------------------------------------------------------

    def test_due_date_persistence(self):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        tid = self.db.add_task(Task(title="Has due", due_date=tomorrow))
        self.assertEqual(self.db.get_task(tid).due_date, tomorrow)

    def test_clear_all_returns_count(self):
        self.db.add_task(Task(title="A"))
        self.db.add_task(Task(title="B"))
        count = self.db.clear_all()
        self.assertEqual(count, 2)
        self.assertEqual(self.db.count_tasks(), 0)

    def test_creates_parent_directories(self):
        nested = Path(self.temp_dir.name) / "sub" / "deeper" / "db.sqlite"
        db = TaskDB(str(nested))
        self.assertTrue(nested.exists())
        self.assertEqual(db.count_tasks(), 0)


if __name__ == "__main__":
    unittest.main()
