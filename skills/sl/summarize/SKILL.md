---
name: sl-summarize
description: Summarize notices, circulars, and documents concisely
homepage: https://github.com/HKUDS/nanobot
metadata: {"nanobot":{"emoji":"📋","requires":{}}}
---

# Notice/Circular Summarizer

Summarize government notices, company circulars, and official documents into brief, actionable points.

## Usage

```
Summarize: [paste notice/circular here]
```

Or:
```
TL;DR: [paste document here]
```

## Output Format

1. **Subject line** (1 sentence)
2. **Key points** (3-5 bullet points)
3. **Action required** (if any)
4. **Deadline** (if mentioned)

## Examples

### Government Circular

Input:
```
Summarize:
Ministry of Public Administration Circular No. 15/2024

Subject: Revision of Working Hours for Public Sector Employees

In accordance with Cabinet Decision dated 15th January 2024, it has been decided to revise the working hours of all public sector employees with effect from 1st February 2024.

The new working hours shall be from 8:30 AM to 4:30 PM with a 30-minute lunch break from 12:00 PM to 12:30 PM.

Flexible working arrangements may be considered for employees with special circumstances, subject to approval by the Head of Department.

All Heads of Departments are requested to ensure compliance and submit implementation reports by 15th February 2024.

Secretary to the Ministry
```

Output:
```
📋 **New Public Sector Working Hours**

• Hours: 8:30 AM - 4:30 PM (from Feb 1)
• Lunch: 12:00 - 12:30 PM (30 min)
• Flexible hours possible with HOD approval
• Per Cabinet Decision dated Jan 15

⚠️ **Action**: HODs submit compliance reports
📅 **Deadline**: February 15, 2024
```

### Company Notice

Input:
```
TL;DR:
Dear Employees,

We are pleased to announce that the annual company retreat will be held from March 15-17, 2024 at Heritance Kandalama. All permanent employees are invited to attend.

Transportation will be provided from the Colombo office departing at 7:00 AM on March 15th. Please register your attendance through the HR portal by March 5th.

Accommodation and meals will be covered by the company. Employees may bring one family member at their own expense (Rs. 25,000 per person for the full package).

Activities include team building exercises, nature walks, and a gala dinner on the final evening.

For any queries, please contact HR at hr@company.lk

Best regards,
HR Department
```

Output:
```
📋 **Annual Company Retreat**

• 📅 March 15-17, 2024
• 📍 Heritance Kandalama
• 🚌 Transport from Colombo office (7 AM)
• 💰 Company-sponsored (employees)
• 👥 Family: Rs. 25,000/person

⚠️ **Action**: Register on HR portal
📅 **Deadline**: March 5, 2024
📧 Queries: hr@company.lk
```

## Token Limits

- Max output: 256 tokens
- Focus on actionable information
- Extract dates and deadlines
- Skip boilerplate text
