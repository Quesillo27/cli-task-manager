"""Markdown exporter for tasks."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from task_manager.models import Task
from task_manager.database import TaskDB


class MarkdownExporter:
    """Export tasks to Markdown format."""

    def __init__(self, db: TaskDB):
        """Initialize exporter with database instance.

        Args:
            db: TaskDB instance
        """
        self.db = db

    def export_all(self, output_path: str) -> str:
        """Export all tasks to markdown file.

        Args:
            output_path: Path where to save the markdown file

        Returns:
            Path to the created file
        """
        tasks = self.db.list_tasks()
        projects = self.db.list_projects()

        markdown = self._generate_markdown(tasks, projects, "All Tasks")
        self._write_file(output_path, markdown)

        return output_path

    def export_project(self, project_name: str, output_path: str) -> str:
        """Export tasks from a specific project.

        Args:
            project_name: Project name to export
            output_path: Path where to save the markdown file

        Returns:
            Path to the created file
        """
        tasks = self.db.get_project_tasks(project_name)
        projects = [p for p in self.db.list_projects() if p.name == project_name]

        markdown = self._generate_markdown(tasks, projects, f"Project: {project_name}")
        self._write_file(output_path, markdown)

        return output_path

    def export_status(self, status: str, output_path: str) -> str:
        """Export tasks with a specific status.

        Args:
            status: Status to filter (pending, in_progress, done)
            output_path: Path where to save the markdown file

        Returns:
            Path to the created file
        """
        tasks = self.db.list_tasks(status=status)
        status_labels = {
            "pending": "Pending Tasks",
            "in_progress": "In Progress Tasks",
            "done": "Completed Tasks"
        }

        markdown = self._generate_markdown(tasks, [], status_labels.get(status, f"Tasks ({status})"))
        self._write_file(output_path, markdown)

        return output_path

    def _generate_markdown(
        self,
        tasks: List[Task],
        projects: List,
        title: str = "Tasks"
    ) -> str:
        """Generate markdown content.

        Args:
            tasks: List of tasks to export
            projects: List of projects (for statistics)
            title: Main title for the document

        Returns:
            Markdown content as string
        """
        lines = []

        # Header
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")

        # Project statistics
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

        # Tasks grouped by project
        if tasks:
            lines.append("## Tasks")
            lines.append("")

            # Group tasks by project
            tasks_by_project = {}
            for task in tasks:
                if task.project not in tasks_by_project:
                    tasks_by_project[task.project] = []
                tasks_by_project[task.project].append(task)

            # Write tasks by project
            for project_name in sorted(tasks_by_project.keys()):
                project_tasks = tasks_by_project[project_name]
                lines.append(f"### {project_name}")
                lines.append("")

                # Group by status
                by_status = {"done": [], "in_progress": [], "pending": []}
                for task in project_tasks:
                    by_status[task.status].append(task)

                for status in ["done", "in_progress", "pending"]:
                    status_tasks = by_status[status]
                    if not status_tasks:
                        continue

                    status_text = {
                        "done": "✅ Completed",
                        "in_progress": "🔄 In Progress",
                        "pending": "⭕ Pending"
                    }[status]

                    lines.append(f"#### {status_text}")
                    lines.append("")

                    for task in status_tasks:
                        lines.append(self._format_task(task))

                    lines.append("")

        else:
            lines.append("*No tasks found.*")
            lines.append("")

        return "\n".join(lines)

    def _format_task(self, task: Task) -> str:
        """Format a single task as markdown.

        Args:
            task: Task to format

        Returns:
            Markdown formatted task
        """
        # Checkbox for completion
        checkbox = "[x]" if task.status == "done" else "[ ]"

        # Priority indicator
        priority_emoji = task.priority_emoji
        priority_text = task.priority.capitalize()

        # Build task line
        line = f"- {checkbox} **{task.title}** {priority_emoji} ({priority_text})"

        # Add ID if available
        if task.id:
            line += f" — ID: {task.id}"

        # Add due date if available
        if task.due_date:
            line += f"\n  - Due: {task.due_date}"

        # Add description if available
        if task.description:
            line += f"\n  - Details: {task.description}"

        # Add completion info
        if task.completed_at:
            line += f"\n  - Completed: {task.completed_at}"

        return line

    @staticmethod
    def _write_file(path: str, content: str) -> None:
        """Write content to file.

        Args:
            path: File path
            content: Content to write
        """
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
