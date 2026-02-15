---
name: time-helper
description: Time conversions, planning, and scheduling. Default timezone Asia/Colombo.
metadata: {"nanobot": {"always": false}}
---

# Time & Planning Helper

Time conversions, meeting planning, and scheduling across timezones.

## Commands

- `/time <city>` - Current time in a city
- `/time plan <event> <duration>` - Help plan time for an event
- `/time convert <time> <from_tz> to <to_tz>` - Convert between timezones

## How to Handle

1. Identify the command type (lookup, plan, convert)
2. Use Asia/Colombo as the default/home timezone
3. Calculate and format the response

### Time lookup

Map common city names to timezones:
- Colombo, Sri Lanka: Asia/Colombo (UTC+5:30)
- New York: America/New_York (UTC-5 / UTC-4 DST)
- Los Angeles: America/Los_Angeles (UTC-8 / UTC-7 DST)
- London: Europe/London (UTC+0 / UTC+1 DST)
- Dubai: Asia/Dubai (UTC+4)
- Sydney: Australia/Sydney (UTC+11 / UTC+10 DST)
- Delhi, Mumbai, India: Asia/Kolkata (UTC+5:30)
- Singapore: Asia/Singapore (UTC+8)
- Tokyo: Asia/Tokyo (UTC+9)

### Meeting planning

- Suggest times that work across specified timezones
- Prefer 09:00-17:00 working hours in all timezones
- If no overlap, suggest the closest reasonable time
- Show time in each participant's timezone

### Sri Lankan context

- Office hours: 08:30-17:00 (government), 09:00-17:00 (private)
- Bank hours: 09:00-15:00 (weekdays)
- Common holidays: Poya days (monthly), New Year (April 13-14), Independence Day (Feb 4)

## Response Format

Time lookup:
```
<City> - <HH:MM> (<Day>)
```

Conversion:
```
<time> <from_city> = <time> <to_city> (<Day>)
```

Planning:
```
Suggested time for <event>:
- <City 1>: <HH:MM> (<Day>)
- <City 2>: <HH:MM> (<Day>)
```

## Rules

- Max 3 lines per response (except planning which allows 5)
- No emojis
- 24-hour format by default
- Clean format: "City - HH:MM (Day)"
- Default timezone: Asia/Colombo
- Account for DST where applicable
