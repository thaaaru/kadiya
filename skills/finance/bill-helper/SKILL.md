---
name: bill-helper
description: Track bills, expenses, and simple budgeting. LKR currency, local storage.
metadata: {"nanobot": {"always": false}}
---

# Bill & Expense Helper

Track bills, log expenses, and get simple monthly summaries.

## Commands

- `/bill <amount> <description>` - Log an expense
- `/bill list` - Show recent expenses
- `/bill summary` - Monthly summary by category
- `/bill due <description> <date>` - Set a bill reminder

## How to Handle

1. Read `{workspace}/memory/store.json`
2. Modify the `finance` object (contains `expenses` and `bills_due` arrays)
3. Write back to `{workspace}/memory/store.json`

### Logging an expense

```json
{
  "id": "<8-char-hex>",
  "amount": 2500,
  "currency": "LKR",
  "description": "lunch at Pagoda",
  "category": "food",
  "date": "2026-02-15",
  "created_at": "2026-02-15T12:30:00"
}
```

### Setting a bill due

```json
{
  "id": "<8-char-hex>",
  "description": "CEB electricity bill",
  "due_date": "2026-02-25",
  "status": "pending",
  "created_at": "2026-02-15T10:00:00"
}
```

### Category auto-detection

- **utilities**: CEB, electricity, water, NWSDB, gas
- **food**: lunch, dinner, breakfast, rice, kottu, restaurant, cafe
- **transport**: bus, train, tuk, uber, pickme, fuel, petrol, diesel
- **phone**: Dialog, SLT, Mobitel, reload, data, internet
- **other**: anything that does not match above

## Response Format

Logging:
```
Logged: LKR <amount> - <description>
Category: <category>
```

Listing (recent 10):
```
Recent expenses:
- LKR <amount> | <description> | <category> | <date>
- LKR <amount> | <description> | <category> | <date>
```

Summary:
```
Monthly summary (<month>):
- Utilities: LKR <total>
- Food: LKR <total>
- Transport: LKR <total>
- Phone: LKR <total>
- Other: LKR <total>
Total: LKR <grand total>
```

Bill due:
```
Bill reminder set: <description>
Due: <date>
ID: <id>
```

If no expenses: "No expenses logged this month."

## Rules

- Max 10 lines for summary
- No emojis
- Simple table format for lists
- Currency: LKR (Sri Lankan Rupees) by default
- Date format: ISO 8601
- Timezone: Asia/Colombo (UTC+5:30)
- Store in memory/store.json under "finance" key
- Privacy: financial data stays local only
