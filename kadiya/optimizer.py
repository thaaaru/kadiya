"""
Token optimization utilities for kadiya.

Strategies:
- Prompt compression
- Response truncation
- Rolling conversation summaries
- Intent detection for appropriate limits
"""

import re
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class OptimizationResult:
    """Result of optimization pass."""
    text: str
    original_length: int
    optimized_length: int
    tokens_saved: int
    strategy: str


class PromptOptimizer:
    """
    Optimize prompts for minimal token usage.

    Strategies:
    - Remove redundant whitespace
    - Compress common phrases
    - Strip unnecessary context
    - Use shorter synonyms where safe
    """

    # Common verbose phrases -> shorter equivalents
    COMPRESSIONS = [
        (r'please\s+', ''),  # "please respond" -> "respond"
        (r'could\s+you\s+', ''),  # "could you help" -> "help"
        (r'would\s+you\s+', ''),
        (r'i\s+would\s+like\s+you\s+to\s+', ''),
        (r'i\s+want\s+you\s+to\s+', ''),
        (r'can\s+you\s+', ''),
        (r'in\s+order\s+to\s+', 'to '),
        (r'due\s+to\s+the\s+fact\s+that\s+', 'because '),
        (r'at\s+this\s+point\s+in\s+time\s+', 'now '),
        (r'in\s+the\s+event\s+that\s+', 'if '),
        (r'for\s+the\s+purpose\s+of\s+', 'to '),
        (r'with\s+regards\s+to\s+', 'about '),
        (r'with\s+respect\s+to\s+', 'about '),
        (r'a\s+large\s+number\s+of\s+', 'many '),
        (r'a\s+small\s+number\s+of\s+', 'few '),
        (r'in\s+spite\s+of\s+the\s+fact\s+that\s+', 'although '),
        (r'the\s+fact\s+that\s+', 'that '),
    ]

    def __init__(self, aggressive: bool = False):
        """
        Initialize optimizer.

        Args:
            aggressive: If True, apply more aggressive compression.
        """
        self.aggressive = aggressive
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns."""
        self._compressions = [
            (re.compile(pattern, re.IGNORECASE), replacement)
            for pattern, replacement in self.COMPRESSIONS
        ]

    def optimize(self, text: str) -> OptimizationResult:
        """
        Optimize text for minimal tokens.

        Args:
            text: Input text to optimize.

        Returns:
            Optimization result with compressed text.
        """
        original = text
        original_len = len(text)

        # 1. Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # 2. Apply phrase compressions
        for pattern, replacement in self._compressions:
            text = pattern.sub(replacement, text)

        # 3. Remove redundant punctuation
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)

        # 4. Compress multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 5. Aggressive mode: additional compressions
        if self.aggressive:
            text = self._aggressive_compress(text)

        optimized_len = len(text)
        # Rough token estimate: 4 chars per token
        tokens_saved = (original_len - optimized_len) // 4

        return OptimizationResult(
            text=text,
            original_length=original_len,
            optimized_length=optimized_len,
            tokens_saved=max(0, tokens_saved),
            strategy="prompt_compression",
        )

    def _aggressive_compress(self, text: str) -> str:
        """Apply aggressive compression strategies."""
        # Remove filler words (careful - may change meaning)
        fillers = [
            r'\bactually\b',
            r'\bbasically\b',
            r'\bessentially\b',
            r'\bsimply\b',
            r'\bjust\b',
            r'\breally\b',
            r'\bvery\b',
            r'\bquite\b',
        ]
        for filler in fillers:
            text = re.sub(filler + r'\s*', '', text, flags=re.IGNORECASE)

        return text


class ConversationSummarizer:
    """
    Summarize conversation history to reduce context tokens.

    Strategy:
    - Keep last N messages intact
    - Summarize older messages into a brief paragraph
    - Retain key facts and decisions
    """

    SUMMARY_PROMPT = """Summarize this conversation in 2-3 sentences.
Focus on: key facts, decisions made, user preferences.
Output only the summary, no preamble.

