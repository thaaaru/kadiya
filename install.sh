#!/usr/bin/env bash
# ============================================================================
# kadiya installer - single-command setup for the kadiya NanoBot distribution
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/your-repo/nanobot/main/install.sh | bash
#   or
#   ./install.sh
#
# What this does:
#   1. Detects OS and validates prerequisites
#   2. Sets up Python virtual environment
#   3. Installs dependencies
#   4. Prompts for LLM provider + API key
#   5. Generates configs/kadiya-sl.yaml and ~/.nanobot/config.json
#   6. Runs validation (kadiya doctor)
#   7. Prints next steps
#
# No manual config editing required.
# ============================================================================

set -euo pipefail

# --- Colors (safe for piped output) ----------------------------------------
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    DIM='\033[2m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' CYAN='' BOLD='' DIM='' NC=''
fi

# --- Helpers ----------------------------------------------------------------
info()    { echo -e "${BLUE}[info]${NC}  $*"; }
ok()      { echo -e "${GREEN}[  ok]${NC}  $*"; }
warn()    { echo -e "${YELLOW}[warn]${NC}  $*"; }
fail()    { echo -e "${RED}[fail]${NC}  $*"; exit 1; }
step()    { echo -e "\n${BOLD}${CYAN}▸ $*${NC}"; }
divider() { echo -e "${DIM}────────────────────────────────────────────────${NC}"; }

# --- Banner -----------------------------------------------------------------
echo ""
echo -e "${BOLD}${CYAN}"
echo "  ┌────────────────────────────────────────┐"
echo "  │                                        │"
echo "  │   kadiya                               │"
echo "  │   Smart bot for Sri Lanka              │"
echo "  │                                        │"
echo "  │   Token-efficient. Cost-first.         │"
echo "  │   Sinhala + English. WhatsApp ready.   │"
echo "  │                                        │"
echo "  └────────────────────────────────────────┘"
echo -e "${NC}"

# ============================================================================
# 1. ENVIRONMENT DETECTION & REPAIR
# ============================================================================
step "Detecting environment"

# --- Detect OS --------------------------------------------------------------
OS="unknown"
IS_WSL=false

case "$(uname -s)" in
    Linux*)
        OS="linux"
        if grep -qEi "(microsoft|wsl)" /proc/version 2>/dev/null; then
            IS_WSL=true
            info "Detected: Linux (WSL)"
        else
            info "Detected: Linux"
        fi
        ;;
    Darwin*)
        OS="macos"
        info "Detected: macOS $(sw_vers -productVersion 2>/dev/null || echo '')"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        OS="windows"
        warn "Native Windows detected. WSL is recommended."
        ;;
    *)
        warn "Unknown OS: $(uname -s). Proceeding anyway."
        ;;
esac

# --- Check git --------------------------------------------------------------
if command -v git &>/dev/null; then
    ok "git found: $(git --version | head -1)"
else
    fail "git not found. Please install git first."
fi

# --- Check python3 ----------------------------------------------------------
PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null; then
        # Verify it's Python 3.11+
        version=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
            PYTHON="$candidate"
            ok "Python found: $($candidate --version)"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo ""
    fail "Python 3.11+ not found.

Install Python:
  macOS:   brew install python@3.12
  Ubuntu:  sudo apt install python3.12 python3.12-venv
  WSL:     sudo apt install python3.12 python3.12-venv"
fi

# --- Determine project directory --------------------------------------------
# If we're already in the nanobot repo, use it. Otherwise clone.
REPO_DIR=""

if [ -f "pyproject.toml" ] && grep -q "nanobot" pyproject.toml 2>/dev/null; then
    REPO_DIR="$(pwd)"
    ok "Already in nanobot directory: $REPO_DIR"
elif [ -f "$(dirname "$0")/pyproject.toml" ] && grep -q "nanobot" "$(dirname "$0")/pyproject.toml" 2>/dev/null; then
    REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
    ok "Found nanobot at: $REPO_DIR"
else
    step "Cloning nanobot repository"
    REPO_DIR="$HOME/nanobot"
    if [ -d "$REPO_DIR/.git" ]; then
        info "Repository already exists at $REPO_DIR, pulling latest..."
        git -C "$REPO_DIR" pull --rebase 2>/dev/null || warn "Pull failed, using existing code"
    else
        git clone https://github.com/HKUDS/nanobot.git "$REPO_DIR" || fail "Failed to clone repository"
    fi
    ok "Repository ready at: $REPO_DIR"
