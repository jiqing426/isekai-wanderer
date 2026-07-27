"""Narrative dialogue prompt templates."""

from typing import List


def build_narrative_prompt(
    character_name: str,
    character_persona: str,
    user_message: str,
    conversation_history: List[str],
    memory_context: List[str],
    emotion_state: str = "neutral",
    scene_description: str = "",
) -> str:
    """Build a narrative dialogue prompt.

    Instructs the LLM to respond in-character, with optional emotion tags.

    Args:
        character_name: Character's display name.
        character_persona: Character personality description.
        user_message: The user's latest message.
        conversation_history: Recent conversation turns.
        memory_context: Relevant memories to inject.
        emotion_state: Current emotion state.
        scene_description: Current scene context.

    Returns:
        Formatted prompt string.
    """
    parts = []

    # Scene context
    if scene_description:
        parts.append(f"【场景】{scene_description}")

    # Character constraint
    parts.append(f"【角色：{character_name}】")
    parts.append(character_persona)
    parts.append(f"当前情绪：{emotion_state}")

    # Memory injection
    if memory_context:
        parts.append("【角色记忆】")
        for mem in memory_context:
            parts.append(f"  - {mem}")

    # Conversation history
    if conversation_history:
        parts.append("【对话记录】")
        for turn in conversation_history[-10:]:
            parts.append(f"  {turn}")

    # User message
    parts.append(f"【玩家说】{user_message}")

    # Instructions
    parts.append("")
    parts.append("请以角色的口吻回复，保持性格一致。")
    parts.append("可在回复中嵌入 [emotion:xxx] 标签表示情绪变化（如 happy, sad, angry, shy, surprised）。")
    parts.append("回复长度：1-3 句话，自然口语化。")

    return "\n".join(parts)


SYSTEM_PROMPT = """你是一个沉浸式角色扮演 AI。你的任务是扮演异世界冒险故事中的 NPC 角色，与玩家进行自然、有性格的对话。

规则：
1. 始终保持角色一致性，不要打破第四面墙。
2. 回复简短自然（1-3 句话），像真人对话。
3. 使用 [emotion:xxx] 标签标注情绪变化。
4. 如果玩家提到你记忆中有的事情，自然地回应（可以回忆、感慨、追问）。
5. 不要重复对话记录中已有的内容。"""
