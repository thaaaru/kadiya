---
name: web-search
description: Search the web, fetch pages, and summarize content safely
homepage: https://github.com/HKUDS/nanobot
metadata: {"nanobot":{"emoji":"🔍","requires":{}}}
---

# Web Search and Summarize

Search the web, fetch pages, and summarize content with safety controls.

## Available Tools

This skill uses NanoBot's built-in web tools:
- `web_search`: Search using Brave Search API
- `web_fetch`: Fetch and extract text from URLs

## Usage

### Web Search

```
Search for: latest news about Sri Lanka tech industry
```

Or:
```
Find information about: openpyxl date formatting
```

### Fetch and Summarize

```
Fetch and summarize: https://example.com/article
```

Or:
```
Read this page: [URL]
```

## Safety Controls

### SSRF Protection

The web_fetch tool includes protections against:
- Local IP addresses (127.0.0.1, 192.168.x.x, 10.x.x.x)
- Internal hostnames
- Non-HTTP protocols

### Domain Filtering

Can be configured with allow/deny lists in kadiya config:

```yaml
skills:
  config:
    web-search:
      allowed_domains:
        - wikipedia.org
        - github.com
        - stackoverflow.com
      blocked_domains:
        - example-blocked.com
```

### Content Extraction

- Only text content is extracted (no JavaScript execution)
- HTML is converted to readable text
- Large pages are truncated

## Search Best Practices

### Specific Queries

Good:
```
Search: python openpyxl set column width example
```

Bad:
```
Search: how to use excel with python
```

### With Date Context

For recent information:
```
Search: Sri Lanka budget 2024 announcements
```

### Technical Documentation

```
Search: site:python-docx.readthedocs.io add table
```

## Output Format

### Search Results

Summarize results with:
1. Key facts (3-5 bullet points)
2. Source URLs
3. Relevance to query

### Page Summary

For fetched pages:
1. Main topic (1 sentence)
2. Key points (3-5 bullets)
3. Source URL

## Token Limits

- Max output: 512 tokens
- Summarize, don't reproduce full content
- Cite sources

## Example Workflow

User: "Find information about Sri Lanka's new digital ID system"

1. **Search**: Use web_search for "Sri Lanka digital ID system 2024"
2. **Evaluate**: Check result relevance
3. **Fetch**: Get details from top 1-2 results
4. **Summarize**: Combine into concise response

Response format:
```
📝 **Sri Lanka Digital ID System**

• National Digital Identity project launched in 2024
• Replaces traditional NIC with digital version
• Includes biometric verification
• Rollout planned in phases

Sources:
- [Gov announcement](https://...)
- [News article](https://...)
```