fi

cd "$REPO_DIR"

# ============================================================================
# 2. VIRTUAL ENVIRONMENT & DEPENDENCIES
# ============================================================================
step "Setting up Python environment"

VENV_DIR="$REPO_DIR/.venv"

# Create or repair venv
if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
    info "Virtual environment exists, verifying..."
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate" 2>/dev/null || {
        warn "Broken venv, recreating..."
        rm -rf "$VENV_DIR"
        "$PYTHON" -m venv "$VENV_DIR" || fail "Failed to create venv"
        source "$VENV_DIR/bin/activate"
    }
else
    info "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR" || fail "Failed to create venv. Try: sudo apt install python3-venv"
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
fi

ok "Virtual environment active: $VENV_DIR"

# Install dependencies
step "Installing dependencies"

pip install --upgrade pip -q 2>/dev/null
pip install -e . -q 2>&1 | tail -3
pip install pyyaml openpyxl python-docx python-pptx -q 2>&1 | tail -1

ok "All dependencies installed"

# ============================================================================
# 3. GUIDED PROVIDER SELECTION (Interactive)
# ============================================================================
step "Provider configuration"

echo ""
echo -e "  Select your LLM provider:"
echo ""
echo -e "  ${BOLD}1${NC}) OpenAI          ${DIM}(GPT-3.5-turbo, default, reliable)${NC}"
echo -e "  ${BOLD}2${NC}) DeepSeek        ${DIM}(Direct API, cheapest option)${NC}"
echo -e "  ${BOLD}3${NC}) DeepSeek via OR  ${DIM}(OpenRouter gateway, flexible)${NC}"
echo ""

PROVIDER=""
PROVIDER_NAME=""
PROVIDER_CONFIG_KEY=""
API_KEY=""
API_BASE=""
DEFAULT_MODEL=""
STRUCTURED_MODEL=""
HIGH_CONTEXT_MODEL=""

while true; do
    echo -ne "  ${BOLD}Choose [1-3]:${NC} "
    read -r choice

    case "$choice" in
        1)
            PROVIDER="openai"
            PROVIDER_NAME="OpenAI"
            PROVIDER_CONFIG_KEY="openai"
            DEFAULT_MODEL="gpt-3.5-turbo"
            STRUCTURED_MODEL="gpt-3.5-turbo"
            HIGH_CONTEXT_MODEL="gpt-3.5-turbo-1106"
            break
            ;;
        2)
            PROVIDER="deepseek"
            PROVIDER_NAME="DeepSeek (Direct)"
            PROVIDER_CONFIG_KEY="deepseek"
            DEFAULT_MODEL="deepseek/deepseek-chat"
            STRUCTURED_MODEL="deepseek/deepseek-chat"
            HIGH_CONTEXT_MODEL="deepseek/deepseek-chat"
            API_BASE="https://api.deepseek.com"
            break
            ;;
        3)
            PROVIDER="openrouter"
            PROVIDER_NAME="DeepSeek via OpenRouter"
            PROVIDER_CONFIG_KEY="openrouter"
            DEFAULT_MODEL="deepseek/deepseek-chat"
            STRUCTURED_MODEL="deepseek/deepseek-chat"
            HIGH_CONTEXT_MODEL="deepseek/deepseek-chat"
            break
            ;;
        *)
            warn "Please enter 1, 2, or 3"
            ;;
    esac
done

ok "Selected: $PROVIDER_NAME"

# --- Prompt for API key (secure, no echo) ------------------------------------
echo ""
echo -e "  ${DIM}Get your API key from:${NC}"
case "$PROVIDER" in
    openai)     echo -e "  ${DIM}https://platform.openai.com/api-keys${NC}" ;;
    deepseek)   echo -e "  ${DIM}https://platform.deepseek.com/api_keys${NC}" ;;
    openrouter) echo -e "  ${DIM}https://openrouter.ai/keys${NC}" ;;
esac
echo ""

