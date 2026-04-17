"""Multi-format exporter for tasks (Markdown, JSON, CSV)."""

import csv
import io
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from task_manager.database import TaskDB
from task_manager.models import Project, Task


_TASK_CSV_COLUMNS = [
    "id",
    "title",
    "description",
    "project",
    "priority",
    "status",
    "due_date",
    "created_at",
    "completed_at",
]


class ExporterError(Exception):
    """Raised on unexpected export failures."""


class MarkdownExporter:
    """Backwards-compatible Markdown exporter.

    Maintains the original public surface (`export_all`, `export_project`,
    `export_status`) while delegating to :class:`Exporter` for the heavy lifting.
    """

    def __init__(self, db: TaskDB):
        self.db = db
        self._exporter = Exporter(db)

    def export_all(self, output_path: str) -> str:
        return self._exporter.export_all(output_path, fmt="md")

    def export_project(self, project_name: str, output_path: str) -> str:
        return self._exporter.export_project(project_name, output_path, fmt="md")

    def export_status(self, status: str, output_path: str) -> str:
        return self._exporter.export_status(status, output_path, fmt="md")


class Exporter:
    """Unified exporter supporting markdown, json, and csv output."""

    def __init__(self, db: TaskDB):
        self.db = db

    # ---- Public API -----------------------------------------------------

    def export_all(self, output_path: str, fmt: str = "md") -> str:
        tasks = self.db.list_tasks()
        projects = self.db.list_projects()
        content = self._render(tasks, projects, title="All Tasks", fmt=fmt)
        self._write_file(output_path, content)
        return output_path

    def export_project(
        self, project_name: str, output_path: str, fmt: str = "md"
    ) -> str:
        tasks = self.db.get_project_tasks(project_name)
        projects = [p for p in self.db.list_projects() if p.name == project_name]
        content = self._render(
            tasks, projects, title=f"Project: {project_name}", fmt=fmt
        )
        self._write_file(output_path, content)
        return output_path

    def export_status(self, status: str, output_path: str, fmt: str = "md") -> str:
        tasks = self.db.list_tasks(status=status)
        status_labels = {
            "pending": "Pending Tasks",
            "in_progress": "In Progress Tasks",
            "done": "Completed Tasks",
        }
        content = self._render(
            tasks, [], title=status_labels.get(status, f"Tasks ({status})"), fmt=fmt
        )
        self._write_file(output_path, content)
        return output_path

    def export_tasks(
        self, tasks: List[Task], output_path: str, fmt: str = "md",
        title: str = "Tasks", projects: Optional[List[Project]] = None,
    ) -> str:
        """Export an arbitrary task list (used by bulk/today/overdue commands)."""
        content = self._render(tasks, projects or [], title=title, fmt=fmt)
        self._write_file(output_path, content)
        return output_path

    # ---- Dispatch -------------------------------------------------------

    def _render(
        self, tasks: List[Task], projects: List[Project], title: str, fmt: str
    ) -> str:
        fmt = fmt.lower()
        if fmt == "md":
            return self._render_markdown(tasks, projects, title)
        if fmt == "json":
            return self._render_json(tasks, projects, title)
        if fmt == "csv":
            return self._render_csv(tasks)
        raise ExporterError(f"Unsupported export format: {fmt!r}")

    # ---- Markdown -------------------------------------------------------

    def _render_markdown(
        self, tasks: List[Task], projects: List[Project], title: str
    ) -> str:
        lines: List[str] = []
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")

        if projects:
            lines.append("## Project Statistics")
            lines.append("")
            for project in projects:
                lines.append(f"### {project.name}")
                lines.append(f"- Total: {project.total} tasks")
                lines.append(f"- Pending: {project.pending}")
                lines.append(f"- In Progress: {project.in_progress}")
                lines.append(f"- Completed: {project.done}")
                lines.append(f"- Completion Rate: {project.completion_rate:.1f}%")
                lines.append("")

        if tasks:
            lines.append("## Tasks")
            lines.append("")

            tasks_by_project: dict = {}
            for task in tasks:
                tasks_by_project.setdefault(task.project, []).append(task)

            for project_name in sorted(tasks_by_project.keys()):
                project_tasks = tasks_by_project[project_name]
                lines.append(f"### {project_name}")
                lines.append("")

                by_status: dict = {"done": [], "in_progress": [], "pending": []}
                for task in project_tasks:
                    by_status.setdefault(task.status, []).append(task)

                for status in ["done", "in_progress", "pending"]:
                    status_tasks = by_status.get(status, [])
                    if not status_tasks:
                        continue
                    status_text = {
                        "done": "✅ Completed",
                        "in_progress": "🔄 In Progress",
                        "pending": "⭕ Pending",
                    }[status]
                    lines.append(f"#### {status_text}")
                    lines.append("")
                    for task in status_tasks:
                        lines.append(self._format_task_md(task))
                    lines.append("")
        else:
            lines.append("*No tasks found.*")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _format_task_md(task: Task) -> str:
        checkbox = "[x]" if task.status == "done" else "[ ]"
        line = (
            f"- {checkbox} **{task.title}** {task.priority_emoji} "
            f"({task.priority.capitalize()})"
        )
        if task.id:
            line += f" — ID: {task.id}"
        if task.due_date:
            line += f"\n  - Due: {task.due_date}"
        if task.description:
            line += f"\n  - Details: {task.description}"
        if task.completed_at:
            line += f"\n  - Completed: {task.completed_at}"
        return line

    # ---- JSON -----------------------------------------------------------

    def _render_json(
        self, tasks: List[Task], projects: List[Project], title: str
    ) -> str:
        payload = {
            "title": title,
            "generated_at": datetime.now().isoformat(),
            "tasks": [t.to_dict() for t in tasks],
            "projects": [p.to_dict() for p in projects],
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)

    # ---- CSV ------------------------------------------------------------

    def _render_csv(self, tasks: List[Task]) -> str:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=_TASK_CSV_COLUMNS)
        writer.writeheader()
        for task in tasks:
            data = task.to_dict()
            writer.writerow({k: ("" if data.get(k) is None else data[k]) for k in _TASK_CSV_COLUMNS})
        return buffer.getvalue()

    # ---- IO -------------------------------------------------------------

    @staticmethod
    def _write_file(path: str, content: str) -> None:
        file_path = Path(path)
        if file_path.parent and str(file_path.parent) not in ("", "."):
            file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")


