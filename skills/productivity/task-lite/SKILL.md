---
name: task-lite
description: Simple task manager - add, list, complete tasks with today view
metadata: {"nanobot": {"always": false}}
---

# Task Manager (Lite)

Simple task tracking. No projects, no complexity.

## Commands

- `/task add <title>` - Add a task (optionally with "by <date>")
- `/task today` - Show tasks due today
- `/task done <id or partial title>` - Mark a task complete
- `/tasks` - List all pending tasks

## How to Handle

1. Read `{workspace}/memory/store.json`
2. Modify the `tasks` array
3. Write back to `{workspace}/memory/store.json`

### Adding a task

```json
{
  "id": "<8-char-hex>",
  "title": "renew insurance",
  "status": "pending",
  "due_at": "2026-02-20",
  "priority": "normal",
  "created_at": "<now>",
  "completed_at": null
}
```

### Completing a task

Match by ID or by title prefix (case-insensitive). Set `status` to `completed` and `completed_at` to now.

## Response Format

Adding:
```
Task added: <title>
Due: <date or "no deadline">
```

Listing:
```
Pending tasks:
- <title> | due <date> | <id>
- <title> | no deadline | <id>
```

Today:
```
Today's tasks:
- <title> | <id>
```

Done:
```
Completed: <title>
```

## Rules

- Max 5 lines per response
- No emojis
- Bullet points for lists
- If no tasks: "No pending tasks."
