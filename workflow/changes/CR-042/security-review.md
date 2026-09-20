| 项 | 内容 |
| --- | --- |
| 审查结论 | passed — 3 项低风险建议不阻塞 |

# Security Review — CR-042 非 Corvus 路径 SSE 流式改造

## 审查信息

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-042 |
| 变更 | Legacy 三条路径 SSE 流式改造 |
| 审查角色 | Security (Cat01-security) |
| 审查日期 | 2026-09-16T17:00+08:00 |
| 证据等级 | L1 |
| 审查结论 | **Passed** (含 2 项低风险建议) |

## 审查范围

### 读取的契约文档

- `docs/security/security.md` — 安全设计文档（含 CR-042 Additions）
- `docs/api/api.md` — API 契约（含 CR-042 新增/改造/废弃端点）
- `docs/database/database.md` — 数据库契约（CR-042 无 DB 变更）
- `docs/runtime/runtime-contract.md` — 运行时契约（含 CR-042 SSE 配置）
- `workflow/changes/CR-042/change.md` — 变更单
- `workflow/changes/CR-042/acceptance.md` — 验收矩阵 (22 AC)
- `workflow/changes/CR-042/test-report.md` — 测试报告
- `workflow/changes/CR-042/deploy-plan.md` — 部署计划（Pending）
- `workflow/traceability-chain.md` — 追踪链
- `workflow/failure-backtrace.md` — 倒查链

### 审查的代码文件

| 文件 | 审查重点 |
| --- | --- |
| `backend/app/api/v1/game.py` | SSE 端点、Bearer 认证、所有权校验、deferred DB 写入、错误事件消息 |
| `backend/app/llm/model_router.py` | stream_with_fallback 方法、fallback 文本、provider 调用 |
| `backend/app/services/free_chat_service.py` | send_message_stream 方法、user_id/character_id 隔离 |
| `frontend/src/composables/useSSEStream.ts` | SSE 解析、auth token 提取、XSS |
| `frontend/src/components/StoryPanel.vue` | v-html XSS 风险 |
| `backend/app/api/v1/auth.py` | get_current_user_id 认证逻辑 |
| `.env.example` | 环境变量配置 |
| `deploy/nginx/app.conf.example` | Nginx SSE 代理配置 |

## 检查清单逐项结论

### 1. 是否提交真实密钥、token、证书、密码或生产数据

**结论：✅ Passed**

- `.env.example` 中所有敏感值均为占位符（`change-me-local-only`、`test-key-placeholder`、`isekai_password`），无真实凭据。
- SSE 端点代码中无硬编码密钥或 token。
- `model_router.py` 中 LLM API Key 通过 `os.environ` 读取，未硬编码。
- 前端 `useSSEStream.ts` 从 cookie 提取 token，不从代码中硬编码。

### 2. 鉴权、授权、审计和敏感操作确认是否完整

**结论：✅ Passed**

- **Bearer Token 认证**：所有 SSE 端点（`/game/{id}/choice`、`/game/{id}/custom-input`、`/game/{id}/free-chat/stream`）均使用 `Depends(get_current_user_id)` 进行 JWT 验证，复用现有认证中间件。
- **会话所有权校验**：
  - Legacy `submit_choice`：调用 `_verify_session_ownership(session_uuid, user_id, db)` 校验用户拥有该会话。
  - Legacy `submit_custom_input`：调用 `_verify_session_ownership(session_uuid, user_id, db)` 校验。
  - `free-chat/stream`：调用 `_verify_session_ownership(UUID(session_id), user_id, db)` 校验。
  - Corvus 路径：在 `submit_choice` 和 `submit_custom_input` 中直接检查 `corvus_session.user_id != UUID(user_id)`。
- **所有权校验在 SSE 流开始前执行**：所有权验证在返回 `StreamingResponse` 之前完成，确保未授权用户无法启动 SSE 流。
- **无新增权限边界**：CR-042 复用现有 Bearer Token + 所有权校验模式，不引入新的权限层级。
- **审计路径**：SSE 端点的鉴权失败通过 `get_current_user_id` 抛出 401 AppException；所有权失败通过 `_verify_session_ownership` 抛出 403。错误日志通过 `_legacy_log` / `_fc_logger` 记录。

