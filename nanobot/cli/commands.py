"""CLI commands for kadiya."""

import asyncio
import os
import signal
from pathlib import Path
import select
import sys

# Windows console setup: UTF-8 encoding + ANSI escape sequence support
if sys.platform == "win32":
    # 1. UTF-8 output (cp1252 cannot encode Unicode symbols like ✓ 🐜)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    # 2. Enable Virtual Terminal Processing so ANSI color codes render
    #    instead of showing raw escape sequences like [1;36m
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(handle, mode)
    except Exception:
        pass

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout

from nanobot import __version__, __logo__

app = typer.Typer(
    name="kadiya",
    help=f"{__logo__} kadiya - Personal AI Assistant",
    no_args_is_help=True,
)

console = Console(legacy_windows=False)
EXIT_COMMANDS = {"exit", "quit", "/exit", "/quit", ":q"}

# Git Bash (MSYS) auto-converts /slash args to Windows paths, e.g. /help -> C:/Program Files/Git/help.
# This regex detects and reverses that mangling for slash commands.
import re
_MSYS_PATH_RE = re.compile(r"^[A-Za-z]:[/\\].*?[/\\](new|help|remind|task|note|brief|rewrite|script|follow|contact|bill|time|search|fetch|whatis|define)$", re.IGNORECASE)


def _fix_msys_path(text: str) -> str:
    """Reverse MSYS/Git Bash path expansion on slash commands."""
    m = _MSYS_PATH_RE.match(text.strip())
    if m:
        return f"/{m.group(1)}"
    return text

# ---------------------------------------------------------------------------
# CLI input: prompt_toolkit for editing, paste, history, and display
# ---------------------------------------------------------------------------

_PROMPT_SESSION: PromptSession | None = None
_SAVED_TERM_ATTRS = None  # original termios settings, restored on exit


def _flush_pending_tty_input() -> None:
    """Drop unread keypresses typed while the model was generating output."""
    try:
        fd = sys.stdin.fileno()
        if not os.isatty(fd):
            return
    except Exception:
        return

    try:
        import termios
        termios.tcflush(fd, termios.TCIFLUSH)
        return
    except Exception:
        pass

    try:
        while True:
            ready, _, _ = select.select([fd], [], [], 0)
            if not ready:
                break
            if not os.read(fd, 4096):
                break
    except Exception:
        return


def _restore_terminal() -> None:
    """Restore terminal to its original state (echo, line buffering, etc.)."""
    if _SAVED_TERM_ATTRS is None:
        return
    try:
        import termios
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _SAVED_TERM_ATTRS)
    except Exception:
        pass


def _init_prompt_session() -> None:
    """Create the prompt_toolkit session with persistent file history."""
    global _PROMPT_SESSION, _SAVED_TERM_ATTRS

    # Save terminal state so we can restore it on exit
    try:
        import termios
        _SAVED_TERM_ATTRS = termios.tcgetattr(sys.stdin.fileno())
    except Exception:
        pass

    history_file = Path.home() / ".nanobot" / "history" / "cli_history"
    history_file.parent.mkdir(parents=True, exist_ok=True)

    _PROMPT_SESSION = PromptSession(
        history=FileHistory(str(history_file)),
        enable_open_in_editor=False,
        multiline=False,   # Enter submits (single line mode)
    )


def _print_agent_response(response: str, render_markdown: bool) -> None:
    """Render assistant response with consistent terminal styling."""
    content = response or ""
    body = Markdown(content) if render_markdown else Text(content)
    console.print()
    console.print(f"[cyan]{__logo__} kadiya[/cyan]")
    console.print(body)
    console.print()


def _is_exit_command(command: str) -> bool:
    """Return True when input should end interactive chat."""
    return command.lower() in EXIT_COMMANDS


async def _read_interactive_input_async() -> str:
    """Read user input using prompt_toolkit (handles paste, history, display).

    prompt_toolkit natively handles:
    - Multiline paste (bracketed paste mode)
    - History navigation (up/down arrows)
    - Clean display (no ghost characters or artifacts)
    """
    if _PROMPT_SESSION is None:
        raise RuntimeError("Call _init_prompt_session() first")
    try:
        with patch_stdout():
            return await _PROMPT_SESSION.prompt_async(
                HTML("<b fg='ansiblue'>You:</b> "),
            )
    except EOFError as exc:
        raise KeyboardInterrupt from exc



def version_callback(value: bool):
    if value:
        console.print(f"{__logo__} kadiya v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    ),
):
    """kadiya - Personal AI Assistant."""
    pass


# ============================================================================
# Onboard / Setup
# ============================================================================


def _detect_provider(api_key: str) -> str:
    """Detect LLM provider from API key pattern.

    Supported patterns:
        sk-ant-...          -> anthropic
        sk-or-...           -> openrouter
        sk-proj-...         -> openai
        sk-... (>60 chars)  -> openai
        sk-... (short)      -> deepseek
        gsk_...             -> groq
        AIza...             -> gemini
        anything else       -> deepseek (cheapest fallback)
    """
    key = api_key.strip()
    # Anthropic keys: sk-ant-api03-...
    if key.startswith("sk-ant-"):
        return "anthropic"
    # OpenRouter keys: sk-or-v1-... or sk-or-...
    if key.startswith("sk-or-"):
        return "openrouter"
    # Groq keys: gsk_...
    if key.startswith("gsk_"):
        return "groq"
    # Gemini (Google AI Studio) keys: AIza...
    if key.startswith("AIza"):
        return "gemini"
    # OpenAI keys: sk-proj-... (project keys, 100+ chars)
    if key.startswith("sk-proj-"):
        return "openai"
    # OpenAI org/user keys are typically longer than DeepSeek keys
    if key.startswith("sk-") and len(key) > 60:
        return "openai"
    # DeepSeek keys: sk-... (shorter, typically 32-50 chars)
    if key.startswith("sk-"):
        return "deepseek"
    # Fallback: assume DeepSeek (cheapest)
    return "deepseek"


