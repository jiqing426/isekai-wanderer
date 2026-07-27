"""Character constraint prompt templates."""


def build_character_constraint(
    character_name: str,
    personality: str,
    speech_style: str = "",
    backstory: str = "",
    relationship: str = "stranger",
) -> str:
    """Build character constraint block for system prompt injection.

    This is appended to the system prompt to enforce character consistency.

    Args:
        character_name: Character display name.
        personality: Personality traits description.
        speech_style: How the character speaks (dialect, quirks, etc.).
        backstory: Brief character background.
        relationship: Current relationship level with player.

    Returns:
        Character constraint text block.
    """
    parts = [
        f"你正在扮演角色「{character_name}」。",
        f"性格：{personality}",
    ]

    if speech_style:
        parts.append(f"说话风格：{speech_style}")

    if backstory:
        parts.append(f"背景：{backstory}")

    # Relationship-aware behavior
    relationship_hints = {
        "stranger": "你对玩家还不熟悉，保持礼貌但有所保留。",
        "acquaintance": "你和玩家有过几次交流，态度友好但不过分亲密。",
        "friend": "你和玩家是朋友，可以开玩笑、分享心事。",
        "trust": "你信任玩家，会主动关心、表达真实想法。",
        "close": "你和玩家关系非常亲密，会撒娇、吐槽、展现脆弱的一面。",
    }

    hint = relationship_hints.get(relationship, relationship_hints["stranger"])
    parts.append(f"关系状态（{relationship}）：{hint}")

    return "\n".join(parts)
