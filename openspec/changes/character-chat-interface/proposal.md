# OpenSpec Change: 角色聊天界面修复

## 变更ID
CR-021-fix

## 变更名称
character-chat-interface-fix

## 变更类型
Bug Fix + Feature Completion

## 变更原因
用户在 2026-07-29 09:53 反馈角色聊天界面存在以下问题：
1. **角色数据不对** - 左侧角色列表显示的数据与实际不符
2. **缺少跳转详情按钮** - 右侧聊天界面右上角应有跳转角色详情页面的按钮
3. **功能缺失较多** - 整体功能完成度不足

## 问题分析

### 问题1: 角色数据不对
**根本原因**: 
- `CharacterChatView.vue` 调用 `characterApi.getCharacters()` 获取角色列表
- 后端 `GET /api/v1/characters` 返回的数据不包含好感度信息（`affection_value`, `affection_level`）
- `CharacterList.vue` 组件期望的 `Character` 类型包含好感度字段，但实际数据为空/默认值
- 需要调用 `GET /api/v1/affection` 获取用户与各角色的好感度数据，然后合并到角色列表

**影响**: 用户看到的好感度进度条和数值都是错误的

### 问题2: 缺少跳转详情按钮
**根本原因**:
- `ChatWindow.vue` 的 `chat-header` 只有角色名称和好感度显示
- 没有实现跳转到 `/characters/{characterId}` 的按钮

**影响**: 用户无法从聊天页面快速跳转到角色详情页查看更多信息

### 问题3: 功能缺失
**缺失功能清单**:
1. **NPC 自动回复** - 发送消息后只有用户消息，没有NPC回复
2. **好感度数据合并** - 角色列表未合并好感度数据
3. **角色详情跳转** - 聊天头部缺少跳转按钮

## 变更内容

### 修复项

#### FIX-001: 角色列表好感度数据修复 (P0)
**描述**: 修复角色列表好感度显示不正确的问题

**实现方案**:
1. 在 `CharacterChatView.vue` 中同时调用 `characterApi.getCharacters()` 和 `affectionApi.getAffections()`
2. 将好感度数据合并到角色列表中
3. 更新 `CharacterList.vue` 正确显示合并后的数据

**验收标准**:
- AC-FIX-001: 左侧角色列表正确显示每个角色的好感度进度条和数值
- AC-FIX-002: 好感度数据与 `/api/v1/affection` 返回的数据一致

#### FIX-002: 添加角色详情跳转按钮 (P0)
**描述**: 在聊天窗口头部添加跳转到角色详情页的按钮

**实现方案**:
1. 在 `ChatWindow.vue` 的 `chat-header` 中添加"查看详情"按钮
2. 点击按钮跳转到 `/characters/{characterId}`

**验收标准**:
- AC-FIX-003: 聊天窗口右上角显示"查看详情"按钮
- AC-FIX-004: 点击按钮跳转到对应角色的详情页

#### FIX-003: NPC 自动回复功能 (P1)
**描述**: 实现发送消息后的NPC自动回复

**实现方案**:
1. 后端 `POST /api/v1/character-chat/{character_id}/messages` 增加NPC回复逻辑
2. 根据角色性格和好感度生成NPC回复
3. 返回用户消息和NPC回复

**验收标准**:
- AC-FIX-005: 用户发送消息后，收到NPC自动回复
- AC-FIX-006: NPC回复符合角色性格设定
- AC-FIX-007: 好感度根据对话内容变化

## 不做范围
- 不修改已有的送礼功能
- 不修改推荐话题功能
- 不修改消息持久化逻辑
- 不修改移动端适配

## 成功标准
1. 角色列表好感度显示正确
2. 可以从聊天页面跳转到角色详情页
3. 发送消息后收到NPC回复
4. 所有修复通过QA验证

## 影响范围
- 前端: `CharacterChatView.vue`, `CharacterList.vue`, `ChatWindow.vue`
- 后端: `chat.py` (NPC回复逻辑)
- API: `GET /api/v1/character-chat/{character_id}/messages`, `POST /api/v1/character-chat/{character_id}/messages`

## 待澄清问题
无。所有问题已通过代码分析确认。

## 风险评估
| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| NPC回复质量不稳定 | 中 | 使用简单的规则引擎生成回复，后续可接入AI |
| 好感度数据合并性能 | 低 | 数据量小，影响可忽略 |

## 创建时间
2026-07-29T10:30:00+08:00

## 创建人
PM
