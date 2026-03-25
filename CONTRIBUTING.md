# Contributing to CLI Task Manager

Thank you for your interest in contributing to CLI Task Manager! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Focus on the code, not the person

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/cli-task-manager.git
cd cli-task-manager
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .

# Install dev dependencies (optional)
pip install pytest pytest-cov black flake8
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/your-bug-fix
```

## Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use meaningful variable names
- Keep functions focused and small
- Add docstrings to functions and classes

### Format Code

```bash
# Using black
black task_manager/ tests/

# Check with flake8
flake8 task_manager/ tests/
```

### Testing

All changes must include tests:

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test
python -m unittest tests.test_database.TestTaskDB.test_add_task -v

# Run with coverage
pytest tests/ --cov=task_manager --cov-report=html
```

### Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions
- Update DEMO.md with new examples
- Keep comments clear and concise

## Contribution Types

### Bug Fixes
1. Open an issue describing the bug
2. Create a fix with tests
3. Submit a pull request with "Fixes #issue-number"

### New Features
1. Discuss in an issue first
2. Implement with tests
3. Update documentation
4. Submit PR with description of changes

### Documentation
1. Fix typos or unclear sections
2. Add examples
3. Improve setup instructions

## Pull Request Process

1. **Ensure tests pass**
   ```bash
   python -m unittest discover tests -v
   ```

2. **Follow code style**
   ```bash
   black task_manager/ tests/
   flake8 task_manager/ tests/
   ```

3. **Update documentation**
   - Add docstrings
   - Update README if needed
   - Update DEMO.md with examples

4. **Create descriptive PR**
   - Clear title describing changes
   - Detailed description of what and why
   - Reference related issues
   - Include any breaking changes

5. **Respond to feedback**
   - Address review comments
   - Request re-review when done

## Reporting Issues

### Bug Reports
Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Error messages/logs

### Feature Requests
Include:
- Clear description of desired feature
- Use cases and examples
- Any related issues
- Suggested implementation (optional)

## Project Structure

```
cli-task-manager/
├── task_manager/           # Main package
│   ├── __init__.py
│   ├── cli.py              # CLI commands (click)
│   ├── database.py         # SQLite database layer
│   ├── models.py           # Data models
│   └── exporter.py         # Markdown export
├── tests/                  # Unit tests
│   ├── __init__.py
│   └── test_database.py
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── setup.py                # Installation script
└── README.md               # User documentation
```

## Key Areas for Contribution

### High Priority
- Additional export formats (JSON, CSV, XML)
- Task filtering improvements
- Performance optimizations
- Documentation improvements

### Medium Priority
- Additional commands
- UI improvements
- Database migrations
- Error handling

### Nice to Have
- Web interface
- Cloud sync
- Advanced search
- Recurring tasks
- Task templates

## Development Tips

### Testing During Development

```bash
# Quick manual test
python main.py add "Test task"
python main.py list

# Test specific functionality
python << 'EOF'
from task_manager.database import TaskDB
from task_manager.models import Task

db = TaskDB("/tmp/test.db")
task = Task(title="Test", priority="high")
task_id = db.add_task(task)
print(f"Created task {task_id}")
EOF
```

### Debugging

```bash
# Use Python debugger
python -m pdb main.py add "Debug task"

# Add print statements (remove before committing)
import sys
print("Debug info", file=sys.stderr)
```

### Documentation

Update docstrings for new code:

```python
def new_function(param1: str, param2: int) -> bool:
    """Short description of what function does.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something is invalid
    """
    pass
```

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
# Good
git commit -m "Add task search functionality"
git commit -m "Fix database connection timeout issue"
git commit -m "Update README with new examples"

# Avoid
git commit -m "fix stuff"
git commit -m "WIP"
git commit -m "asdf"
```

Format:
- Use present tense ("add" not "added")
- Be specific and descriptive
- Keep first line under 70 characters
- Add detailed description if needed

## Release Process

Version format: `MAJOR.MINOR.PATCH`

1. Update version in `task_manager/__init__.py`
2. Update version in `setup.py`
3. Update CHANGELOG.md
4. Create git tag: `git tag v1.0.0`
5. Create GitHub release with notes

## Additional Resources

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## Questions?

- Open an issue with [Question] prefix
- Check existing discussions
- Review documentation
- Look at existing code examples

---

Thank you for contributing! Your help makes this project better.
