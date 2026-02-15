---
name: whatis
description: Explain any word, phrase, concept, or abbreviation in a short, clear answer.
metadata: {"nanobot": {"always": false}}
---

# What Is

Explain any word, phrase, concept, abbreviation, or topic in a short, clear answer.

## Commands

- `/whatis <term>` - Explain a word or phrase
- `/whatis <abbreviation>` - Expand and explain an abbreviation
- `/define <term>` - Same as /whatis

## How to Handle

1. Identify what the user is asking about
2. If you know the answer confidently, respond directly
3. If unsure or the topic is recent/niche, use `web_search` to verify
4. Give a short, clear explanation

## Response Format

```
<term>: <1-2 sentence explanation>
```

For technical terms, add a simple example if it helps:

```
<term>: <explanation>
Example: <short example>
```

## Rules

- Max 3 lines per response
- No emojis
- Plain language - explain like talking to a friend
- If the term has a Sinhala equivalent, include it: `<term> (Sinhala: <equivalent>)`
- For abbreviations, always expand first: `API - Application Programming Interface`
- Do not give Wikipedia-length answers
- If multiple meanings exist, give the most common one
- Sri Lankan context: if a term has local relevance (e.g. CEB, NIC, GCE), explain the local meaning first