@app.command()
def onboard():
    """Interactive setup: configure provider, API key, workspace, and channels."""
    from nanobot.config.loader import get_config_path, load_config, save_config
    from nanobot.config.schema import Config
    from nanobot.utils.helpers import get_workspace_path

    # --- Banner ---
    console.print()
    console.print("[bold cyan]  kadiya setup[/bold cyan]")
    console.print("[dim]  Cost-first AI assistant for Sri Lanka[/dim]")
    console.print()

    # --- 1. Load or create config ---
    config_path = get_config_path()
    if config_path.exists():
        config = load_config()
        console.print(f"[green]✓[/green] Config loaded from {config_path}")
    else:
        config = Config()
        console.print("[dim]  Creating new configuration...[/dim]")

    # --- 2. API key (ask first, detect provider from key) ---
    PROVIDER_MAP = {
        "deepseek": {
            "name": "deepseek",
            "label": "DeepSeek",
            "model": "deepseek/deepseek-chat",
            "structured_model": "deepseek/deepseek-chat",
            "api_base": "https://api.deepseek.com",
        },
        "openai": {
            "name": "openai",
            "label": "OpenAI",
            "model": "gpt-4o-mini",
            "structured_model": "gpt-4o-mini",
            "api_base": None,
        },
        "anthropic": {
            "name": "anthropic",
            "label": "Anthropic",
            "model": "anthropic/claude-sonnet-4-5-20250929",
            "structured_model": "anthropic/claude-sonnet-4-5-20250929",
            "api_base": None,
        },
        "groq": {
            "name": "groq",
            "label": "Groq",
            "model": "groq/llama-3.1-8b-instant",
            "structured_model": "groq/llama-3.1-8b-instant",
            "api_base": None,
        },
        "gemini": {
            "name": "gemini",
            "label": "Gemini",
            "model": "gemini/gemini-2.0-flash",
            "structured_model": "gemini/gemini-2.0-flash",
            "api_base": None,
        },
        "openrouter": {
            "name": "openrouter",
            "label": "OpenRouter",
            "model": "deepseek/deepseek-chat",
            "structured_model": "deepseek/deepseek-chat",
            "api_base": None,
        },
    }

    console.print()
    console.print("[bold]Paste your API key:[/bold]")
    console.print("[dim]  Auto-detects: DeepSeek, OpenAI, Anthropic, Groq, Gemini, OpenRouter[/dim]")
    console.print()

    api_key = ""
    while not api_key:
        api_key = typer.prompt("  API Key").strip()
        if not api_key:
            console.print("  [yellow]API key cannot be empty.[/yellow]")

    # Auto-detect provider from key pattern
    detected = _detect_provider(api_key)
    prov = PROVIDER_MAP[detected]
    console.print(f"[green]✓[/green] Detected provider: {prov['label']} ({len(api_key)} chars)")

    # Set the provider's API key in config
    provider_config = getattr(config.providers, prov["name"])
    provider_config.api_key = api_key
    if prov["api_base"]:
        provider_config.api_base = prov["api_base"]

    # Set default model and kadiya-optimized defaults
    config.agents.defaults.model = prov["model"]
    config.agents.defaults.max_tokens = 2048
    config.agents.defaults.temperature = 0.3
    config.agents.defaults.max_tool_iterations = 10
    config.agents.defaults.memory_window = 30

    # --- 4. Telegram (optional) ---
    console.print()
    enable_tg = typer.confirm("  Enable Telegram bot?", default=False)

    if enable_tg:
        console.print()
        console.print("  [dim]Get a bot token from @BotFather on Telegram[/dim]")
        tg_token = typer.prompt("  Bot token", default="").strip()
        config.channels.telegram.enabled = True
        if tg_token:
            config.channels.telegram.token = tg_token
            console.print(f"[green]✓[/green] Telegram configured")
        else:
            console.print("[yellow]![/yellow] Telegram enabled without token (set later in config.json)")
    else:
        console.print("[dim]  Telegram skipped (enable later in config.json)[/dim]")

    # --- 5. Save config ---
    save_config(config)
    console.print()
    console.print(f"[green]✓[/green] Config saved to {config_path}")

    # --- 6. Create workspace ---
    workspace = get_workspace_path()
    if not workspace.exists():
        workspace.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓[/green] Created workspace at {workspace}")
    _create_workspace_templates(workspace)

    # --- 7. Generate kadiya-sl.yaml ---
    _generate_kadiya_config(prov)

    # --- 8. Validation ---
    console.print()
    console.print("[bold]Validating...[/bold]")

    errors = 0
    if config_path.exists():
        console.print("[green]✓[/green] Config file exists")
    else:
        console.print("[red]✗[/red] Config file missing")
        errors += 1

    if api_key:
        console.print(f"[green]✓[/green] API key set ({prov['label']})")
    else:
        errors += 1

    if workspace.exists():
        console.print(f"[green]✓[/green] Workspace ready")
    else:
        errors += 1

    # Test provider connectivity
    console.print("[dim]  Testing provider connectivity...[/dim]")
    try:
        import httpx
        test_urls = {
            "deepseek": "https://api.deepseek.com/models",
            "openai": "https://api.openai.com/v1/models",
            "openrouter": "https://openrouter.ai/api/v1/models",
        }
        url = test_urls.get(prov["name"])
        if url:
            resp = httpx.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            if resp.status_code in (200, 401, 403):
                console.print(f"[green]✓[/green] Provider reachable")
            else:
                console.print(f"[yellow]![/yellow] Provider returned {resp.status_code}")
    except Exception:
        console.print("[yellow]![/yellow] Could not test connectivity")

    # --- 9. Done ---
    console.print()
    if errors == 0:
        console.print("[bold green]Setup complete![/bold green]")
    else:
        console.print(f"[bold yellow]Setup complete with {errors} warning(s).[/bold yellow]")

    console.print()
    console.print("[bold]Quick start:[/bold]")
    console.print()
    console.print(f"  [cyan]kadiya agent -m \"Hello!\"[/cyan]")
    console.print()
    console.print("[bold]Interactive mode:[/bold]")
    console.print()
    console.print(f"  [cyan]kadiya agent[/cyan]")
    console.print()
    console.print("[bold]Diagnostics:[/bold]")
    console.print()
    console.print(f"  [cyan]kadiya doctor[/cyan]")
    console.print()