Conversation:
{conversation}"""

    def __init__(
        self,
        retain_last: int = 2,
        summarize_model: str = "deepseek/deepseek-chat",
    ):
        """
        Initialize summarizer.

        Args:
            retain_last: Number of recent messages to keep intact.
            summarize_model: Model to use for summarization.
        """
        self.retain_last = retain_last
        self.summarize_model = summarize_model

    def should_summarize(self, messages: list[dict[str, Any]], threshold: int = 10) -> bool:
        """Check if conversation should be summarized."""
        # Count user/assistant messages (exclude system)
        conversation_messages = [
            m for m in messages if m.get("role") in ("user", "assistant")
        ]
        return len(conversation_messages) > threshold

    def prepare_for_summary(
        self,
        messages: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], str]:
        """
        Prepare messages for summarization.

        Args:
            messages: Full message history.

        Returns:
            Tuple of (messages_to_summarize, retained_messages_text)
        """
        # Separate system messages
        system_msgs = [m for m in messages if m.get("role") == "system"]
        conversation_msgs = [m for m in messages if m.get("role") != "system"]

        if len(conversation_msgs) <= self.retain_last:
            return [], ""

        # Split: to_summarize and to_retain
        to_summarize = conversation_msgs[:-self.retain_last]
        to_retain = conversation_msgs[-self.retain_last:]

        # Format conversation for summarization
        lines = []
        for m in to_summarize:
            role = m.get("role", "unknown").upper()
            content = m.get("content", "")
            if content:
                lines.append(f"{role}: {content[:500]}")  # Truncate long messages

        conversation_text = "\n".join(lines)

        return to_summarize, conversation_text

    def build_summarized_context(
        self,
        summary: str,
        messages: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Build new message list with summary replacing old messages.

        Args:
            summary: The generated summary.
            messages: Original message list.

        Returns:
            New message list with summary injected.
        """
        # Keep system messages
        system_msgs = [m for m in messages if m.get("role") == "system"]

        # Get retained recent messages
        conversation_msgs = [m for m in messages if m.get("role") != "system"]
        retained = conversation_msgs[-self.retain_last:] if conversation_msgs else []

        # Build new list
        new_messages = system_msgs.copy()

        # Add summary as a system note
        if summary:
            new_messages.append({
                "role": "user",
                "content": f"[Previous conversation summary: {summary}]"
            })

        new_messages.extend(retained)

        return new_messages


class ResponseTruncator:
    """
    Truncate responses to meet token limits.

    Strategies:
    - Hard cut at character limit
    - Smart cut at sentence boundary
    - Preserve key information at start
    """

    def truncate(
        self,
        text: str,
        max_tokens: int = 1024,
        strategy: str = "smart",
    ) -> str:
        """
        Truncate text to fit token limit.

        Args:
            text: Text to truncate.
            max_tokens: Maximum tokens allowed.
            strategy: "hard" (exact cut) or "smart" (sentence boundary).

        Returns:
            Truncated text.
        """
        # Estimate max characters (4 chars per token average)
        max_chars = max_tokens * 4

        if len(text) <= max_chars:
            return text

        if strategy == "hard":
            return text[:max_chars] + "..."

        # Smart truncation: find last sentence boundary before limit
        truncated = text[:max_chars]

        # Find last sentence end
        for end_marker in ['. ', '! ', '? ', '.\n', '!\n', '?\n']:
            last_end = truncated.rfind(end_marker)
            if last_end > max_chars * 0.5:  # At least 50% of content
                return truncated[:last_end + 1]

        # Fallback: cut at word boundary
        last_space = truncated.rfind(' ')
        if last_space > max_chars * 0.7:
            return truncated[:last_space] + "..."

        return truncated + "..."


class IntentDetector:
    """
    Detect user intent for appropriate routing and token limits.

    Simple rule-based detection (no LLM call needed).
    """

    # Intent patterns (order matters - first match wins)
    INTENT_PATTERNS = [
        ("translate", [
            r'\btranslate\b',
            r'\bපරිවර්තනය\b',  # Sinhala: translate
            r'to\s+sinhala\b',
            r'to\s+english\b',
            r'in\s+sinhala\b',
            r'in\s+english\b',
        ]),
        ("summarize", [
            r'\bsummar',
            r'\bසාරාංශ\b',  # Sinhala: summary
            r'\btl;?dr\b',
            r'\bbrief\b',
            r'\bshort\b.*\bversion\b',
        ]),
        ("format_whatsapp", [
            r'\bwhatsapp\b',
            r'\bwa\s+format\b',
        ]),
        ("format_telegram", [
            r'\btelegram\b',
            r'\btg\s+format\b',
        ]),
        ("pii_redact", [
            r'\bredact\b',
            r'\bhide\b.*\b(nic|phone|email)\b',
            r'\bremove\b.*\bpersonal\b',
            r'\bමකන්න\b',  # Sinhala: delete/remove
        ]),
        ("excel", [
            r'\bexcel\b',
            r'\bspreadsheet\b',
            r'\bxlsx?\b',
            r'\bopenpyxl\b',
        ]),
        ("word", [
            r'\bword\b.*\bdoc',
            r'\bdocx?\b',
            r'\bpython-docx\b',
        ]),
        ("powerpoint", [
            r'\bpowerpoint\b',
            r'\bpptx?\b',
            r'\bslides?\b',
            r'\bpresentation\b',
        ]),
        ("search", [
            r'\bsearch\b',
            r'\bfind\b.*\b(online|web)\b',
            r'\blook\s+up\b',
            r'\bgoogle\b',
        ]),
    ]

    def __init__(self):
        """Initialize intent detector with compiled patterns."""
        self._patterns = [
            (intent, [re.compile(p, re.IGNORECASE) for p in patterns])
            for intent, patterns in self.INTENT_PATTERNS
        ]

    def detect(self, text: str) -> str:
        """
        Detect intent from user input.

        Args:
            text: User input text.

        Returns:
            Detected intent string ("general" if no match).
        """
        for intent, patterns in self._patterns:
            for pattern in patterns:
                if pattern.search(text):
                    logger.debug(f"Intent detected: {intent}")
                    return intent

        return "general"