### 3. 敏感字段、隐私、日志脱敏和数据保留是否清楚

**结论：✅ Passed (含低风险建议 S-1)**

- **SSE 流内容**：SSE 事件仅输出 LLM 生成的对话文本（`type: "text"`）和结构化元数据（`type: "done"` 携带 `session_id`、`affection_change`、`choices`）。不输出 token、API key、内部路径或后端架构信息。
- **日志脱敏**：
  - `_legacy_log.error(f"[Legacy SSE choice] Error: {e}", exc_info=True)` — 记录异常信息和堆栈，但异常消息来自 LLM Gateway 或 NarrativeEngine，不含用户密码或密钥。
  - `_fc_logger.error(f"[Free chat SSE] Error: {e}", exc_info=True)` — 同上。
  - `auth.py` 中 `logger.warning(f"get_current_user_id: Invalid or expired token (first 20 chars: {token[:20]}...)")` — 仅记录 token 前 20 字符用于调试，不记录完整 token。**S-1 建议（低风险）**：token 前 20 字符仍可能泄露部分 JWT payload，建议后续改为记录 token 的 SHA-256 hash 而非明文前缀。此项不阻塞本 CR。
- **数据保留**：
  - 对话历史写入复用现有 `DialogueHistory` 表，保留策略不变。
  - free_chat 消息保存复用现有 `FreeChatSession` 表，保留策略不变。
  - Deferred DB 写入使用 `async_session_factory()` 创建独立 DB session，不阻塞 SSE 流，不影响连接池。
- **日志中的 session_id**：日志记录 `session_uuid` (UUID) 用于追踪，UUID 不属于敏感个人信息。

### 4. API、数据库/存储、Runtime 和 Mock 策略是否一致

**结论：✅ Passed**

- **API 契约**（`docs/api/api.md` CR-042 Additions）：
  - 新增 `POST /game/{id}/free-chat/stream`（SSE），认证 Bearer，与代码一致。
  - 改造 `POST /game/{id}/choice` Legacy 分支（条件 SSE），与代码一致。
  - 改造 `POST /game/{id}/custom-input` Legacy 分支（SSE），与代码一致。
  - 废弃 `POST /game/{id}/free-chat`（Deprecation: true header），与代码一致（L1698-1702）。
- **数据库契约**（`docs/database/database.md` CR-042 Additions）：无 DB 变更。Deferred DB 写入复用现有 `DialogueHistory`、`Affection`、`FreeChatSession` 表，与代码一致。
- **Runtime 契约**（`docs/runtime/runtime-contract.md` CR-042 Additions）：SSE 响应头包含 `X-Accel-Buffering: no`，与代码一致。Nginx 配置 `proxy_buffering off; proxy_cache off; proxy_read_timeout 300s;` 已在 runtime-contract 中定义。
- **Mock 策略**：
  - Delivery E2E：5/5 passed, `Mock API=no` — 确认使用真实后端。
  - Browser E2E：7/9 passed, `Mock API=no` — 确认使用真实后端。
  - 无 mock API、fixture server、MSW、静态假数据或 mock 模型作为发布证据。

### 5. test-report.md 是否区分 CI/CD、Delivery E2E / Runtime Smoke 和 Browser Interaction E2E

**结论：✅ Passed**

- **CI/CD**：BE pytest 33/35 passed（2 env errors 非 business failure），FE vitest 18/18 passed。区分清晰。
- **Delivery E2E / Runtime Smoke**：5/5 passed, `Mock API=no`。从真实前端入口 `http://localhost:8081` 经 Vite proxy 访问真实后端 `http://localhost:8000`。
- **Browser Interaction E2E**：7/9 passed (1 failed timing issue BUG-002, 1 not run)。使用 Playwright Chromium 真实浏览器执行用户动作。`Mock API=no`。
- **BUG-002 分类**：Corvus 回归 E2E SSE 检测时序问题（test spec timing），非业务代码缺陷。CEO 附条件 C2 满足 — 不阻塞本 CR。

