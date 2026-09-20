# Capability Spec

### Requirement: REQ-001 Legacy submit_choice SSE 流式化

当 Legacy 引擎的 `submit_choice` 推进到 `transition`/`ai_dialog` 类型节点时，后端必须返回 `StreamingResponse`（`text/event-stream`），逐字输出 LLM 生成的对话文本。对于 `preset`/`choice` 等无需 LLM 的节点，保持快速 JSON 响应。

#### Scenario: transition 节点 SSE 流式输出（P0）

- **前置条件**: 用户在 Legacy 引擎游戏会话中，当前节点推进后下一节点类型为 `transition`
- **用户动作**: 用户在游戏对话界面点击选项（submit_choice）
- **可观察结果**: 前端收到 `text/event-stream` 响应，对话文本逐字显示，用户无需等待 LLM 完整生成
- **数据状态**: SSE 流结束后，对话历史异步写入数据库（复用 Corvus `_run_deferred` 模式）；数据库可查询到新对话记录
- **SSE 事件格式**: `data: {"type":"text","content":"..."}\n\n` 逐字推送，`data: {"type":"done",...}\n\n` 结束
- **验证方式**: Browser Interaction E2E — 前端打开游戏页面，点击选项，观察对话逐字显示；API/DB 契约验证 — 流结束后查询对话历史确认写入
- **覆盖 AC**: AC-001, AC-003, AC-004, AC-005
- **下游测试标记**: 需要 Browser Interaction E2E；需要 API/DB/Runtime 契约验证

#### Scenario: preset/choice 节点保持 JSON 响应（P0）

- **前置条件**: 用户在 Legacy 引擎游戏会话中，当前节点推进后下一节点类型为 `preset` 或 `choice`
- **用户动作**: 用户在游戏对话界面点击选项（submit_choice）
- **可观察结果**: 前端收到标准 JSON 响应，快速返回预设对话内容和选项，不触发 SSE 流
- **数据状态**: 数据库更新当前节点状态，与原有逻辑一致
- **验证方式**: Browser Interaction E2E — 前端点击选项，观察 JSON 响应快速返回，无逐字显示
- **覆盖 AC**: AC-002
- **下游测试标记**: 需要 Browser Interaction E2E

#### Scenario: ai_dialog 节点 SSE 流式输出（P1）

- **前置条件**: 用户在 Legacy 引擎游戏会话中，当前节点推进后下一节点类型为 `ai_dialog`
- **用户动作**: 用户在游戏对话界面点击选项（submit_choice）
- **可观察结果**: 前端收到 `text/event-stream` 响应，对话文本逐字显示
- **数据状态**: SSE 流结束后，对话历史异步写入数据库
- **验证方式**: Browser Interaction E2E — 前端点击选项，观察对话逐字显示
- **覆盖 AC**: AC-001
- **下游测试标记**: 需要 Browser Interaction E2E；需要 API/DB/Runtime 契约验证

#### Scenario: SSE 流结束后推送元数据（P1）

- **前置条件**: 用户在 Legacy 引擎游戏会话中，submit_choice 触发 SSE 流式输出
- **用户动作**: 等待 SSE 流完成
- **可观察结果**: SSE 流在 `done` 事件中推送好感度变化、成就解锁等元数据
- **数据状态**: 好感度变化异步写入数据库，刷新后仍然存在
- **验证方式**: API/DB 契约验证 — SSE 流结束后查询好感度确认更新
- **覆盖 AC**: AC-004
- **下游测试标记**: 需要 API/DB/Runtime 契约验证

#### Scenario: 前端去掉 fetchDialogue 二次请求（P1）

- **前置条件**: 用户在 Legacy 引擎游戏会话中，submit_choice 触发 SSE 流式输出
- **用户动作**: 用户点击选项后观察对话显示
- **可观察结果**: 前端在 SSE 流中直接获得对话内容，不再发送 `fetchDialogue()` 二次请求
- **验证方式**: Browser Interaction E2E — 通过浏览器 Network 面板或请求拦截确认无 `fetchDialogue` 请求
- **覆盖 AC**: AC-005
- **下游测试标记**: 需要 Browser Interaction E2E

### Requirement: REQ-002 Legacy submit_custom_input SSE 流式化

将 Legacy 引擎的 `submit_custom_input` 改为 SSE 流式输出，使用 `llm_gateway.stream_dialogue()` 替代同步 `generate_dialogue()`。

#### Scenario: custom-input 返回 SSE 流（P0）

