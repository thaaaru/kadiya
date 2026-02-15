---
name: sl-telegram
description: Format messages for Telegram with markdown support
homepage: https://github.com/HKUDS/nanobot
metadata: {"nanobot":{"emoji":"✈️","requires":{}}}
---

# Telegram Message Formatter

Format text for Telegram: markdown-enabled, structured, with appropriate formatting.

## Usage

```
Format for Telegram: [your content here]
```

Or:
```
TG format: [your content here]
```

## Formatting Rules

1. **Length**: Keep under 1000 characters
2. **Markdown**: Use Telegram's MarkdownV2
3. **Headers**: Use **bold** for section titles
4. **Code**: Use `backticks` for technical terms
5. **Links**: Format as [text](url)

## Telegram MarkdownV2 Syntax

| Format | Syntax |
|--------|--------|
| Bold | `**text**` or `__text__` |
| Italic | `*text*` or `_text_` |
| Underline | `__text__` (double underscore) |
| Strikethrough | `~~text~~` |
| Code | `` `code` `` |
| Code block | ` ```language\ncode\n``` ` |
| Link | `[text](url)` |
| Spoiler | `\|\|spoiler\|\|` |

## Examples

### Technical Update

Input:
```
Format for Telegram: Server maintenance scheduled for Sunday 2AM to 4AM. All services will be offline. Backup your work.
```

Output:
```
🔧 **Server Maintenance**

📅 Sunday, 2:00 AM - 4:00 AM

⚠️ All services will be **offline**

Please backup your work before then.

Status: [status.example.com](https://status.example.com)
```

### Code Snippet Share

Input:
```
TG format: Here's how to connect to the database: use psycopg2.connect with host localhost and port 5432
```

Output:
```
📝 **Database Connection**

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432
)
```

Use `psycopg2.connect()` with your credentials.
```

### Event Information

Input:
```
Format for Telegram: Tech meetup next Saturday at TRACE Expert City, Maradana. Topic is AI in Sri Lanka. Free entry, register at meetup.lk/ai2024
```

Output:
```
🎯 **Tech Meetup: AI in Sri Lanka**

📅 Next Saturday
📍 TRACE Expert City, Maradana
💰 Free entry

🔗 [Register here](https://meetup.lk/ai2024)
```

## Token Limits

- Max output: 512 tokens
- Preserve structure over brevity
- Include relevant links
