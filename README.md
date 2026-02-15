<div align="center">

  <h1>🐜 kadiya</h1>
  <p><strong>A lightweight, cost-first AI assistant for Sri Lanka</strong></p>
  <p>
    <img src="https://img.shields.io/badge/Telegram-ready-2CA5E0?style=flat&logo=telegram&logoColor=white" alt="Telegram">
    <img src="https://img.shields.io/badge/cost-$10--15%2Fmo-brightgreen" alt="Cost">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/python-%E2%89%A53.11-blue" alt="Python">
  </p>
</div>

---

## What is kadiya?

**kadiya** is a fork of [NanoBot](https://github.com/HKUDS/nanobot) optimized for Sri Lanka.

NanoBot is an ultra-lightweight AI assistant (~4,000 lines of core code). kadiya adds a cost-first routing layer, Sinhala/English support, and Sri Lanka-specific skills on top of it — so you get a personal AI assistant that runs on Telegram for under $2/month.

## What we added

| Feature | kadiya | upstream NanoBot |
|---------|--------|-----------------|
| Smart model routing | Routes to cheapest model that fits the task | Single model |
| Token optimization | Prompt compression, conversation summarization | Full context |
| Sri Lanka locale | Sinhala/English, LKR, Asia/Colombo, Singlish input | Global/CN focus |
| Sri Lanka skills | Translation, PII redaction, Telegram formatting | General skills |
| Office skills | Excel, Word, PowerPoint generation | -- |
| Cost target | $10+/mo LLM + $0-5/mo server | Varies |
| Primary channel | Telegram | Feishu, DingTalk, QQ, WeChat, etc. |
| Update checker | Checks GitHub releases on gateway startup | -- |
| Windows installer | One-click `install.bat` (native, no WSL) | Manual |

Everything else -- the agent loop, tools, memory, cron, and all upstream channels -- is inherited from NanoBot.

## Install

**Windows (recommended)**

Download and double-click `install.bat`. It installs Python (if needed), sets up kadiya, runs guided setup, and adds `kadiya` to your PATH.

After install, open any terminal:

```
kadiya agent -m "Hello!"
```

**From source (macOS/Linux)**

```bash
git clone https://github.com/thaaaru/kadiya.git
cd kadiya
pip install -e .
kadiya onboard
```

## Quick start

**1. Initialize**

```bash
kadiya onboard
```

The guided setup will ask you to:
- Choose a provider (DeepSeek, OpenAI, or OpenRouter)
- Enter your API key
- Optionally configure Telegram

**2. Chat**

```bash
kadiya agent -m "What is 2+2?"
```

**3. Interactive mode**

```bash
kadiya agent
```

Exit with `exit`, `quit`, `Ctrl+C`, or `:q`.

**4. Diagnostics**

```bash
kadiya doctor
```

## Telegram setup

**1. Create a bot**

- Open Telegram, search `@BotFather`
- Send `/newbot`, follow the prompts
- Copy the bot token

**2. Run onboard** (or edit `~/.nanobot/config.json` manually)

```bash
kadiya onboard
```

Select your provider, enter your API key, then answer **y** to "Enable Telegram bot?" and paste your token.

**3. Start the gateway**

```bash
kadiya gateway
```

Message your bot on Telegram -- kadiya replies.

> Other channels (Discord, Slack, Email, Feishu, DingTalk, QQ) are available via upstream NanoBot -- see the [NanoBot README](https://github.com/HKUDS/nanobot#-chat-apps) for setup.

## Skills

### Sri Lanka skills

| Skill | What it does |
|-------|-------------|
| `sl-translate` | Sinhala/English translation with formal/informal tone |
| `sl-telegram` | Telegram-friendly formatting |
| `sl-summarize` | Concise summaries optimized for mobile |
| `sl-pii-redact` | Redact personal information from text |

### Office skills

| Skill | What it does |
|-------|-------------|
| `office-excel` | Generate Excel spreadsheets |
| `office-word` | Generate Word documents |
| `office-pptx` | Generate PowerPoint presentations |

### Web

| Skill | What it does |
|-------|-------------|
| `web-search` | Search the web (DuckDuckGo default, Brave optional) |

### Inherited from NanoBot

GitHub integration, weather, cron/scheduling, memory, and the skill creator. See `nanobot/skills/` for the full list.

## Cost

kadiya is designed to cost **$10-15/month** for typical personal use, depending on your setup.

### Cost breakdown

| Component | Local setup | Cloud setup |
|-----------|------------|-------------|
| LLM API calls | $10+/mo | $10+/mo |
| Cloud server | $0 (runs on your PC) | $3-5/mo (cheap VPS) |
| **Total** | **$10+/mo** | **$13-15/mo** |

> **Local setup** — run kadiya on your own PC or laptop (no server cost).
> **Cloud setup** — run 24/7 on a VPS so Telegram works while your PC is off (e.g., Oracle Cloud free tier, Hetzner $3.29/mo, DigitalOcean $4/mo).

### What keeps LLM costs low

| What makes it cheap | How |
|--------------------|----|
| Smart routing | Routes most messages to DeepSeek Chat (~$0.14/M input tokens) |
| Token compression | Strips unnecessary tokens from prompts |
| Conversation summarization | Summarizes after 5 turns instead of sending full history |
| Lower defaults | `max_tokens: 2048`, `max_tool_iterations: 10`, `memory_window: 30` |
| Escalation only when needed | Falls back to GPT-4o-mini only for structured/complex tasks |

### Comparison

| Service | Monthly cost | Includes |
|---------|-------------|----------|
| ChatGPT Plus | $20 | LLM only |
| Claude Pro | $20 | LLM only |
| Typical API usage (GPT-4o) | $10-50+ | LLM only |
| **kadiya (local)** | **$10+** | LLM API |
| **kadiya (cloud)** | **$13-15** | LLM API + VPS |

## Configuration

### Providers

| Provider | Purpose | Get API key |
|----------|---------|-------------|
| `deepseek` | LLM (cheapest, recommended) | [platform.deepseek.com](https://platform.deepseek.com) |
| `openai` | LLM (GPT-3.5-turbo / GPT-4o-mini) | [platform.openai.com](https://platform.openai.com) |
| `openrouter` | LLM (multi-provider gateway) | [openrouter.ai](https://openrouter.ai) |
| `anthropic` | LLM (Claude direct) | [console.anthropic.com](https://console.anthropic.com) |
| `groq` | LLM + voice transcription (Whisper, free) | [console.groq.com](https://console.groq.com) |
| `gemini` | LLM (Gemini direct) | [aistudio.google.com](https://aistudio.google.com) |
| `vllm` | LLM (local, any OpenAI-compatible server) | -- |

> All providers from upstream NanoBot are supported. See the [full provider list](https://github.com/HKUDS/nanobot#providers).

### Security

| Option | Default | Description |
|--------|---------|-------------|
| `tools.restrictToWorkspace` | `false` | Sandbox agent to workspace directory |
| `channels.*.allowFrom` | `[]` | Whitelist user IDs (empty = allow all) |

## CLI reference

| Command | Description |
|---------|-------------|
| `kadiya onboard` | Guided setup (provider, API key, Telegram) |
| `kadiya agent -m "..."` | Send a message |
| `kadiya agent` | Interactive chat |
| `kadiya gateway` | Start the gateway (Telegram, etc.) |
| `kadiya channels status` | Show channel status |
| `kadiya status` | Show system status |
| `kadiya doctor` | Run diagnostics |
| `kadiya cron add` | Add a scheduled task |
| `kadiya cron list` | List scheduled tasks |

## Project structure

```
kadiya/
├── kadiya/              # kadiya additions
│   ├── config.py        #   Configuration loader
│   ├── router.py        #   Smart model routing
│   ├── optimizer.py     #   Token optimization
│   └── provider.py      #   Cost-first provider wrapper
├── skills/              # kadiya skills
│   ├── sl/              #   Sri Lanka (translate, telegram, summarize, pii-redact)
│   ├── office/          #   Office (excel, word, pptx)
│   └── web/             #   Web (search)
├── configs/
│   └── kadiya-sl.yaml   #   Sri Lanka configuration
├── install.bat          # Windows installer launcher
├── install.ps1          # Windows installer (native, no WSL)
├── kadiya.bat           # Windows launcher
└── nanobot/             # Upstream NanoBot engine
    ├── agent/           #   Core agent logic + skills loader
    ├── skills/          #   Built-in skills (memory, cron, weather, etc.)
    ├── channels/        #   Chat integrations (Telegram, Discord, Slack, etc.)
    ├── providers/       #   LLM providers
    ├── bus/             #   Message routing
    ├── cron/            #   Scheduled tasks
    ├── config/          #   Configuration
    └── cli/             #   CLI commands
```

## Upstream

kadiya is built on [NanoBot](https://github.com/HKUDS/nanobot) by [HKUDS](https://github.com/HKUDS). All credit for the core agent, tools, channels, and architecture goes to the NanoBot team.

If you need channels beyond Telegram (Feishu, DingTalk, QQ, Discord, Slack, Email, Mochat), or want the full documentation, see the [NanoBot repository](https://github.com/HKUDS/nanobot).

## License

MIT
