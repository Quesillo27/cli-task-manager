"""Integration-style tests for the Click CLI."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from task_manager.cli import cli


class CLITestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / "cli.sqlite")
        self._prev_env = os.environ.get("TASK_MANAGER_DB")
        os.environ["TASK_MANAGER_DB"] = self.db_path
        self.runner = CliRunner()

    def tearDown(self):
        if self._prev_env is None:
            os.environ.pop("TASK_MANAGER_DB", None)
        else:
            os.environ["TASK_MANAGER_DB"] = self._prev_env
        self.tmp.cleanup()

    def invoke(self, *args, input_: str = None):
        return self.runner.invoke(cli, list(args), input=input_, catch_exceptions=False)


class TestAddList(CLITestCase):
    def test_add_and_list(self):
        result = self.invoke("add", "Hello world")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Task created", result.output)

        result = self.invoke("list")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Hello world", result.output)

    def test_add_rejects_invalid_due(self):
        result = self.invoke("add", "Bad", "--due", "17/04/2026")
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Error", result.output)

    def test_add_rejects_empty_title(self):
        result = self.invoke("add", "   ")
        self.assertNotEqual(result.exit_code, 0)

    def test_list_with_filters(self):
        self.invoke("add", "A", "--project", "P1", "--priority", "high")
        self.invoke("add", "B", "--project", "P2", "--priority", "low")
        result = self.invoke("list", "--project", "P1")
        self.assertIn("A", result.output)
        self.assertNotIn("B", result.output)

    def test_list_empty(self):
        result = self.invoke("list")
        self.assertIn("No tasks found", result.output)


class TestShowUpdateDelete(CLITestCase):
    def _add_task(self, title: str = "Demo") -> int:
        self.invoke("add", title)
        # ID is autoincrement, assume 1-based within fresh DB
        result = self.invoke("list")
        # naive: extract first task id — but within tests we always know it's 1
        return 1

    def test_show_task(self):
        self._add_task("Demo")
        result = self.invoke("show", "1")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Demo", result.output)

    def test_show_missing_task(self):
        result = self.invoke("show", "999")
        self.assertNotEqual(result.exit_code, 0)

    def test_update_task(self):
        self._add_task("Original")
        result = self.invoke("update", "1", "--title", "Updated", "--priority", "high")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("updated", result.output.lower())

        result = self.invoke("show", "1")
        self.assertIn("Updated", result.output)

    def test_update_no_fields_says_so(self):
        self._add_task("T")
        result = self.invoke("update", "1")
        self.assertIn("No updates", result.output)

    def test_update_missing_task(self):
        result = self.invoke("update", "999", "--title", "x")
        self.assertNotEqual(result.exit_code, 0)

    def test_update_invalid_due(self):
        self._add_task("X")
        result = self.invoke("update", "1", "--due", "not-a-date")
        self.assertNotEqual(result.exit_code, 0)

    def test_done(self):
        self._add_task("T")
        result = self.invoke("done", "1")
        self.assertEqual(result.exit_code, 0)
        show = self.invoke("show", "1")
        self.assertIn("Done", show.output)

    def test_delete_with_yes(self):
        self._add_task("T")
        result = self.invoke("delete", "1", "--yes")
        self.assertEqual(result.exit_code, 0)
        missing = self.invoke("show", "1")
        self.assertNotEqual(missing.exit_code, 0)

    def test_delete_aborted(self):
        self._add_task("T")
        result = self.invoke("delete", "1", input_="n\n")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Aborted", result.output)
        still = self.invoke("show", "1")
        self.assertEqual(still.exit_code, 0)


class TestSearch(CLITestCase):
    def test_search(self):
        self.invoke("add", "Buy bread")
        self.invoke("add", "Call mom")
        result = self.invoke("search", "bread")
        self.assertIn("Buy bread", result.output)
        self.assertNotIn("Call mom", result.output)

    def test_search_no_match(self):
        self.invoke("add", "Hello")
        result = self.invoke("search", "xyz")
        self.assertIn("No tasks found", result.output)


class TestBulk(CLITestCase):
    def test_bulk_done(self):
        for i in range(3):
            self.invoke("add", f"T{i}")
        result = self.invoke("bulk-done", "1", "2", "3")
        self.assertIn("3", result.output)

    def test_bulk_delete_with_yes(self):
        self.invoke("add", "A")
        self.invoke("add", "B")
        result = self.invoke("bulk-delete", "1", "2", "--yes")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Deleted", result.output)

    def test_bulk_delete_requires_ids(self):
        result = self.invoke("bulk-delete", "--yes")
        self.assertNotEqual(result.exit_code, 0)

    def test_clear_empty_db(self):
        result = self.invoke("clear", "--yes")
        self.assertIn("empty", result.output.lower())

    def test_clear_with_tasks(self):
        self.invoke("add", "A")
        result = self.invoke("clear", "--yes")
        self.assertIn("Cleared", result.output)


class TestFilters(CLITestCase):
    def test_today_empty(self):
        result = self.invoke("today")
        self.assertIn("No tasks due today", result.output)

    def test_overdue_empty(self):
        result = self.invoke("overdue")
        self.assertIn("No overdue", result.output)

    def test_overdue_with_task(self):
        self.invoke("add", "Late", "--due", "2020-01-01")
        result = self.invoke("overdue")
        self.assertIn("Late", result.output)

    def test_upcoming_invalid_days(self):
        result = self.invoke("upcoming", "--days", "0")
        self.assertNotEqual(result.exit_code, 0)


class TestProjectsAndStats(CLITestCase):
    def test_projects_empty(self):
        result = self.invoke("projects")
        self.assertIn("No projects", result.output)

    def test_projects_with_data(self):
        self.invoke("add", "T", "--project", "Work")
        result = self.invoke("projects")
        self.assertIn("Work", result.output)

    def test_stats_empty_does_not_crash(self):
        """Regression: stats used to crash on empty DB due to division-by-zero."""
        result = self.invoke("stats")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Total Tasks: 0", result.output)
        self.assertIn("Completion Rate: 0.0%", result.output)

    def test_stats_with_data(self):
        self.invoke("add", "T1")
        self.invoke("add", "T2")
        self.invoke("done", "1")
        result = self.invoke("stats")
        self.assertIn("Total Tasks: 2", result.output)

    def test_version(self):
        result = self.invoke("version")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("cli-task-manager", result.output)


class TestExportImport(CLITestCase):
    def test_export_markdown(self):
        self.invoke("add", "T")
        out = Path(self.tmp.name) / "out.md"
        result = self.invoke("export", "--output", str(out))
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(out.exists())
        self.assertIn("All Tasks", out.read_text())

    def test_export_json(self):
        self.invoke("add", "T")
        out = Path(self.tmp.name) / "out.json"
        result = self.invoke("export", "--output", str(out), "--format", "json")
        self.assertEqual(result.exit_code, 0)
        payload = json.loads(out.read_text())
        self.assertIn("tasks", payload)

    def test_export_csv(self):
        self.invoke("add", "T")
        out = Path(self.tmp.name) / "out.csv"
        result = self.invoke("export", "--output", str(out), "--format", "csv")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("title", out.read_text())

    def test_export_unknown_project(self):
        out = Path(self.tmp.name) / "out.md"
        result = self.invoke("export", "--project", "Ghost", "--output", str(out))
        self.assertNotEqual(result.exit_code, 0)

    def test_import_json(self):
        path = Path(self.tmp.name) / "in.json"
        path.write_text(json.dumps([{"title": "Imported"}]), encoding="utf-8")
        result = self.invoke("import", "--input", str(path))
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Imported", result.output)

    def test_import_detects_csv(self):
        path = Path(self.tmp.name) / "in.csv"
        path.write_text("title\nFromCsv\n", encoding="utf-8")
        result = self.invoke("import", "--input", str(path))
        self.assertEqual(result.exit_code, 0)

    def test_import_unknown_extension_requires_format(self):
        path = Path(self.tmp.name) / "in.txt"
        path.write_text("title\nx\n", encoding="utf-8")
        result = self.invoke("import", "--input", str(path))
        self.assertNotEqual(result.exit_code, 0)


class TestCliHelp(CLITestCase):
    def test_root_help(self):
        result = self.invoke("--help")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("CLI Task Manager", result.output)

    def test_version_flag(self):
        result = self.invoke("--version")
        self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
