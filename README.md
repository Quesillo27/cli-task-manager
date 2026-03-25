# CLI Task Manager

A powerful command-line task management tool built with Python, Click, and SQLite. Organize your tasks, projects, and deadlines efficiently from the terminal.

## Features

- **Create & Manage Tasks**: Add tasks with titles, descriptions, priorities, and due dates
- **Project Organization**: Group tasks by projects
- **Priority Levels**: Set task priority (high, medium, low)
- **Status Tracking**: Track task status (pending, in_progress, done)
- **Task Search**: Find tasks by keyword
- **Markdown Export**: Export tasks to beautifully formatted Markdown files
- **Project Statistics**: View project completion rates and task counts
- **Rich Output**: Beautiful tables and colored output using Rich library
- **SQLite Backend**: Lightweight, local database at `~/.task-manager/tasks.db`

## Installation

### Option 1: Install from repository (Development)

```bash
cd /root/cli-task-manager
pip install -e .
```

### Option 2: Install from requirements

```bash
cd /root/cli-task-manager
pip install -r requirements.txt
python main.py --help
```

### Option 3: Docker

```bash
docker build -t cli-task-manager .
docker run cli-task-manager list
```

## Usage

Once installed, use the `task` command:

```bash
task --help
```

### Basic Commands

#### Add a Task

```bash
# Simple task
task add "Buy groceries"

# Task with project and priority
task add "Write report" --project "Work" --priority high

# Task with due date
task add "Project deadline" --project "Work" --due "2026-04-15"

# Task with description
task add "Fix bug" --project "Dev" --priority high --description "Navigation menu not working" --due "2026-03-30"
```

#### List Tasks

```bash
# List all tasks
task list

# List by project
task list --project "Work"

# List by status
task list --status pending
task list --status done

# Sort by different criteria
task list --sort created
task list --sort due_date
task list --sort priority
```

#### View Task Details

```bash
task show 1
task show 5
```

#### Mark Task as Done

```bash
task done 1
task done 3
```

#### Update Task

```bash
# Update status
task update 1 --status in_progress

# Update priority
task update 2 --priority high

# Update multiple fields
task update 3 --status done --title "Updated title" --project "NewProject"

# Update due date
task update 4 --due "2026-04-20"

# Update description
task update 5 --description "New task details"
```

#### Delete Task

```bash
task delete 1
```

#### Search Tasks

```bash
# Search by keyword
task search "grocery"
task search "urgent"
```

#### View Projects

```bash
task projects
```

Output:
```
┏━━━━━━━━┳━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━┳━━━━━━━━━━┓
┃ Project ┃ Total ┃ Pending ┃ In Progress ┃ Done ┃ Completion ┃
┡━━━━━━━━╇━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━╇━━━━━━━━━━┩
│ Work    │  10  │   5    │     3     │  2  │    20%   │
│ Home    │   8  │   4    │     2     │  2  │    25%   │
│ General │   5  │   3    │     1     │  1  │    20%   │
└─────────┴───────┴──────────┴───────────┴─────┴──────────┘
```

#### Export to Markdown

```bash
# Export all tasks
task export --output tasks.md

# Export specific project
task export --project "Work" --output work_tasks.md

# Export by status
task export --status done --output completed.md
```

#### View Statistics

```bash
task stats
```

Output:
```
┏━━━━━━━━━━━━━━━━━━━━┓
┃ Task Statistics    ┃
├────────────────────┤
│ Overall Statistics │
│                    │
│ Total Tasks: 23    │
│ Pending: 12        │
│ In Progress: 6     │
│ Completed: 5       │
│ Overdue: 2         │
│                    │
│ Projects: 3        │
│ Completion Rate: 21.7% │
└────────────────────┘
```

## Command Reference

### Global Options

- `--help`: Show help message for any command

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Create a new task | `task add "Task title" --project "Work" --priority high` |
| `list` | List tasks with filters | `task list --project "Work" --status pending` |
| `show` | Show task details | `task show 1` |
| `done` | Mark task as completed | `task done 1` |
| `update` | Update task fields | `task update 1 --status in_progress` |
| `delete` | Delete a task | `task delete 1` |
| `search` | Search tasks | `task search "keyword"` |
| `projects` | List all projects | `task projects` |
| `export` | Export to Markdown | `task export --output tasks.md` |
| `stats` | View statistics | `task stats` |

