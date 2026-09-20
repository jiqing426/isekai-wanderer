"""Memory extraction prompt templates."""


MEMORY_EXTRACTION_SYSTEM = """你是一个记忆提取器。从玩家和角色的对话中，提取值得长期记住的信息。

提取规则：
1. 只提取玩家主动透露的个人信息、偏好、经历、情感表达。
2. 不要提取角色的话语（那是角色的台词，不是记忆）。
3. 不要提取无关紧要的闲聊（如"好的"、"嗯"）。
4. 每条记忆应简短、自包含（15-40 字）。
5. 为每条记忆标注 importance (0.1-1.0) 和 category。

**重点提取内容**：
- 爱好（喜欢做什么、兴趣爱好）
- 害怕什么（恐惧、担忧、不喜欢的事物）
- 爱吃什么（食物偏好、喜欢的食物）
- 讨厌什么（厌恶的事物）

类别 (category) 选项：
- personal_info: 个人信息（名字、年龄、职业等）
- preference: 喜好（食物、颜色、音乐等）
- fear: 害怕的事物（恐惧、担忧）
- food: 食物偏好（爱吃什么、讨厌吃什么）
- hobby: 爱好（兴趣爱好、喜欢做什么）
- experience: 经历（去过哪里、做过什么）
- emotion: 情感表达（开心、难过、担心等）
- relationship: 对角色或他人的看法
- goal: 目标或计划

输出格式：JSON 数组
[
  {"content": "玩家说他喜欢向日葵", "importance": 0.6, "category": "preference"},
  {"content": "玩家提到最近工作压力很大", "importance": 0.8, "category": "emotion"},
  {"content": "玩家害怕黑暗", "importance": 0.7, "category": "fear"},
  {"content": "玩家爱吃火锅", "importance": 0.6, "category": "food"}
]

如果没有值得提取的记忆，返回空数组 []。"""


def build_memory_extract_prompt(conversation: str, character_name: str = "") -> str:
    """Build prompt for extracting memories from a conversation.

    Args:
        conversation: Raw conversation text (player + character turns).
        character_name: Character's display name (to avoid UUID leaking into memories).

    Returns:
        Prompt string for memory extraction.
    """
    name_hint = f"\n注意：角色名称是「{character_name}」，在记忆中请使用角色名，不要使用任何 ID 或 UUID。" if character_name else ""
    return f"""以下是玩家和角色之间的一段对话：

---
{conversation}
---

请从中提取值得长期记住的信息，以 JSON 数组格式输出。{name_hint}"""


MEMORY_SUMMARY_SYSTEM = """你是一个记忆压缩器。将多条旧记忆压缩合并为更简洁的摘要，保留关键信息。

规则：
1. 合并相似/重复的记忆。
2. 保留最重要的细节。
3. 输出不超过 3 条压缩记忆。
4. 每条压缩记忆 20-50 字。

输出格式：JSON 数组
[
  {"content": "压缩后的记忆摘要", "importance": 0.7, "category": "personal_info"}
]"""


def build_memory_summary_prompt(memories: list[str]) -> str:
    """Build prompt for compressing/summarizing old memories.

    Args:
        memories: List of existing memory texts.

    Returns:
        Prompt string for memory compression.
    """
    memory_list = "\n".join(f"- {m}" for m in memories)
    return f"""以下是角色的旧记忆列表：

{memory_list}

请将这些记忆压缩合并为更简洁的摘要。"""
