---
name: reminder
description: Smart reminders with natural language, one-time and recurring, Asia/Colombo timezone
metadata: {"nanobot": {"always": false}}
---

# Smart Reminders

Set reminders using natural language. Supports one-time and recurring schedules.

## Commands

- `/remind <text> on <date/time>` - Set a one-time reminder
- `/remind every <pattern> <text>` - Set a recurring reminder
- `/reminders` - List all active reminders
- `/remind cancel <id>` - Cancel a reminder

## How to Handle

When the user sets a reminder:

1. Parse the natural language to extract: reminder text, trigger type (datetime or recurring), trigger value
2. Read the memory store at `{workspace}/memory/store.json`
3. Add a reminder entry to the `reminders` array:
   ```json
   {
     "id": "<8-char-hex>",
     "text": "pay electricity bill",
     "trigger": {"type": "datetime", "value": "2026-02-25T09:00:00"},
     "created_at": "<now>",
     "last_triggered_at": null
   }
   ```
4. If recurring, use the cron tool to schedule it
5. Respond with confirmation (max 3 lines)

## Date Parsing Rules

- "tomorrow" = next day 09:00 Asia/Colombo
- "on 25th" = 25th of current/next month 09:00
- "every monday 9am" = recurring weekly
- "in 3 days" = 3 days from now 09:00
- Default time is 09:00 if not specified
- Timezone: Asia/Colombo (UTC+5:30)

## Response Format

```
Reminder set: <text>
When: <formatted date/time>
ID: <id>
```

## Listing Format

```
Active reminders:
- <text> | <when> | <id>
- <text> | <when> | <id>
```

If no reminders: "No active reminders."

## Rules

- Max 5 lines per response
- No emojis
- Store in memory/store.json under "reminders" key
- Use write_file tool to update store.json
