"""Unit tests for the multi-format exporter."""

import json
import tempfile
import unittest
from pathlib import Path

from task_manager.database import TaskDB
from task_manager.exporter import (
    Exporter,
    ExporterError,
    MarkdownExporter,
    import_tasks_from_csv,
    import_tasks_from_json,
)
from task_manager.models import Task


class ExporterTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = TaskDB(str(Path(self.tmp.name) / "db.sqlite"))
        self.db.add_task(Task(title="T1", project="Work", priority="high"))
        self.db.add_task(Task(
            title="T2", project="Work", priority="low", status="done",
            description="Complete",
        ))
        self.db.add_task(Task(title="T3", project="Home", due_date="2030-01-01"))
        self.exporter = Exporter(self.db)

    def tearDown(self):
        self.tmp.cleanup()


class TestMarkdownExport(ExporterTestBase):
    def test_export_all_markdown(self):
        out = Path(self.tmp.name) / "all.md"
        self.exporter.export_all(str(out))
        body = out.read_text(encoding="utf-8")
        self.assertIn("# All Tasks", body)
        self.assertIn("T1", body)
        self.assertIn("T2", body)
        self.assertIn("T3", body)

    def test_export_project_markdown(self):
        out = Path(self.tmp.name) / "work.md"
        self.exporter.export_project("Work", str(out))
        body = out.read_text(encoding="utf-8")
        self.assertIn("Project: Work", body)
        self.assertIn("T1", body)
        self.assertNotIn("T3", body)

    def test_export_status_markdown(self):
        out = Path(self.tmp.name) / "done.md"
        self.exporter.export_status("done", str(out))
        body = out.read_text(encoding="utf-8")
        self.assertIn("Completed Tasks", body)
        self.assertIn("T2", body)

    def test_markdown_exporter_backwards_compat(self):
        out = Path(self.tmp.name) / "bc.md"
        MarkdownExporter(self.db).export_all(str(out))
        self.assertTrue(out.exists())


class TestJsonExport(ExporterTestBase):
    def test_export_all_json(self):
        out = Path(self.tmp.name) / "all.json"
        self.exporter.export_all(str(out), fmt="json")
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["title"], "All Tasks")
        self.assertEqual(len(data["tasks"]), 3)
        self.assertIn("generated_at", data)

    def test_json_contains_projects(self):
        out = Path(self.tmp.name) / "all.json"
        self.exporter.export_all(str(out), fmt="json")
        data = json.loads(out.read_text(encoding="utf-8"))
        names = {p["name"] for p in data["projects"]}
        self.assertEqual(names, {"Work", "Home"})

    def test_export_project_json(self):
        out = Path(self.tmp.name) / "work.json"
        self.exporter.export_project("Work", str(out), fmt="json")
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(len(data["tasks"]), 2)


class TestCsvExport(ExporterTestBase):
    def test_export_all_csv(self):
        out = Path(self.tmp.name) / "all.csv"
        self.exporter.export_all(str(out), fmt="csv")
        body = out.read_text(encoding="utf-8")
        lines = [line for line in body.splitlines() if line]
        self.assertEqual(len(lines), 4)  # header + 3 rows
        self.assertIn("title", lines[0])
        self.assertIn("T1", body)

    def test_csv_null_fields_become_empty(self):
        out = Path(self.tmp.name) / "all.csv"
        self.exporter.export_all(str(out), fmt="csv")
        body = out.read_text(encoding="utf-8")
        self.assertNotIn("None", body)


class TestExportErrors(ExporterTestBase):
    def test_unknown_format(self):
        out = Path(self.tmp.name) / "bad.xml"
        with self.assertRaises(ExporterError):
            self.exporter.export_all(str(out), fmt="xml")


class TestImport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = TaskDB(str(Path(self.tmp.name) / "db.sqlite"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_import_json_list(self):
        payload = [
            {"title": "X", "project": "P", "priority": "low"},
            {"title": "Y", "project": "P", "priority": "high"},
        ]
        path = Path(self.tmp.name) / "in.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        count = import_tasks_from_json(self.db, str(path))
        self.assertEqual(count, 2)
        self.assertEqual(self.db.count_tasks(), 2)

    def test_import_json_exported_payload(self):
        payload = {"tasks": [{"title": "Z"}]}
        path = Path(self.tmp.name) / "in.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual(import_tasks_from_json(self.db, str(path)), 1)

    def test_import_json_invalid_payload(self):
        path = Path(self.tmp.name) / "bad.json"
        path.write_text(json.dumps("not-a-list"), encoding="utf-8")
        with self.assertRaises(ExporterError):
            import_tasks_from_json(self.db, str(path))

    def test_import_csv(self):
        path = Path(self.tmp.name) / "in.csv"
        path.write_text(
            "title,project,priority\nA,Demo,high\nB,Demo,low\n",
            encoding="utf-8",
        )
        self.assertEqual(import_tasks_from_csv(self.db, str(path)), 2)
        self.assertEqual(self.db.count_tasks(), 2)

    def test_import_csv_skips_rows_without_title(self):
        path = Path(self.tmp.name) / "in.csv"
        path.write_text(
            "title,project\nA,Demo\n,Demo\n",
            encoding="utf-8",
        )
        self.assertEqual(import_tasks_from_csv(self.db, str(path)), 1)

    def test_import_json_is_atomic_on_invalid_task(self):
        payload = [{"title": "Valid"}, {"title": "", "priority": "high"}]
        path = Path(self.tmp.name) / "bad.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(ExporterError):
            import_tasks_from_json(self.db, str(path))
        self.assertEqual(self.db.count_tasks(), 0)

    def test_import_csv_is_atomic_on_invalid_row(self):
        path = Path(self.tmp.name) / "bad.csv"
        path.write_text(
            "title,priority\nValid,high\nBroken,urgent\n",
            encoding="utf-8",
        )
        with self.assertRaises(ExporterError):
            import_tasks_from_csv(self.db, str(path))
        self.assertEqual(self.db.count_tasks(), 0)


if __name__ == "__main__":
    unittest.main()
