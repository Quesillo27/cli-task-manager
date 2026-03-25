# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### [1.1.0] - Planned
- [ ] JSON and CSV export formats
- [ ] Recurring task support
- [ ] Task tags/categories
- [ ] Bulk operations (delete/update multiple)
- [ ] Date range filtering
- [ ] Config file support
- [ ] Shell completion (bash, zsh)

### [1.2.0] - Planned
- [ ] Task history/audit log
- [ ] Task templates
- [ ] Email/Slack notifications
- [ ] Task dependencies
- [ ] Kanban board view
- [ ] Web interface
- [ ] Cloud sync support

### [2.0.0] - Planned
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
