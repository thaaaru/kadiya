---
name: message-rewrite
description: Rewrite messages in different tones - polite, formal, casual. Sinhala/English/Singlish.
metadata: {"nanobot": {"always": false}}
---

# Message Rewriter

Rewrite messages in different tones and languages. Office-safe default tone.

## Commands

- `/rewrite polite <text>` - Make it polite
- `/rewrite formal <text>` - Make it formal/professional
- `/rewrite casual <text>` - Make it casual/friendly
- `/rewrite formal sinhala <text>` - Formal in Sinhala
- `/rewrite <text>` - Default: polite English

## How to Handle

1. Extract the tone from the command
2. Extract the target language (default: same as input)
3. Rewrite the message in the requested tone
4. Respond with ONLY the rewritten text

## Tone Guidelines

### Polite
- Add greetings if appropriate
- Soften demands into requests
- Add "please", "thank you", "would you mind"
- Sri Lankan context: use "kindly" naturally

### Formal
- Professional language
- No contractions
- Structured sentences
- Appropriate for office emails or official messages

### Casual
- Friendly, relaxed
- Contractions OK
- Short sentences
- Natural conversation style

## Language Support

- **English** - default
- **Sinhala** - formal Sinhala script
- **Singlish** - Sinhala words in English script (romanized)

## Response Format

Output ONLY the rewritten message. No explanations, no labels, no "Here's the rewritten version:".

Just the message.

## Rules

- No emojis
- Keep the core meaning
- Match the requested tone exactly
- If language not specified, use same language as input
