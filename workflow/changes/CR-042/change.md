# Change

## 变更单

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-042 |
| 来源 | 用户 PRD |
| 类型 | feature |
| 优先级 | P1 |
| 当前状态 | intake-ready |
| 负责人 | pl |
| 关联 PRD | `docs/prd/prd.md` |
| 关联 OpenSpec Change | `../../../openspec/changes/CR-042-prd-cr-040-非-corvus-路径-sse-流式改造/` |

## 问题和目标

- 现状：来自用户 PRD，待 PM 在 REQUIREMENT 阶段结构化。
- 目标：PRD: CR-040 — 非 Corvus 路径 SSE 流式改造
- 成功标准：PRD 中 P0/P1 验收项被拆成可测试 acceptance，并通过后续设计、开发、QA 与发布关口。
- 本次不做：PRD 未明确授权的生产部署、真实支付、真实 AI/付费资源调用、不可逆数据操作。

## 原始 PRD

```markdown
# PRD: CR-040 — 非 Corvus 路径 SSE 流式改造

## 背景

当前系统中，Corvus 引擎的对话已使用 SSE 流式输出（`_stream_corvus_turn`），前端逐字显示。但 Legacy 引擎的三条路径仍然是非流式的同步 JSON 响应，用户必须等待 LLM 完整生成后才能看到回复，体验明显滞后。

### 慢的根因

| 路径 | 当前模式 | 瓶颈 |
|---|---|---|
| `POST /game/{session_id}/choice`（Legacy） | 同步 JSON | `NarrativeEngine.process_choice()` → 如果下一节点是 `transition`/`ai_dialog`，同步等 LLM 完整返回后才发 JSON；之后前端再发 `fetchDialogue()` 二次请求 |
| `POST /game/{session_id}/custom-input`（Legacy） | 同步 JSON | `NarrativeEngine.process_custom_input()` → 同步等 LLM 完整返回 |
| `POST /game/{session_id}/free-chat` | 同步 JSON | `free_chat_service.send_message()` → `model_router.call_with_fallback()` 同步等 LLM 完整返回 |

### 已有基础设施

- `llm_gateway` 已有 `stream_dialogue()` / `stream_complete()` 异步生成器
- 所有 Provider（Thoushub / OpenAI / Mock）均已实现 `stream()` 方法
- `NarrativeEngine` 已有 `generate_dialogue_stream()` 异步生成器（用于 `GET /dialogue/stream`，但前端未消费）
- 前端 Corvus 分支已有完整的 SSE 解析逻辑（`fetch` + `ReadableStream` reader）
- 前端 `characterChat.ts` 已有 `sendMessageStream()` SSE 消费逻辑

## 变更目标

将 Legacy 引擎的三条非流式路径改为 SSE 流式输出，让用户在 LLM 生成的同时就能逐字看到回复。

## 功能需求

### REQ-001：Legacy `submit_choice` SSE 流式化

**描述**：当 Legacy 引擎的 `submit_choice` 推进到 `transition`/`ai_dialog` 类型节点时，返回 `StreamingResponse` 逐字输出 LLM 生成的对话文本。对于 `preset`/`choice` 等无需 LLM 的节点，保持快速 JSON 响应。

**验收标准**：
- AC-001：`transition` 节点的 `submit_choice` 返回 `text/event-stream`，前端逐字显示
- AC-002：`preset`/`choice` 节点保持 JSON 响应（快速返回，无需 LLM）
- AC-003：SSE 事件格式与 Corvus 路径一致（`data: {"type":"text","content":"..."}` / `data: {"type":"done",...}`）
- AC-004：SSE 流结束后推送好感度变化、成就解锁等元数据
- AC-005：前端 Legacy 分支用 `fetch` + reader 解析 SSE，去掉后续 `fetchDialogue()` 二次请求

### REQ-002：Legacy `submit_custom_input` SSE 流式化

**描述**：将 Legacy 引擎的自由输入推进改为 SSE 流式输出。

**验收标准**：
- AC-006：`POST /game/{session_id}/custom-input` 返回 `text/event-stream`
- AC-007：使用 `llm_gateway.stream_dialogue()` 替代同步 `generate_dialogue()`
- AC-008：SSE 流式逐字输出角色回应文本
- AC-009：SSE 流结束后推送好感度变化和下一节点选项
- AC-010：前端 Legacy 分支用 SSE reader 解析，逐字显示

### REQ-003：`free-chat` SSE 流式化

**描述**：将自由对话端点改为 SSE 流式输出。

**验收标准**：
- AC-011：新增 `POST /game/{session_id}/free-chat/stream` 端点，返回 `text/event-stream`
- AC-012：`model_router` 新增 `stream_with_fallback()` 方法，支持流式 + 降级
- AC-013：SSE 逐字输出角色回复
- AC-014：SSE 流结束后推送好感度变化
- AC-015：旧 `POST /game/{session_id}/free-chat` 保留兼容，标记 deprecated
- AC-016：`FreeChatView.vue` 改用流式端点，逐字显示回复

### REQ-004：`model_router` 流式支持

**描述**：给 `model_router` 增加流式调用能力。

**验收标准**：
- AC-017：新增 `stream_with_fallback(scenario, messages, **kwargs) -> AsyncGenerator[str, None]` 方法
- AC-018：主模型流式失败时自动切换 fallback 模型
- AC-019：所有 fallback 模型均失败时返回 fallback 文本（非流式）

### REQ-005：前端 SSE 解析复用

**描述**：提取 Corvus 分支已有的 SSE 解析逻辑为公共 composable，供三条 Legacy 路径复用。

**验收标准**：
- AC-020：提取 `useSSEStream()` composable，封装 fetch + reader + SSE 解析
- AC-021：`submitChoice`（Legacy 分支）、`submitCustomInput`（Legacy 分支）、`FreeChatView` 均使用该 composable
- AC-022：Corvus 分支迁移到 composable 后功能不变（回归验证）

## 技术约束

- SSE 事件格式与 Corvus 路径保持一致：`data: {"type":"text"|"done"|"error"|"gm_update", ...}\n\n`
- 所有流式端点必须设置 `X-Accel-Buffering: no` 头（已有模式）
- 流式过程中的 DB 写操作（对话历史、好感度等）必须在 SSE 流结束后异步执行（deferred task），不阻塞流式输出
- 旧端点保留兼容，不删除
- Provider 的 `stream()` 方法已实现，无需修改

## 影响范围

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

## 不变项

- Corvus 引擎路径（已 SSE，不改）
- 数据库结构（无变化）
- 旧端点保留兼容（不删除）

## 风险

1. **SSE + DB 写入时序**：流式输出期间不能 commit DB，需要在 finally 中异步执行 — 已有模式（Corvus 的 `_run_deferred`）
2. **Legacy 节点类型判断**：`submit_choice` 需要先推进节点再判断类型，如果节点是 `preset` 则不应流式 — 解决方案：先推进，判断类型，preset 直接返回 JSON
3. **回归风险**：Corvus 路径已有 SSE，提取 composable 后需确保不破坏 — 需要回归 E2E
```

