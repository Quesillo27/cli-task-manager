# CLI Task Manager - Demo & Testing Guide

This document provides examples and demonstrations of all CLI Task Manager features.

## Setup

### Installation

```bash
# Navigate to project directory
cd /root/cli-task-manager

# Install dependencies
pip install -r requirements.txt

# Option 1: Run directly
python main.py --help

# Option 2: Install as package and use 'task' command
pip install -e .
task --help
```

## Quick Start Demo

### 1. Create Some Tasks

```bash
# Create a work project with high priority task
task add "Complete project proposal" --project "Work" --priority high --due "2026-03-30" --description "Write and review Q2 project proposal"

# Add more work tasks
task add "Review code changes" --project "Work" --priority high --due "2026-03-28"
task add "Update documentation" --project "Work" --priority medium --due "2026-04-05"
task add "Attend team meeting" --project "Work" --priority medium --due "2026-03-26"

# Personal tasks
task add "Buy groceries" --project "Home" --priority medium --due "2026-03-27" --description "Milk, eggs, bread, chicken"
task add "Fix kitchen sink" --project "Home" --priority high --due "2026-03-26"
task add "Paint living room" --project "Home" --priority low --due "2026-04-10"

# General tasks
task add "Exercise" --priority medium --due "2026-03-26"
task add "Read book" --priority low
```

### 2. List Tasks

```bash
# List all tasks (sorted by creation date, most recent first)
task list

# List only work tasks
task list --project "Work"

# List only pending tasks
task list --status pending

# List only completed tasks
task list --status done

# List tasks sorted by due date
task list --sort due_date

# List high priority pending tasks
task list --status pending --sort priority
```

### 3. View Task Details

```bash
# Show task with ID 1
task show 1

# Show task with ID 3
task show 3
```

### 4. Update Tasks

```bash
# Start working on task 1
task update 1 --status in_progress

# Complete task 2
task done 2

# Change task priority and due date
task update 3 --priority high --due "2026-04-01"

# Update task title and description
task update 4 --title "Team sync meeting" --description "Discuss sprint progress and blockers"
```

### 5. Search Tasks

```bash
# Search for "kitchen"
task search "kitchen"

# Search for "document"
task search "document"

# Search for "meeting"
task search "meeting"
```

### 6. View Projects

```bash
# Show all projects with statistics
task projects

# Output:
# ┏━━━━━━━━┳━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━┳━━━━━━━━━━┓
# ┃ Project ┃ Total ┃ Pending ┃ In Progress ┃ Done ┃ Completion ┃
# ┡━━━━━━━━╇━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━╇━━━━━━━━━━┩
# │ Work    │   4  │   2    │     1     │  1  │    25%   │
# │ Home    │   3  │   3    │     0     │  0  │     0%   │
# │ General │   1  │   1    │     0     │  0  │     0%   │
# └─────────┴───────┴──────────┴───────────┴─────┴──────────┘
```

### 7. Export to Markdown

```bash
# Export all tasks to file
task export --output /tmp/all_tasks.md

# Export only Work project
task export --project "Work" --output /tmp/work_tasks.md

# Export only completed tasks
task export --status done --output /tmp/completed.md

# Check the files
cat /tmp/all_tasks.md
cat /tmp/work_tasks.md
```

### 8. View Statistics

```bash
task stats

# Output:
# ┏────────────────────┓
# ┃ Task Statistics    ┃
# ├────────────────────┤
# │ Overall Statistics │
# │                    │
# │ Total Tasks: 8     │
# │ Pending: 5         │
# │ In Progress: 1     │
# │ Completed: 1       │
# │ Overdue: 0         │
# │                    │
# │ Projects: 3        │
# │ Completion Rate: 12.5% │
# └────────────────────┘
```

### 9. Delete Tasks

```bash
# Delete task 5 (with confirmation)
task delete 5

# Delete task 6
task delete 6
```

## Expected Output Examples

### list command
```
┏━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┓
┃ ID ┃ Title           ┃ Project ┃ Priority ┃ Status   ┃ Due Date ┃ Created ┃
┡━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━┩
│ 1  │ Complete...     │ Work    │ 🔴     │ ⭕     │ 2026-03-30 │ 2026-03-25 │
│ 2  │ Review code...  │ Work    │ 🔴     │ ✅     │ 2026-03-28 │ 2026-03-25 │
│ 3  │ Update doc...   │ Work    │ 🟡     │ ⭕     │ 2026-04-05 │ 2026-03-25 │
│ 4  │ Attend team...  │ Work    │ 🟡     │ ⭕     │ 2026-03-26 │ 2026-03-25 │
│ 5  │ Buy groceries   │ Home    │ 🟡     │ ⭕     │ 2026-03-27 │ 2026-03-25 │
│ 6  │ Fix kitchen...  │ Home    │ 🔴     │ ⭕     │ 2026-03-26 │ 2026-03-25 │
│ 7  │ Paint living... │ Home    │ 🟢     │ ⭕     │ 2026-04-10 │ 2026-03-25 │
│ 8  │ Exercise        │ General │ 🟡     │ ⭕     │ 2026-03-26 │ 2026-03-25 │
└────┴─────────────────┴─────────┴──────────┴──────────┴────────────┴──────────┘

Total: 8 | Pending: 6 | In Progress: 1 | Done: 1
```

