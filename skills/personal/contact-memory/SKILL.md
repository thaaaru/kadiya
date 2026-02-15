---
name: contact-memory
description: Remember key details about contacts. Lightweight personal CRM.
metadata: {"nanobot": {"always": false}}
---

# Contact Memory

Remember key details about people you interact with. Lightweight personal CRM.

## Commands

- `/contact <name> <detail>` - Save a detail about someone
- `/contact <name>` - Recall everything about someone
- `/contact list` - List all saved contacts

## How to Handle

1. Read `{workspace}/memory/store.json`
2. Modify the `contacts` array
3. Write back to `{workspace}/memory/store.json`

### Adding a detail

If contact exists, append to their `details` array. If new, create entry.

```json
{
  "name": "Nuwan",
  "details": [
    "works at Dialog",
    "birthday March 15",
    "prefers WhatsApp over calls"
  ],
  "last_updated": "2026-02-15T10:30:00"
}
```

### Recalling a contact

Search by name (case-insensitive). If no exact match, try prefix match.

### Detail types

- Preferences (communication, food, meeting times)
- Birthday or important dates
- Relationship (colleague, friend, client, vendor)
- Notes (anything the user wants to remember)
- Work details (company, role, department)

## Response Format

Adding:
```
Saved: <name> - <detail>
```

Recalling:
```
<name>:
- <detail 1>
- <detail 2>
- <detail 3>
Last updated: <date>
```

Listing:
```
Saved contacts:
- <name> (<number of details> details)
- <name> (<number of details> details)
```

If not found: "No contact found for '<name>'."

## Context Awareness

When the user mentions a person's name in conversation, check if that person exists in contacts. If so, silently use the stored details to provide more contextual responses. Do not proactively display contact info unless asked.

## Rules

- Max 5 lines per response for recall
- No emojis
- Privacy-first: all data stored locally only
- Never share contact info in responses to others
- Never include contact details in summaries shared externally
- Store in memory/store.json under "contacts" key
