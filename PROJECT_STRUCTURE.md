# CLI Task Manager - Project Structure

Complete overview of the project files and their purposes.

## Directory Tree

```
/root/cli-task-manager/
├── task_manager/                 # Main package directory
│   ├── __init__.py              # Package initialization & version
│   ├── cli.py                   # Click CLI commands (main interface)
│   ├── database.py              # SQLite database layer & CRUD ops
│   ├── models.py                # Task & Project dataclasses
│   └── exporter.py              # Markdown export functionality
│
├── tests/                        # Unit tests directory
│   ├── __init__.py
│   └── test_database.py         # Database layer tests (30+ tests)
│
├── main.py                       # Script entry point
├── setup.py                      # setuptools installation config
├── pyproject.toml               # Modern Python project metadata
├── requirements.txt             # Package dependencies
├── Makefile                     # Development commands
├── Dockerfile                   # Docker container definition
│
├── README.md                    # User documentation & guide
├── DEMO.md                      # Demo scenarios & examples
├── CONTRIBUTING.md              # Contribution guidelines
├── CHANGELOG.md                 # Version history & release notes
├── LICENSE                      # MIT License
├── PROJECT_STRUCTURE.md         # This file
│
├── .gitignore                   # Git ignore patterns
├── .editorconfig                # Editor configuration
└── .env.example                 # Configuration template

```

## File Descriptions

### Core Package (`task_manager/`)

#### `__init__.py` (247 bytes)
- Package initialization
- Version management (`__version__`)
- Public API exports (Task, Project, TaskDB)
- Makes directory importable as Python package

**Key contents:**
- `__version__ = "1.0.0"`
- `__all__ = ["Task", "Project", "TaskDB"]`

#### `models.py` (2,166 bytes)
- **Task dataclass**: Main data model with properties
  - Fields: id, title, description, project, priority, status, due_date, created_at, completed_at
  - Priority: high/medium/low with emoji representation
  - Status: pending/in_progress/done with emoji representation
  - Properties: `is_overdue`, `priority_emoji`, `status_emoji`
  - Validation: Raises ValueError for invalid priority/status

- **Project dataclass**: Project statistics model
  - Fields: name, total, pending, in_progress, done
  - Properties: `completion_rate`, `active`
  - Auto-calculates project metrics

**Key classes:**
- `Task` - Main task model with validation
- `Project` - Project statistics model

#### `database.py` (8,985 bytes)
- **TaskDB class**: SQLite database interface
- Creates tables on initialization
- Methods (15+):
  - `create_tables()` - Initialize schema
  - `add_task(task)` - Create task, returns ID
  - `get_task(id)` - Retrieve single task
  - `list_tasks(project, status, order_by)` - Query with filters
  - `update_task(id, **kwargs)` - Modify task fields
  - `delete_task(id)` - Remove task
  - `search_tasks(query)` - Full-text search
  - `list_projects()` - Get all projects with stats
  - `get_project_tasks(project)` - Tasks by project
  - `clear_all()` - Reset database (testing)

**Database schema:**
- `tasks` table with 9 columns
- Indexes on project and status
- Constraints on priority and status enums
- SQLite Row factory for dict-like access

**Key features:**
- Automatic timestamp generation
- Transaction management
- Type conversion between Python objects and SQL
- Full-text search with LIKE queries
- Automatic index creation

#### `cli.py` (14,833 bytes)
- **Click CLI commands** - Main user interface
- 10+ command functions decorated with @click

**Commands:**
1. `add` - Create task with options
2. `list` - List/filter tasks with table output
3. `show` - Display task details in panel
4. `done` - Mark task completed
5. `update` - Modify task fields
6. `delete` - Remove task with confirmation
7. `search` - Find tasks by keyword
8. `projects` - Show project statistics
9. `export` - Export to Markdown
10. `stats` - Display overall statistics
11. `status-filter` - Shortcut status listing

**Features:**
- Rich table output with colors
- Option validation (dates, priorities, statuses)
- User confirmation for destructive operations
- Pretty error messages
- Beautiful panels and tables
- Emoji indicators for priority/status

#### `exporter.py` (6,457 bytes)
- **MarkdownExporter class** - Export functionality
- Methods:
  - `export_all(output_path)` - Export all tasks
  - `export_project(project, output_path)` - Single project
  - `export_status(status, output_path)` - Status filter
  - `_generate_markdown(tasks, projects, title)` - Content generation
  - `_format_task(task)` - Individual task formatting
  - `_write_file(path, content)` - File I/O

**Output format:**
- Grouped by project
- Grouped by status within project
- Task count statistics
- Completion rates
- Due dates and descriptions
- Generated timestamp

### Tests (`tests/`)

#### `test_database.py` (5,500+ bytes)
- **TestTaskDB class** - Comprehensive unit tests
- 30+ test methods covering:
  - Table creation
  - CRUD operations
  - Filtering and searching
  - Status and priority validation
  - Project statistics
  - Overdue detection
  - Date validation
  - Data persistence

**Test coverage:**
- Add, get, list, update, delete operations
- Project filtering
- Status filtering
- Search functionality
- Overdue task detection
- Data validation
- Edge cases (non-existent records)