### show command
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Task #1                              ┃
├────────────────────────────────────────┤
│ Complete project proposal             │
│                                        │
│ Project: Work                          │
│ Priority: 🔴 High                    │
│ Status: ⭕ Pending                   │
│                                        │
│ ID: 1                                 │
│ Created: 2026-03-25T14:30:00         │
│ Due: 2026-03-30                       │
│                                        │
│ Description:                          │
│ Write and review Q2 project proposal │
└────────────────────────────────────────┘
```

### projects command
```
┏━━━━━━━━┳━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━┳━━━━━━━━━┓
┃ Project ┃ Total ┃ Pending ┃ In Progress ┃ Done ┃ Completion ┃
┡━━━━━━━━╇━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━╇━━━━━━━━┩
│ General │   1  │   1    │     0     │  0  │    0%  │
│ Home    │   3  │   2    │     0     │  1  │   33%  │
│ Work    │   4  │   2    │     1     │  1  │   25%  │
└─────────┴───────┴──────────┴───────────┴─────┴────────┘
```

## Test Scenarios

### Scenario 1: New User Setup

```bash
# User creates first task
task add "Get started with task manager"

# Views it
task list

# Adds more tasks
task add "Learn Python"
task add "Practice coding"

# Check progress
task projects
```

### Scenario 2: Work Project Management

```bash
# Create work sprint tasks
task add "Feature A: User authentication" --project "Sprint1" --priority high --due "2026-04-01"
task add "Feature B: Database optimization" --project "Sprint1" --priority high --due "2026-04-05"
task add "Bugfix: Login timeout" --project "Sprint1" --priority medium --due "2026-03-28"
task add "Docs: API documentation" --project "Sprint1" --priority low --due "2026-04-10"

# Start work
task update 1 --status in_progress

# Complete tasks
task done 3

# Export for reporting
task export --project "Sprint1" --output sprint_report.md

# Check progress
task projects
```

### Scenario 3: Personal Task Management

```bash
# Home maintenance
task add "Spring cleaning" --project "Home" --priority low --due "2026-04-15"
task add "Fix door hinge" --project "Home" --priority medium --due "2026-03-28"
task add "Plant garden" --project "Home" --priority low --due "2026-04-20"

# Hobbies
task add "Read 'Clean Code'" --project "Learning" --priority medium --due "2026-05-01"
task add "Practice guitar" --project "Learning" --priority medium

# List all Home tasks
task list --project "Home"

# Complete some
task done 2
task done 4

# View stats
task stats
```

### Scenario 4: Search and Filter

```bash
# Search for specific tasks
task search "document"
task search "meeting"
task search "urgent"

# Filter by status
task list --status pending
task list --status in_progress
task list --status done

# Find overdue tasks (will show in red)
task list --sort due_date
```

## Database Inspection

The database is stored at `~/.task-manager/tasks.db`. You can inspect it:

```bash
# Using sqlite3 CLI
sqlite3 ~/.task-manager/tasks.db ".tables"
sqlite3 ~/.task-manager/tasks.db "SELECT * FROM tasks LIMIT 5;"

# Or view in Python
python3 << 'EOF'
from task_manager.database import TaskDB
db = TaskDB()
tasks = db.list_tasks()
for task in tasks[:3]:
    print(f"Task #{task.id}: {task.title} ({task.status})")
EOF
```

## Performance Testing

```bash
# Create many tasks
for i in {1..100}; do
    task add "Task $i" --project "Bulk" --priority $((RANDOM % 3 + 1)) &
done

# List all (should be fast)
time task list

# Filter by project
time task list --project "Bulk"

# Search (full-text search)
time task search "Task"
```

## Unit Tests

```bash
# Run tests
python -m unittest tests.test_database -v

# Or with pytest if installed
pytest tests/ -v

# Test specific functionality
python -m unittest tests.test_database.TestTaskDB.test_add_task -v
python -m unittest tests.test_database.TestTaskDB.test_search_tasks -v
```

## Common Issues & Solutions

### Issue: "task: command not found"
**Solution**: Either use `python main.py` or install with `pip install -e .`

### Issue: Database errors
**Solution**: Delete the database file `rm ~/.task-manager/tasks.db` (data will be lost)

### Issue: Permission errors
**Solution**: Ensure write access to home directory

### Issue: No tasks showing
**Solution**: Make sure you've created tasks first with `task add`

## Tips & Tricks

- Use `--project` filter to work with specific projects
- Set `--due` dates in YYYY-MM-DD format
- Search is case-insensitive and searches both title and description
- Mark tasks as `in_progress` before marking `done`
- Export to markdown for sharing or archiving
- Use priority levels to focus on important work
- Check `task stats` regularly to track progress

## Next Steps

1. Customize the project for your workflow
2. Create projects that match your real work structure
3. Set up a cron job to remind about overdue tasks
4. Export tasks regularly for backups
5. Share exported markdown files with team members

---

Happy task managing!
