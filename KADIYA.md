<div align="center">
  <img src="assets/kadiya-logo.svg" alt="kadiya" width="400"/>

  <br/><br/>

  <strong>Smart bot for Sri Lanka</strong>

  <p>
    Token-optimized | Cost-first routing | Sinhala + English | WhatsApp ready
  </p>

  <p>
    <a href="#installation"><img src="https://img.shields.io/badge/install-one--line-E8A838?style=flat-square" alt="Install"/></a>
    <a href="#whatsapp-bot-setup"><img src="https://img.shields.io/badge/WhatsApp-ready-25D366?style=flat-square&logo=whatsapp&logoColor=white" alt="WhatsApp"/></a>
    <a href="#cost-optimization-strategy"><img src="https://img.shields.io/badge/cost-$2%2Fmo-blue?style=flat-square" alt="Cost"/></a>
    <a href="https://github.com/thaaaru/kadiya/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"/></a>
  </p>
</div>

---

## What is kadiya?

**kadiya** is a fork of [NanoBot](https://github.com/HKUDS/nanobot) optimized for:

- **Low token usage** - Aggressive prompt compression and response limits
- **Low cost operation** - Cost-first model routing (cheapest capable model wins)
- **Predictable execution** - Deterministic routing, no heuristic LLM reasoning
- **Practical skills** - Office documents, web search, message formatting
- **Bilingual support** - Sinhala, English, and Singlish input

This is **NOT** a chatbot product. This is a **skill-driven execution bot** with smart routing and strict cost control.

## Relationship to NanoBot

kadiya extends NanoBot without modifying its core. All enhancements are:

| Aspect | Approach |
|--------|----------|
| Configuration | Profile-based YAML configs |
| Features | Modular skills in `skills/` |
| Routing | Wrapper around LiteLLM provider |
| Compatibility | 100% upstream compatible |

You can update NanoBot independently and kadiya will continue to work.

---

## Installation

### One-Line Install (Recommended)

```bash
git clone https://github.com/thaaaru/kadiya.git && cd kadiya && ./install.sh
```

That's it. The installer will:
1. Detect your OS (Linux, WSL, macOS)
2. Set up a Python virtual environment
3. Install all dependencies
4. Guide you through provider selection (OpenAI, DeepSeek, or OpenRouter)
5. Securely prompt for your API key
6. Generate all config files automatically
7. Run validation to confirm everything works

**No manual config editing required.**

### Prerequisites

- Python 3.11+
- git
- curl

### Windows Users

**Double-click `install.bat`** -- that's it. It handles everything:

```
install.bat          <- double-click from Explorer, or run from cmd
```

Or from PowerShell:
```powershell
.\install.bat
```

The installer will:
1. Auto-elevate to Administrator (opens a new window if needed)
2. Enable WSL 2 (may require a restart on first run)
3. Install Ubuntu if not present
4. Install Python 3.12, git, curl inside Ubuntu
5. Clone the repo and run `install.sh` inside Ubuntu
6. Guide you through provider selection interactively

No manual WSL setup, no command-line flags, no config editing.

If WSL/Ubuntu is already set up, you can also run directly in Ubuntu:
```bash
git clone https://github.com/thaaaru/kadiya.git && cd kadiya && ./install.sh
```

### Docker

```bash
docker build -t kadiya .
docker run -it -v ~/.nanobot:/root/.nanobot -e KADIYA_PROFILE=sl kadiya
```

### After Installation

```bash
# Activate the environment
source .venv/bin/activate

# Send a message
nanobot agent -m "Translate 'good morning' to Sinhala"

# Interactive mode
nanobot agent

# Check health
nanobot doctor
```

### WhatsApp Bot Setup

kadiya comes pre-configured for WhatsApp. During installation, choose "Enable WhatsApp bot" and provide your phone number (+94 format for Sri Lanka).

```bash
# 1. Install the Node.js bridge
cd bridge && npm install && npm run build && cd ..

# 2. Start the bridge (scan QR code with your phone)
node bridge/dist/index.js

# 3. In another terminal, start kadiya
source .venv/bin/activate
nanobot agent
```

Messages sent to your WhatsApp will be processed by kadiya. Features:
- Automatic language detection (Sinhala, English, Singlish)
- WhatsApp-optimized formatting (bold, lists, emojis)
- Phone number allowlist for security
- Local bridge (no data leaves your machine except to LLM provider)

### Diagnostics

If anything goes wrong, run:

```bash
nanobot doctor
```

This checks config files, API keys, dependencies, workspace, and provider connectivity. It auto-fixes what it can and tells you how to fix the rest.

---

## Cost Optimization Strategy

### Why Cost Matters

| Model | Input Cost | Output Cost | Relative Cost |
|-------|------------|-------------|---------------|
| DeepSeek Chat | $0.14/1M | $0.28/1M | 1x (baseline) |
| GPT-4o-mini | $0.15/1M | $0.60/1M | 2x |
| Claude 3 Haiku | $0.25/1M | $1.25/1M | 4x |
| Claude 3.5 Sonnet | $3.00/1M | $15.00/1M | 50x |
| GPT-4o | $5.00/1M | $15.00/1M | 50x |

**kadiya's philosophy**: Use the cheapest model that can do the job. Upgrade only when necessary.

### Routing Tiers

| Tier | When Used | Default Model | Max Output |
|------|-----------|---------------|------------|
| `cheap_general` | Most tasks | deepseek-chat | 1024 tokens |
| `structured` | JSON output, large input | claude-3-haiku | 2048 tokens |
| `fallback` | After retries | gpt-4o-mini | 4096 tokens |
| `sensitive` | PII detected | claude-3-haiku | 2048 tokens |

### Token Saving Strategies

1. **Short system prompts** - kadiya uses minimal identity prompts
2. **Rolling summaries** - Old conversation compressed after 5 turns
3. **Intent-based limits** - Translation: 512, Summary: 256, Format: 256
4. **Prompt compression** - Removes verbose phrases automatically
5. **Hard caps** - Never exceed configured limits

### Estimated Costs

For typical usage (100 messages/day, mixed intents):

| Strategy | Est. Monthly Cost |
|----------|-------------------|
| kadiya (DeepSeek default) | $0.50 - $2.00 |
| Standard NanoBot (Claude) | $5.00 - $20.00 |
| Heavy usage (GPT-4) | $50.00 - $200.00 |

---

## Skills

### Sri Lanka Skills

| Skill | Description |
|-------|-------------|
| `sl-translate` | Sinhala <-> English with tone control |
| `sl-whatsapp` | Format for WhatsApp (concise, emoji) |
| `sl-telegram` | Format for Telegram (markdown) |
| `sl-summarize` | Summarize notices and circulars |
| `sl-pii-redact` | Redact NIC, phone, email |

### Office Skills

| Skill | Description | Requires |
|-------|-------------|----------|
| `office-excel` | Generate Excel files | openpyxl |
| `office-word` | Generate Word documents | python-docx |
| `office-pptx` | Generate PowerPoint | python-pptx |

### Web Skill

| Skill | Description |
|-------|-------------|
| `web-search` | Search, fetch, summarize with safety controls |

---

## Usage Examples

### Translation

```
User: Translate to Sinhala: Good morning, how are you?
kadiya: suba udaesanak, kohomada?
```

### WhatsApp Formatting

```
User: Format for WhatsApp: Meeting tomorrow at 3 PM in the conference room. Please bring your laptops.

kadiya:
*Meeting Tomorrow*

3:00 PM
Conference room

Please bring laptops
```

### Document Generation

```
User: Create an Excel file with a sales report for January

kadiya: [Generates and saves sales_report.xlsx to workspace]
```

### Notice Summarization

```
User: Summarize: [Long government circular...]

kadiya:
**New Working Hours Effective Feb 1**

- Hours: 8:30 AM - 4:30 PM
- Lunch: 12:00 - 12:30 PM
- Flexible arrangements possible

**Action**: Submit compliance report
**Deadline**: February 15, 2024
```

---

## Configuration Reference

### kadiya-sl.yaml

```yaml
# Profile
profile:
  name: sl
  version: "1.0.0"

# Locale
locale:
  timezone: Asia/Colombo
  currency: LKR
  languages: [si, en]
  allow_singlish: true

# Agent defaults (cost-optimized)
agents:
  defaults:
    model: deepseek/deepseek-chat
    max_tokens: 2048
    temperature: 0.3
    max_tool_iterations: 10

# Routing
routing:
  default_tier: cheap_general
  tiers:
    cheap_general:
      models: [deepseek/deepseek-chat]
      max_output_tokens: 1024

# Token limits
token_limits:
  max_output_tokens: 2048
  intent_limits:
    translate: 512
    summarize: 256
```

See `configs/kadiya-sl.yaml` for full configuration.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KADIYA_PROFILE` | Profile name to load | `sl` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |

---

## Development

### Project Structure

```
nanobot/
├── kadiya/             # kadiya Python module
│   ├── __init__.py
│   ├── config.py       # Configuration loader
│   ├── router.py       # Model routing
│   ├── optimizer.py    # Token optimization
│   └── provider.py     # Provider wrapper
├── configs/
│   └── kadiya-sl.yaml  # Sri Lanka config
├── profiles/
│   └── sl/             # Sri Lanka profile
├── skills/
│   ├── sl/             # Sri Lanka skills
│   ├── office/         # Office skills
│   └── web/            # Web skills
└── KADIYA.md           # This file
```

### Adding Skills

1. Create directory: `skills/category/skill-name/`
2. Add `SKILL.md` with frontmatter:

```markdown
---
name: skill-name
description: What it does
metadata: {"nanobot":{"emoji":"","requires":{}}}
---

# Skill Name

Instructions for the LLM...
```

3. Add to config's enabled skills list

### Testing

```bash
# Run tests
pytest tests/

# Test specific skill
python -c "from kadiya import ModelRouter; r = ModelRouter(); print(r.route(...))"
```

---

## Design Principles

1. **Cost predictability > Peak capability** - We'd rather have consistent $2/month than occasional brilliance at $50/month

2. **Deterministic routing** - No LLM calls to decide which LLM to call

3. **Extend, don't modify** - kadiya wraps NanoBot, doesn't fork it

4. **Token consciousness** - Every prompt character costs money

5. **Local context** - Sri Lanka timezone, currency, and language by default

---

## Acknowledgments

- [NanoBot](https://github.com/HKUDS/nanobot) - The upstream project
- [LiteLLM](https://github.com/BerriAI/litellm) - Multi-provider support

---

## License

MIT (same as upstream NanoBot)

---

## Support

- **Issues**: Open on GitHub
- **Discussions**: Use NanoBot discussions
- **Sri Lanka community**: Coming soon
