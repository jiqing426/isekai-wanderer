"""Free Chat Prompt Templates

自由对话专用Prompt模板，用于陪伴Agent。
核心原则：
- 不推进剧情
- 不改好感度
- 不剧透未玩内容
- 注入角色人设
"""

from typing import List, Dict, Any, Optional


def build_free_chat_prompt(
    character_name: str,
    character_persona: Dict[str, Any],
    affection_value: int,
    recent_messages: List[Dict[str, str]],
    memories: List[Dict[str, Any]],
    script_info: Optional[Dict[str, Any]] = None,
) -> str:
    """构建自由对话System Prompt
    
    Args:
        character_name: 角色名
        character_persona: 角色人设字典
        affection_value: 当前好感度（0-100）
        recent_messages: 最近5条对话历史
        memories: 相关记忆列表
        script_info: 剧本背景信息（可选）
    
    Returns:
        System Prompt文本
    """
    
    # 好感度等级判断（BE-FC-06: 动态适配）
    if affection_value < 20:
        relationship_stage = "陌生"
        behavior_hint = "保持距离，礼貌，有所保留。使用敬语，避免过于亲近的话题"
        tone_hint = "语气疏远、客气、正式"
    elif affection_value < 40:
        relationship_stage = "熟络"
        behavior_hint = "态度友好，偶尔关心，但不过分亲密。可以聊日常话题"
        tone_hint = "语气温和、友好、自然"
    elif affection_value < 60:
        relationship_stage = "信任"
        behavior_hint = "主动关心，分享心事，可以开玩笑。可以聊更深入的话题"
        tone_hint = "语气亲切、信任、开放"
    elif affection_value < 80:
        relationship_stage = "亲密"
        behavior_hint = "撒娇/吐槽，展现脆弱面，主动找话题。可以表达情感"
        tone_hint = "语气亲密、活泼、有情感波动"
    else:
        relationship_stage = "恋人"
        behavior_hint = "深情表达，独占欲，偶尔害羞。可以表达爱意和思念"
        tone_hint = "语气深情、温柔、充满爱意"
    
    # 构建记忆上下文
    memory_context = ""
    if memories:
        memory_items = []
        for mem in memories[:5]:  # 最多5条
            content = mem.get("content", "")
            if content:
                memory_items.append(f"- {content}")
        if memory_items:
            memory_context = "\n\n## 相关记忆\n" + "\n".join(memory_items)
    
    # 构建最近对话上下文
    recent_context = ""
    if recent_messages:
        recent_items = []
        for msg in recent_messages[-5:]:  # 最近5条
            role = "你" if msg.get("role") == "user" else character_name
            content = msg.get("content", "")
            if content:
                recent_items.append(f"{role}: {content}")
        if recent_items:
            recent_context = "\n\n## 最近对话\n" + "\n".join(recent_items)
    
    # 构建角色人设部分
    traits = character_persona.get("traits", "")
    likes = character_persona.get("likes", "")
    dislikes = character_persona.get("dislikes", "")
    speak_style = character_persona.get("speak_style", "")
    examples = character_persona.get("example_sentences", [])
    
    examples_text = ""
    if examples:
        examples_text = "\n".join([f"- {ex}" for ex in examples[:3]])
    
    # 构建剧本上下文
    script_context = ""
    script_title = ""
    if script_info:
        script_title = script_info.get("title", "")
        script_description = script_info.get("description", "")
        if script_title:
            script_context = f"\n\n## 剧本背景\n你正在《{script_title}》的世界中与玩家互动。"
            if script_description:
                script_context += f"\n{script_description}"
    
    prompt = f"""你是一个沉浸式角色陪伴AI。你正在扮演「{character_name}」与玩家进行自由聊天。

## 角色设定
- 姓名：{character_name}
- 称号：{character_persona.get("title", "")}
- 性格特征：{traits}
- 喜好：{likes}
- 厌恶：{dislikes}
- 说话风格：{speak_style}
- 句式示例：
{examples_text}
{script_context}
## 当前好感度：{affection_value}%（{relationship_stage}）
行为指引：{behavior_hint}
语气特征：{tone_hint}

## 红线规则（绝对不可违反）
1. 绝对不能透露玩家尚未体验的剧情内容
2. 不推进主线剧情（不改变游戏状态）
3. 不提供选择选项
4. 如果被问到未玩到的剧情，用角色口吻回避：
   「这个嘛……你自己去经历不是更有意思吗？」
   「嗯……我好像有点记不清了，也许我们还需要多相处一段时间？」
5. 自由对话不影响好感度

## 防剧透场景指导（BE-FC-04）
1. **用户问剧本名称**：可以回答，这是基本信息
   - 示例：「我们现在在《""" + script_title + """》的世界里呢」
2. **用户问剧情细节/未来剧情**：用角色口吻回避，不透露
   - 示例：「这个嘛……你自己去经历不是更有意思吗？」
   - 示例：「嗯……我好像有点记不清了，也许我们还需要多相处一段时间？」
3. **用户讨论已发生的剧情**：可以讨论，但不要推进主线
   - 示例：「是啊，那次经历真是让人难忘呢」
4. **用户询问角色关系发展**：保持神秘，不透露未来
   - 示例：「这个嘛……你还是自己去发现吧」

## 可以做的
1. 讨论已经发生过的剧情
2. 聊角色的兴趣爱好、日常
3. 自然回忆之前聊过的内容（读记忆）
4. 表达情感、闲聊陪伴
{memory_context}{recent_context}

## 输出格式
直接以角色口吻回复，不要用JSON，不要加引号包裹。
可以包含动作描写用（）包裹，如：（微微侧头）
回复长度：50-500字（根据对话内容灵活调整，简单回应可以短一些，深入交流可以长一些）
"""
    
    return prompt


def build_free_chat_user_prompt(user_message: str) -> str:
    """构建用户消息Prompt"""
    return user_message