- **前置条件**: 用户在 Legacy 引擎游戏会话中，当前节点允许自由输入
- **用户动作**: 用户在输入框填写自由文本并提交（submit_custom_input）
- **可观察结果**: 前端收到 `text/event-stream` 响应，角色回应文本逐字显示
- **数据状态**: SSE 流结束后，对话历史异步写入数据库
- **SSE 事件格式**: 与 REQ-001 一致
- **验证方式**: Browser Interaction E2E — 前端填写输入并提交，观察逐字显示
- **覆盖 AC**: AC-006, AC-007, AC-008
- **下游测试标记**: 需要 Browser Interaction E2E；需要 API/DB/Runtime 契约验证

#### Scenario: SSE 流结束后推送好感度和选项（P1）

- **前置条件**: 用户在 Legacy 引擎游戏会话中，submit_custom_input 触发 SSE 流式输出
- **用户动作**: 等待 SSE 流完成
- **可观察结果**: SSE 流在 `done` 事件中推送好感度变化和下一节点选项
- **数据状态**: 好感度变化异步写入数据库，刷新后仍然存在
- **验证方式**: API/DB 契约验证 — SSE 流结束后查询好感度确认更新
- **覆盖 AC**: AC-009
- **下游测试标记**: 需要 API/DB/Runtime 契约验证

#### Scenario: 前端 Legacy 分支 SSE reader 解析（P1）

- **前置条件**: 用户在 Legacy 引擎游戏会话中，submit_custom_input 触发 SSE 流式输出
- **用户动作**: 用户提交自由输入后观察角色回应显示
- **可观察结果**: 前端 Legacy 分支使用 SSE reader 解析，角色回应逐字显示
- **验证方式**: Browser Interaction E2E — 前端提交输入，观察逐字显示
- **覆盖 AC**: AC-010
- **下游测试标记**: 需要 Browser Interaction E2E

### Requirement: REQ-003 free-chat SSE 流式化

新增 `POST /game/{session_id}/free-chat/stream` 端点返回 SSE 流式输出。旧 `POST /game/{session_id}/free-chat` 保留兼容（不删除），标记 deprecated。`FreeChatView.vue` 改用流式端点。

#### Scenario: 新增 free-chat/stream 端点返回 SSE（P0）

- **前置条件**: 用户在自由对话界面中
- **用户动作**: 用户发送消息，前端调用 `POST /game/{session_id}/free-chat/stream`
- **可观察结果**: 后端返回 `text/event-stream`，角色回复逐字输出
- **数据状态**: SSE 流结束后，对话历史异步写入数据库
- **响应头**: `X-Accel-Buffering: no`
- **验证方式**: API 契约验证 — 直接调用端点确认返回 `text/event-stream`；DB 契约验证 — 流结束后查询对话历史
- **覆盖 AC**: AC-011, AC-013
- **下游测试标记**: 需要 API/DB/Runtime 契约验证

#### Scenario: 旧 free-chat 端点保留兼容（P0）

- **前置条件**: 旧端点 `POST /game/{session_id}/free-chat` 已存在
- **用户动作**: 调用旧端点
- **可观察结果**: 旧端点仍返回同步 JSON 响应，功能不变
- **验证方式**: API 契约验证 — 调用旧端点确认返回 JSON 200，响应包含 deprecation header 或标记
- **覆盖 AC**: AC-015
- **下游测试标记**: 需要 API/DB/Runtime 契约验证

#### Scenario: SSE 流结束后推送好感度变化（P1）

- **前置条件**: 用户在自由对话中，free-chat/stream 触发 SSE 流式输出
- **用户动作**: 等待 SSE 流完成
- **可观察结果**: SSE 流在 `done` 事件中推送好感度变化
- **数据状态**: 好感度变化异步写入数据库
- **验证方式**: API/DB 契约验证 — SSE 流结束后查询好感度确认更新
- **覆盖 AC**: AC-014
- **下游测试标记**: 需要 API/DB/Runtime 契约验证

#### Scenario: FreeChatView 改用流式端点（P1）

- **前置条件**: 用户打开自由对话界面
- **用户动作**: 用户发送消息
- **可观察结果**: `FreeChatView.vue` 调用流式端点，角色回复逐字显示
- **验证方式**: Browser Interaction E2E — 前端打开自由对话，发送消息，观察逐字显示
- **覆盖 AC**: AC-016
- **下游测试标记**: 需要 Browser Interaction E2E

### Requirement: REQ-004 model_router 流式支持

给 `model_router` 增加 `stream_with_fallback(scenario, messages, **kwargs) -> AsyncGenerator[str, None]` 方法，支持流式调用 + 自动降级 fallback 模型。

#### Scenario: stream_with_fallback 正常流式输出（P0）