## OpenSpec Change 生成

- PM 根据本文件创建或更新对应 OpenSpec change：`proposal.md`、`specs/**/spec.md`；同时维护 `docs/prd/prd.md` 摘要和 `acceptance.md`。
- 未确认内容必须以 Q 编号登记；非阻塞问题可以记录为暂缓，不得伪装为已确认事实。
- OpenSpec change 或 workflow 追踪文件不完整时，不能直接让关口 `passed`。

## 影响范围

| 领域 | 是否影响 | 说明 |
| --- | --- | --- |
| PROJECT / 项目事实 | 是 | 已确认：PM 已从 PRD 识别项目目标、范围和依赖，见 Q-001~Q-003（非阻塞） |
| PRD / 需求输入 | 是 | 本 CR 来自用户 PRD |
| 架构 / 模块边界 | 否 | 不涉及架构变更，Architect 在 DESIGN 阶段判断 |
| API / 契约 | 是 | 新增 free-chat/stream 端点，旧端点保留兼容；Architect/BE 在 DESIGN 阶段判断 |
| 数据库 / 迁移 | 否 | 无数据库变更（PRD 已明确） |
| 权限 / 安全 / 隐私 | 否 | 复用现有 Bearer Token 认证，无新增权限边界；Security 在后续阶段审查 |
| 前端 / 管理端体验 | 是 | 前端 stores/game.ts + FreeChatView.vue + 新增 composable；FE 按任务单执行 |
| 测试 / 验收 | 是 | QA/PM 生成 acceptance 和 test-plan |
| 部署 / 生产 / 回滚 | 否 | 不涉及生产环境变更、部署平台变更；Ops 在发布阶段处理 |

## 人工确认

以下任一项为 `是` 时，不能由 LLM 自动通过，只能由人工确认后继续。

| 项 | 是 / 否 | 说明 |
| --- | --- | --- |
| 生产环境变更 | 否 | 不涉及生产环境变更 |
| 数据删除或不可逆迁移 | 否 | 无数据库变更，无数据删除 |
| 认证、授权或权限边界变更 | 否 | 复用现有 Bearer Token 认证，无新增权限边界 |
| 支付、账务或合规承诺 | 否 | 不涉及支付/账务/合规 |
| 公共 API 破坏性变更 | 否 | 旧端点保留兼容（C3），新增端点为非破坏性新增 |
| 大范围跨模块重构 | 否 | 范围明确：后端 4 文件 + 前端 4 文件，复用已有基础设施 |

## 自动入口记录

- 创建时间：2026-09-15T05:38:46Z
- 执行方式：`tools/bootstrap-openclaw-prd.py`
- 初始授权：仅授权创建 CR、记录 PRD、生成初始 workflow / OpenSpec 骨架；不授权自动通过阶段、关口或部署。
- 放行要求：每个推进型流转仍必须由 PL 展示交付物清单、关键结论、缺口和风险，并取得用户明确同意后，才能运行 readiness 并推进。
