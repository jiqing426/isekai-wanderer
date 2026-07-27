"""Prompt template registry."""

from .narrative import build_narrative_prompt, SYSTEM_PROMPT as NARRATIVE_SYSTEM_PROMPT
from .character import build_character_constraint
from .memory_extract import (
    build_memory_extract_prompt,
    build_memory_summary_prompt,
    MEMORY_EXTRACTION_SYSTEM,
    MEMORY_SUMMARY_SYSTEM,
)
from .style import build_style_prompt, get_available_styles

__all__ = [
    "build_narrative_prompt",
    "NARRATIVE_SYSTEM_PROMPT",
    "build_character_constraint",
    "build_memory_extract_prompt",
    "build_memory_summary_prompt",
    "MEMORY_EXTRACTION_SYSTEM",
    "MEMORY_SUMMARY_SYSTEM",
    "build_style_prompt",
    "get_available_styles",
]