while true; do
    echo -ne "  ${BOLD}API Key:${NC} "
    read -rs API_KEY
    echo ""

    if [ -z "$API_KEY" ]; then
        warn "API key cannot be empty. Try again."
        continue
    fi

    # Basic format validation
    case "$PROVIDER" in
        openai)
            if [[ ! "$API_KEY" == sk-* ]]; then
                warn "OpenAI keys usually start with 'sk-'. Continuing anyway."
            fi
            ;;
        openrouter)
            if [[ ! "$API_KEY" == sk-or-* ]]; then
                warn "OpenRouter keys usually start with 'sk-or-'. Continuing anyway."
            fi
            ;;
    esac

    ok "API key received (${#API_KEY} chars)"
    break
done

# ============================================================================
# 4. GENERATE CONFIGURATION (NO MANUAL EDITING)
# ============================================================================
step "Generating configuration"

# --- Set environment variable for API key ------------------------------------
# Determine the env var name based on provider
ENV_VAR_NAME=""
case "$PROVIDER" in
    openai)     ENV_VAR_NAME="OPENAI_API_KEY" ;;
    deepseek)   ENV_VAR_NAME="DEEPSEEK_API_KEY" ;;
    openrouter) ENV_VAR_NAME="OPENROUTER_API_KEY" ;;
esac

# Write to shell profile
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.profile" ]; then
    SHELL_RC="$HOME/.profile"
fi

if [ -n "$SHELL_RC" ]; then
    # Remove old entry if present
    if grep -q "^export ${ENV_VAR_NAME}=" "$SHELL_RC" 2>/dev/null; then
        # Use a temp file for portability (macOS sed -i requires extension)
        grep -v "^export ${ENV_VAR_NAME}=" "$SHELL_RC" > "$SHELL_RC.tmp" && mv "$SHELL_RC.tmp" "$SHELL_RC"
    fi
    echo "export ${ENV_VAR_NAME}='${API_KEY}'" >> "$SHELL_RC"
    ok "API key saved to $SHELL_RC as \$${ENV_VAR_NAME}"
fi

# Export for current session
export "$ENV_VAR_NAME=$API_KEY"

# --- Generate ~/.nanobot/config.json -----------------------------------------
NANOBOT_DIR="$HOME/.nanobot"
mkdir -p "$NANOBOT_DIR"

# Build the provider JSON block
PROVIDER_JSON=""
case "$PROVIDER" in
    openai)
        PROVIDER_JSON='"openai": {"apiKey": "'"$API_KEY"'"}'
        ;;
    deepseek)
        PROVIDER_JSON='"deepseek": {"apiKey": "'"$API_KEY"'"}'
        ;;
    openrouter)
        PROVIDER_JSON='"openrouter": {"apiKey": "'"$API_KEY"'"}'
        ;;
esac

# --- WhatsApp bot setup (optional) -------------------------------------------
echo ""
echo -ne "  ${BOLD}Enable WhatsApp bot?${NC} ${DIM}(y/N):${NC} "
read -r ENABLE_WA

WHATSAPP_JSON=""
if [[ "$ENABLE_WA" =~ ^[Yy] ]]; then
    echo ""
    echo -e "  ${DIM}WhatsApp uses a local Node.js bridge (Baileys).${NC}"
    echo -e "  ${DIM}You'll need Node.js 18+ installed to run the bridge.${NC}"
    echo ""

    # Ask for allowed phone number
    echo -e "  ${DIM}Enter your WhatsApp number (with country code, e.g. +94771234567)${NC}"
    echo -e "  ${DIM}Only this number will be allowed to interact with the bot.${NC}"
    echo -ne "  ${BOLD}Phone:${NC} "
    read -r WA_PHONE

    if [ -n "$WA_PHONE" ]; then
        # Normalize: ensure + prefix
        if [[ ! "$WA_PHONE" == +* ]]; then
            WA_PHONE="+$WA_PHONE"
        fi
        WHATSAPP_JSON='"whatsapp": {"enabled": true, "bridgeUrl": "ws://localhost:3001", "allowFrom": ["'"$WA_PHONE"'"]}'
        ok "WhatsApp configured for $WA_PHONE"
    else
        WHATSAPP_JSON='"whatsapp": {"enabled": true, "bridgeUrl": "ws://localhost:3001", "allowFrom": []}'
        warn "WhatsApp enabled without phone filter (all numbers allowed)"
    fi
else
    WHATSAPP_JSON='"whatsapp": {"enabled": false}'
    info "WhatsApp skipped (can enable later in config.json)"
