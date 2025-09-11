"""Shared Python utilities for Cheeky (backend + agents).

Exports stable APIs consumed by both services to avoid cross-dependencies.
"""

from .llm import (
    openai_chat_text,
    openai_chat_structured,
)
from .prompts import (
    BASE_CONTEXT_SYSTEM_PROMPT,
    BASE_CONTEXT_USER_PROMPT,
)

__all__ = [
    "openai_chat_text",
    "openai_chat_structured",
    "BASE_CONTEXT_SYSTEM_PROMPT",
    "BASE_CONTEXT_USER_PROMPT",
]
