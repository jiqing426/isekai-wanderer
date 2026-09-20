# PRD: Corvus 玩家选项功能 (CR-039)

## 概述

在 Corvus 引擎的 SSE 流式对话中，增加动态玩家选项功能。每轮对话结束后，Game Master（GM）根据当前对话上下文生成 2-4 个情境化选项，通过 `gm_update` 事件推送到前端，与自由文字输入共存。

## 目标用户

- 喜欢选择驱动叙事但使用 Corvus 引擎的玩家
- 希望有引导提示但不限制自由输入的玩家

## 用户故事

1. **作为玩家**，我希望在 Corvus 对话结束后看到 2-4 个情境化选项，这样我可以快速选择行动方向，而不必每次都自己想说什么
2. **作为玩家**，我希望选项是动态生成的，根据当前对话内容变化，这样每次体验不同
3. **作为玩家**，我希望即使有选项显示，我仍然可以自由输入文字，不被选项限制
4. **作为玩家**，我希望点击选项后等同于以选项文字发送消息，行为一致

## 功能需求

### REQ-GM-001: GM prompt 扩展

- GM 的 JSON 输出 schema 增加 `playerOptions` 字段
- `playerOptions` 是数组，每个元素包含 `text`（必填）和 `hint`（可选）
- 每轮生成 2-4 个选项，反映不同态度/行动/对话方向
- 纯叙事过渡场景可返回空数组
- 选项文字简洁（≤30 字）

### REQ-SSE-001: SSE 事件扩展

- `gm_update` 事件带上 `playerOptions` 数据
- 后端 SSE 透传时将 `playerOptions` 映射为前端期望的 `choices` 格式
- 映射规则：`{ text, hint }` → `{ id: index, text, hint }`

### REQ-FE-001: 前端选项渲染

- `gm_update` 事件处理中，将 `playerOptions` 赋值到 `pendingChoices`
- ChoicePanel 已有组件，`hasChoices=true` 时自动显示
- FreeChatInput 不隐藏，始终可用
- 选项点击后以选项文字作为 `custom-input` 发送

### REQ-FE-002: 向后兼容

- GM 未返回 `playerOptions` 时，`pendingChoices` 为空数组
- `hasChoices=false`，ChoicePanel 隐藏
- FreeChatInput 始终显示
- 不影响已有 Corvus 自由输入流程

## 验收标准

| AC 编号 | 需求 | 验收标准 | 优先级 |
|---|---|---|---|
| AC-039-001 | REQ-GM-001 | GM 输出的 JSON 中包含 `playerOptions` 字段，类型为数组，每元素含 `text`（必填）和 `hint`（可选） | P0 |
| AC-039-002 | REQ-GM-001 | 每轮 GM 输出 2-4 个选项（纯叙事过渡场景可为空数组） | P0 |
| AC-039-003 | REQ-SSE-001 | `gm_update` SSE 事件包含 `playerOptions` 数据 | P0 |
| AC-039-004 | REQ-SSE-001 | 后端 SSE 透传将 `playerOptions` 映射为 `choices` 格式（含 id/text/hint） | P0 |
| AC-039-005 | REQ-FE-001 | 对话结束后 ChoicePanel 显示 2-4 个选项 | P0 |
| AC-039-006 | REQ-FE-001 | 玩家点击选项 → 以选项文字作为 custom-input 发送 → SSE 正常流式回应 | P0 |
| AC-039-007 | REQ-FE-001 | FreeChatInput 在有选项时仍显示，玩家可自由输入 | P0 |
| AC-039-008 | REQ-FE-002 | GM 未返回 `playerOptions` 时，ChoicePanel 隐藏，FreeChatInput 正常 | P0 |
| AC-039-009 | REQ-FE-002 | Legacy 引擎选择逻辑不受影响 | P1 |

## 非目标

- 不增加预设节点/分支系统（Legacy 已有）
- 不增加结局判定机制
- 不增加选项的好感度影响（GM 已有 relationshipUpdates）
- 不改数据库结构
- 不新增 API 端点