fi

# --- Generate config.json with all settings ---
cat > "$NANOBOT_DIR/config.json" <<JSONEOF
{
  "agents": {
    "defaults": {
      "model": "$DEFAULT_MODEL",
      "maxTokens": 2048,
      "temperature": 0.3,
      "maxToolIterations": 10,
      "memoryWindow": 30
    }
  },
  "providers": {
    $PROVIDER_JSON
  },
  "channels": {
    $WHATSAPP_JSON
  },
  "tools": {
    "restrictToWorkspace": true,
    "exec": {
      "timeout": 30
    },
    "web": {
      "search": {
        "maxResults": 3
      }
    }
  }
}
JSONEOF

ok "Generated: $NANOBOT_DIR/config.json"

# --- Generate configs/kadiya-sl.yaml ------------------------------------------
# Token-optimized configuration with cost-first routing
mkdir -p "$REPO_DIR/configs"

# Build routing models block based on provider
ROUTE_DEFAULT="$DEFAULT_MODEL"
ROUTE_TRANSLATE="$DEFAULT_MODEL"
ROUTE_SUMMARIZE="$DEFAULT_MODEL"
ROUTE_EXTRACT="$STRUCTURED_MODEL"

cat > "$REPO_DIR/configs/kadiya-sl.yaml" <<YAMLEOF
# kadiya Sri Lanka Configuration
# Auto-generated by install.sh
# Provider: $PROVIDER_NAME
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

profile:
  name: sl
  description: Sri Lanka profile - $PROVIDER_NAME
  version: "1.0.0"

# Locale
locale:
  timezone: Asia/Colombo
  currency: LKR
  units: metric
  languages: [si, en]
  allow_singlish: true
  bilingual_output: false

# Tone - optimized for low token usage
tone:
  verbosity: low
  style: concise
  format: plain

# Agent defaults - cost-optimized
agents:
  defaults:
    model: "$DEFAULT_MODEL"
    max_tokens: 2048         # Hard cap (upstream default: 8192)
    temperature: 0.3         # More deterministic than default 0.7
    max_tool_iterations: 10  # Half of upstream default 20
    memory_window: 30        # Lower than upstream 50

# Model configuration - per-provider defaults
models:
  default: "$DEFAULT_MODEL"
  structured: "$STRUCTURED_MODEL"
  high_context: "$HIGH_CONTEXT_MODEL"

# Routing - deterministic, no LLM calls for routing decisions
routing:
  default_tier: cheap_general
  tiers:
    cheap_general:
      models: ["$ROUTE_DEFAULT"]
      max_input_tokens: 4000
      max_output_tokens: 1024    # Token optimization: hard cap per request
    structured:
      models: ["$STRUCTURED_MODEL"]
      max_input_tokens: 8000
      max_output_tokens: 2048
    fallback:
      models: ["$DEFAULT_MODEL"]
      max_input_tokens: 16000
      max_output_tokens: 4096
    sensitive:
      models: ["$DEFAULT_MODEL"]
      max_input_tokens: 8000
      max_output_tokens: 2048

  # Per-intent routing
  intent_routing:
    default: "$ROUTE_DEFAULT"
    translation: "$ROUTE_TRANSLATE"
    summaries: "$ROUTE_SUMMARIZE"
    extraction: "$ROUTE_EXTRACT"

  rules:
    - name: json_required
      condition: {needs_json: true}
      tier: structured
    - name: large_input
      condition: {input_tokens_gt: 4000}
      tier: structured
    - name: retry_escalation
      condition: {retry_count_gt: 1}
      tier: fallback
    - name: sensitive_content
      condition: {sensitivity: true}
      tier: sensitive

# Token limits - aggressive optimization
# These limits are critical for cost control
token_limits:
  max_input_tokens: 8000
  max_output_tokens: 2048
  intent_limits:
    translate: 512     # Translations don't need long output
    summarize: 256     # Summaries must be brief
    format: 256        # Formatting is short by nature
    format_whatsapp: 256
    format_telegram: 512
    search: 512        # Search results: facts only
    general: 1024

# Conversation management - rolling summaries to control context size
conversation:
  summarize_after_turns: 5          # Summarize history after 5 turns
  summarize_model: "$DEFAULT_MODEL" # Use cheapest model for summaries
  retain_last_messages: 1           # Keep only last message + summary

