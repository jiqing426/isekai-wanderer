# Spec: Corvus 玩家选项 — 前端规格

### Requirement: REQ-FE-001 — gm_update 事件处理扩展

前端 `game.ts` 的 SSE 事件处理中，收到 `gm_update` 事件时将 `player_options`/`choices` 赋值到 `pendingChoices`。

#### Scenario: 处理 playerOptions

- **Given** 前端 `game.ts` 的 SSE 事件处理中收到 `gm_update` 事件
- **When** 事件数据包含 `player_options` 或 `choices` 字段
- **Then** `pendingChoices.value` 被赋值为该字段值
- **And** ChoicePanel 自动响应 `hasChoices` 变化

#### Scenario: 选项点击发送

- **Given** ChoicePanel 显示选项，玩家点击某选项
- **When** 点击事件触发
- **Then** 调用 `submitCustomInput(option.text)`
- **And** 清空 `pendingChoices`
- **And** 进入 SSE 流式对话

### Requirement: REQ-FE-002 — 向后兼容

GM 未返回 `playerOptions` 时前端 fallback 到纯自由输入模式。

#### Scenario: 无 playerOptions 时 fallback

- **Given** `gm_update` 事件不含 `player_options` 字段
- **When** 前端处理事件
- **Then** `pendingChoices.value` 保持为空数组
- **And** `hasChoices` 为 false
- **And** ChoicePanel 隐藏
- **And** FreeChatInput 正常显示
