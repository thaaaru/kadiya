---
name: sl-pii-redact
description: Redact Sri Lankan PII (NIC, phone, email, addresses)
homepage: https://github.com/HKUDS/nanobot
metadata: {"nanobot":{"emoji":"🔒","requires":{}}}
---

# PII Redaction for Sri Lanka

Redact personally identifiable information (PII) common in Sri Lankan documents.

## Usage

```
Redact PII: [text with personal information]
```

Or:
```
Hide personal info: [text]
```

## What Gets Redacted

| Data Type | Pattern | Replacement |
|-----------|---------|-------------|
| NIC (Old) | 9 digits + V/X | [NIC_REDACTED] |
| NIC (New) | 12 digits | [NIC_REDACTED] |
| Mobile | 07X XXX XXXX | [PHONE_REDACTED] |
| Landline | 0XX XXX XXXX | [PHONE_REDACTED] |
| Intl Phone | +94 XX XXX XXXX | [PHONE_REDACTED] |
| Email | user@domain.com | [EMAIL_REDACTED] |
| Address | Common patterns | [ADDRESS_REDACTED] |
| Bank Account | Account numbers | [ACCOUNT_REDACTED] |

## Examples

### Basic Redaction

Input:
```
Redact PII: Please contact Mr. Perera at 0771234567 or email him at perera@gmail.com. His NIC is 199012345678.
```

Output:
```
Please contact Mr. Perera at [PHONE_REDACTED] or email him at [EMAIL_REDACTED]. His NIC is [NIC_REDACTED].
```

### Document Redaction

Input:
```
Hide personal info:
Application Form

Name: Kamal Silva
NIC: 852345678V
Address: 45, Galle Road, Colombo 03
Phone: +94 77 123 4567
Email: kamal.silva@company.lk
Bank Account: 0012345678 (BOC)
```

Output:
```
Application Form

Name: Kamal Silva
NIC: [NIC_REDACTED]
Address: [ADDRESS_REDACTED]
Phone: [PHONE_REDACTED]
Email: [EMAIL_REDACTED]
Bank Account: [ACCOUNT_REDACTED] (BOC)
```

### Partial Redaction (Show Last 4)

For cases where partial info is needed:
```
Redact PII (show last 4): His NIC is 199012345678
```

Output:
```
His NIC is [NIC: ****5678]
```

## Sri Lankan NIC Patterns

**Old Format (before 2016):**
- 9 digits + V or X
- Example: 852345678V
- Birth year encoded in first 2 digits

**New Format (2016+):**
- 12 digits
- Example: 199012345678
- Full birth year in first 4 digits

## Phone Patterns

| Type | Pattern |
|------|---------|
| Dialog/Mobitel | 077, 076 |
| Airtel | 075 |
| Hutch | 078 |
| Etisalat | 072 |
| Landline | 011 (Colombo), 081 (Kandy), etc. |

## Token Limits

- Max output: 1024 tokens
- Preserve document structure
- Only redact recognized PII patterns
- Keep names (unless specifically requested)