# Logging - token tracking enabled, PII logging disabled
logging:
  log_tokens: true    # Track token usage per request
  log_cost: true      # Track estimated cost per request
  log_latency: true   # Track response latency
  log_prompts: false  # NEVER log full prompts (privacy + storage)
  log_pii: false      # NEVER log PII

# Skills
skills:
  enabled:
    - sl-translate
    - sl-whatsapp
    - sl-telegram
    - sl-summarize
    - sl-pii-redact
    - office-excel
    - office-word
    - office-pptx
    - web-search

# Tools
tools:
  restrict_to_workspace: true
  exec:
    timeout: 30
  web:
    search:
      max_results: 3
YAMLEOF

ok "Generated: $REPO_DIR/configs/kadiya-sl.yaml"

# --- Create workspace templates ----------------------------------------------
step "Setting up workspace"

WORKSPACE="$NANOBOT_DIR/workspace"
mkdir -p "$WORKSPACE/memory" "$WORKSPACE/skills"

# Create AGENTS.md with kadiya identity (token-optimized prompt)
cat > "$WORKSPACE/AGENTS.md" <<'AGENTSEOF'
# Instructions

You are kadiya, a helpful assistant optimized for Sri Lanka.
Be concise. Be practical. Save tokens.

## Rules
- Answer directly. No preamble.
- Use tools when needed, explain briefly.
- Remember facts in memory/MEMORY.md
- Keep responses under 500 words unless asked for more.
AGENTSEOF

# Create IDENTITY.md
cat > "$WORKSPACE/IDENTITY.md" <<'IDEOF'
# Identity

name: kadiya
locale: Sri Lanka (Asia/Colombo)
languages: Sinhala, English, Singlish
tone: concise, practical, mobile-friendly
IDEOF

# Create MEMORY.md if missing
if [ ! -f "$WORKSPACE/memory/MEMORY.md" ]; then
    cat > "$WORKSPACE/memory/MEMORY.md" <<'MEMEOF'
# Long-term Memory

## User Information

(Important facts about the user)

## Preferences

(Learned over time)
MEMEOF
fi

# Create HISTORY.md if missing
[ -f "$WORKSPACE/memory/HISTORY.md" ] || touch "$WORKSPACE/memory/HISTORY.md"

ok "Workspace ready: $WORKSPACE"

# ============================================================================
# 5. SET KADIYA_PROFILE ENVIRONMENT VARIABLE
# ============================================================================

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "^export KADIYA_PROFILE=" "$SHELL_RC" 2>/dev/null; then
        echo "export KADIYA_PROFILE='sl'" >> "$SHELL_RC"
    fi
fi
export KADIYA_PROFILE=sl

# ============================================================================
# 6. VALIDATION (kadiya doctor)
# ============================================================================
step "Running validation"

ERRORS=0

# Check 1: Config file exists
if [ -f "$NANOBOT_DIR/config.json" ]; then
    ok "Config file exists"
else
    warn "Config file missing"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: kadiya config exists
if [ -f "$REPO_DIR/configs/kadiya-sl.yaml" ]; then
    ok "kadiya config exists"
else
    warn "kadiya config missing"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: API key is set
if [ -n "${!ENV_VAR_NAME:-}" ]; then
    ok "API key set (\$$ENV_VAR_NAME)"
else
    warn "API key not set in environment"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: Python can import nanobot
if "$VENV_DIR/bin/python" -c "import nanobot" 2>/dev/null; then
    ok "nanobot importable"
else
    warn "Cannot import nanobot"
    ERRORS=$((ERRORS + 1))
fi

# Check 5: Config is valid JSON
if "$VENV_DIR/bin/python" -c "import json; json.load(open('$NANOBOT_DIR/config.json'))" 2>/dev/null; then
    ok "Config JSON valid"
else
    warn "Config JSON invalid"
    ERRORS=$((ERRORS + 1))
fi

# Check 6: YAML config is valid
if "$VENV_DIR/bin/python" -c "import yaml; yaml.safe_load(open('$REPO_DIR/configs/kadiya-sl.yaml'))" 2>/dev/null; then
    ok "kadiya YAML config valid"
else
    warn "kadiya YAML config invalid"
    ERRORS=$((ERRORS + 1))