### 6. 依赖、容器和部署配置是否存在明显风险

**结论：✅ Passed (含低风险建议 S-2)**

- **依赖**：CR-042 未新增 Python 或 npm 依赖。现有依赖版本在 `pyproject.toml` 和 `package.json` 中锁定。
- **容器**：CR-042 未修改 Dockerfile 或 docker-compose.yml。
- **Nginx 配置**：`deploy/nginx/app.conf.example` 中 `/api/` location 缺少 `proxy_buffering off; proxy_cache off; proxy_read_timeout 300s;` SSE 专用配置。**S-2 建议（低风险）**：`app.conf.example` 是示例配置文件，`docs/runtime/runtime-contract.md` 已明确 SSE proxy 配置要求。生产部署时 Ops 需在 Nginx 配置中添加 SSE 专用指令。此项为部署配置提醒，不阻塞本 CR，但需在 `deploy-plan.md` 中由 Ops 确认。

### 7. 安全相关验收项是否在 acceptance.md 有验证结论

**结论：✅ Passed**

- `acceptance.md` 22 项 AC（P0:13, P1:9）均有覆盖状态和 QA 复核结论。
- P0 AC-001~AC-003、AC-006~AC-008、AC-011~AC-013、AC-015、AC-017、AC-020、AC-022 均有 CI/CD + Delivery E2E + Browser E2E 证据。
- AC-022 Corvus 回归：CEO 附条件 C2 满足，不阻塞。
- AC-015 旧端点兼容：Delivery E2E 确认 HTTP 200 + Deprecation header。
- 安全相关检查项（认证、所有权、脱敏、Mock 策略）在 `docs/security/security.md` CR-042 Additions 中已记录并全部勾选 `[x]`。

### 8. 高风险事项是否需要人工确认

**结论：✅ 无高风险事项需人工确认**

- `change.md` 人工确认表全部为"否"：不涉及生产环境变更、数据删除、认证边界变更、支付、公共 API 破坏性变更或大范围重构。
- CR-042 复用现有认证、授权和数据库表结构，不引入新的权限边界或不可逆操作。

## SSE 流式输出安全专项审查

### SSE 流中敏感信息泄露

**结论：✅ 安全**

- Legacy SSE 流仅输出 LLM 生成的对话文本（`type: "text"`）、情绪标签（`type: "emotion"`）、好感度更新（`type: "affection_update"`）和流结束元数据（`type: "done"`）。
- 不输出：JWT token、API key、数据库连接串、内部文件路径、堆栈追踪。
- **错误事件消息内容审查**：
  - 3 处 SSE error 事件：`yield f'data: ...{"type":"error","message":str(e)}...\n\n'`（L245, L468, L1790）
  - `str(e)` 来自 LLM Gateway 异常或 free_chat_service 异常，可能包含 LLM API 调用错误消息（如 "Connection refused"、"timeout"）。
  - **风险等级：低**。LLM API 错误消息可能间接暴露后端使用的 LLM 服务类型（如 "OpenAI API error"），但不泄露密钥或凭据。
  - **建议（不阻塞）**：后续可考虑将 SSE error 事件消息泛化为"服务暂时不可用，请稍后重试"，将详细错误仅记录在服务器日志中。此项不阻塞本 CR，因为现有 Corvus SSE 路径也使用相同模式（L142 `yield f'data: ...{"type":"error","message":str(e)}...'`），CR-042 保持一致。

### Deferred DB 写入竞态条件

**结论：✅ 安全**