def import_tasks_from_json(db: TaskDB, path: str) -> int:
    """Load tasks from a JSON file produced by Exporter.

    The file may either be a bare list of task dicts or the full export payload
    (``{"tasks": [...]}``). Returns the number of tasks imported.
    """
    content = Path(path).read_text(encoding="utf-8")
    data = json.loads(content)
    if isinstance(data, dict) and "tasks" in data:
        raw_tasks = data["tasks"]
    elif isinstance(data, list):
        raw_tasks = data
    else:
        raise ExporterError("Invalid import payload: expected list or {'tasks': [...]}")

    imported = 0
    for entry in raw_tasks:
        if not isinstance(entry, dict):
            continue
        entry = dict(entry)
        entry.pop("id", None)
        entry.pop("created_at", None)
        entry.pop("completed_at", None)
        task = Task.from_dict(entry)
        db.add_task(task)
        imported += 1
    return imported


def import_tasks_from_csv(db: TaskDB, path: str) -> int:
    """Load tasks from a CSV file with the same columns emitted by the CSV exporter."""
    imported = 0
    with open(path, newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            cleaned = {k: (v if v != "" else None) for k, v in row.items()}
            cleaned.pop("id", None)
            cleaned.pop("created_at", None)
            cleaned.pop("completed_at", None)
            if not cleaned.get("title"):
                continue
            task = Task.from_dict(cleaned)
            db.add_task(task)
            imported += 1
    return imported
