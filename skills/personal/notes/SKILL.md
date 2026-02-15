---
name: notes
description: Short notes - taggable, searchable, stored via structured memory
metadata: {"nanobot": {"always": false}}
---

# Notes & Memory

Quick notes with tags and search.

## Commands

- `/note <content>` - Save a note (auto-detect tags from content)
- `/notes` - List recent notes
- `/notes <tag>` - Filter notes by tag
- `/forget last` - Delete the most recent note
- `/forget all` - Delete all notes (ask confirmation first)
- `/export my data` - Export all memory data as JSON

## How to Handle

1. Read `{workspace}/memory/store.json`
2. Modify the `notes` array
3. Write back to `{workspace}/memory/store.json`

### Adding a note

Auto-detect tags from content keywords (health, work, family, finance, etc.).

```json
{
  "id": "<8-char-hex>",
  "content": "doctor said reduce sugar",
  "tags": ["health"],
  "created_at": "<now>"
}
```

### Tag detection rules

- health: doctor, medicine, hospital, sick, pain, sugar, blood
- work: office, meeting, deadline, boss, project, salary
- family: son, daughter, wife, husband, mother, father, school
- finance: bill, payment, loan, bank, salary, expense
- If no match, use empty tags

## Response Format

Adding:
```
Noted: <content>
Tags: <tags or "none">
```

Listing:
```
Recent notes:
- <content> [<tags>] | <date>
- <content> [<tags>] | <date>
```

## Rules

- Max 5 lines per response
- No emojis
- Show most recent first (max 10)