### Command Options

#### `add` Command Options
- `--project`, `-p`: Project name (default: "General")
- `--priority`: Priority level: `high`, `medium`, `low` (default: "medium")
- `--due`: Due date in YYYY-MM-DD format
- `--description`, `-d`: Task description

#### `list` Command Options
- `--project`, `-p`: Filter by project
- `--status`, `-s`: Filter by status: `pending`, `in_progress`, `done`
- `--sort`: Sort by: `created`, `due_date`, `priority` (default: "created")

#### `update` Command Options
- `--status`, `-s`: New status
- `--priority`: New priority
- `--title`: New title
- `--project`, `-p`: New project
- `--due`: New due date
- `--description`, `-d`: New description

#### `export` Command Options
- `--project`, `-p`: Export specific project only
- `--status`, `-s`: Export specific status only
- `--output`, `-o`: Output file path (required)

## Data Storage

Tasks are stored in SQLite database located at:

```
~/.task-manager/tasks.db
```

The database is automatically created on first use. You can safely delete this file to reset all tasks.

## Project Structure

```
cli-task-manager/
├── task_manager/
│   ├── __init__.py        # Package init
│   ├── cli.py             # CLI commands using Click
│   ├── database.py        # SQLite database layer
│   ├── models.py          # Data models (Task, Project)
│   └── exporter.py        # Markdown exporter
├── tests/
│   ├── __init__.py
│   └── test_database.py   # Unit tests
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
├── setup.py               # Installation script
├── Dockerfile             # Docker configuration
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Dependencies

- **click**: CLI framework for building command-line interfaces
- **rich**: Library for rich text and beautiful formatting in terminal
- **sqlite3**: Built-in Python SQLite support (no external dependency)

## Running Tests

```bash
python -m pytest tests/
# or
python -m unittest tests.test_database
```

## Examples

### Complete Workflow

```bash
# Create a new project
task add "Design mockups" --project "Website" --priority high --due "2026-04-05"
task add "Setup database" --project "Website" --priority high --due "2026-04-10"
task add "API integration" --project "Website" --priority medium --due "2026-04-15"

# List project tasks
task list --project "Website"

# Start working on a task
task update 1 --status in_progress

# Complete a task
task done 1

# Check project progress
task projects

# Export for documentation
task export --project "Website" --output website_tasks.md

# View statistics
task stats
```

### Markdown Export Example

Generated markdown file structure:

```markdown
# All Tasks

*Generated on 2026-03-25 14:30:45*

## Project Statistics

### Work
- Total: 10 tasks
- Pending: 5
- In Progress: 3
- Completed: 2
- Completion Rate: 20.0%

## Tasks

### Work

#### ✅ Completed
- [x] **Complete project A** 🟢 (Low) — ID: 1
  - Due: 2026-03-20
  - Completed: 2026-03-22T14:30:00

#### 🔄 In Progress
- [ ] **Review documentation** 🟡 (Medium) — ID: 3
  - Due: 2026-04-01

#### ⭕ Pending
- [ ] **Setup CI/CD** 🔴 (High) — ID: 2
  - Due: 2026-03-30
  - Details: Configure GitHub Actions pipeline
```

## Troubleshooting

### Database file not found

If you see database errors, the database directory will be created automatically:

```bash
mkdir -p ~/.task-manager
```

### Permission errors

If you encounter permission errors, ensure you have write access to your home directory.

### SQLite errors

If the database becomes corrupted, you can reset it:

```bash
rm ~/.task-manager/tasks.db
```

This will delete all tasks. The database will be recreated on next use.

## Performance Tips

- Use `--project` filter when listing tasks from large databases
- Search is case-insensitive and uses full-text matching
- Database is indexed by project and status for fast queries

## Future Enhancements

- Recurring tasks
- Task categories/tags
- Due date notifications
- Task filtering by date range
- Bulk operations (delete/update multiple)
- Task history/changelog
- Export to JSON, CSV formats
- Web interface
- Cloud sync

## License

MIT License - Feel free to use this project for personal or commercial purposes.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Support

For issues or questions, please open an issue in the repository.

---

Made with Python, Click, and Rich. Happy task managing!
