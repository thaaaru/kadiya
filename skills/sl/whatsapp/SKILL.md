---
name: sl-whatsapp
description: Format messages for WhatsApp (concise, emoji-friendly)
homepage: https://github.com/HKUDS/nanobot
metadata: {"nanobot":{"emoji":"💬","requires":{}}}
---

# WhatsApp Message Formatter

Format text for WhatsApp: concise, mobile-friendly, with appropriate emojis.

## Usage

```
Format for WhatsApp: [your content here]
```

Or:
```
WA format: [your content here]
```

## Formatting Rules

1. **Length**: Keep under 500 characters
2. **Emojis**: Use sparingly (1-3 max)
3. **Line breaks**: Use for readability
4. **Bold**: Use *asterisks* for emphasis
5. **Lists**: Use bullet points (•) or numbers

## Examples

### Notice/Announcement

Input:
```
Format for WhatsApp: Tomorrow's meeting has been postponed to 3 PM due to the workshop. Please confirm attendance.
```

Output:
```
📅 *Meeting Update*

Tomorrow's meeting postponed to 3 PM
(Workshop conflict)

Please reply to confirm ✅
```

### Quick Update

Input:
```
WA format: The package has been shipped and will arrive in 2-3 days. Tracking number is LK123456789.
```

Output:
```
📦 *Shipped!*

Arrives: 2-3 days
Track: LK123456789
```

### Event Reminder

Input:
```
Format for WhatsApp: Reminder about the company dinner next Friday at 7PM at Kingsbury Hotel. Dress code is smart casual.
```

Output:
```
🍽️ *Dinner Reminder*

📅 Next Friday, 7 PM
📍 Kingsbury Hotel
👔 Smart casual

See you there! 🎉
```

## Token Limits

- Max output: 256 tokens
- Compress long content
- Prioritize key information
