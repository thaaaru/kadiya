---
name: web-search
description: Search the web and summarize results. Uses web_search and web_fetch tools.
metadata: {"nanobot": {"always": false}}
---

# Web Search

Search the web for current information, news, prices, or anything the user needs.

## Commands

- `/search <query>` - Search and summarize top results
- `/search news <topic>` - Search for recent news
- `/fetch <url>` - Fetch and summarize a specific page

## How to Handle

1. Use the `web_search` tool with the user's query
2. Review the results (titles, URLs, snippets)
3. If the user needs more detail, use `web_fetch` on the most relevant URL
4. Summarize the findings concisely

## Response Format

For `/search`:

```
<one-line answer if possible>

Sources:
- <title> - <url>
- <title> - <url>
```

For `/fetch`:

```
<summary of page content in 3-5 bullet points>

Source: <url>
```

## Rules

- Max 5 lines for search results unless user asks for more
- Always cite sources with URLs
- No emojis
- If web_search returns no results, say so directly
- Web search works out of the box via DuckDuckGo (no API key needed)
- If BRAVE_API_KEY is set, Brave Search is used instead for higher quality results
- Prefer recent results for news queries
- Do not fabricate URLs or results
- Bullet points only
- Sri Lankan context: prioritize local results when query is location-relevant