fi

# Check 7: Provider connectivity (lightweight check)
echo -ne "  ${BLUE}[....]${NC}  Testing provider connectivity..."
CONNECTIVITY_OK=false
case "$PROVIDER" in
    openai)
        if curl -sf -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $API_KEY" \
            "https://api.openai.com/v1/models" 2>/dev/null | grep -qE "^(200|401)"; then
            CONNECTIVITY_OK=true
        fi
        ;;
    deepseek)
        if curl -sf -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $API_KEY" \
            "https://api.deepseek.com/models" 2>/dev/null | grep -qE "^(200|401|403)"; then
            CONNECTIVITY_OK=true
        fi
        ;;
    openrouter)
        if curl -sf -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $API_KEY" \
            "https://openrouter.ai/api/v1/models" 2>/dev/null | grep -qE "^(200|401)"; then
            CONNECTIVITY_OK=true
        fi
        ;;
esac
echo -ne "\r"

if [ "$CONNECTIVITY_OK" = true ]; then
    ok "Provider reachable ($PROVIDER_NAME)"
else
    warn "Could not reach provider (may work anyway if key is correct)"
fi

# Check 8: Workspace structure
if [ -d "$WORKSPACE" ] && [ -f "$WORKSPACE/AGENTS.md" ]; then
    ok "Workspace structure valid"
else
    warn "Workspace incomplete"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================================
# 7. COMPLETION
# ============================================================================

divider
echo ""

if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}  Installation complete!${NC}"
else
    echo -e "${YELLOW}${BOLD}  Installation complete with $ERRORS warning(s).${NC}"
fi

echo ""
echo -e "  ${BOLD}Config:${NC}     $NANOBOT_DIR/config.json"
echo -e "  ${BOLD}kadiya:${NC}     $REPO_DIR/configs/kadiya-sl.yaml"
echo -e "  ${BOLD}Workspace:${NC}  $WORKSPACE"
echo -e "  ${BOLD}Provider:${NC}   $PROVIDER_NAME"
echo -e "  ${BOLD}Model:${NC}      $DEFAULT_MODEL"
echo -e "  ${BOLD}Venv:${NC}       $VENV_DIR"
echo ""

divider
echo ""
echo -e "  ${BOLD}Quick start:${NC}"
echo ""
echo -e "  ${CYAN}# Activate the environment${NC}"
echo -e "  source $VENV_DIR/bin/activate"
echo ""
echo -e "  ${CYAN}# Send a message${NC}"
echo -e "  nanobot agent -m \"Hello, translate 'good morning' to Sinhala\""
echo ""
echo -e "  ${CYAN}# Interactive mode${NC}"
echo -e "  nanobot agent"
echo ""
echo -e "  ${CYAN}# Check status${NC}"
echo -e "  nanobot status"
echo ""
echo -e "  ${CYAN}# Run diagnostics${NC}"
echo -e "  nanobot doctor"
echo ""

if [[ "$ENABLE_WA" =~ ^[Yy] ]]; then
    divider
    echo ""
    echo -e "  ${BOLD}WhatsApp bot setup:${NC}"
    echo ""
    echo -e "  ${CYAN}# 1. Install Node.js bridge dependencies${NC}"
    echo -e "  cd bridge && npm install && npm run build && cd .."
    echo ""
    echo -e "  ${CYAN}# 2. Start the WhatsApp bridge${NC}"
    echo -e "  node bridge/dist/index.js"
    echo ""
    echo -e "  ${CYAN}# 3. Scan the QR code with your phone${NC}"
    echo -e "  ${DIM}(WhatsApp > Linked Devices > Link a Device)${NC}"
    echo ""
    echo -e "  ${CYAN}# 4. Start kadiya in another terminal${NC}"
    echo -e "  source .venv/bin/activate && nanobot agent"
    echo ""
    echo -e "  ${DIM}Messages from your WhatsApp will be processed by kadiya.${NC}"
    echo ""
fi

if [ -n "$SHELL_RC" ]; then
    echo -e "  ${DIM}Note: Run 'source $SHELL_RC' or open a new terminal"
    echo -e "  to load the API key into your environment.${NC}"
    echo ""
fi

echo -e "  ${DIM}Docs: $REPO_DIR/KADIYA.md${NC}"
echo ""
