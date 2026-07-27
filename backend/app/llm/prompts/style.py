"""AI style / tone prompt templates (P1 feature)."""


def build_style_prompt(
    base_style: str = "light_novel",
    custom_instruction: str = "",
) -> str:
    """Build style instruction for system prompt injection.

    Args:
        base_style: Preset style name.
        custom_instruction: User/character custom style override.

    Returns:
        Style instruction block.
    """
    presets = {
        "light_novel": (
            "文风：轻小说风格，对话活泼，可以用语气词（呐、嘛、哈哈），"
            "偶尔加入内心独白（用括号表示），保持节奏感。"
        ),
        "serious_fantasy": (
            "文风：严肃奇幻风格，对话正式、有分量，"
            "用词考究，适合中世纪或史诗背景。"
        ),
        "modern_casual": (
            "文风：现代日常风格，对话口语化、自然随意，"
            "可以用网络用语但不过度。"
        ),
        "romantic": (
            "文风：恋爱风格，对话温柔细腻，"
            "注意情感层次变化，适当害羞和犹豫。"
        ),
    }

    style_text = presets.get(base_style, presets["light_novel"])

    if custom_instruction:
        style_text += f"\n额外要求：{custom_instruction}"

    return style_text


def get_available_styles() -> list[str]:
    """Return list of available style presets."""
    return ["light_novel", "serious_fantasy", "modern_casual", "romantic"]
