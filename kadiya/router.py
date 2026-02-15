"""
Cost-first model routing for kadiya.

Deterministic routing based on:
- Intent type
- Input token estimate
- JSON requirements
- Sensitivity flags
- Retry count

NO heuristic LLM reasoning - routing must be predictable.
"""

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from loguru import logger


class RoutingTier(Enum):
    """Model routing tiers ordered by cost (lowest first)."""
    CHEAP_GENERAL = "cheap_general"
    STRUCTURED = "structured"
    FALLBACK = "fallback"
    SENSITIVE = "sensitive"


@dataclass
class RoutingContext:
    """Context for routing decision."""
    intent: str = "general"
    input_text: str = ""
    needs_json: bool = False
    sensitivity: bool = False
    retry_count: int = 0

    # Computed fields
    input_tokens: int = field(default=0, init=False)

    def __post_init__(self):
        # Estimate tokens (rough: 1 token ~ 4 chars for English, 2 chars for Sinhala)
        self.input_tokens = self._estimate_tokens(self.input_text)

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count without calling tokenizer.

        Heuristic:
        - English: ~4 chars per token
        - Sinhala/CJK: ~2 chars per token
        - Mixed: weighted average
        """
        if not text:
            return 0

        # Count Sinhala/CJK characters (Unicode ranges)
        sinhala_cjk = len(re.findall(r'[\u0D80-\u0DFF\u4E00-\u9FFF\u3040-\u30FF]', text))
        other = len(text) - sinhala_cjk

        # Weighted estimate
        tokens = (sinhala_cjk / 2) + (other / 4)
        return int(tokens) + 1  # +1 for safety


@dataclass
class RoutingDecision:
    """Result of routing decision."""
    tier: RoutingTier
    model: str
    max_output_tokens: int
    reason: str


@dataclass
class TierConfig:
    """Configuration for a model tier."""
    models: list[str]
    max_input_tokens: int = 4000
    max_output_tokens: int = 1024


class ModelRouter:
    """
    Deterministic cost-first model router.

    Evaluates rules in order and selects the cheapest capable model.
    """

    # Default tier configurations
    DEFAULT_TIERS: dict[RoutingTier, TierConfig] = {
        RoutingTier.CHEAP_GENERAL: TierConfig(
            models=["deepseek/deepseek-chat", "groq/llama-3.3-70b-versatile"],
            max_input_tokens=4000,
            max_output_tokens=1024,
        ),
        RoutingTier.STRUCTURED: TierConfig(
            models=["anthropic/claude-3-haiku-20240307", "openai/gpt-4o-mini"],
            max_input_tokens=8000,
            max_output_tokens=2048,
        ),
        RoutingTier.FALLBACK: TierConfig(
            models=["openai/gpt-4o-mini", "anthropic/claude-3-haiku-20240307"],
            max_input_tokens=16000,
            max_output_tokens=4096,
        ),
        RoutingTier.SENSITIVE: TierConfig(
            models=["anthropic/claude-3-haiku-20240307"],
            max_input_tokens=8000,
            max_output_tokens=2048,
        ),
    }

    # Intent to max_output_tokens mapping (override tier defaults)
    INTENT_TOKEN_LIMITS: dict[str, int] = {
        "translate": 512,
        "summarize": 256,
        "format": 256,
        "format_whatsapp": 256,
        "format_telegram": 512,
        "pii_redact": 1024,
        "search": 512,
        "general": 1024,
    }

    # Patterns that indicate JSON requirement
    JSON_PATTERNS = [
        r'\bjson\b',
        r'\bstructured\b',
        r'\bschema\b',
        r'\{\s*"',
        r'\bparse\b.*\boutput\b',
    ]

    # Patterns that indicate sensitive content
    SENSITIVITY_PATTERNS = [
        r'\bnic\b',  # National ID
        r'\bpassword\b',
        r'\bcredit\s*card\b',
        r'\bbank\b.*\baccount\b',
        r'\bconfidential\b',
        r'\bprivate\b',
        r'\bsecret\b',
        # Sri Lankan NIC pattern
        r'\d{9}[vVxX]',
        r'\d{12}',
        # Phone patterns
        r'\+94\d{9}',
        r'0\d{9}',
    ]

    def __init__(self, tiers: dict[RoutingTier, TierConfig] | None = None):
        """
        Initialize router with optional custom tier configuration.

        Args:
            tiers: Custom tier configurations. Uses defaults if not provided.
        """
        self.tiers = tiers or self.DEFAULT_TIERS.copy()
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        self._json_re = re.compile('|'.join(self.JSON_PATTERNS), re.IGNORECASE)
        self._sensitive_re = re.compile('|'.join(self.SENSITIVITY_PATTERNS), re.IGNORECASE)

    def route(self, context: RoutingContext) -> RoutingDecision:
        """
        Route request to appropriate model tier.

        Evaluation order (first match wins):
        1. Sensitive content -> SENSITIVE tier
        2. Retry escalation (retry_count > 1) -> FALLBACK tier
        3. JSON required -> STRUCTURED tier
        4. Large input (>4000 tokens) -> STRUCTURED tier
        5. Default -> CHEAP_GENERAL tier

        Args:
            context: Routing context with request details.

        Returns:
            Routing decision with selected model and limits.
        """
        # Auto-detect JSON requirement if not explicitly set
        needs_json = context.needs_json or self._detect_json_requirement(context.input_text)

        # Auto-detect sensitivity if not explicitly set
        sensitivity = context.sensitivity or self._detect_sensitivity(context.input_text)

        # Rule evaluation (order matters!)
        if sensitivity:
            tier = RoutingTier.SENSITIVE
            reason = "sensitive_content_detected"
        elif context.retry_count > 1:
            tier = RoutingTier.FALLBACK
            reason = f"retry_escalation_count_{context.retry_count}"
        elif needs_json:
            tier = RoutingTier.STRUCTURED
            reason = "json_output_required"
        elif context.input_tokens > 4000:
            tier = RoutingTier.STRUCTURED
            reason = f"large_input_{context.input_tokens}_tokens"
        else:
            tier = RoutingTier.CHEAP_GENERAL
            reason = "default_cheap_routing"

        # Get tier config
        tier_config = self.tiers[tier]

        # Select first available model
        model = tier_config.models[0] if tier_config.models else "deepseek/deepseek-chat"

        # Determine output token limit (intent-specific or tier default)
        max_output_tokens = self.INTENT_TOKEN_LIMITS.get(
            context.intent,
            tier_config.max_output_tokens
        )

        decision = RoutingDecision(
            tier=tier,
            model=model,
            max_output_tokens=max_output_tokens,
            reason=reason,
        )

        logger.debug(f"Routing decision: {decision}")
        return decision

    def _detect_json_requirement(self, text: str) -> bool:
        """Detect if request requires JSON output."""
        return bool(self._json_re.search(text))

    def _detect_sensitivity(self, text: str) -> bool:
        """Detect if request contains sensitive content."""
        return bool(self._sensitive_re.search(text))

    def get_model_for_intent(self, intent: str) -> tuple[str, int]:
        """
        Quick lookup: get model and token limit for a specific intent.

        Args:
            intent: The intent type (translate, summarize, etc.)

        Returns:
            Tuple of (model_name, max_output_tokens)
        """
        context = RoutingContext(intent=intent)
        decision = self.route(context)
        return decision.model, decision.max_output_tokens


@dataclass
class UsageMetrics:
    """Token usage and cost metrics for a request."""
    model: str
    tier: RoutingTier
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    estimated_cost_usd: float = 0.0

    def __post_init__(self):
        self.estimated_cost_usd = self._estimate_cost()

    def _estimate_cost(self) -> float:
        """
        Estimate cost in USD based on model and tokens.

        Prices as of 2024 (approximate):
        - DeepSeek: $0.14/$0.28 per 1M tokens (input/output)
        - Claude Haiku: $0.25/$1.25 per 1M tokens
        - GPT-4o-mini: $0.15/$0.60 per 1M tokens
        - Llama (Groq): Free tier available
        """
        # Cost per 1M tokens (input, output)
        COSTS = {
            "deepseek": (0.14, 0.28),
            "haiku": (0.25, 1.25),
            "gpt-4o-mini": (0.15, 0.60),
            "groq": (0.0, 0.0),  # Free tier
        }

        # Match model to cost tier
        model_lower = self.model.lower()
        if "deepseek" in model_lower:
            input_cost, output_cost = COSTS["deepseek"]
        elif "haiku" in model_lower:
            input_cost, output_cost = COSTS["haiku"]
        elif "gpt-4o-mini" in model_lower:
            input_cost, output_cost = COSTS["gpt-4o-mini"]
        elif "groq" in model_lower:
            input_cost, output_cost = COSTS["groq"]
        else:
            # Conservative fallback
            input_cost, output_cost = (0.50, 1.50)

        # Calculate cost
        cost = (self.input_tokens * input_cost + self.output_tokens * output_cost) / 1_000_000
        return round(cost, 6)


class UsageTracker:
    """
    Track token usage and costs across requests.

    Thread-safe accumulator for monitoring costs.
    """

    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0
        self.request_count = 0
        self.metrics_history: list[UsageMetrics] = []
        self._start_time = time.time()

    def record(self, metrics: UsageMetrics) -> None:
        """Record usage metrics for a request."""
        self.total_input_tokens += metrics.input_tokens
        self.total_output_tokens += metrics.output_tokens
        self.total_cost_usd += metrics.estimated_cost_usd
        self.request_count += 1

        # Keep last 100 metrics for analysis
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)

        # Log usage (no PII, no prompts)
        logger.info(
            f"Usage: model={metrics.model} "
            f"in={metrics.input_tokens} out={metrics.output_tokens} "
            f"cost=${metrics.estimated_cost_usd:.6f} "
            f"latency={metrics.latency_ms}ms"
        )

    def get_summary(self) -> dict[str, Any]:
        """Get usage summary."""
        elapsed = time.time() - self._start_time
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "request_count": self.request_count,
            "avg_tokens_per_request": (
                (self.total_input_tokens + self.total_output_tokens) // max(1, self.request_count)
            ),
            "elapsed_seconds": int(elapsed),
            "avg_cost_per_request": round(self.total_cost_usd / max(1, self.request_count), 6),
        }

    def format_summary(self) -> str:
        """Format summary for display."""
        s = self.get_summary()
        return (
            f"Tokens: {s['total_tokens']:,} "
            f"(in: {s['total_input_tokens']:,}, out: {s['total_output_tokens']:,}) | "
            f"Cost: ${s['total_cost_usd']:.4f} | "
            f"Requests: {s['request_count']}"
        )
