# CLI Task Manager

![tests](https://img.shields.io/badge/tests-135%20passing-brightgreen)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

A production-grade command-line task manager built with Python, Click, Rich and SQLite. Organize tasks across projects, track priorities and deadlines, and export to Markdown / JSON / CSV — all from the terminal.

---

## Features

- **CRUD**: add, list, show, update, done, delete tasks
- **Projects**: auto-grouped tasks with completion statistics
- **Filters**: by project, status, priority, due date
- **Time-based views**: `today`, `overdue`, `upcoming --days N`
- **Bulk operations**: `bulk-done`, `bulk-delete`, `clear`
- **Export**: Markdown, JSON, CSV formats
- **Import**: JSON and CSV round-trip
- **Pagination**: `--limit` / `--offset` on `list`
- **Structured logger** (env-var controlled, silent by default)
- **Configurable DB path** via `TASK_MANAGER_DB`
- **SQLite backend** — zero external services

## Installation

```bash
git clone https://github.com/Quesillo27/cli-task-manager.git
cd cli-task-manager
pip install -e .
task --help
```

Docker:

```bash
docker build -t cli-task-manager .
docker run --rm -v $HOME/.task-manager:/root/.task-manager cli-task-manager list
```

## Quickstart

```bash
task add "Write report" --project Work --priority high --due 2026-04-30
task add "Review PR" --project Work --priority medium
task list
task done 1
task stats
task export --output tasks.md
```

## Command reference

### Task CRUD

| Command | Description |
|---|---|
| `add TITLE [--project P] [--priority P] [--due YYYY-MM-DD] [--description TEXT]` | Create a new task |
| `list [--project P] [--status S] [--sort KEY] [--order asc/desc] [--limit N] [--offset N]` | List with filters, sort and pagination |
| `show ID` | Display full task details |
| `update ID [--status] [--priority] [--title] [--project] [--due] [--description]` | Update fields |
| `done ID` | Mark a task as completed |
| `delete ID [--yes]` | Delete a task (confirmation unless `--yes`) |
| `search QUERY` | Full-text search on title + description |

### Time filters

| Command | Description |
|---|---|
| `today` | List tasks due today (non-completed) |
| `overdue` | List tasks past their due date and not done |
| `upcoming --days N` | List tasks due within the next N days |

### Bulk operations

| Command | Description |
|---|---|
| `bulk-done ID1 ID2 …` | Mark multiple tasks as done in one transaction |
| `bulk-delete ID1 ID2 … [--yes]` | Delete multiple tasks |
| `clear [--yes]` | Wipe the whole database |

### Projects & stats

| Command | Description |
|---|---|
| `projects` | List every project with task counts and completion rate |
| `stats` | Aggregate statistics across all tasks |
| `version` | Show installed version |

### Import / Export

| Command | Description |
|---|---|
| `export --output FILE [--format md/json/csv] [--project P] [--status S]` | Export tasks to Markdown, JSON or CSV |
| `import --input FILE [--format json/csv]` | Import from JSON or CSV (auto-detected by extension) |

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `TASK_MANAGER_DB` | `~/.task-manager/tasks.db` | Override the SQLite file path |
| `TASK_MANAGER_LOG_LEVEL` | `WARNING` | Logger verbosity (`DEBUG`/`INFO`/`WARNING`/`ERROR`) |

## Project layout

```
task_manager/
├── __init__.py
├── cli.py                  # Click root group — wires commands together
├── config.py               # Constants, defaults, env-var resolution
├── database.py             # SQLite layer (parameterized queries)
├── exporter.py             # Markdown / JSON / CSV exporter + importer
├── logger.py               # Structured logger
├── models.py               # Task, Project dataclasses
├── renderers.py            # Reusable Rich tables / panels
├── validators.py           # Input validation helpers
└── commands/
    ├── task_cmds.py        # add / list / show / update / done / delete / search
    ├── project_cmds.py     # projects / stats / version
    ├── filter_cmds.py      # today / overdue / upcoming
    ├── bulk_cmds.py        # bulk-done / bulk-delete / clear
    └── export_cmds.py      # export / import

tests/
├── test_cli.py             # 39 Click runner tests
├── test_database.py        # 38 DB integration tests
├── test_exporter.py        # 15 format tests (MD, JSON, CSV, import)
├── test_models.py          # 20 model + serialization tests
└── test_validators.py      # 23 validator tests
```

## Development

```bash
make install-dev       # deps + pytest + black + flake8 + mypy
make test              # run the suite (135 tests)
make test-coverage     # coverage report (htmlcov/)
make lint              # flake8
make format            # black
```

## Security & data integrity notes

- All SQL queries use **parameterized statements**. `list_tasks` now rejects any `order_by` / `direction` value that isn't on an allowlist, preventing SQL injection through sort parameters.
- `stats` is safe on an empty database (no division-by-zero).
- `update` preserves `completed_at` semantics: set on `done`, cleared when reverting to pending/in_progress.
- Bulk operations use a single transaction each — partial failures roll back.

## Roadmap

Larger features worth their own sprint:

- **Recurring tasks** — cron-style schedules with automatic instance creation
- **Tags / labels** — many-to-many taxonomy independent from projects
- **Due-date notifications** — local / email / Telegram via the notification-service sibling project
- **Web UI** — Flask / FastAPI dashboard reading the same SQLite file
- **Cloud sync** — S3 / Dropbox backend, merge conflict handling
- **Task history & undo** — per-task audit log
- **JSON Schema validation** on import
- **i18n** of CLI messages

## License

MIT — see `LICENSE`.
