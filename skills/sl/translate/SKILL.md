---
name: sl-translate
description: Translate between Sinhala and English with tone control
homepage: https://github.com/HKUDS/nanobot
metadata: {"nanobot":{"emoji":"🌐","requires":{}}}
---

# Sinhala ↔ English Translation

Translate text between Sinhala and English with tone control.

## Usage

### Basic Translation

To English:
```
Translate to English: මම හෙට එනවා
```

To Sinhala:
```
Translate to Sinhala: I will come tomorrow
```

### With Tone Control

**Formal tone** (for official documents, business):
```
Translate formally to Sinhala: Please submit your application by Friday.
```

**Casual tone** (for messages, chat):
```
Translate casually to Sinhala: See you later!
```

## Output Format

Return ONLY the translation. No explanations, no alternatives.

## Examples

| Input | Output |
|-------|--------|
| Translate to English: ස්තූතියි | Thank you |
| Translate to Sinhala: Good morning | සුභ උදෑසනක් |
| Translate formally: Hello sir | මහත්මයා, ආයුබෝවන් |
| Translate casually: Hello sir | හැලෝ සර් |

## Singlish Input

Accept mixed Sinhala-English (Singlish) naturally:
```
Translate: Mama today office එනවා meeting ekkata
→ I'm coming to office today for a meeting
```

## Token Limits

- Max output: 512 tokens
- Keep translations concise
- Preserve meaning over word-for-word accuracy