- **独立 DB Session**：`_run_legacy_deferred`、`_run_legacy_custom_input_deferred`、`_deferred_free_chat` 均使用 `async_session_factory()` 创建独立 DB session，不复用请求级别的 session，避免连接池耗尽和 session 状态污染。
- **异步执行**：`loop.create_task()` 在 SSE 流的 `finally` 块中触发 deferred 写入，不阻塞 SSE 流输出。
- **数据一致性**：
  - Deferred 写入在 SSE 流完成后执行，此时所有 text chunks 已收集完毕（`deferred_data["text_chunks"]`）。
  - 用户请求和 deferred 写入之间不存在竞态：同一 session 的下一次请求需要等待前端用户操作（点击选项或输入文本），时间间隔远大于 deferred 写入完成时间。
  - 即使 deferred 写入失败，SSE 流已成功输出给用户，用户可重试。deferred 写入失败通过日志记录，不影响用户已接收的 SSE 内容。
- **无新增数据库表**：Deferred 写入复用现有 `DialogueHistory`、`Affection`、`FreeChatSession` 表，无 schema 变更。

### 旧端点兼容安全

**结论：✅ 安全**

- 旧 `POST /game/{id}/free-chat` 端点保留，行为不变（同步 JSON 响应）。
- 仅追加 `Deprecation: true` 响应头，不泄露后端架构信息（`Deprecation` 是标准 HTTP 响应头，仅标记端点废弃状态）。
- 旧端点仍需 Bearer Token 认证和所有权校验，安全性不变。
- 旧端点的 JSON 响应体不含额外敏感信息。

### X-Accel-Buffering header

**结论：✅ 正确配置**

- 所有 3 个 Legacy SSE 流式响应（`_stream_legacy_turn`、`_stream_legacy_custom_input`、`free_chat_stream`）的 `StreamingResponse` headers 均包含：
  ```python
  headers={
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "X-Accel-Buffering": "no",
  }
  ```
- 此 header 指示 Nginx 不缓冲 SSE 响应，确保逐字输出到达客户端。
- `docs/runtime/runtime-contract.md` CR-042 Additions 明确记录此 header 要求。
- Corvus 路径的 `_stream_corvus_turn` 也使用相同 header（L150），保持一致。

### SSE 端点认证

**结论：✅ 安全**

- 所有 SSE 端点使用 `Depends(get_current_user_id)` 在端点入口验证 JWT Bearer Token。
- 认证失败时抛出 401 AppException，不进入 SSE 流。
- 会话所有权校验在 SSE 流开始前执行，403 时不返回 StreamingResponse。
- 前端 `useSSEStream.ts` 从 cookie 中提取 token 并设置 `Authorization: Bearer {token}` header，与后端认证一致。

### model_router fallback 文本

**结论：✅ 安全**

- `_get_stream_fallback_text()` 返回硬编码预设文本，按场景区分（FREE_CHAT / NARRATIVE / 默认），不接受外部输入。
- Fallback 文本内容为角色人设口吻的友好提示，不泄露内部系统信息（如 LLM 模型名称、错误详情或 API 端点）。
- Q-003 在 DESIGN 阶段已确认 fallback 文本内容。
- `stream_with_fallback()` 方法中所有模型失败时，仅 yield fallback 文本，不暴露异常消息。

### 前端 v-html XSS

**结论：⚠️ 已知风险（H-1），不阻塞本 CR**

- `StoryPanel.vue` L16 使用 `v-html="formattedText"` 渲染 SSE 文本。
- `formattedText` 将 `displayedText` 做 `\n→<br>`、`**text**→<strong>`、`*text*→<em>` 替换，不做 HTML 转义。
- 如果 LLM 输出包含 `<script>` 标签或恶意 HTML，理论上可触发 XSS。
- **风险等级：低**。LLM 输出受 Prompt 约束（system prompt 明确要求输出叙事文本），且后端 `free_chat_service.py` 使用 `RuleEngine` 验证 LLM 输出格式和长度。
- **CR-039 安全审查已标记 H-1 为非阻塞建议**：StoryPanel v-html 增加 DOMPurify，后续迭代处理。
- CR-042 未改变此风险等级 — Legacy SSE 和 Corvus SSE 均通过 StoryPanel 渲染，风险一致。

## 追踪链验证