- **前置条件**: `model_router` 配置了主模型和 fallback 模型
- **用户动作**: 调用 `stream_with_fallback(scenario, messages)`
- **可观察结果**: 返回 `AsyncGenerator[str, None]`，逐个 yield 文本 token
- **验证方式**: 单元测试/集成测试 — 调用方法确认返回异步生成器，逐 token yield
- **覆盖 AC**: AC-017
- **下游测试标记**: 需要 API/DB/Runtime 契约验证

#### Scenario: 主模型流式失败时切换 fallback（P1）

- **前置条件**: 主模型流式调用失败（如超时、连接错误）
- **用户动作**: 调用 `stream_with_fallback(scenario, messages)`
- **可观察结果**: 自动切换到 fallback 模型继续流式输出，不中断用户体验
- **验证方式**: 集成测试 — mock 主模型失败，确认 fallback 模型被调用并返回流式输出
- **覆盖 AC**: AC-018
- **下游测试标记**: 需要 API/DB/Runtime 契约验证

#### Scenario: 所有 fallback 均失败时返回非流式文本（P1）

- **前置条件**: 主模型和所有 fallback 模型均流式失败
- **用户动作**: 调用 `stream_with_fallback(scenario, messages)`
- **可观察结果**: 返回 fallback 文本（非流式，一次性 yield）
- **验证方式**: 集成测试 — mock 所有模型失败，确认返回非流式 fallback 文本
- **覆盖 AC**: AC-019
- **下游测试标记**: 需要 API/DB/Runtime 契约验证
- **备注**: fallback 文本具体内容见 Q-003，暂缓到 DESIGN 阶段由 SA 确认

### Requirement: REQ-005 前端 SSE 解析复用

提取 Corvus 分支已有的 SSE 解析逻辑为公共 `useSSEStream()` composable，封装 `fetch` + `ReadableStream` reader + SSE 事件解析。`submitChoice`（Legacy 分支）、`submitCustomInput`（Legacy 分支）、`FreeChatView` 均使用该 composable。Corvus 分支迁移到 composable 后功能不变（回归验证）。

#### Scenario: 提取 useSSEStream composable（P0）

- **前置条件**: Corvus 分支已有 SSE 解析逻辑（`fetch` + reader）
- **用户动作**: 开发者提取公共 composable
- **可观察结果**: `composables/useSSEStream.ts` 存在，封装 fetch + reader + SSE 解析，提供可复用接口
- **验证方式**: 单元测试 — composable 可独立调用，正确解析 SSE 事件
- **覆盖 AC**: AC-020
- **下游测试标记**: 需要 API/DB/Runtime 契约验证

#### Scenario: 三条 Legacy 路径使用 composable（P1）

- **前置条件**: `useSSEStream()` composable 已提取
- **用户动作**: 开发者在 `submitChoice`（Legacy 分支）、`submitCustomInput`（Legacy 分支）、`FreeChatView` 中使用 composable
- **可观察结果**: 三处代码均调用 `useSSEStream()`，SSE 解析逻辑复用，无重复代码
- **验证方式**: 代码审查 + 集成测试 — 确认三处使用 composable
- **覆盖 AC**: AC-021
- **下游测试标记**: 需要 Browser Interaction E2E

#### Scenario: Corvus 分支迁移后回归验证（P0）

- **前置条件**: Corvus 分支已有 SSE 流式输出功能
- **用户动作**: 将 Corvus 分支迁移到 `useSSEStream()` composable
- **可观察结果**: Corvus 路径 SSE 流式输出功能不变，对话逐字显示、好感度推送、元数据推送均正常
- **验证方式**: Browser Interaction E2E — Corvus 路径完整对话流程回归测试
- **覆盖 AC**: AC-022
- **下游测试标记**: 需要 Browser Interaction E2E
- **备注**: CEO 附条件 C2 — 若回归失败，Corvus 保持原逻辑，不阻塞本 CR

## 约束

### SSE 事件格式

所有流式端点的 SSE 事件格式必须与 Corvus 路径一致：

```
data: {"type":"text","content":"..."}\n\n
data: {"type":"done",...}\n\n
data: {"type":"error","content":"..."}\n\n
data: {"type":"gm_update",...}\n\n
```

### 响应头

所有流式端点必须设置 `X-Accel-Buffering: no` 头（已有模式）。

### DB 写入时序

流式过程中的 DB 写操作（对话历史、好感度等）必须在 SSE 流结束后异步执行（deferred task），不阻塞流式输出。复用 Corvus `_run_deferred` 模式。

### 旧端点保留兼容

旧端点保留兼容（不删除）为 CEO 附条件 C3 硬性约束。禁止在本次改造中移除任何现有端点。

### Provider 不修改

Provider 的 `stream()` 方法已实现，无需修改。
