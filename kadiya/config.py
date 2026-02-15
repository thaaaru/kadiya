"""
kadiya configuration loader.

Extends NanoBot config with profile-based settings and token optimization.
"""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class LocaleConfig(BaseModel):
    """Locale settings for regional customization."""
    timezone: str = "Asia/Colombo"
    currency: str = "LKR"
    units: str = "metric"
    languages: list[str] = Field(default_factory=lambda: ["si", "en"])
    allow_singlish: bool = True
    bilingual_output: bool = False


class ToneConfig(BaseModel):
    """Output tone configuration."""
    verbosity: str = "low"  # low | medium | high
    style: str = "concise"
    format: str = "plain"  # plain | markdown | whatsapp | telegram


class TierConfig(BaseModel):
    """Model tier configuration."""
    models: list[str] = Field(default_factory=list)
    max_input_tokens: int = 4000
    max_output_tokens: int = 1024


class RoutingRule(BaseModel):
    """Single routing rule."""
    name: str
    condition: dict[str, Any]
    tier: str


class RoutingConfig(BaseModel):
    """Model routing configuration."""
    default_tier: str = "cheap_general"
    tiers: dict[str, TierConfig] = Field(default_factory=dict)
    rules: list[RoutingRule] = Field(default_factory=list)


class TokenLimitsConfig(BaseModel):
    """Token limit configuration."""
    max_input_tokens: int = 8000
    max_output_tokens: int = 2048
    intent_limits: dict[str, int] = Field(default_factory=dict)


class ConversationConfig(BaseModel):
    """Conversation management configuration."""
    summarize_after_turns: int = 5
    summarize_model: str = "deepseek/deepseek-chat"
    retain_last_messages: int = 1


class LoggingConfig(BaseModel):
    """Logging configuration."""
    log_tokens: bool = True
    log_cost: bool = True
    log_latency: bool = True
    log_prompts: bool = False  # NEVER log full prompts
    log_pii: bool = False  # NEVER log PII


class SkillsConfig(BaseModel):
    """Skills configuration."""
    enabled: list[str] = Field(default_factory=list)
    config: dict[str, dict[str, Any]] = Field(default_factory=dict)


class ProfileConfig(BaseModel):
    """Profile metadata."""
    name: str = "default"
    description: str = ""
    version: str = "1.0.0"


class KadiyaAgentDefaults(BaseModel):
    """Override agent defaults for cost optimization."""
    model: str = "deepseek/deepseek-chat"
    max_tokens: int = 2048
    temperature: float = 0.3
    max_tool_iterations: int = 10
    memory_window: int = 30


class KadiyaAgentsConfig(BaseModel):
    """Agent configuration with kadiya defaults."""
    defaults: KadiyaAgentDefaults = Field(default_factory=KadiyaAgentDefaults)


class KadiyaConfig(BaseModel):
    """
    kadiya configuration schema.

    Extends NanoBot configuration with:
    - Profile-based settings
    - Cost-first model routing
    - Token optimization
    - Sri Lanka locale support
    """
    profile: ProfileConfig = Field(default_factory=ProfileConfig)
    locale: LocaleConfig = Field(default_factory=LocaleConfig)
    tone: ToneConfig = Field(default_factory=ToneConfig)
    agents: KadiyaAgentsConfig = Field(default_factory=KadiyaAgentsConfig)
    routing: RoutingConfig = Field(default_factory=RoutingConfig)
    token_limits: TokenLimitsConfig = Field(default_factory=TokenLimitsConfig)
    conversation: ConversationConfig = Field(default_factory=ConversationConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    skills: SkillsConfig = Field(default_factory=SkillsConfig)


def get_kadiya_config_path() -> Path:
    """Get kadiya config path based on KADIYA_PROFILE env var."""
    profile = os.environ.get("KADIYA_PROFILE", "sl")

    # Check for config in multiple locations
    paths = [
        Path(f"configs/kadiya-{profile}.yaml"),
        Path.home() / ".nanobot" / f"kadiya-{profile}.yaml",
        Path(__file__).parent.parent / "configs" / f"kadiya-{profile}.yaml",
    ]

    for path in paths:
        if path.exists():
            return path

    # Return default path (may not exist)
    return paths[0]


def load_kadiya_config(config_path: Path | None = None) -> KadiyaConfig:
    """
    Load kadiya configuration from YAML file.

    Args:
        config_path: Optional path to config file. Auto-detects if not provided.

    Returns:
        Loaded kadiya configuration.
    """
    path = config_path or get_kadiya_config_path()

    if path.exists():
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return KadiyaConfig.model_validate(data)

    # Return defaults if no config found
    return KadiyaConfig()


def merge_with_nanobot_config(kadiya_config: KadiyaConfig, nanobot_config: Any) -> Any:
    """
    Merge kadiya config into NanoBot config.

    This allows kadiya to override specific NanoBot settings while
    maintaining upstream compatibility.

    Args:
        kadiya_config: The kadiya configuration.
        nanobot_config: The base NanoBot configuration.

    Returns:
        Merged configuration (NanoBot config with kadiya overrides).
    """
    # Override agent defaults
    nanobot_config.agents.defaults.model = kadiya_config.agents.defaults.model
    nanobot_config.agents.defaults.max_tokens = kadiya_config.agents.defaults.max_tokens
    nanobot_config.agents.defaults.temperature = kadiya_config.agents.defaults.temperature
    nanobot_config.agents.defaults.max_tool_iterations = kadiya_config.agents.defaults.max_tool_iterations
    nanobot_config.agents.defaults.memory_window = kadiya_config.agents.defaults.memory_window

    # Apply tool restrictions
    nanobot_config.tools.restrict_to_workspace = True

    return nanobot_config