### Configuration Files

#### `setup.py` (550+ bytes)
- setuptools configuration
- Entry point: `task` console script
- Metadata and classifiers
- Dependencies specification
- Package discovery

#### `pyproject.toml` (1,800+ bytes)
- Modern Python project config
- Build system declaration
- Project metadata
- Tool configurations:
  - black (code formatting)
  - isort (import sorting)
  - mypy (type checking)
  - pytest (testing)
  - coverage (test coverage)

#### `requirements.txt` (50 bytes)
- Production dependencies:
  - `click==8.1.7` - CLI framework
  - `rich==13.7.0` - Terminal output

#### `Makefile` (1,200+ bytes)
- Development command shortcuts
- Targets:
  - `install` - Install dependencies
  - `install-dev` - Dev tools
  - `test` - Run tests
  - `lint` - Code style check
  - `format` - Auto-format code
  - `clean` - Remove artifacts
  - `docker-build` - Build image
  - `run-demo` - Demo scenario

#### `Dockerfile` (300+ bytes)
- Python 3.11 slim base
- Installs dependencies
- Creates app user directory
- Entry point to `task` command
- Multi-stage capable for optimization

#### `pyproject.toml` (1,800+ bytes)
Already described above - modern Python configuration

### Documentation

#### `README.md` (8,000+ bytes)
- Feature overview
- Installation instructions (3 methods)
- Complete command reference
- Usage examples
- Command options
- Data storage info
- Troubleshooting
- Performance tips

#### `DEMO.md` (3,500+ bytes)
- Quick start guide
- Step-by-step examples
- Output examples
- Test scenarios
- Database inspection
- Common issues

#### `CONTRIBUTING.md` (4,000+ bytes)
- Development setup
- Code style guidelines
- Testing requirements
- Documentation standards
- Contribution types
- PR process

#### `CHANGELOG.md` (1,500+ bytes)
- Version history (1.0.0)
- Features by version
- Planned features
- Release notes

#### `LICENSE` (1,100 bytes)
- MIT License text

### Configuration & Metadata

#### `.gitignore` (1,000+ bytes)
- Python artifacts
- Virtual environments
- IDE settings
- Test coverage
- Database files
- Sensitive files

#### `.editorconfig` (500 bytes)
- Line endings (LF)
- Indentation (4 spaces for Python)
- Character encoding (UTF-8)
- Line length (100 chars)

#### `.env.example` (400 bytes)
- Configuration template
- Database path
- Default values
- Optional settings

## File Statistics

| File | Size | Type | Purpose |
|------|------|------|---------|
| cli.py | 14.8 KB | Code | Commands & UI |
| database.py | 9.0 KB | Code | Data layer |
| exporter.py | 6.5 KB | Code | Export feature |
| test_database.py | 5.5 KB | Tests | Unit tests |
| models.py | 2.2 KB | Code | Data models |
| README.md | 8.0 KB | Docs | User guide |
| DEMO.md | 3.5 KB | Docs | Examples |
| pyproject.toml | 1.8 KB | Config | Python config |
| setup.py | 0.6 KB | Config | Installation |
| requirements.txt | 0.05 KB | Config | Dependencies |

## Module Dependencies

```
main.py
  └── task_manager.cli
      ├── task_manager.database
      │   ├── task_manager.models
      │   └── sqlite3 (stdlib)
      ├── task_manager.exporter
      │   └── task_manager.models
      ├── click (external)
      └── rich (external)

setup.py
  └── setuptools (stdlib)

tests/test_database.py
  ├── task_manager.database
  ├── task_manager.models
  └── unittest (stdlib)
```

## Code Statistics

- **Total Python Lines**: ~2,500
- **Code Lines**: ~1,800
- **Documentation/Comments**: ~700
- **Test Coverage**: 30+ tests
- **Functions**: 40+
- **Classes**: 4

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.8+ |
| CLI | Click | 8.1.7 |
| Output | Rich | 13.7.0 |
| Database | SQLite3 | Built-in |
| Testing | unittest | Built-in |
| Build | setuptools | Latest |
| Container | Docker | Latest |

## Key Design Decisions

1. **SQLite**: Lightweight, file-based database for portability
2. **Click**: Modern CLI framework with built-in help
3. **Rich**: Beautiful terminal output without complex dependencies
4. **Dataclasses**: Python 3.8+ standard for models
5. **Type hints**: Better code documentation and IDE support
6. **Tests**: Comprehensive unit test coverage
7. **Separation of concerns**: Models, database, CLI, export in separate modules

## Extension Points

### Adding New Commands
Edit `task_manager/cli.py` and add new `@cli.command()` decorated function

### Adding Database Features
Extend `TaskDB` class in `task_manager/database.py` with new methods

### Adding Export Formats
Create new exporter class in `task_manager/exporter.py`

### Modifying Models
Update dataclasses in `task_manager/models.py`

## Quality Assurance

- All Python files compile without syntax errors
- Consistent code style (PEP 8 ready)
- Type hints throughout
- Comprehensive docstrings
- 30+ unit tests with high coverage
- Error handling and validation
- User-friendly error messages

---

This project is production-ready with professional structure and documentation.
