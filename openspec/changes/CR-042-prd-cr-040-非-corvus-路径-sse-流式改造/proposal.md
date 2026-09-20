# Proposal

## Why

### 背景

当前系统中，Corvus 引擎的对话已使用 SSE 流式输出（`_stream_corvus_turn`），前端逐字显示。但 Legacy 引擎的三条路径仍然是非流式同步 JSON 响应，用户必须等待 LLM 完整生成后才能看到回复，体验明显滞后。

### 慢的根因

| 路径 | 当前模式 | 瓶颈 |
|---|---|---|
| `POST /game/{session_id}/choice`（Legacy） | 同步 JSON | `NarrativeEngine.process_choice()` → transition/ai_dialog 节点同步等 LLM 完整返回；之后前端再发 `fetchDialogue()` 二次请求 |
| `POST /game/{session_id}/custom-input`（Legacy） | 同步 JSON | `NarrativeEngine.process_custom_input()` → 同步等 LLM 完整返回 |
| `POST /game/{session_id}/free-chat` | 同步 JSON | `free_chat_service.send_message()` → `model_router.call_with_fallback()` 同步等 LLM 完整返回 |

### 已有基础设施

- `llm_gateway` 已有 `stream_dialogue()` / `stream_complete()` 异步生成器
- 所有 Provider（Thoushub / OpenAI / Mock）均已实现 `stream()` 方法
- `NarrativeEngine` 已有 `generate_dialogue_stream()` 异步生成器
- 前端 Corvus 分支已有完整的 SSE 解析逻辑（`fetch` + `ReadableStream` reader）
- 前端 `characterChat.ts` 已有 `sendMessageStream()` SSE 消费逻辑

### 业务目标

- 将 Legacy 引擎的三条非流式路径改为 SSE 流式输出，让用户在 LLM 生成的同时就能逐字看到回复，消除体验滞后。
- 目标用户：使用 Legacy 引擎 `submit_choice` / `submit_custom_input` / `free-chat` 的玩家。

## What Changes

- REQ-001: Legacy `submit_choice` 推进到 `transition`/`ai_dialog` 节点时返回 SSE 流式输出；`preset`/`choice` 节点保持 JSON 响应。
- REQ-002: Legacy `submit_custom_input` 改为 SSE 流式输出，使用 `llm_gateway.stream_dialogue()` 替代同步 `generate_dialogue()`。
- REQ-003: 新增 `POST /game/{session_id}/free-chat/stream` 端点返回 SSE；旧端点保留兼容（不删除），标记 deprecated。
- REQ-004: `model_router` 新增 `stream_with_fallback()` 方法，支持流式 + 自动降级 fallback 模型。
- REQ-005: 提取 Corvus 分支 SSE 解析逻辑为公共 `useSSEStream()` composable，供三条 Legacy 路径复用。Corvus 路径迁移后必须回归验证。

## Non-Goals

- Corvus 引擎路径（已 SSE，不改）
- 数据库结构变更（无变化）
- 旧端点删除（保留兼容，CEO 附条件 C3 硬性约束）
- Provider `stream()` 方法修改（已实现）
- 新增 LLM 网关或 AI 模型
- 管理后台改动
- 真实支付/订阅
- OAuth 登录

## Success Criteria

- Legacy 引擎 `submit_choice` 在 transition/ai_dialog 节点返回 SSE 流式输出，前端逐字显示。
- Legacy 引擎 `submit_custom_input` 返回 SSE 流式输出。
- `free-chat` 新增流式端点，旧端点保留兼容。
- `model_router` 具备 `stream_with_fallback()` 流式 + 降级能力。
- 前端三条 Legacy 路径使用公共 `useSSEStream()` composable 解析 SSE。
- Corvus 路径迁移到 composable 后功能不变（回归验证通过）。
- 所有 SSE 事件格式与 Corvus 路径一致。
- 旧端点保留，未被删除。

## Impact

| 层面 | 影响 |
|---|---|
| 后端 `game.py` | `submit_choice` Legacy 路径 + `submit_custom_input` Legacy 路径改为条件 SSE |
| 后端 `game.py` | 新增 `free-chat/stream` 端点 |
| 后端 `model_router.py` | 新增 `stream_with_fallback()` |
| 后端 `free_chat_service.py` | 新增 `send_message_stream()` |
| 后端 `narrative_engine.py` | 新增 `process_choice_stream()` / `process_custom_input_stream()` |
| 前端 `stores/game.ts` | Legacy 分支 `submitChoice` / `submitCustomInput` 改为 SSE reader |
| 前端 `FreeChatView.vue` | 改用流式端点 |
| 前端 `composables/useSSEStream.ts` | 新增公共 SSE 解析 composable |
| `docs/runtime/runtime-contract.md` | 追加 streaming 端点说明 |
| `docs/api/api.md` | 追加 streaming 端点文档 |

## CEO 附条件

| 编号 | 条件 | 纳入跟踪 |
|---|---|---|
| C1 | PRD 中技术实现细节不替代 REQUIREMENT/DESIGN 正式产出；PM/SA 必须独立确认 | ✅ PM 已独立确认需求，不依赖 PRD 技术细节做需求判断；SA 在 DESIGN 阶段独立确认技术方案 |
| C2 | composable 提取后 Corvus 路径必须回归验证；失败则 Corvus 保持原逻辑 | ✅ AC-022 要求 Corvus 回归验证；失败时 Corvus 保持原逻辑不阻塞本 CR |
| C3 | 旧端点保留兼容（不删除）为硬性约束 | ✅ AC-015 验证旧端点保留；AC-002 验证 preset/choice 保持 JSON |

## Open Questions

| 编号 | 问题 | 阻塞 MVP | 处理结论 | 展示状态 |
|---|---|---|---|---|
| Q-001 | SSE 流中断时的错误恢复行为是否需特殊处理？ | 否 | 非阻塞暂缓：建议复用 Corvus 路径已有模式（error 事件 + 关闭流 + 记录日志）。暂缓到 DESIGN 阶段由 SA 确认。 | PRD 自动入口已记录，暂缓到 DESIGN 阶段 |
| Q-002 | SSE 流式端点是否需要 heartbeat/timeout 机制？ | 否 | 非阻塞暂缓：建议复用 Corvus 路径已有模式（无 heartbeat，依赖 Provider stream timeout）。暂缓到 DESIGN 阶段由 SA 确认。 | PRD 自动入口已记录，暂缓到 DESIGN 阶段 |
| Q-003 | AC-019 fallback 文本具体内容是什么？ | 否 | 非阻塞暂缓：建议返回预设友好提示文本。暂缓到 DESIGN 阶段由 SA 确认。 | PRD 自动入口已记录，暂缓到 DESIGN 阶段 |
