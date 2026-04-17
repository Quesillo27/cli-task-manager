# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-17

### Added
- Modular package layout under `task_manager/commands/` (CRUD, bulk, filter, project, export command groups).
- Centralized configuration (`config.py`), structured logger (`logger.py`), reusable Rich renderers (`renderers.py`), shared validators (`validators.py`).
- JSON and CSV export formats (via `--format` on `export`).
- Import command (`task import --input FILE`) for JSON and CSV payloads.
- New commands: `today`, `overdue`, `upcoming`, `bulk-done`, `bulk-delete`, `clear`, `version`.
- `list --order asc/desc`, `list --limit`, `list --offset` (pagination).
- `TASK_MANAGER_DB` and `TASK_MANAGER_LOG_LEVEL` environment variables.
- `is_due_today` property on `Task`, `to_dict` / `from_dict` serializers on `Task` and `Project`.
- Integration test suite covering the Click CLI end-to-end; total tests grew **19 → 135**.

### Fixed
- **Security**: `list_tasks` now validates `order_by` and `direction` against an allowlist, blocking SQL injection via sort parameters.
- **Crash**: `stats` no longer errors on an empty database (prior division-by-zero / malformed f-string).
- `is_overdue` now compares dates at day granularity instead of date-vs-datetime.
- `MarkdownExporter` preserves backwards compatibility while the new `Exporter` handles multi-format output.

### Changed
- `update` always clears `completed_at` when moving out of `done`, and sets it when moving into `done`.
- `delete` now accepts `--yes` for non-interactive use (the Click confirmation still applies by default).
- Parent directories are created automatically when the SQLite path lives in a nested folder.

## [1.0.0] - 2026-03-25

### Added
- Initial release of CLI Task Manager
- Task creation with title, description, project, priority, and due date
- Task listing with filtering by project and status
- Task completion and status management
- Task deletion with confirmation
- Task search functionality
- Project management with task statistics
- Markdown export for all tasks, specific projects, or by status
- Task detail viewing
- Statistics dashboard
- Rich terminal output with colors and tables
- SQLite database backend
- Unit tests for database operations
- Docker support
- Comprehensive documentation

### Features
- **CRUD Operations**: Create, read, update, delete tasks
- **Filtering**: Filter by project, status, priority
- **Sorting**: Sort by creation date, due date, or priority
- **Search**: Full-text search across title and description
- **Export**: Markdown export with project grouping
- **Statistics**: Project completion rates and task counts
- **Status Tracking**: Pending, in progress, done statuses
- **Priority Levels**: High, medium, low priority support
- **Due Dates**: Track task deadlines with overdue detection

### Technical Details
- Built with Click for CLI framework
- Rich library for beautiful terminal output
- SQLite3 for local database storage
- Python 3.8+ compatible
- Fully type-hinted code
- Comprehensive docstrings
- 30+ unit tests

## Planned Features (Future Releases)

### [1.2.0] - Planned
- [ ] Recurring task support
- [ ] Task tags/categories
- [ ] Date range filtering
- [ ] Config file support (TOML)
- [ ] Shell completion (bash, zsh)

### [1.3.0] - Planned
- [ ] Task history/audit log
- [ ] Task templates
- [ ] Email/Slack notifications
- [ ] Task dependencies
- [ ] Kanban board view
- [ ] Web interface
- [ ] Cloud sync support

### [2.0.0] - Planned (was [1.3.0])
- [ ] Multi-user support
- [ ] Team collaboration features
- [ ] Web API
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Integrations (GitHub, Jira, etc.)

---

## Release Notes by Version

### 1.0.0 Release Highlights

This is the initial release of CLI Task Manager. All core features are implemented and tested.

**Key Features:**
- Lightweight: No external dependencies beyond click and rich
- Fast: SQLite provides instant performance
- Portable: Database stored in ~/.task-manager/
- Extensible: Well-structured code ready for enhancements

**Installation:**
```bash
pip install -e .
```

**Quick Start:**
```bash
task add "My first task"
task list
task done 1
```

For detailed usage, see [README.md](README.md) or run `task --help`
