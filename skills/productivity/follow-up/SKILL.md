---
name: follow-up
description: Track things you're waiting on from others. Auto-remind after 3 days.
metadata: {"nanobot": {"always": false}}
---

# Follow-Up Tracker

Track things you're waiting on from other people.

## Commands

- `/follow <person> <topic>` - Add a follow-up
- `/follow list` - Show all pending follow-ups
- `/follow done <id>` - Mark a follow-up as resolved

## How to Handle

1. Read `{workspace}/memory/store.json`
2. Modify the `followups` array
3. Write back to `{workspace}/memory/store.json`

### Adding a follow-up

```json
{
  "id": "<8-char-hex>",
  "person": "Nuwan",
  "topic": "send updated proposal",
  "date_added": "2026-02-15T10:30:00",
  "status": "pending",
  "remind_after": "2026-02-18T09:00:00"
}
```

### Completing a follow-up

Match by ID or by person name (case-insensitive). Set `status` to `resolved`.

### Auto-remind logic

- `remind_after` is set to 3 days after `date_added` at 09:00 Asia/Colombo
- If current date is past `remind_after` and status is still `pending`, flag as overdue
- Show overdue items in daily brief

## Response Format

Adding:
```
Follow-up added: <person> - <topic>
Remind after: <date>
ID: <id>
```

Listing:
```
Pending follow-ups:
- <person>: <topic> | added <date> | <id>
- <person>: <topic> | added <date> (overdue) | <id>
```

Done:
```
Resolved: <person> - <topic>
```

If no follow-ups: "No pending follow-ups."

## Rules

- Max 5 lines per response
- No emojis
- Bullet points only
- Date format: ISO 8601
- Timezone: Asia/Colombo (UTC+5:30)
- Show overdue items with "(overdue)" suffix
- Store in memory/store.json under "followups" key
