"""Unit tests for data models (Task, Project)."""

import unittest
from datetime import datetime, timedelta

from task_manager.models import Project, Task


class TestTaskValidation(unittest.TestCase):
    def test_valid_task(self):
        task = Task(title="Hello", priority="high", status="pending")
        self.assertEqual(task.title, "Hello")

    def test_invalid_priority(self):
        with self.assertRaises(ValueError):
            Task(title="x", priority="bogus")

    def test_invalid_status(self):
        with self.assertRaises(ValueError):
            Task(title="x", status="bogus")

    def test_empty_title_rejected(self):
        with self.assertRaises(ValueError):
            Task(title="")

    def test_whitespace_title_rejected(self):
        with self.assertRaises(ValueError):
            Task(title="   ")


class TestTaskProperties(unittest.TestCase):
    def test_is_overdue_true(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertTrue(Task(title="x", due_date=yesterday).is_overdue)

    def test_is_overdue_false_future(self):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertFalse(Task(title="x", due_date=tomorrow).is_overdue)

    def test_is_overdue_false_no_due(self):
        self.assertFalse(Task(title="x").is_overdue)

    def test_is_overdue_false_when_done(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertFalse(Task(title="x", due_date=yesterday, status="done").is_overdue)

    def test_is_overdue_malformed_date(self):
        self.assertFalse(Task(title="x", due_date="not-a-date").is_overdue)

    def test_is_due_today_true(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.assertTrue(Task(title="x", due_date=today).is_due_today)

    def test_is_due_today_false_when_done(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.assertFalse(Task(title="x", due_date=today, status="done").is_due_today)

    def test_priority_emoji(self):
        self.assertEqual(Task(title="x", priority="high").priority_emoji, "🔴")
        self.assertEqual(Task(title="x", priority="medium").priority_emoji, "🟡")
        self.assertEqual(Task(title="x", priority="low").priority_emoji, "🟢")

    def test_status_emoji(self):
        self.assertEqual(Task(title="x", status="pending").status_emoji, "⭕")
        self.assertEqual(Task(title="x", status="in_progress").status_emoji, "🔄")
        self.assertEqual(Task(title="x", status="done").status_emoji, "✅")


class TestTaskSerialization(unittest.TestCase):
    def test_to_dict_roundtrip(self):
        task = Task(title="Hello", project="Demo", priority="high", description="Body")
        data = task.to_dict()
        self.assertEqual(data["title"], "Hello")
        self.assertEqual(data["priority"], "high")
        restored = Task.from_dict(data)
        self.assertEqual(restored.title, "Hello")
        self.assertEqual(restored.priority, "high")

    def test_from_dict_ignores_unknown_keys(self):
        task = Task.from_dict({"title": "Hi", "made_up": 42})
        self.assertEqual(task.title, "Hi")


class TestProject(unittest.TestCase):
    def test_completion_rate(self):
        p = Project(name="X", total=4, done=1)
        self.assertEqual(p.completion_rate, 25.0)

    def test_completion_rate_zero_tasks(self):
        self.assertEqual(Project(name="Empty").completion_rate, 0.0)

    def test_active_tasks(self):
        p = Project(name="X", pending=3, in_progress=2, done=1)
        self.assertEqual(p.active, 5)

    def test_to_dict(self):
        data = Project(name="X", total=2, done=1).to_dict()
        self.assertEqual(data["name"], "X")
        self.assertEqual(data["completion_rate"], 50.0)


if __name__ == "__main__":
    unittest.main()