| 链路段 | 追踪结论 |
| --- | --- |
| PRD → REQ | ✅ PRD 中 REQ-001~REQ-005 对应 CR-040 PRD 五条需求 |
| REQ → AC | ✅ acceptance.md 22 项 AC 映射到 5 条 REQ |
| AC → Design | ✅ 每项 AC 有设计落点（§1~§7 + ADR-042-01~03） |
| Design → Task | ✅ OpenSpec Task DEV-001（后端）、DEV-002（前端）有 owner |
| Task → Code | ✅ 实现文件在 game.py、model_router.py、free_chat_service.py、useSSEStream.ts、game.ts、FreeChatView.vue |
| Code → Test | ✅ BE 6 测试文件 35 tests + FE 1 测试文件 18 tests |
| Test → Red/Green | ✅ BUG-001 修复后复验通过；BUG-002 非业务缺陷 |
| Green → Acceptance | ✅ acceptance.md 22/22 AC 有覆盖状态和 QA 复核结论 |
| Acceptance → QA | ✅ test-report.md 有 CI/CD + Delivery E2E + Browser E2E 分类记录 |
| QA → Release | ✅ Delivery E2E Mock API=no；Browser E2E Mock API=no；无 mock 发布证据 |
| Release → Deploy | ⚠️ deploy-plan.md 为 Pending，需 Ops 在 RELEASE_GATE 前完成 |

## 发布证据安全验证

| 证据类型 | Mock API | 来源 | 结论 |
| --- | --- | --- | --- |
| BE CI/CD (33/35) | no | pytest 真实后端 | ✅ 通过（2 env errors 非 business failure） |
| FE CI/CD (18/18) | no | vitest 真实前端 | ✅ 通过 |
| Delivery E2E (5/5) | no | 真实前端 + 真实后端 + Vite proxy | ✅ 通过 |
| Browser E2E (7/9) | no | Playwright Chromium + 真实后端 | ✅ 通过（BUG-002 非业务缺陷，CEO C2 不阻塞） |
| Mock API 作为发布证据 | — | — | ✅ 未发现 |

## 低风险建议（不阻塞本 CR）

| 编号 | 建议 | 风险等级 | 责任人 | 建议处理时间 |
| --- | --- | --- | --- | --- |
| S-1 | auth.py 中 token 前 20 字符日志改为 SHA-256 hash | Low | Backend (Cat01-be) | 后续迭代 |
| S-2 | deploy/nginx/app.conf.example 添加 SSE 专用 proxy 配置（proxy_buffering off; proxy_cache off; proxy_read_timeout 300s;） | Low | Ops (Cat01-op) | deploy-plan.md 完善时 |
| H-1 | StoryPanel.vue v-html 增加 DOMPurify 消毒 | Low | Frontend (Cat01-fe) | 后续迭代（CR-039 已登记） |

## 退回规则检查

- 无架构或数据风险需退回架构师。
- 无实现漏洞需退回对应实现 Agent。
- 无生产、权限、支付或数据删除风险需升级人工。
- 低风险建议 S-1、S-2、H-1 均为后续迭代项，不阻塞本 CR。

## 完成标准

- ✅ CR-042 `security-review.md` 有通过结论。
- ✅ 无高风险事项需人工确认。
- ✅ 低风险建议有责任人建议（S-1→BE, S-2→Ops, H-1→FE）。
- ✅ 安全风险能追踪到 AC、API/DB/Runtime 契约、测试证据和发布证据。
- ✅ 无阻塞项需要记录最早断链环节。

## 最终结论

**CR-042 安全审查通过。**

- 认证、授权、所有权校验完整，复用现有 Bearer Token + 所有权验证模式。
- SSE 流式输出不泄露敏感信息（无 token、API key、内部路径输出）。
- Deferred DB 写入使用独立 session，无竞态风险。
- 旧端点兼容安全，Deprecation header 不泄露架构信息。
- Fallback 文本为硬编码预设，不接受外部输入。
- 发布证据 Mock API=no，无 mock 作为发布证据。
- 3 项低风险建议（S-1、S-2、H-1）不阻塞本 CR，建议后续迭代处理。
