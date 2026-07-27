# Free Conversation Mode — CR-002 P1 功能

> 本规格定义自由对话模式功能。用户可在剧本间进入自由对话，从 5 个预设话题中选择，角色根据话题和记忆生成对话。

## Background

CR-001 MVP 聚焦结构化剧本叙事，但缺少剧本间的自由互动。CR-002 补齐此 P1 功能，让用户可以在不进入剧本的情况下与角色自由对话，增强角色陪伴感和用户粘性。

## Requirements

### Requirement: 自由对话入口

用户在游戏首页可进入自由对话模式，选择角色和话题开始对话。

#### Scenario: 进入自由对话模式

- Given: 用户在游戏首页
- When: 用户点击"自由对话"入口
- Then: 展示角色选择界面
- And: 用户选择角色后展示 5 个预设话题

#### Scenario: 选择话题开始对话

- Given: 用户已选择角色
- When: 用户从 5 个话题中选择一个
- Then: 进入对话界面
- And: 角色根据话题和记忆生成开场白

### Requirement: 5 个预设话题

系统提供 5 个预设话题，覆盖不同互动场景。

#### Scenario: 话题列表展示

- Given: 用户进入自由对话角色选择后
- When: 用户查看话题列表
- Then: 展示以下 5 个话题：
  - 日常闲聊（Daily Chat）
  - 角色故事（Character Story）
  - 世界观探讨（World Discussion）
  - 情感倾诉（Emotional Support）
  - 冒险建议（Adventure Advice）

### Requirement: LLM 角色约束对话

自由对话使用 LLM Gateway 生成对话，但必须保持角色性格一致性。

#### Scenario: 角色性格一致性

- Given: 用户选择特定角色并开始对话
- When: 用户发送消息
- Then: LLM 响应必须符合该角色性格约束
- And: 不得出现角色性格不一致的回复

#### Scenario: 跨会话记忆引用

- Given: 用户与该角色有历史对话记忆
- When: 对话涉及相关话题
- Then: 角色可引用历史记忆（如果置信度 >0.8）
- And: 引用时保持自然流畅

### Requirement: 对话界面和交互

自由对话界面与剧本对话界面风格一致，支持流式文本展示。

#### Scenario: 流式对话展示

- Given: 用户在自由对话模式
- When: 用户发送消息后
- Then: 角色回复以流式打字效果展示
- And: 帧率 ≥30fps（与剧本对话一致）

#### Scenario: 对话历史保存

- Given: 用户完成一次自由对话
- When: 用户退出对话
- Then: 对话历史保存到 free_chat_sessions 表
- And: 用户可查看历史对话记录

## Implementation Notes

- **BE API**: POST /free-chat（接收用户消息 + 角色 + 话题，返回 LLM 响应）
- **LLM Gateway**: 使用现有 mock provider，prompt 包含角色性格约束 + 话题上下文
- **DB 表**: free_chat_sessions（session_id, user_id, character_id, topic, messages, created_at）
- **FE 页面**: FreeChatView.vue（角色选择 → 话题选择 → 对话界面）
- **记忆集成**: 调用 memory_service 获取相关记忆（如果存在）

## R/C/U/D Matrix

| Action | User | System | Notes |
|---|---|---|---|
| Create | user | system | 用户发起对话，系统创建 session |
| Read | user | system | 用户查看对话历史和话题 |
| Update | user + system | system | 用户发消息，系统生成回复 |
| Delete | user | system | 用户可删除对话历史 |

## Downstream Constraints

| Consumer | Contract |
|---|---|
| DEV-CR2-009 | POST /free-chat API + FreeChatView.vue + LLM 角色约束 prompt |
| QA Phase 1 | Playwright：话题选择 + 对话流程验证 |
