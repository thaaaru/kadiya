---
name: daily-brief
description: Daily overview of tasks, reminders, follow-ups, and notes. Critical retention feature.
metadata: {"nanobot": {"always": true}}
---

# Daily Brief

Generate a structured overview of the user's day. This is a CRITICAL feature for user retention.

## Commands

- `/brief` - Today's overview
- `/brief tomorrow` - Tomorrow's overview

## How to Handle

1. Read `{workspace}/memory/store.json`
2. Get current date (Asia/Colombo timezone)
3. For "tomorrow", use next day's date
4. Compile overview from all memory sections

## Output Template (MANDATORY FORMAT)

For `/brief`:

```
Today - Quick Overview

Tasks:
- <pending tasks due today or overdue>

Reminders:
- <reminders scheduled for today>

Follow-Ups:
- <follow-ups due today or overdue>

Notes to Remember:
- <recent important notes from last 3 days>
```

For `/brief tomorrow`:

```
Tomorrow - Quick Overview

Tasks:
- <tasks due tomorrow>

Reminders:
- <reminders scheduled for tomorrow>

Follow-Ups:
- <follow-ups due tomorrow>

Suggested Prep:
- <any preparation needed based on tomorrow's items>
```

## Rules

- If a section is empty, show "Nothing scheduled"
- Show overdue items with "(overdue)" suffix
- Max 15 lines total
- No emojis
- Bullet points only
- Date format: "Mon 16 Feb"
- This skill should be suggested when user says "good morning" or similar greetings

## Night Summary

When triggered in the evening (after 18:00) or via `/brief tomorrow`, generate the tomorrow overview. This helps the user prepare for the next day.

## Empty State

If memory store has no data:

```
No items scheduled.
Use /task, /remind, or /note to start tracking.
```
