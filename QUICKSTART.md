# Quick Start Guide

Get up and running with CLI Task Manager in 5 minutes.

## 1. Installation

```bash
# Navigate to project directory
cd /root/cli-task-manager

# Install dependencies
pip install -r requirements.txt

# Option A: Use directly with Python
python main.py --help

# Option B: Install as command (recommended)
pip install -e .
task --help
```

## 2. Create Your First Tasks

```bash
# Create a simple task
task add "Buy milk"

# Add task with more details
task add "Write report" --project "Work" --priority high --due "2026-04-01"

# Quick task with description
task add "Fix bug" --description "Navigation menu broken"
```

## 3. View Your Tasks

```bash
# See all tasks
task list

# See work tasks only
task list --project "Work"

# See only pending tasks
task list --status pending
```

## 4. Manage Tasks

```bash
# Complete a task (ID can be seen in list output)
task done 1

# View task details
task show 2

# Update a task
task update 3 --status in_progress

# Delete a task
task delete 4
```

## 5. Export and Share

```bash
# Export all tasks to markdown
task export --output my_tasks.md

# Export a specific project
task export --project "Work" --output work.md
```

## Key Commands

| Command | Purpose |
|---------|---------|
| `task add "..."` | Create new task |
| `task list` | Show all tasks |
| `task show ID` | View task details |
| `task done ID` | Mark task complete |
| `task delete ID` | Remove task |
| `task projects` | View project stats |
| `task search "..."` | Find tasks |
| `task export` | Save to markdown |
| `task stats` | Show overview |

## Common Patterns

### Daily standup
```bash
task list --project "Work" --status pending
```

### End of day review
```bash
task list --status done
task stats
```

### Weekly planning
```bash
task projects
task add "New task" --project "Next Week" --due "2026-04-01"
```

### Project tracking
```bash
task list --project "MyProject"
task update 1 --status in_progress
task done 1
```

## Tips

- Use `--project` to organize by work area
- Set `--due` dates to track deadlines
- Use `--priority high/medium/low` for focus
- Export to Markdown for sharing
- Check `task stats` for progress

## Database Location

Tasks are stored in: `~/.task-manager/tasks.db`

To reset: `rm ~/.task-manager/tasks.db`

## Need Help?

```bash
# Get help on any command
task add --help
task list --help
task --help

# See detailed documentation
# Read README.md or DEMO.md
```

## Next Steps

1. Check out [DEMO.md](DEMO.md) for examples
2. Read [README.md](README.md) for all features
3. Run `task stats` to track progress
4. Export to markdown: `task export --output tasks.md`

---

Happy task managing! Start by creating your first task:

```bash
task add "My first task"
task list
```
