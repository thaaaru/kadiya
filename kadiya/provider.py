"""
kadiya provider wrapper.

Wraps NanoBot's LiteLLM provider with:
- Cost-first model routing
- Token optimization
- Usage tracking
- Hard limits enforcement
"""

import time
from typing import Any

from loguru import logger

from nanobot.providers.base import LLMProvider, LLMResponse
from nanobot.providers.litellm_provider import LiteLLMProvider

from kadiya.config import KadiyaConfig, load_kadiya_config
from kadiya.router import (
    ModelRouter,
    RoutingContext,
    RoutingDecision,
    UsageMetrics,
    UsageTracker,
)
from kadiya.optimizer import (
    IntentDetector,
    PromptOptimizer,
    ResponseTruncator,
)


class KadiyaProvider(LLMProvider):
    """
    Cost-optimized LLM provider for kadiya.

    Wraps the upstream LiteLLM provider with:
    - Automatic model routing based on intent/complexity
    - Token optimization on prompts
    - Response truncation to meet limits
    - Usage tracking and cost estimation
    """

    def __init__(
        self,
        base_provider: LiteLLMProvider,
        config: KadiyaConfig | None = None,
    ):
        """
        Initialize kadiya provider.

        Args:
            base_provider: The underlying LiteLLM provider.
            config: kadiya configuration. Loads default if not provided.
        """
        self.base = base_provider
        self.config = config or load_kadiya_config()

        # Initialize components
        self.router = ModelRouter()
        self.intent_detector = IntentDetector()
        self.prompt_optimizer = PromptOptimizer(aggressive=False)
        self.response_truncator = ResponseTruncator()
        self.usage_tracker = UsageTracker()

        # Track retry counts per session
        self._retry_counts: dict[str, int] = {}

        super().__init__(base_provider.api_key, base_provider.api_base)

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs,
    ) -> LLMResponse:
        """
        Send chat request with cost-first routing.

        Args:
            messages: Message list.
            tools: Optional tool definitions.
            model: Model override (uses routing if not provided).
            max_tokens: Max output tokens (may be overridden by routing).
            temperature: Sampling temperature.
            **kwargs: Additional arguments passed to base provider.

        Returns:
            LLM response.
        """
        start_time = time.time()

        # Extract user message for analysis
        user_message = self._get_last_user_message(messages)

        # Detect intent
        intent = self.intent_detector.detect(user_message)

        # Build routing context
        session_key = kwargs.get("session_key", "default")
        retry_count = self._retry_counts.get(session_key, 0)

        context = RoutingContext(
            intent=intent,
            input_text=user_message,
            needs_json=self._detect_json_need(messages, tools),
            sensitivity=False,  # Router will auto-detect
            retry_count=retry_count,
        )

        # Get routing decision
        if model:
            # Model override - use provided model with intent limits
            decision = RoutingDecision(
                tier=self.router.route(context).tier,
                model=model,
                max_output_tokens=min(max_tokens, self.config.token_limits.max_output_tokens),
                reason="model_override",
            )
        else:
            decision = self.router.route(context)

        # Apply token limits
        effective_max_tokens = min(
            decision.max_output_tokens,
            max_tokens,
            self.config.token_limits.max_output_tokens,
        )

        # Optimize prompts if enabled
        optimized_messages = self._optimize_messages(messages)

        # Log routing decision (no PII)
        logger.info(
            f"Routing: intent={intent} tier={decision.tier.value} "
            f"model={decision.model} max_tokens={effective_max_tokens} "
            f"reason={decision.reason}"
        )

        # Call base provider
        try:
            response = await self.base.chat(
                messages=optimized_messages,
                tools=tools,
                model=decision.model,
                max_tokens=effective_max_tokens,
                temperature=self.config.agents.defaults.temperature,
            )

            # Reset retry count on success
            self._retry_counts[session_key] = 0

        except Exception as e:
            # Increment retry count
            self._retry_counts[session_key] = retry_count + 1
            raise

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Track usage
        usage = response.usage or {}
        metrics = UsageMetrics(
            model=decision.model,
            tier=decision.tier,
            input_tokens=usage.get("prompt_tokens", context.input_tokens),
            output_tokens=usage.get("completion_tokens", 0),
            latency_ms=latency_ms,
        )
        self.usage_tracker.record(metrics)

        # Truncate response if needed
        if response.content and len(response.content) > effective_max_tokens * 4:
            response.content = self.response_truncator.truncate(
                response.content,
                max_tokens=effective_max_tokens,
            )

        return response

    def _get_last_user_message(self, messages: list[dict[str, Any]]) -> str:
        """Extract last user message from message list."""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content
                # Handle vision content (list of parts)
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            return part.get("text", "")
        return ""

    def _detect_json_need(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
    ) -> bool:
        """Detect if request needs JSON output."""
        # Tool calls require structured output
        if tools:
            return True

        # Check system prompt for JSON instructions
        for msg in messages:
            if msg.get("role") == "system":
                content = msg.get("content", "").lower()
                if "json" in content or "structured" in content:
                    return True

        return False

    def _optimize_messages(
        self,
        messages: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Optimize messages for token efficiency.

        Only optimizes user messages, preserving system prompts.
        """
        optimized = []

        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str) and len(content) > 100:
                    result = self.prompt_optimizer.optimize(content)
                    if result.tokens_saved > 5:
                        logger.debug(f"Prompt optimized: saved ~{result.tokens_saved} tokens")
                        optimized.append({**msg, "content": result.text})
                        continue

            optimized.append(msg)

        return optimized

    def get_default_model(self) -> str:
        """Get default model from config."""
        return self.config.agents.defaults.model

    def get_usage_summary(self) -> str:
        """Get formatted usage summary."""
        return self.usage_tracker.format_summary()


def create_kadiya_provider(
    api_key: str | None = None,
    api_base: str | None = None,
    config: KadiyaConfig | None = None,
    **kwargs,
) -> KadiyaProvider:
    """
    Factory function to create a kadiya provider.

    Args:
        api_key: API key (uses env if not provided).
        api_base: API base URL.
        config: kadiya configuration.
        **kwargs: Additional args for LiteLLM provider.

    Returns:
        Configured KadiyaProvider instance.
    """
    config = config or load_kadiya_config()

    # Create base LiteLLM provider
    base_provider = LiteLLMProvider(
        api_key=api_key,
        api_base=api_base,
        default_model=config.agents.defaults.model,
        **kwargs,
    )

    return KadiyaProvider(base_provider, config)
