<div align="center">

  <h1>kadiya</h1>
  <p><strong>A lightweight, cost-first AI assistant for Sri Lanka</strong></p>
  <p>
    <img src="https://img.shields.io/badge/WhatsApp-ready-25D366?style=flat&logo=whatsapp&logoColor=white" alt="WhatsApp">
    <img src="https://img.shields.io/badge/Telegram-ready-2CA5E0?style=flat&logo=telegram&logoColor=white" alt="Telegram">
    <img src="https://img.shields.io/badge/cost-$0.50--2%2Fmo-brightgreen" alt="Cost">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/python-%E2%89%A53.11-blue" alt="Python">
  </p>
</div>

---

## What is kadiya?

**kadiya** is a fork of [NanoBot](https://github.com/HKUDS/nanobot) optimized for Sri Lanka.

NanoBot is an ultra-lightweight AI assistant (~4,000 lines of core code). kadiya adds a cost-first routing layer, Sinhala/English support, and Sri Lanka-specific skills on top of it — so you get a personal AI assistant that runs on WhatsApp or Telegram for under $2/month.

## What we added

| Feature | kadiya | upstream NanoBot |
|---------|--------|-----------------|
| Smart model routing | Routes to cheapest model that fits the task | Single model |
| Token optimization | Prompt compression, conversation summarization | Full context |
| Sri Lanka locale | Sinhala/English, LKR, Asia/Colombo, Singlish input | Global/CN focus |
| Sri Lanka skills | Translation, PII redaction, WhatsApp/Telegram formatting | General skills |
| Office skills | Excel, Word, PowerPoint generation | — |
| Cost target | $0.50–2/month | Varies |
| Primary channels | WhatsApp + Telegram | Feishu, DingTalk, QQ, WeChat, etc. |
| Windows installer | One-click `install.bat` for WSL setup | Manual |

Everything else — the agent loop, tools, memory, cron, and all upstream channels — is inherited from NanoBot.

## Install

**From source (recommended)**

```bash
git clone https://github.com/thaaaru/kadiya.git
cd kadiya
pip install -e .
```

**Windows**

Download and double-click `install.bat` — it sets up WSL, Ubuntu, and kadiya automatically.

**With uv**

```bash
uv tool install nanobot-ai
```

## Quick start

**1. Initialize**

```bash
nanobot onboard
```

**2. Configure** (`~/.nanobot/config.json`)

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  },
  "agents": {
    "defaults": {
      "model": "deepseek/deepseek-chat"
    }
  }
}
```

> Get an API key from [OpenRouter](https://openrouter.ai/keys) (recommended) or [DeepSeek](https://platform.deepseek.com) directly.

**3. Chat**

```bash
nanobot agent -m "What is 2+2?"
```

**4. Interactive mode**

```bash
nanobot agent
```

Exit with `exit`, `quit`, `Ctrl+D`, or `:q`.

## WhatsApp setup

Sri Lanka's most-used messaging app. kadiya connects via linked device — no business API needed.

**Requirements:** Node.js >= 18

**1. Link your device**

```bash
nanobot channels login
# Scan the QR code with WhatsApp > Settings > Linked Devices
```

**2. Configure**

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+94771234567"]
    }
  }
}
```

**3. Run** (two terminals)

```bash
# Terminal 1 — keep the WhatsApp bridge running
nanobot channels login

# Terminal 2 — start the gateway
nanobot gateway
```

Send a message to yourself on WhatsApp — kadiya replies.

## Telegram setup

**1. Create a bot**

- Open Telegram, search `@BotFather`
- Send `/newbot`, follow the prompts
- Copy the token

**2. Configure**

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

**3. Run**

```bash
nanobot gateway
```

