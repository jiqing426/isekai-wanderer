# Free Chat Dynamic Adaptation Spec — CR-008 V2

## 需求概述

自由对话必须根据当前剧本、角色动态适配，不能硬编码角色人设。

## 当前问题

1. `character_personas.py` 只有 3 个硬编码角色（雪乃/阳菜/辉夜）
2. `game.py` 用 `route_id` 代理 `character_id`（逻辑错误）
3. 用户玩任何剧本，自由对话 AI 都扮演固定角色

## 需求列表

### REQ-FC-01: 角色人设从数据库读取（P0）

**修改文件**：`backend/app/llm/prompts/character_personas.py`

**场景 1**: 数据库有角色
- 调用 `get_character_persona(character_id, db)`
- 从 `characters` 表读取 name, personality, likes, speak_style
- 返回角色人设字典

**场景 2**: 数据库无角色（兼容旧数据）
- Fallback 到硬编码 CHARACTER_PERSONAS
- 默认返回雪乃人设

**验收标准**:
- AC-FC-01-1: 从 `characters` 表读取角色信息
- AC-FC-01-2: 返回 name, traits, likes, speak_style 字段
- AC-FC-01-3: 数据库无记录时 fallback 到硬编码

### REQ-FC-02: API 查询正确 character_id（P0）

**修改文件**：`backend/app/api/v1/game.py`

**场景 1**: 从 session metadata 读取
- `character_id = game_session.metadata.get("character_id")`
- 如果 metadata 有值，直接使用

**场景 2**: 从用户选择记录推断
- 查询用户在该剧本中最后使用的角色
- 从 `game_sessions` 表按 created_at DESC 查询

**场景 3**: 无历史记录
- 使用剧本的第一个 main character
- 从 `characters` 表查询 `is_main=True` 的角色

**验收标准**:
- AC-FC-02-1: 不再使用 `route_id` 作为 character_id
- AC-FC-02-2: 优先从 metadata 读取
- AC-FC-02-3: 无 metadata 时从历史记录推断
- AC-FC-02-4: 无历史记录时使用 main character

### REQ-FC-03: 注入剧本背景到 prompt（P0）

**修改文件**：`backend/app/services/free_chat_service.py`

**场景 1**: 构建 prompt
- 查询当前 script 信息
- 注入剧本标题、背景描述
- 注入角色性格、说话风格

**场景 2**: prompt 模板
```
你是 {character.name}，来自剧本《{script.title}》。
剧本背景：{script.description}
你的性格：{character.personality.traits}
你喜欢：{character.likes}
你的说话风格：{character.speak_style}
请保持角色设定，用角色的口吻回复。
```

**验收标准**:
- AC-FC-03-1: prompt 包含剧本标题和背景
- AC-FC-03-2: prompt 包含角色性格和说话风格
- AC-FC-03-3: AI 回复符合角色设定

### REQ-FC-04: 添加防剧透规则（P1）

**修改文件**：`backend/app/services/free_chat_service.py`

**场景 1**: 用户问剧本名字
- AI 可以回答剧本名称
- 不视为剧透

**场景 2**: 用户问剧情细节
- AI 用角色口吻回避
- 示例："这个嘛...我们还是聊点别的吧~"

**场景 3**: 讨论已发生剧情
- 可以讨论已经发生的剧情
- 不主动推进主线

**验收标准**:
- AC-FC-04-1: 用户问剧本名字，AI 可以回答
- AC-FC-04-2: 用户问未发生剧情，AI 回避不剧透
- AC-FC-04-3: 可讨论已发生的剧情

### REQ-FC-05: 前端参数传递确认（P0）

**修改文件**：`frontend/src/views/FreeChatView.vue`

**场景 1**: 进入自由对话
- 从 GameView 跳转时传递 characterId, scriptId, sessionId
- FreeChatView 从 route.query 读取参数

**验收标准**:
- AC-FC-05-1: 进入自由对话时传递 characterId
- AC-FC-05-2: 进入自由对话时传递 scriptId
- AC-FC-05-3: 进入自由对话时传递 sessionId

### REQ-FC-06: 历史对话显示验证（P1）

**修改文件**：`frontend/src/views/FreeChatView.vue`

**场景 1**: 加载历史对话
- 调用 `GET /game/{sessionId}/free-chat/history`
- 显示当前角色的历史对话

**验收标准**:
- AC-FC-06-1: 历史对话正确加载
- AC-FC-06-2: 历史对话属于当前角色

## 依赖关系

```
FC-01 → FC-03（persona 数据用于 prompt）
FC-02 → FC-03（character_id 用于查询 persona）
FC-03 → FC-06（prompt 完成后才能测试历史）
FC-05 可与 BE 并行
```

## 工作量

| 任务 | 角色 | 工作量 |
|------|------|--------|
| FC-01 | BE | 2h |
| FC-02 | BE | 1.5h |
| FC-03 | BE | 1.5h |
| FC-04 | BE | 1h |
| FC-05 | FE | 1h |
| FC-06 | FE | 1h |
| **合计** | - | **8h** |

## 执行顺序

```
Day 1: FC-01 + FC-02（BE 4h）
       FC-05（FE 1h，并行）
Day 2: FC-03 + FC-04（BE 2.5h）
       FC-06（FE 1h）
       联调（0.5h）
```

## 验收场景

**核心场景**：
1. 用户玩「星月奇缘」选择「沈星澜」
2. 进入自由对话
3. AI 以「沈星澜」身份回复
4. 性格符合数据库中 personality 字段
5. 用户问剧情细节，AI 回避不剧透
