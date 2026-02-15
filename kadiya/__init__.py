"""
kadiya - A lightweight, Sri Lanka-optimized NanoBot distribution.

Token-optimized, cost-first execution bot with Sinhala/English support.
"""

__version__ = "0.1.0"
__upstream__ = "nanobot"

from kadiya.config import KadiyaConfig, load_kadiya_config
from kadiya.router import (
    ModelRouter,
    RoutingTier,
    RoutingContext,
    RoutingDecision,
    UsageMetrics,
    UsageTracker,
)
from kadiya.optimizer import (
    PromptOptimizer,
    ConversationSummarizer,
    ResponseTruncator,
    IntentDetector,
)
from kadiya.provider import KadiyaProvider, create_kadiya_provider

__all__ = [
    # Config
    "KadiyaConfig",
    "load_kadiya_config",
    # Routing
    "ModelRouter",
    "RoutingTier",
    "RoutingContext",
    "RoutingDecision",
    "UsageMetrics",
    "UsageTracker",
    # Optimization
    "PromptOptimizer",
    "ConversationSummarizer",
    "ResponseTruncator",
    "IntentDetector",
    # Provider
    "KadiyaProvider",
    "create_kadiya_provider",
]