> Other channels (Discord, Slack, Email, Feishu, DingTalk, QQ) are available via upstream NanoBot — see the [NanoBot README](https://github.com/HKUDS/nanobot#-chat-apps) for setup.

## Skills

### Sri Lanka skills

| Skill | What it does |
|-------|-------------|
| `sl-translate` | Sinhala/English translation with formal/informal tone |
| `sl-whatsapp` | WhatsApp-friendly formatting |
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
| `web-search` | Search the web (via Brave Search API) |

### Inherited from NanoBot

GitHub integration, weather, cron/scheduling, memory, tmux, and the skill creator. See `nanobot/skills/` for the full list.

## Cost

kadiya is designed to cost under $2/month for typical personal use.

| What makes it cheap | How |
|--------------------|----|
| Smart routing | Routes most messages to DeepSeek Chat (~$0.14/M input tokens) |
| Token compression | Strips unnecessary tokens from prompts |
| Conversation summarization | Summarizes after 5 turns instead of sending full history |
| Lower defaults | `max_tokens: 2048`, `max_tool_iterations: 10`, `memory_window: 30` |
| Escalation only when needed | Falls back to Claude Haiku or GPT-4o-mini only for structured/complex tasks |

**Comparison:**

| Service | Monthly cost |
|---------|-------------|
| ChatGPT Plus | $20 |
| Claude Pro | $20 |
| Typical API usage (GPT-4o) | $10–50+ |
| **kadiya** | **$0.50–2** |

## Configuration

### Providers

| Provider | Purpose | Get API key |
|----------|---------|-------------|
| `openrouter` | LLM (recommended, access to all models) | [openrouter.ai](https://openrouter.ai) |
| `deepseek` | LLM (cheapest for general tasks) | [platform.deepseek.com](https://platform.deepseek.com) |
| `anthropic` | LLM (Claude direct) | [console.anthropic.com](https://console.anthropic.com) |
| `openai` | LLM (GPT direct) | [platform.openai.com](https://platform.openai.com) |
| `groq` | LLM + voice transcription (Whisper, free) | [console.groq.com](https://console.groq.com) |
| `gemini` | LLM (Gemini direct) | [aistudio.google.com](https://aistudio.google.com) |
| `vllm` | LLM (local, any OpenAI-compatible server) | — |

> All providers from upstream NanoBot are supported. See the [full provider list](https://github.com/HKUDS/nanobot#providers).

### kadiya profile

Set the `KADIYA_PROFILE` environment variable to load the Sri Lanka profile:

```bash
export KADIYA_PROFILE=sl
```

Or pass the config file directly:

```bash
nanobot agent --config configs/kadiya-sl.yaml -m "hello"
```

The `kadiya-sl.yaml` config sets:
- Default model: `deepseek/deepseek-chat`
- Timezone: `Asia/Colombo`
- Languages: Sinhala + English (Singlish accepted)
- Token limits tuned for cost
- Routing tiers: cheap_general → structured → fallback → sensitive

### Security

| Option | Default | Description |
|--------|---------|-------------|
| `tools.restrictToWorkspace` | `false` | Sandbox agent to workspace directory |
| `channels.*.allowFrom` | `[]` | Whitelist user IDs (empty = allow all) |

## Docker

```bash
# Build
docker build -t kadiya .

# Initialize (first time)
docker run -v ~/.nanobot:/root/.nanobot --rm kadiya onboard

# Run gateway
docker run -v ~/.nanobot:/root/.nanobot -p 18790:18790 kadiya gateway

# Single command
docker run -v ~/.nanobot:/root/.nanobot --rm kadiya agent -m "Hello!"
```

## CLI reference

| Command | Description |
|---------|-------------|
| `nanobot onboard` | Initialize config and workspace |
| `nanobot agent -m "..."` | Send a message |
| `nanobot agent` | Interactive chat |
| `nanobot gateway` | Start the gateway (WhatsApp, Telegram, etc.) |
| `nanobot channels login` | Link WhatsApp (scan QR) |
| `nanobot channels status` | Show channel status |
| `nanobot status` | Show system status |
| `nanobot cron add` | Add a scheduled task |
| `nanobot cron list` | List scheduled tasks |

## Project structure

```
kadiya/
├── kadiya/              # kadiya additions
│   ├── config.py        #   Configuration loader
│   ├── router.py        #   Smart model routing
│   ├── optimizer.py     #   Token optimization
│   └── provider.py      #   Cost-first provider wrapper
├── configs/
│   └── kadiya-sl.yaml   #   Sri Lanka configuration
├── profiles/
│   └── sl/              #   Sri Lanka profile
│       ├── profile.yaml
│       └── prompts.yaml
├── install.bat          # Windows installer launcher
├── install.ps1          # Windows installer (PowerShell)
└── nanobot/             # Upstream NanoBot (unmodified)
    ├── agent/           #   Core agent logic
    ├── skills/          #   Bundled skills
    ├── channels/        #   Chat integrations
    ├── providers/       #   LLM providers
    ├── bus/             #   Message routing
    ├── cron/            #   Scheduled tasks
    ├── config/          #   Configuration
    └── cli/             #   CLI commands
```

## Upstream

kadiya is built on [NanoBot](https://github.com/HKUDS/nanobot) by [HKUDS](https://github.com/HKUDS). All credit for the core agent, tools, channels, and architecture goes to the NanoBot team.

If you need channels beyond WhatsApp and Telegram (Feishu, DingTalk, QQ, Discord, Slack, Email, Mochat), or want the full documentation, see the [NanoBot repository](https://github.com/HKUDS/nanobot).

## License

MIT