def _generate_kadiya_config(prov: dict) -> None:
    """Generate configs/kadiya-sl.yaml based on provider selection."""
    import datetime

    # Find the configs directory relative to the package
    configs_dir = Path(__file__).parent.parent.parent / "configs"
    configs_dir.mkdir(parents=True, exist_ok=True)
    config_path = configs_dir / "kadiya-sl.yaml"

    model = prov["model"]
    structured = prov["structured_model"]

    yaml_content = f"""\
# kadiya Sri Lanka Configuration
# Auto-generated by kadiya onboard
# Provider: {prov['label']}
# Generated: {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

profile:
  name: sl
  description: Sri Lanka profile - {prov['label']}
  version: "1.0.0"

locale:
  timezone: Asia/Colombo
  currency: LKR
  units: metric
  languages: [si, en]
  allow_singlish: true
  bilingual_output: false

tone:
  verbosity: low
  style: concise
  format: plain

agents:
  defaults:
    model: "{model}"
    max_tokens: 2048
    temperature: 0.3
    max_tool_iterations: 10
    memory_window: 30

routing:
  default_tier: cheap_general
  tiers:
    cheap_general:
      models: ["{model}"]
      max_input_tokens: 4000
      max_output_tokens: 1024
    structured:
      models: ["{structured}"]
      max_input_tokens: 8000
      max_output_tokens: 2048
    fallback:
      models: ["{model}"]
      max_input_tokens: 16000
      max_output_tokens: 4096
    sensitive:
      models: ["{structured}"]
      max_input_tokens: 8000
      max_output_tokens: 2048

  rules:
    - name: json_required
      condition: {{needs_json: true}}
      tier: structured
    - name: large_input
      condition: {{input_tokens_gt: 4000}}
      tier: structured
    - name: retry_escalation
      condition: {{retry_count_gt: 1}}
      tier: fallback
    - name: sensitive_content
      condition: {{sensitivity: true}}
      tier: sensitive

token_limits:
  max_input_tokens: 8000
  max_output_tokens: 2048
  intent_limits:
    translate: 1024
    summarize: 512
    format: 256
    search: 1024

conversation:
  summarize_after_turns: 5
  summarize_model: "{model}"
  retain_last_messages: 1

logging:
  log_tokens: true
  log_cost: true
  log_latency: true
  log_prompts: false
  log_pii: false

skills:
  enabled:
    - productivity-reminder
    - productivity-task-lite
    - productivity-follow-up
    - productivity-time-helper
    - personal-notes
    - personal-daily-brief
    - personal-contact-memory
    - communication-message-rewrite
    - communication-call-script
    - finance-bill-helper
    - productivity-web-search
    - productivity-whatis

tools:
  restrict_to_workspace: true
  exec:
    timeout: 30
  web:
    search:
      max_results: 3
"""

    config_path.write_text(yaml_content)
    console.print(f"[green]✓[/green] Generated {config_path}")




def _create_workspace_templates(workspace: Path):
    """Create default workspace template files."""
    templates = {
        "AGENTS.md": """# Agent Instructions

You are a helpful AI assistant. Be concise, accurate, and friendly.

## Guidelines

- Always explain what you're doing before taking actions
- Ask for clarification when the request is ambiguous
- Use tools to help accomplish tasks
- Remember important information in memory/MEMORY.md; past events are logged in memory/HISTORY.md
""",
        "SOUL.md": """# Soul

I am kadiya, a personal AI assistant for Sri Lanka.

## Personality

- Concise and direct
- Polite but not wordy
- Helpful, no fluff

## Values

- Privacy first - all data stays local
- Cost first - minimal token usage
- Accuracy over speed
""",
        "USER.md": """# User

Information about the user goes here.

## Preferences

- Communication style: (casual/formal)
- Timezone: (your timezone)
- Language: (your preferred language)
""",
    }
    
    for filename, content in templates.items():
        file_path = workspace / filename
        if not file_path.exists():
            file_path.write_text(content)
            console.print(f"  [dim]Created {filename}[/dim]")
    
    # Create memory directory and MEMORY.md
    memory_dir = workspace / "memory"
    memory_dir.mkdir(exist_ok=True)
    memory_file = memory_dir / "MEMORY.md"
    if not memory_file.exists():
        memory_file.write_text("""# Long-term Memory

This file stores important information that should persist across sessions.

## User Information

(Important facts about the user)

## Preferences

(User preferences learned over time)

## Important Notes

(Things to remember)
""")
        console.print("  [dim]Created memory/MEMORY.md[/dim]")
    
    history_file = memory_dir / "HISTORY.md"
    if not history_file.exists():
        history_file.write_text("")
        console.print("  [dim]Created memory/HISTORY.md[/dim]")

    # Create skills directory and install kadiya skills
    skills_dir = workspace / "skills"
    skills_dir.mkdir(exist_ok=True)
    _install_kadiya_skills(skills_dir)


