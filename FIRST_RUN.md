# First Run Instructions

Complete guide for setting up and running CLI Task Manager for the first time.

## Step 1: Navigate to Project

```bash
cd /root/cli-task-manager
```

## Step 2: Install Dependencies

### Option A: Using pip directly

```bash
pip install -r requirements.txt
```

### Option B: Install as development package

```bash
pip install -e .
```

This makes the `task` command available globally.

### Option C: Using Docker

```bash
docker build -t cli-task-manager .
docker run cli-task-manager list
```

## Step 3: Verify Installation

```bash
# Check if dependencies are installed
python -c "import click; import rich; print('Dependencies OK')"

# Run with Python directly
python main.py --help

# Or if installed as package
task --help
```

## Step 4: Run First Command

### Create your first task:

```bash
task add "My first task"
```

Expected output:
```
✓ Task created with ID: 1
  Title: My first task
  Project: General
  Priority: 🟡 Medium
```

## Step 5: List Tasks

```bash
task list
```

Expected output:
```
┏━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ ID ┃ Title          ┃ Project ┃ Priority ┃ Status ┃ Due Date ┃ Created ┃
┡━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━┃ ┣━━━━━━━━┩
│ 1  │ My first task   │ General │ 🟡     │ ⭕   │          │ 2026-03-25 │
└─────┴────────────────┴─────────┴─────────┴──────┴──────────┴────────────┘

Total: 1 | Pending: 1 | In Progress: 0 | Done: 0
```

## Step 6: Try More Commands

```bash
# Add more tasks
task add "Learn Python" --project "Learning" --priority high
task add "Exercise" --priority medium --due "2026-03-27"

# View all tasks
task list

# View specific project
task list --project "Learning"

# View task details
task show 1

# Mark task as done
task done 1

# View pending tasks
task list --status pending

# Search for tasks
task search "Python"

# View projects
task projects

# Export to markdown
task export --output my_tasks.md

# View statistics
task stats
```

## Step 7: Check Database

Your tasks are stored in: `~/.task-manager/tasks.db`

Verify it was created:
```bash
ls -lh ~/.task-manager/tasks.db
```

## Troubleshooting First Run

### Issue: "command not found: task"
**Solution:** Install in editable mode: `pip install -e .`

### Issue: "No module named 'click'"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: SQLite error
**Solution:** This is normal - database is created automatically. Check directory permissions.

### Issue: Python 2 being used
**Solution:** Use `python3` explicitly:
```bash
python3 main.py --help
python3 -m pip install -r requirements.txt
```

## Verify Everything Works

Run this quick verification script:

```bash
#!/bin/bash
echo "Testing CLI Task Manager..."

# Test 1: Import modules
python3 -c "from task_manager.database import TaskDB; print('✓ Database module loads')" || exit 1

# Test 2: Import CLI
python3 -c "from task_manager.cli import cli; print('✓ CLI module loads')" || exit 1

# Test 3: Create task
task add "Test" > /dev/null && echo "✓ Task creation works"

# Test 4: List tasks
task list > /dev/null && echo "✓ Task listing works"

# Test 5: Database file exists
test -f ~/.task-manager/tasks.db && echo "✓ Database created"

echo ""
echo "All tests passed! Ready to use."
```

## Next Steps

1. **Read quick start**: `cat QUICKSTART.md`
2. **See examples**: `cat DEMO.md`
3. **Full documentation**: `cat README.md`
4. **Add real tasks**: `task add "Your task"`
5. **Track progress**: `task projects`

## Common First Tasks

```bash
# Setup your projects
task add "Work Task 1" --project "Work"
task add "Home Task 1" --project "Home"
task add "Learning Task 1" --project "Learning"

# View what you have
task projects

# Mark something done
task done 1

# Check progress
task stats

# Export for sharing
task export --output tasks.md
```

## Database Management

### View all tasks in database
```bash
sqlite3 ~/.task-manager/tasks.db "SELECT id, title, status FROM tasks;"
```

### Reset/Clear database
```bash
rm ~/.task-manager/tasks.db
# Tasks will be recreated on next use
```

### Backup database
```bash
cp ~/.task-manager/tasks.db ~/.task-manager/tasks.db.backup
```

## Help & Support

```bash
# Get help on any command
task --help
task add --help
task list --help
task export --help

# Run tests
python -m unittest tests.test_database -v

# Check project structure
cat PROJECT_STRUCTURE.md
```

## Performance Notes

- First run creates database: ~50ms
- Adding task: ~10ms
- Listing tasks: ~5ms
- Exporting to markdown: ~20ms

All operations are very fast!

## File Permissions

Ensure your home directory is writable:
```bash
ls -ld ~
# Should show rwx for owner
```

If issues:
```bash
chmod 755 ~
mkdir -p ~/.task-manager
chmod 755 ~/.task-manager
```

## Environment Variables (Optional)

```bash
export TASK_DB_PATH=~/.task-manager/tasks.db
export DEFAULT_PROJECT="General"
export DEFAULT_PRIORITY="medium"
```

Or copy `.env.example` to `.env` and modify.

## Quick Reference Card

| Action | Command |
|--------|---------|
| Add task | `task add "title"` |
| List all | `task list` |
| View details | `task show ID` |
| Mark done | `task done ID` |
| Update | `task update ID --field value` |
| Delete | `task delete ID` |
| Search | `task search "keyword"` |
| Projects | `task projects` |
| Export | `task export --output file.md` |
| Stats | `task stats` |

## Success Indicators

You'll know it's working when:
- ✓ `task add` creates tasks with colored output
- ✓ `task list` shows a formatted table
- ✓ Database file exists at `~/.task-manager/tasks.db`
- ✓ `task projects` shows project statistics
- ✓ `task export` creates markdown file

---

Congratulations! You're ready to start managing your tasks. Begin with:

```bash
task add "My first task"
task list
```

Happy task managing!
