---
name: call-script
description: Pre-written scripts for common calls and messages. Sri Lankan context with bilingual support.
metadata: {"nanobot": {"always": false}}
---

# Call & Message Scripts

Pre-written scripts for common phone calls and messages. Sri Lankan service providers and bilingual support.

## Commands

- `/script call <situation>` - Get a call script
- `/script message <situation>` - Get a message template
- `/script complaint <service>` - Complaint script for Sri Lankan services

## How to Handle

1. Identify the situation type (call, message, complaint)
2. Identify the service provider or context
3. Generate a script in the appropriate format
4. Output the script directly with no explanations

## Supported Services

- **Telecom**: Dialog, SLT, Mobitel, Airtel, Hutch
- **Utilities**: CEB (electricity), Water Board (NWSDB)
- **Banking**: Commercial Bank, HNB, Sampath, BOC, People's Bank
- **Government**: Divisional Secretariat, DMV, Passport Office
- **Other**: landlord, school, hospital

## Common Situations

- Complaint about service/billing
- Inquiry about status/balance
- Appointment booking
- Service cancellation
- Payment arrangement
- Escalation request

## Script Format

### Call Script

```
Opening: <greeting and introduction>
State purpose: <why you are calling>
Details: <specific information to mention>
If transferred: <what to repeat>
If escalating: <how to ask for supervisor>
Closing: <thank and confirm next steps>
```

### Message Template

```
<full message text ready to copy-paste>
```

### Complaint Script

```
Opening: <greeting>
Reference: <account/reference number placeholder>
Issue: <describe the problem>
Request: <what resolution you want>
Escalation: <if not resolved, next step>
Closing: <thank you>
```

## Bilingual Support

- Default: English
- Include common Sinhala phrases where natural
- Useful phrases:
  - "Mama call karanney..." (I am calling about...)
  - "Mage account number eka..." (My account number is...)
  - "Supervisor kenek ekkala kata karana puluwan da?" (Can I speak with a supervisor?)
  - "Meeka solve karanna puluwan da?" (Can this be solved?)

## Tone Guidelines

- Polite but firm
- Professional, not aggressive
- Assert rights without being rude
- Include specific details (dates, amounts, reference numbers as placeholders)

## Rules

- Output the script directly, no explanations before or after
- No emojis
- Keep scripts under 10 lines
- Use placeholders for personal details: <your name>, <account number>, <date>
- Sri Lankan context always