def _install_kadiya_skills(skills_dir: Path):
    """Copy kadiya skills from project into workspace with flattened names."""
    import shutil

    # kadiya skills live in <project>/skills/<category>/<name>/
    project_skills = Path(__file__).parent.parent.parent / "skills"
    if not project_skills.exists():
        return

    # Build set of valid skill names from project
    valid_skills: set[str] = set()
    for category_dir in sorted(project_skills.iterdir()):
        if not category_dir.is_dir():
            continue
        for skill_dir in sorted(category_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            if (skill_dir / "SKILL.md").exists():
                valid_skills.add(f"{category_dir.name}-{skill_dir.name}")

    # Remove workspace skills that are no longer in the project
    if skills_dir.exists():
        for existing in list(skills_dir.iterdir()):
            if existing.is_dir() and existing.name not in valid_skills:
                shutil.rmtree(existing)
                console.print(f"  [dim]Removed old skill: {existing.name}[/dim]")

    # Install/update skills
    installed = 0
    for category_dir in sorted(project_skills.iterdir()):
        if not category_dir.is_dir():
            continue
        for skill_dir in sorted(category_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            flat_name = f"{category_dir.name}-{skill_dir.name}"
            dest_dir = skills_dir / flat_name

            # Replace existing to keep skills up to date
            if dest_dir.exists():
                shutil.rmtree(dest_dir)

            shutil.copytree(skill_dir, dest_dir)
            console.print(f"  [dim]Installed skill: {flat_name}[/dim]")
            installed += 1

    if installed:
        console.print(f"[green]✓[/green] Installed {installed} skills")


def _make_provider(config):
    """Create LiteLLMProvider from config. Exits if no API key found."""
    from nanobot.providers.litellm_provider import LiteLLMProvider
    p = config.get_provider()
    model = config.agents.defaults.model
    if not (p and p.api_key) and not model.startswith("bedrock/"):
        console.print("[red]Error: No API key configured.[/red]")
        console.print("Set one in ~/.nanobot/config.json under providers, or run: kadiya onboard")
        raise typer.Exit(1)
    return LiteLLMProvider(
        api_key=p.api_key if p else None,
        api_base=config.get_api_base(),
        default_model=model,
        extra_headers=p.extra_headers if p else None,
        provider_name=config.get_provider_name(),
    )


# ============================================================================
# Gateway / Server
# ============================================================================


@app.command()
def gateway(
    port: int = typer.Option(18790, "--port", "-p", help="Gateway port"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Start the kadiya gateway."""
    from nanobot.config.loader import load_config, get_data_dir
    from nanobot.bus.queue import MessageBus
    from nanobot.agent.loop import AgentLoop
    from nanobot.channels.manager import ChannelManager
    from nanobot.session.manager import SessionManager
    from nanobot.cron.service import CronService
    from nanobot.cron.types import CronJob
    from nanobot.heartbeat.service import HeartbeatService
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    console.print(f"{__logo__} Starting kadiya gateway on port {port}...")
    
    config = load_config()
    bus = MessageBus()
    provider = _make_provider(config)
    session_manager = SessionManager(config.workspace_path)
    
    # Create cron service first (callback set after agent creation)
    cron_store_path = get_data_dir() / "cron" / "jobs.json"
    cron = CronService(cron_store_path)
    
    # Create agent with cron service
    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=config.workspace_path,
        model=config.agents.defaults.model,
        temperature=config.agents.defaults.temperature,
        max_tokens=config.agents.defaults.max_tokens,
        max_iterations=config.agents.defaults.max_tool_iterations,
        memory_window=config.agents.defaults.memory_window,
        brave_api_key=config.tools.web.search.api_key or None,
        exec_config=config.tools.exec,
        cron_service=cron,
        restrict_to_workspace=config.tools.restrict_to_workspace,
        session_manager=session_manager,
    )
    
    # Set cron callback (needs agent)
    async def on_cron_job(job: CronJob) -> str | None:
        """Execute a cron job through the agent."""
        response = await agent.process_direct(
            job.payload.message,
            session_key=f"cron:{job.id}",
            channel=job.payload.channel or "cli",
            chat_id=job.payload.to or "direct",
        )
        if job.payload.deliver and job.payload.to:
            from nanobot.bus.events import OutboundMessage
            await bus.publish_outbound(OutboundMessage(
                channel=job.payload.channel or "cli",
                chat_id=job.payload.to,
                content=response or ""
            ))
        return response
    cron.on_job = on_cron_job
    
    # Create heartbeat service
    async def on_heartbeat(prompt: str) -> str:
        """Execute heartbeat through the agent."""
        return await agent.process_direct(prompt, session_key="heartbeat")
    
    heartbeat = HeartbeatService(
        workspace=config.workspace_path,
        on_heartbeat=on_heartbeat,
        interval_s=30 * 60,  # 30 minutes
        enabled=True
    )
    
    # Create channel manager
    channels = ChannelManager(config, bus)
    
    if channels.enabled_channels:
        console.print(f"[green]✓[/green] Channels enabled: {', '.join(channels.enabled_channels)}")
    else:
        console.print("[yellow]Warning: No channels enabled[/yellow]")
    
    cron_status = cron.status()
    if cron_status["jobs"] > 0:
        console.print(f"[green]✓[/green] Cron: {cron_status['jobs']} scheduled jobs")
    
    console.print(f"[green]✓[/green] Heartbeat: every 30m")
    
    async def run():
        try:
            await cron.start()
            await heartbeat.start()
            await asyncio.gather(
                agent.run(),
                channels.start_all(),
            )
        except KeyboardInterrupt:
            console.print("\nShutting down...")
            heartbeat.stop()
            cron.stop()
            agent.stop()
            await channels.stop_all()
    
    asyncio.run(run())




# ============================================================================
# Agent Commands
# ============================================================================


@app.command()
def agent(
    message: str = typer.Option(None, "--message", "-m", help="Message to send to the agent"),
    session_id: str = typer.Option("cli:direct", "--session", "-s", help="Session ID"),
    markdown: bool = typer.Option(True, "--markdown/--no-markdown", help="Render assistant output as Markdown"),
    logs: bool = typer.Option(False, "--logs/--no-logs", help="Show kadiya runtime logs during chat"),
):
    """Interact with the agent directly."""
    from nanobot.config.loader import load_config
    from nanobot.bus.queue import MessageBus
    from nanobot.agent.loop import AgentLoop
    from loguru import logger
    
    config = load_config()
    
    bus = MessageBus()
    provider = _make_provider(config)

    if logs:
        logger.enable("nanobot")
    else:
        logger.disable("nanobot")
    
    agent_loop = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=config.workspace_path,
        model=config.agents.defaults.model,
        temperature=config.agents.defaults.temperature,
        max_tokens=config.agents.defaults.max_tokens,
        max_iterations=config.agents.defaults.max_tool_iterations,
        memory_window=config.agents.defaults.memory_window,
        brave_api_key=config.tools.web.search.api_key or None,
        exec_config=config.tools.exec,
        restrict_to_workspace=config.tools.restrict_to_workspace,
    )
    
    # Show spinner when logs are off (no output to miss); skip when logs are on
    def _thinking_ctx():
        if logs:
            from contextlib import nullcontext
            return nullcontext()
        # Animated spinner is safe to use with prompt_toolkit input handling
        return console.status("[dim]kadiya is thinking...[/dim]", spinner="dots")

    if message:
        # Single message mode
        async def run_once():
            msg = _fix_msys_path(message)
            with _thinking_ctx():
                response = await agent_loop.process_direct(msg, session_id)
            _print_agent_response(response, render_markdown=markdown)

        asyncio.run(run_once())
    else:
        # Interactive mode
        _init_prompt_session()
        console.print(f"{__logo__} Interactive mode (type [bold]exit[/bold] or [bold]Ctrl+C[/bold] to quit)\n")

        def _exit_on_sigint(signum, frame):
            _restore_terminal()
            console.print("\nGoodbye!")
            os._exit(0)

        signal.signal(signal.SIGINT, _exit_on_sigint)
        
        async def run_interactive():
            while True:
                try:
                    _flush_pending_tty_input()
                    user_input = await _read_interactive_input_async()
                    command = user_input.strip()
                    if not command:
                        continue

                    if _is_exit_command(command):
                        _restore_terminal()
                        console.print("\nGoodbye!")
                        break
                    
                    with _thinking_ctx():
                        response = await agent_loop.process_direct(_fix_msys_path(user_input), session_id)
                    _print_agent_response(response, render_markdown=markdown)
                except KeyboardInterrupt:
                    _restore_terminal()
                    console.print("\nGoodbye!")
                    break
                except EOFError:
                    _restore_terminal()
                    console.print("\nGoodbye!")
                    break
        
        asyncio.run(run_interactive())


# ============================================================================
# Channel Commands
# ============================================================================


channels_app = typer.Typer(help="Manage channels")
app.add_typer(channels_app, name="channels")


@channels_app.command("status")
def channels_status():
    """Show channel status."""
    from nanobot.config.loader import load_config

    config = load_config()

    table = Table(title="Channel Status")
    table.add_column("Channel", style="cyan")
    table.add_column("Enabled", style="green")
    table.add_column("Configuration", style="yellow")

    # WhatsApp
    wa = config.channels.whatsapp
    table.add_row(
        "WhatsApp",
        "✓" if wa.enabled else "✗",
        wa.bridge_url
    )

    dc = config.channels.discord
    table.add_row(
        "Discord",
        "✓" if dc.enabled else "✗",
        dc.gateway_url
    )

    # Feishu
    fs = config.channels.feishu
    fs_config = f"app_id: {fs.app_id[:10]}..." if fs.app_id else "[dim]not configured[/dim]"
    table.add_row(
        "Feishu",
        "✓" if fs.enabled else "✗",
        fs_config
    )

    # Mochat
    mc = config.channels.mochat
    mc_base = mc.base_url or "[dim]not configured[/dim]"
    table.add_row(
        "Mochat",
        "✓" if mc.enabled else "✗",
        mc_base
    )
    
    # Telegram
    tg = config.channels.telegram
    tg_config = f"token: {tg.token[:10]}..." if tg.token else "[dim]not configured[/dim]"
    table.add_row(
        "Telegram",
        "✓" if tg.enabled else "✗",
        tg_config
    )

    # Slack
    slack = config.channels.slack
    slack_config = "socket" if slack.app_token and slack.bot_token else "[dim]not configured[/dim]"
    table.add_row(
        "Slack",
        "✓" if slack.enabled else "✗",
        slack_config
    )

    console.print(table)


def _get_bridge_dir() -> Path:
    """Get the bridge directory, setting it up if needed."""
    import shutil
    import subprocess
    
    # User's bridge location
    user_bridge = Path.home() / ".nanobot" / "bridge"
    
    # Check if already built
    if (user_bridge / "dist" / "index.js").exists():
        return user_bridge
    
    # Check for npm
    if not shutil.which("npm"):
        console.print("[red]npm not found. Please install Node.js >= 18.[/red]")
        raise typer.Exit(1)
    
    # Find source bridge: first check package data, then source dir
    pkg_bridge = Path(__file__).parent.parent / "bridge"  # nanobot/bridge (installed)
    src_bridge = Path(__file__).parent.parent.parent / "bridge"  # repo root/bridge (dev)
    
    source = None
    if (pkg_bridge / "package.json").exists():
        source = pkg_bridge
    elif (src_bridge / "package.json").exists():
        source = src_bridge
    
    if not source:
        console.print("[red]Bridge source not found.[/red]")
        console.print("Try reinstalling: pip install --force-reinstall kadiya")
        raise typer.Exit(1)
    
    console.print(f"{__logo__} Setting up bridge...")
    
    # Copy to user directory
    user_bridge.parent.mkdir(parents=True, exist_ok=True)
    if user_bridge.exists():
        shutil.rmtree(user_bridge)
    shutil.copytree(source, user_bridge, ignore=shutil.ignore_patterns("node_modules", "dist"))
    
    # Install and build
    try:
        console.print("  Installing dependencies...")
        subprocess.run(["npm", "install"], cwd=user_bridge, check=True, capture_output=True)
        
        console.print("  Building...")
        subprocess.run(["npm", "run", "build"], cwd=user_bridge, check=True, capture_output=True)
        
        console.print("[green]✓[/green] Bridge ready\n")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Build failed: {e}[/red]")
        if e.stderr:
            console.print(f"[dim]{e.stderr.decode()[:500]}[/dim]")
        raise typer.Exit(1)
    
    return user_bridge


@channels_app.command("login")
def channels_login():
    """Link device via QR code."""
    import subprocess
    from nanobot.config.loader import load_config
    
    config = load_config()
    bridge_dir = _get_bridge_dir()
    
    console.print(f"{__logo__} Starting bridge...")
    console.print("Scan the QR code to connect.\n")
    
    env = {**os.environ}
    if config.channels.whatsapp.bridge_token:
        env["BRIDGE_TOKEN"] = config.channels.whatsapp.bridge_token
    
    try:
        subprocess.run(["npm", "start"], cwd=bridge_dir, check=True, env=env)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Bridge failed: {e}[/red]")
    except FileNotFoundError:
        console.print("[red]npm not found. Please install Node.js.[/red]")


# ============================================================================
# Cron Commands
# ============================================================================

cron_app = typer.Typer(help="Manage scheduled tasks")
app.add_typer(cron_app, name="cron")


@cron_app.command("list")
def cron_list(
    all: bool = typer.Option(False, "--all", "-a", help="Include disabled jobs"),
):
    """List scheduled jobs."""
    from nanobot.config.loader import get_data_dir
    from nanobot.cron.service import CronService
    
    store_path = get_data_dir() / "cron" / "jobs.json"
    service = CronService(store_path)
    
    jobs = service.list_jobs(include_disabled=all)
    
    if not jobs:
        console.print("No scheduled jobs.")
        return
    
    table = Table(title="Scheduled Jobs")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Schedule")
    table.add_column("Status")
    table.add_column("Next Run")
    
    import time
    for job in jobs:
        # Format schedule
        if job.schedule.kind == "every":
            sched = f"every {(job.schedule.every_ms or 0) // 1000}s"
        elif job.schedule.kind == "cron":
            sched = job.schedule.expr or ""
        else:
            sched = "one-time"
        
        # Format next run
        next_run = ""
        if job.state.next_run_at_ms:
            next_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(job.state.next_run_at_ms / 1000))
            next_run = next_time
        
        status = "[green]enabled[/green]" if job.enabled else "[dim]disabled[/dim]"
        
        table.add_row(job.id, job.name, sched, status, next_run)
    
    console.print(table)


@cron_app.command("add")
def cron_add(
    name: str = typer.Option(..., "--name", "-n", help="Job name"),
    message: str = typer.Option(..., "--message", "-m", help="Message for agent"),
    every: int = typer.Option(None, "--every", "-e", help="Run every N seconds"),
    cron_expr: str = typer.Option(None, "--cron", "-c", help="Cron expression (e.g. '0 9 * * *')"),
    at: str = typer.Option(None, "--at", help="Run once at time (ISO format)"),
    deliver: bool = typer.Option(False, "--deliver", "-d", help="Deliver response to channel"),
    to: str = typer.Option(None, "--to", help="Recipient for delivery"),
    channel: str = typer.Option(None, "--channel", help="Channel for delivery (e.g. 'telegram', 'whatsapp')"),
):
    """Add a scheduled job."""
    from nanobot.config.loader import get_data_dir
    from nanobot.cron.service import CronService
    from nanobot.cron.types import CronSchedule
    
    # Determine schedule type
    if every:
        schedule = CronSchedule(kind="every", every_ms=every * 1000)
    elif cron_expr:
        schedule = CronSchedule(kind="cron", expr=cron_expr)
    elif at:
        import datetime
        dt = datetime.datetime.fromisoformat(at)
        schedule = CronSchedule(kind="at", at_ms=int(dt.timestamp() * 1000))
    else:
        console.print("[red]Error: Must specify --every, --cron, or --at[/red]")
        raise typer.Exit(1)
    
    store_path = get_data_dir() / "cron" / "jobs.json"
    service = CronService(store_path)
    
    job = service.add_job(
        name=name,
        schedule=schedule,
        message=message,
        deliver=deliver,
        to=to,
        channel=channel,
    )
    
    console.print(f"[green]✓[/green] Added job '{job.name}' ({job.id})")


@cron_app.command("remove")
def cron_remove(
    job_id: str = typer.Argument(..., help="Job ID to remove"),
):
    """Remove a scheduled job."""
    from nanobot.config.loader import get_data_dir
    from nanobot.cron.service import CronService
    
    store_path = get_data_dir() / "cron" / "jobs.json"
    service = CronService(store_path)
    
    if service.remove_job(job_id):
        console.print(f"[green]✓[/green] Removed job {job_id}")
    else:
        console.print(f"[red]Job {job_id} not found[/red]")


@cron_app.command("enable")
def cron_enable(
    job_id: str = typer.Argument(..., help="Job ID"),
    disable: bool = typer.Option(False, "--disable", help="Disable instead of enable"),
):
    """Enable or disable a job."""
    from nanobot.config.loader import get_data_dir
    from nanobot.cron.service import CronService
    
    store_path = get_data_dir() / "cron" / "jobs.json"
    service = CronService(store_path)
    
    job = service.enable_job(job_id, enabled=not disable)
    if job:
        status = "disabled" if disable else "enabled"
        console.print(f"[green]✓[/green] Job '{job.name}' {status}")
    else:
        console.print(f"[red]Job {job_id} not found[/red]")


@cron_app.command("run")
def cron_run(
    job_id: str = typer.Argument(..., help="Job ID to run"),
    force: bool = typer.Option(False, "--force", "-f", help="Run even if disabled"),
):
    """Manually run a job."""
    from nanobot.config.loader import get_data_dir
    from nanobot.cron.service import CronService
    
    store_path = get_data_dir() / "cron" / "jobs.json"
    service = CronService(store_path)
    
    async def run():
        return await service.run_job(job_id, force=force)
    
    if asyncio.run(run()):
        console.print(f"[green]✓[/green] Job executed")
    else:
        console.print(f"[red]Failed to run job {job_id}[/red]")


# ============================================================================
# Status Commands
# ============================================================================


@app.command()
def status():
    """Show kadiya status."""
    from nanobot.config.loader import load_config, get_config_path

    config_path = get_config_path()
    config = load_config()
    workspace = config.workspace_path

    console.print(f"{__logo__} kadiya Status\n")

    console.print(f"Config: {config_path} {'[green]✓[/green]' if config_path.exists() else '[red]✗[/red]'}")
    console.print(f"Workspace: {workspace} {'[green]✓[/green]' if workspace.exists() else '[red]✗[/red]'}")

    if config_path.exists():
        from nanobot.providers.registry import PROVIDERS

        console.print(f"Model: {config.agents.defaults.model}")
        
        # Check API keys from registry
        for spec in PROVIDERS:
            p = getattr(config.providers, spec.name, None)
            if p is None:
                continue
            if spec.is_local:
                # Local deployments show api_base instead of api_key
                if p.api_base:
                    console.print(f"{spec.label}: [green]✓ {p.api_base}[/green]")
                else:
                    console.print(f"{spec.label}: [dim]not set[/dim]")
            else:
                has_key = bool(p.api_key)
                console.print(f"{spec.label}: {'[green]✓[/green]' if has_key else '[dim]not set[/dim]'}")


# ============================================================================
# Doctor / Validation
# ============================================================================


@app.command()
def doctor():
    """Run diagnostics and attempt auto-fix for common issues."""
    import json
    import shutil
    from nanobot.config.loader import load_config, get_config_path, save_config
    from nanobot.config.schema import Config

    console.print(f"{__logo__} kadiya doctor\n")

    config_path = get_config_path()
    errors = 0
    warnings = 0

    # --- Check 1: Config file ---
    if config_path.exists():
        console.print("[green]✓[/green] Config file exists")
        try:
            with open(config_path) as f:
                json.load(f)
            console.print("[green]✓[/green] Config JSON is valid")
        except json.JSONDecodeError as e:
            console.print(f"[red]✗[/red] Config JSON invalid: {e}")
            console.print("  [dim]Fix: Delete and re-run install.bat or kadiya onboard[/dim]")
            errors += 1
    else:
        console.print("[red]✗[/red] Config file missing")
        console.print("  [yellow]Auto-fix: Creating default config...[/yellow]")
        try:
            save_config(Config())
            console.print("  [green]✓[/green] Default config created")
        except Exception as e:
            console.print(f"  [red]Failed: {e}[/red]")
            errors += 1

    # --- Check 2: Config loads without error ---
    config = None
    try:
        config = load_config()
        console.print("[green]✓[/green] Config loads successfully")
    except Exception as e:
        console.print(f"[red]✗[/red] Config load error: {e}")
        errors += 1

    if not config:
        console.print(f"\n[red]Cannot continue: {errors} error(s)[/red]")
        raise typer.Exit(1)

    # --- Check 3: API key ---
    provider = config.get_provider()
    provider_name = config.get_provider_name()
    if provider and provider.api_key:
        key_preview = provider.api_key[:8] + "..." if len(provider.api_key) > 8 else "***"
        console.print(f"[green]✓[/green] API key found ({provider_name}: {key_preview})")
    else:
        console.print("[red]✗[/red] No API key configured")
        console.print("  [dim]Fix: Set API key in ~/.nanobot/config.json or run: kadiya onboard[/dim]")
        errors += 1

    # --- Check 4: Workspace ---
    workspace = config.workspace_path
    if workspace.exists():
        console.print(f"[green]✓[/green] Workspace exists: {workspace}")
    else:
        console.print("[yellow]![/yellow] Workspace missing")
        console.print("  [yellow]Auto-fix: Creating workspace...[/yellow]")
        try:
            workspace.mkdir(parents=True, exist_ok=True)
            (workspace / "memory").mkdir(exist_ok=True)
            console.print("  [green]✓[/green] Workspace created")
        except Exception as e:
            console.print(f"  [red]Failed: {e}[/red]")
            errors += 1

    # --- Check 5: Memory files ---
    memory_dir = workspace / "memory"
    memory_file = memory_dir / "MEMORY.md"
    history_file = memory_dir / "HISTORY.md"

    if memory_dir.exists():
        console.print("[green]✓[/green] Memory directory exists")
    else:
        console.print("  [yellow]Auto-fix: Creating memory directory...[/yellow]")
        memory_dir.mkdir(parents=True, exist_ok=True)

    if not memory_file.exists():
        memory_file.write_text("# Long-term Memory\n\n")
        console.print("  [yellow]Auto-fix: Created MEMORY.md[/yellow]")
    if not history_file.exists():
        history_file.write_text("")
        console.print("  [yellow]Auto-fix: Created HISTORY.md[/yellow]")

    # --- Check 6: kadiya config ---
    kadiya_config_path = Path(__file__).parent.parent.parent / "configs" / "kadiya-sl.yaml"
    if kadiya_config_path.exists():
        console.print(f"[green]✓[/green] kadiya config exists: {kadiya_config_path}")
        try:
            import yaml
            with open(kadiya_config_path) as f:
                yaml.safe_load(f)
            console.print("[green]✓[/green] kadiya YAML is valid")
        except ImportError:
            console.print("[yellow]![/yellow] pyyaml not installed, skipping YAML validation")
            warnings += 1
        except Exception as e:
            console.print(f"[red]✗[/red] kadiya YAML invalid: {e}")
            errors += 1
    else:
        console.print("[yellow]![/yellow] kadiya config not found (optional)")
        console.print("  [dim]Run install.sh to generate it[/dim]")
        warnings += 1

    # --- Check 7: Python dependencies ---
    missing_deps = []
    for pkg in ["litellm", "typer", "pydantic", "httpx", "loguru", "rich"]:
        try:
            __import__(pkg)
        except ImportError:
            missing_deps.append(pkg)

    if not missing_deps:
        console.print("[green]✓[/green] Core dependencies installed")
    else:
        console.print(f"[red]✗[/red] Missing dependencies: {', '.join(missing_deps)}")
        console.print("  [dim]Fix: pip install -e .[/dim]")
        errors += 1

    # --- Check 8: Optional kadiya dependencies ---
    optional_missing = []
    for pkg, name in [("yaml", "pyyaml"), ("openpyxl", "openpyxl"),
                       ("docx", "python-docx"), ("pptx", "python-pptx")]:
        try:
            __import__(pkg)
        except ImportError:
            optional_missing.append(name)

    if not optional_missing:
        console.print("[green]✓[/green] Optional dependencies installed")
    else:
        console.print(f"[yellow]![/yellow] Optional deps missing: {', '.join(optional_missing)}")
        console.print(f"  [dim]Install: pip install {' '.join(optional_missing)}[/dim]")
        warnings += 1

    # --- Check 9: Required tools ---
    for tool in ["curl", "git"]:
        if shutil.which(tool):
            console.print(f"[green]✓[/green] {tool} available")
        else:
            console.print(f"[yellow]![/yellow] {tool} not found")
            warnings += 1

    # --- Check 10: Provider connectivity ---
    if provider and provider.api_key:
        console.print("[dim]Testing provider connectivity...[/dim]")
        try:
            import httpx
            url = None
            headers = {"Authorization": f"Bearer {provider.api_key}"}

            if provider_name == "openai":
                url = "https://api.openai.com/v1/models"
            elif provider_name == "deepseek":
                url = "https://api.deepseek.com/models"
            elif provider_name == "openrouter":
                url = "https://openrouter.ai/api/v1/models"

            if url:
                resp = httpx.get(url, headers=headers, timeout=10)
                if resp.status_code in (200, 401, 403):
                    console.print(f"[green]✓[/green] Provider reachable ({provider_name})")
                else:
                    console.print(f"[yellow]![/yellow] Provider returned {resp.status_code}")
                    warnings += 1
            else:
                console.print("[dim]  Skipping connectivity test (unknown provider)[/dim]")
        except Exception as e:
            console.print(f"[yellow]![/yellow] Connectivity test failed: {e}")
            warnings += 1

    # --- Summary ---
    console.print()
    if errors == 0 and warnings == 0:
        console.print("[green]All checks passed![/green]")
    elif errors == 0:
        console.print(f"[yellow]{warnings} warning(s), 0 errors. kadiya should work fine.[/yellow]")
    else:
        console.print(f"[red]{errors} error(s), {warnings} warning(s). Please fix errors above.[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
