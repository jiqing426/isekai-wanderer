# Design

## Overview

- CR-042 将 Legacy 引擎的三条非流式路径改为 SSE 流式输出，复用已有 Corvus SSE 基础设施（`_stream_corvus_turn` 模式、`StreamingResponse` + async generator、`_run_deferred` 异步 DB 写入）
- 后端改造范围：`submit_choice` Legacy 分支条件 SSE（transition/ai_dialog → SSE, preset/choice → JSON）、`submit_custom_input` Legacy 分支 SSE、新增 `free-chat/stream` 端点、`model_router.stream_with_fallback()` 降级方法
- 前端改造范围：提取 `useSSEStream()` composable 复用于三条 Legacy 路径 + Corvus 回归迁移
- 无新增技术选型、无 DB 变更、无新增依赖、无新增端口/proxy 变更

## Technical Approach

- 复用 Corvus SSE 基础设施（`StreamingResponse` + async generator + `_run_deferred` 模式），在 `game.py` 端点层新建 SSE 组装函数
- `model_router` 新增 `stream_with_fallback()` 方法，支持流式 + 自动降级
- 前端提取 `useSSEStream()` composable 封装 fetch + ReadableStream reader + SSE 事件解析

### 1. SSE 事件格式（复用 Corvus 已有模式）

所有 Legacy SSE 流式端点统一使用与 Corvus 路径一致的事件格式：

```
data: {"type":"text","content":"..."}\n\n          ← 逐字/逐 token 推送
data: {"type":"emotion","emotion":"happy","character_id":"..."}\n\n  ← 情绪标签（可选，在 text 之前）
data: {"type":"affection_update","character_id":"...","value":45,"level":"trust"}\n\n  ← 好感度更新（可选）
data: {"type":"done","session_id":"...","node_id":"...","affection_change":{...}}\n\n  ← 流结束 + 元数据
data: {"type":"error","message":"..."}\n\n           ← 错误事件
```

**关键决策**：Legacy 路径不使用 `gm_update` 事件（那是 Corvus 特有的 GM 循环输出）。Legacy 路径的元数据（好感度变化、下一节点选项）通过 `done` 事件一次性推送，因为 Legacy 引擎的元数据在 `process_choice` / `process_custom_input` 返回值中已有结构化字段，不需要像 Corvus 那样从 GM 输出流中解析。

### 2. 后端端点设计

#### 2.1 `POST /game/{session_id}/choice` — Legacy 分支 SSE 改造

**触发条件**：当 `submit_choice` 走到 Legacy 分支（非 Corvus），先执行 `process_choice()` 推进节点，然后检查 `next_node.node_type`：
- `preset` / `choice` → 保持 JSON 响应（AC-002）
- `transition` / `ai_dialog` → 返回 SSE 流式响应（AC-001, AC-003）

**端点行为**：

```python
# game.py submit_choice() Legacy 分支改造

# 1. 现有逻辑：process_choice() 推进节点、扣 quota、存对话历史
result = await engine.process_choice(...)

# 2. 新增：判断下一节点类型
next_node = await _get_node(result["next_node_id"])
if next_node.node_type in ("preset", "choice"):
    # 保持 JSON 响应
    return result  # 现有行为不变

# 3. transition/ai_dialog 节点 → SSE 流式
if next_node.node_type in ("transition", "ai_dialog"):
    return _stream_legacy_turn(session_uuid, user_uuid, result, next_node, db)
```

**`_stream_legacy_turn()` 函数**：

```python
def _stream_legacy_turn(
    session_uuid: UUID,
    user_uuid: UUID,
    choice_result: dict,
    next_node: Node,
    db: AsyncSession,
) -> StreamingResponse:
    """Stream a Legacy engine turn via SSE for transition/ai_dialog nodes."""
    
    deferred_data = {
        "session_id": session_uuid,
        "user_id": user_uuid,
        "choice_result": choice_result,
        "next_node": next_node,
        "char_id": None,
        "char_name": None,
    }

    async def event_generator():
        try:
            # 获取角色信息
            character = await _get_node_character(next_node, db)
            if character:
                deferred_data["char_id"] = character.id
                deferred_data["char_name"] = character.name
                # 推送情绪
                yield f'data: {json.dumps({"type":"emotion","emotion":"neutral","character_id":str(character.id)})}\n\n'

            # 使用 llm_gateway.stream_dialogue() 或 narrative_engine 流式生成
            if next_node.node_type == "transition" and character:
                # transition 节点：使用 llm_gateway.stream_dialogue()
                async for chunk in llm_gateway.stream_dialogue(
                    character_name=character.name,
                    character_personality=character.personality or "",
                    context=next_node.content.get("context", ""),
                    user_input=choice_result.get("choice_text", ""),
                    conversation_history=[],  # 从 DialogueHistory 查询
                ):
                    yield f'data: {json.dumps({"type":"text","content":chunk})}\n\n'

            elif next_node.node_type == "ai_dialog" and character:
                # ai_dialog 节点：同样使用 stream_dialogue()
                async for chunk in llm_gateway.stream_dialogue(
                    character_name=character.name,
                    character_personality=character.personality or "",
                    context=next_node.content.get("context", ""),
                    user_input=choice_result.get("choice_text", ""),
                    conversation_history=[],
                ):
                    yield f'data: {json.dumps({"type":"text","content":chunk})}\n\n'

            # done 事件：推送元数据
            done_payload = {
                "type": "done",
                "session_id": str(session_uuid),
                "node_id": str(next_node.id),
            }
            # 合入好感度变化
            if choice_result.get("affection_change"):
                done_payload["affection_change"] = choice_result["affection_change"]
            # 合入下一节点选项
            if next_node.choices:
                done_payload["choices"] = _format_choices(next_node.choices)

            yield f'data: {json.dumps(done_payload, default=str)}\n\n'

        except Exception as e:
            import logging
            logging.error(f"[Legacy SSE] Error: {e}", exc_info=True)
            yield f'data: {json.dumps({"type":"error","message":str(e)})}\n\n'
        finally:
            # 异步 DB 写入（deferred）
            import asyncio
            loop = asyncio.get_event_loop()
            loop.create_task(_run_legacy_deferred(deferred_data))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

**DB 写入时序**：SSE 流期间不执行 `db.commit()`；流结束后在 `finally` 块中通过 `asyncio.create_task(_run_legacy_deferred(deferred_data))` 异步执行：
- 对话历史写入 `DialogueHistory`
- 好感度变化写入 `Affection` 表
- 成就检查和写入
- 收敛检查
- `db.commit()` 在 deferred task 中执行

**前端不再发 `fetchDialogue()`**：`done` 事件中携带 `node_id` 和 `choices`，前端直接更新状态，不需要二次请求（AC-005）。

#### 2.2 `POST /game/{session_id}/custom-input` — Legacy 分支 SSE 改造

**触发条件**：当 `submit_custom_input` 走到 Legacy 分支（非 Corvus），改为 SSE 流式响应。

**端点行为**：

```python
# game.py submit_custom_input() Legacy 分支改造

# 1. 现有逻辑：quota 检查、角色获取
# 2. 改为：使用 llm_gateway.stream_dialogue() 流式生成角色回应
#    不再调用 _generate_custom_response() 同步方法

# 3. 返回 SSE
return _stream_legacy_custom_input(session_uuid, user_uuid, user_text, node, character, db)
```

**`_stream_legacy_custom_input()` 函数**：

```python
def _stream_legacy_custom_input(
    session_uuid: UUID,
    user_uuid: UUID,
    user_text: str,
    node: Node,
    character: Optional[Character],
    db: AsyncSession,
) -> StreamingResponse:
    """Stream Legacy custom input response via SSE."""

    deferred_data = {
        "session_id": session_uuid,
        "user_id": user_uuid,
        "user_text": user_text,
        "node": node,
        "character": character,
    }

    async def event_generator():
        try:
            if character:
                # 推送情绪
                yield f'data: {json.dumps({"type":"emotion","emotion":"neutral","character_id":str(character.id)})}\n\n'

                # 使用 llm_gateway.stream_dialogue() 替代 _generate_custom_response()
                async for chunk in llm_gateway.stream_dialogue(
                    character_name=character.name,
                    character_personality=character.personality or "",
                    context=node.content.get("context", ""),
                    user_input=user_text,
                    conversation_history=[],  # 从 DialogueHistory 查询
                ):
                    yield f'data: {json.dumps({"type":"text","content":chunk})}\n\n'

                # done 事件：推送好感度和下一选项
                done_payload = {
                    "type": "done",
                    "session_id": str(session_uuid),
                    "node_id": str(node.id),
                }
                # 推进节点逻辑（原 process_custom_input 中的 advance_session）
                # 在 deferred 中执行，done 事件携带结果
                yield f'data: {json.dumps(done_payload, default=str)}\n\n'
            else:
                # 无角色 → 旁白回应（流式）
                async for chunk in llm_gateway.provider.stream_complete(
                    [LLMMessage(role="system", content="..."),
                     LLMMessage(role="user", content=user_text)],
                    temperature=0.7, max_tokens=500
                ):
                    yield f'data: {json.dumps({"type":"text","content":chunk})}\n\n'

                yield f'data: {json.dumps({"type":"done","session_id":str(session_uuid),"node_id":str(node.id)})}\n\n'

        except Exception as e:
            yield f'data: {json.dumps({"type":"error","message":str(e)})}\n\n'
        finally:
            import asyncio
            loop = asyncio.get_event_loop()
            loop.create_task(_run_legacy_custom_input_deferred(deferred_data))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
```

#### 2.3 `POST /game/{session_id}/free-chat/stream` — 新增端点

**端点签名**：

```python
@router.post("/game/{session_id}/free-chat/stream")
async def free_chat_stream(
    session_id: str,
    request: FreeChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Stream free chat response via SSE.

    New endpoint for CR-042 REQ-003.
    Old POST /game/{session_id}/free-chat remains for backward compatibility (deprecated).
    """
```

**行为**：调用 `free_chat_service.send_message_stream()` 获取 async generator，逐 token 包装为 SSE `text` 事件推送。流结束后在 `done` 事件中推送好感度变化。DB 写入（对话保存、记忆提取）在 deferred task 中执行。

**旧端点保留**：`POST /game/{session_id}/free-chat` 不删除、不修改行为，在响应头中追加 `Deprecation: true` + `Sunset: delta`（RFC 8594 informal）标记。

#### 2.4 `model_router.stream_with_fallback()` — 新增方法

```python
class ModelRouter:
    async def stream_with_fallback(
        self,
        scenario: ScenarioType,
        messages: List[dict],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream with automatic fallback model switching.

        Tries primary model's stream() first. On failure (timeout, connection error),
        switches to next model in fallback chain. If all models fail, yields a
        fallback text as a single chunk (non-streaming fallback).

        Yields:
            str: Text tokens from the LLM.
        """
        chain = self.get_fallback_chain(scenario)
        import logging
        log = logging.getLogger(__name__)

        for i, model in enumerate(chain):
            try:
                # Get the provider and call its stream method
                from app.services.llm.gateway import llm_gateway
                provider = llm_gateway.provider

                # Build messages for stream_complete
                from app.services.llm.gateway import LLMMessage
                llm_messages = [
                    LLMMessage(role=m["role"], content=m["content"])
                    for m in messages
                ]

                async for chunk in provider.stream_complete(
                    llm_messages,
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", 500),
                ):
                    yield chunk
                return  # Success, no fallback needed

            except Exception as e:
                log.warning(
                    f"Model {model.name} stream failed (chain pos {i}): {e}, "
                    f"trying fallback..."
                )
                continue

        # All models failed — yield fallback text (Q-003 confirmation)
        fallback_text = self._get_stream_fallback_text(scenario)
        yield fallback_text

    def _get_stream_fallback_text(self, scenario: ScenarioType) -> str:
        """Get fallback text when all models fail (Q-003)."""
        fallback_texts = {
            ScenarioType.FREE_CHAT: "（微微侧头，轻轻笑了笑）抱歉，我刚才走神了……你说的真有意思，能再和我说说吗？",
            ScenarioType.NARRATIVE: "（故事在这一刻仿佛停滞了片刻，随后又缓缓流淌……）",
            ScenarioType.CHOICE_GENERATION: "选项似乎暂时无法生成，请稍后再试。",
        }
        return fallback_texts.get(scenario, "抱歉，暂时无法回应，请稍后再试。")
```

**降级策略**：
1. 主模型 `stream_complete()` → 逐 token yield
2. 主模型失败（超时/连接错误）→ 切换到 fallback 链下一个模型
3. 所有模型都失败 → 一次性 yield 友好提示文本（AC-019, Q-003 确认）

#### 2.5 `narrative_engine` 流式方法

`narrative_engine.py` 已有 `generate_dialogue_stream()` 方法（SSE 事件生成器），但该方法是一个独立的对话生成流程，不直接用于 `submit_choice` / `submit_custom_input` 的流式改造。本 CR 不修改 `generate_dialogue_stream()`，而是在 `game.py` 端点层新建 `_stream_legacy_turn()` 和 `_stream_legacy_custom_input()` 函数，直接调用 `llm_gateway.stream_dialogue()` 获取流式输出。

**设计决策**：不把流式逻辑放在 `narrative_engine` 内部，而是放在 `game.py` 端点层。原因：
- `process_choice()` 的逻辑（推进节点、好感度、对话历史、成就、收敛）已经足够复杂，将流式输出混入会导致方法职责不清
- Corvus 路径的 `_stream_corvus_turn()` 也是在 `game.py` 端点层组装 SSE 流，保持一致
- `narrative_engine` 继续负责节点推进和状态变更，流式 LLM 调用在端点层处理

#### 2.6 `free_chat_service.send_message_stream()`

```python
class FreeChatService:
    async def send_message_stream(
        self,
        db: AsyncSession,
        user_id: str,
        character_id: str,
        message: str,
        script_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream free chat response using model_router.stream_with_fallback().

        Yields text tokens for SSE wrapping.
        """
        # 1-6: Same as send_message() — get session, character, memories, prompt
        # 7: Use stream_with_fallback instead of call_with_fallback
        async for chunk in model_router.stream_with_fallback(
            scenario=ScenarioType.FREE_CHAT,
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        ):
            yield chunk

        # DB writes happen in the caller's deferred task (not here)
```

### 3. 前端 Composable 设计

#### 3.1 `useSSEStream()` composable 接口

```typescript
// frontend/src/composables/useSSEStream.ts

interface SSEStreamOptions {
  url: string
  method?: 'POST' | 'GET'
  body?: Record<string, any>
  headers?: Record<string, string>
}

interface SSEStreamCallbacks {
  onText: (content: string) => void
  onDone?: (data: any) => void
  onError?: (error: string) => void
  onEmotion?: (data: { emotion: string; character_id?: string }) => void
  onAffectionUpdate?: (data: { character_id: string; value: number; level?: string }) => void
}

interface SSEStreamResult {
  start: () => Promise<void>
  abort: () => void
  isStreaming: Ref<boolean>
}

export function useSSEStream(
  options: SSEStreamOptions,
  callbacks: SSEStreamCallbacks
): SSEStreamResult {
  // Extracts the fetch + ReadableStream reader + SSE event parsing logic
  // that is currently duplicated in submitChoice (Corvus) and submitCustomInput (Corvus)
  // and characterChat.ts sendMessageStream()

  // Cookie-based auth token extraction (same as current)
  // fetch + reader + decode + split('\n') + parse('data: ') + dispatch callbacks
}
```

#### 3.2 三条 Legacy 路径使用 composable

- `submitChoice()` Legacy 分支：检测响应 `Content-Type: text/event-stream` → 使用 `useSSEStream` 解析；否则保持 JSON 处理
- `submitCustomInput()` Legacy 分支：同上
- `FreeChatView.vue`：改用 `useSSEStream` 调用 `/game/{id}/free-chat/stream`

#### 3.3 Corvus 路径迁移 + 回归验证

将 `submitChoice()` 和 `submitCustomInput()` 中 Corvus 分支的 SSE 解析逻辑替换为 `useSSEStream()` 调用。Corvus 路径的 `gm_update` 事件通过 `onGmUpdate` callback 处理（composable 扩展一个 `onGmUpdate` 可选 callback）。

**CEO 附条件 C2**：迁移后必须运行 Corvus 回归 E2E。如果回归失败，Corvus 分支回退到原始 inline SSE 解析逻辑，不影响本 CR 通过。

### 4. DB 写入时序设计

| 阶段 | 操作 | DB 事务 |
|------|------|---------|
| SSE 流前 | quota 扣减、节点推进（`process_choice`） | 在请求 db session 中 commit |
| SSE 流中 | LLM 流式生成，逐 token yield | 不触碰 DB |
| SSE 流后（deferred） | 对话历史写入、好感度更新、成就检查、收敛检查 | 新 db session 中 commit |

**关键约束**：SSE 流期间绝对不执行 `db.commit()`，否则会导致连接池耗尽和流式中断。deferred task 使用 `async_session_factory()` 创建独立 session。

### 5. Q 编号确认

#### Q-001: SSE 流中断错误恢复

**确认结论**：复用 Corvus 路径已有模式。

- SSE 流中发生异常时，yield `{"type":"error","message":"..."}` 事件并关闭流
- 后端记录错误日志（`logging.error`）
- 前端 `onError` callback 设置 `error.value`，显示错误提示
- 不需要自动重试机制（与 Corvus 路径保持一致）
- `finally` 块确保 deferred DB 写入仍然执行（即使流中途出错，已推进的节点状态需要持久化）

#### Q-002: SSE heartbeat/timeout

**确认结论**：复用 Corvus 路径已有模式，不引入 heartbeat。

- 不添加 SSE heartbeat（`:keep-alive` 注释行）
- 依赖 Provider 的 `stream()` 超时设置（Thoushub Provider 使用 OpenAI SDK 默认超时）
- Nginx 已配置 `proxy_read_timeout 300s` + `proxy_buffering off` + `proxy_cache off`
- 如果 Provider 长时间无输出，前端 reader 会在 TCP 超时后报错，走 `onError` 处理

#### Q-003: AC-019 fallback 文本内容

**确认结论**：预设友好提示文本，按场景区分。

```python
fallback_texts = {
    ScenarioType.FREE_CHAT: "（微微侧头，轻轻笑了笑）抱歉，我刚才走神了……你说的真有意思，能再和我说说吗？",
    ScenarioType.NARRATIVE: "（故事在这一刻仿佛停滞了片刻，随后又缓缓流淌……）",
    ScenarioType.CHOICE_GENERATION: "选项似乎暂时无法生成，请稍后再试。",
}
# 默认: "抱歉，暂时无法回应，请稍后再试。"
```

文本设计原则：保持角色人设口吻（第一人称、含动作描述括号），不让用户感觉到是系统错误，而是角色"走神"或"停顿"。

### 6. composable `onGmUpdate` 扩展

Corvus 路径使用 `gm_update` 事件类型推送 GM 循环输出。`useSSEStream()` composable 需要支持此事件类型：

```typescript
interface SSEStreamCallbacks {
  onText: (content: string) => void
  onDone?: (data: any) => void
  onError?: (error: string) => void
  onEmotion?: (data: any) => void
  onAffectionUpdate?: (data: any) => void
  onGmUpdate?: (data: any) => void  // ← Corvus 路径使用
}
```

composable 内部 SSE 事件分发逻辑：
```typescript
if (data.type === 'text') callbacks.onText?.(data.content)
else if (data.type === 'done') callbacks.onDone?.(data)
else if (data.type === 'error') callbacks.onError?.(data.message)
else if (data.type === 'emotion') callbacks.onEmotion?.(data)
else if (data.type === 'affection_update') callbacks.onAffectionUpdate?.(data)
else if (data.type === 'gm_update') callbacks.onGmUpdate?.(data)
```

### 7. 旧端点保留兼容（CEO 附条件 C3）

| 旧端点 | 新端点 | 旧端点行为 |
|--------|--------|------------|
| `POST /game/{id}/free-chat` | `POST /game/{id}/free-chat/stream` | 保留，行为不变，响应头追加 `Deprecation: true` |
| `POST /game/{id}/choice` (Legacy 分支) | 同一端点，条件 SSE | preset/choice 节点保持 JSON；transition/ai_dialog 改为 SSE |
| `POST /game/{id}/custom-input` (Legacy 分支) | 同一端点改为 SSE | 全部改为 SSE（无节点类型判断） |

**注意**：`submit_choice` 和 `submit_custom_input` 旧端点本身不删除，只是 Legacy 分支的响应类型从 JSON 变为 SSE。这是 CEO 附条件 C3 的合规范围——C3 要求的是"旧端点保留兼容（不删除）"，本 CR 不删除任何端点。`free-chat` 旧端点保留同步 JSON 行为，`free-chat/stream` 是新增端点。

## Technology Decisions

| Decision | Selected | Status | Evidence |
| --- | --- | --- | --- |
| 语言 / 框架 | Not Required | Not Required | CR-042 无新增语言/框架选型；后端 Python/FastAPI 已有，前端 Vue 3/TypeScript 已有 |
| 数据库 / 存储 | Not Required | Not Required | CR-042 无 DB 变更；复用现有 PostgreSQL + Redis |
| 缓存 / 队列 | Not Required | Not Required | CR-042 无新增缓存/队列 |
| 云服务 / 部署方式 | Not Required | Not Required | CR-042 无部署方式变更；复用现有 Docker + Nginx |
| 模型供应商 / AI 工具 | Not Required | Not Required | CR-042 无新增模型供应商；复用现有 Thoushub Provider + model_router 降级链 |
| SSE 库选型 | Not Required | Not Required | CR-042 复用 FastAPI `StreamingResponse` + 原生 `fetch` + `ReadableStream` reader，不引入 EventSource 或第三方 SSE 库 |
| composable 模式 | Not Required | Not Required | Vue 3 Composition API `useSSEStream()` 是项目既有模式的扩展，非新选型 |

## Document Sync

| Target Doc | Status | Summary / Evidence |
| --- | --- | --- |
| `docs/architecture/architecture.md` | Synced | 追加 CR-042 Legacy SSE 流式架构：`_stream_legacy_turn()` / `_stream_legacy_custom_input()` 端点层 SSE 组装函数；Legacy submit_choice 条件 SSE 分支（transition/ai_dialog → SSE, preset/choice → JSON）；`model_router.stream_with_fallback()` 降级策略；前端 `useSSEStream()` composable 复用模式 |
| `docs/api/api.md` | Synced | 追加 CR-042 streaming 端点文档：`POST /game/{id}/free-chat/stream` 新增端点签名/SSE 事件格式；`submit_choice` Legacy 分支条件 SSE 行为说明；`submit_custom_input` Legacy 分支 SSE 行为说明；`model_router.stream_with_fallback()` 方法签名 |
| `docs/database/database.md` | Not Required | CR-042 无 DB 表结构变更、无迁移、无新增表。对话历史写入复用现有 `DialogueHistory` 表；好感度更新复用现有 `Affection` 表；free_chat 消息保存复用现有 `FreeChatSession` 表 |
| `docs/security/security.md` | Synced | 追加 CR-042 安全审查：SSE 流式输出无新增鉴权需求（复用现有 Bearer Token）；deferred DB 写入使用独立 session 不阻塞流；fallback 文本不含敏感信息；旧端点 deprecation header 不泄露后端架构 |
| `docs/decisions/decisions.md` | Synced | 追加 CR-042 ADR：ADR-042-01 Legacy SSE 在端点层组装（非 narrative_engine 内部）；ADR-042-02 Legacy done 事件一次性推送元数据（不使用 gm_update）；ADR-042-03 fallback 文本按场景区分设计 |
| `docs/runtime/runtime-contract.md` | Synced | 追加 CR-042 streaming 端点说明：新增 `POST /game/{id}/free-chat/stream` 端点；`submit_choice` / `submit_custom_input` Legacy 分支条件 SSE；SSE 事件格式复用 Corvus 模式；Browser E2E 用户动作追加 |

## Design Decisions (ADRs)

### ADR-042-01: Legacy SSE 在端点层组装

**Status**: Accepted

**Context**: Legacy `submit_choice` 和 `submit_custom_input` 已有 `process_choice()` / `process_custom_input()` 方法处理节点推进、好感度、对话历史、成就和收敛检查。SSE 流式输出需要在这之上增加 LLM 流式调用和 SSE 事件包装。

**Decision**: 在 `game.py` 端点层新建 `_stream_legacy_turn()` 和 `_stream_legacy_custom_input()` 函数，调用 `llm_gateway.stream_dialogue()` 获取流式输出并包装为 SSE 事件。不修改 `narrative_engine` 内部方法。

**Alternatives**:
| Dimension | 端点层组装 (Selected) | narrative_engine 内部 |
|-----------|----------------------|----------------------|
| 职责清晰 | ✅ narrative_engine 负责状态，game.py 负责传输 | ❌ 混合状态和传输 |
| 一致性 | ✅ 与 Corvus `_stream_corvus_turn()` 模式一致 | ❌ 引入新模式 |
| 改动范围 | ✅ 只改 game.py + 新增函数 | ❌ 需改 narrative_engine 多个方法 |
| 测试 | ✅ 端点测试覆盖 | ❌ 需要引擎层 + 端点层双重测试 |

**Rationale**: 与 Corvus 路径的 `_stream_corvus_turn()` 保持架构一致；`narrative_engine` 继续专注节点推进和状态变更；流式传输是端点层关注点。

### ADR-042-02: Legacy done 事件一次性推送元数据

**Status**: Accepted

**Context**: Corvus 路径使用 `gm_update` 事件从 GM 输出流中解析元数据。Legacy 路径的 `process_choice()` 返回值中已有结构化的 `affection_change`、`choices` 等字段。

**Decision**: Legacy SSE 流在 `done` 事件中一次性推送所有元数据（好感度变化、下一节点选项），不使用 `gm_update` 事件。

**Rationale**: Legacy 路径的元数据来源是结构化的（DB 查询 + affection_service），不需要从 LLM 输出流中解析。`done` 事件一次性推送更简洁、更可靠。

### ADR-042-03: fallback 文本按场景区分设计

**Status**: Accepted

**Context**: Q-003 暂缓到 DESIGN 阶段确认 AC-019 fallback 文本内容。所有 fallback 模型均失败时需要返回友好提示文本。

**Decision**: 按场景类型预设不同 fallback 文本，保持角色人设口吻（第一人称、含动作描述括号），不让用户感觉是系统错误。

**Rationale**: 不同场景（自由对话 vs 叙事生成 vs 选项生成）的 fallback 文本应该匹配上下文；使用角色口吻比 "系统错误" 更友好。

## AC → Design → Task 追踪矩阵

| AC | 设计落点 | Task |
|----|---------|------|
| AC-001 | §2.1 `submit_choice` Legacy 分支条件 SSE：transition 节点 → `_stream_legacy_turn()` | DEV-001 |
| AC-002 | §2.1 `submit_choice` Legacy 分支：preset/choice 节点 → 保持 JSON 响应 | DEV-001 |
| AC-003 | §1 SSE 事件格式：`text` + `done` 事件与 Corvus 一致 | DEV-001 |
| AC-004 | §4 DB 写入时序：deferred task 异步写入好感度；done 事件推送 affection_change | DEV-001 |
| AC-005 | §2.1 `done` 事件携带 `node_id` + `choices`，前端不需要 `fetchDialogue()` | DEV-002 |
| AC-006 | §2.2 `submit_custom_input` Legacy 分支 SSE 改造 | DEV-001 |
| AC-007 | §2.2 使用 `llm_gateway.stream_dialogue()` 替代 `_generate_custom_response()` | DEV-001 |
| AC-008 | §2.2 SSE 逐字输出角色回应 | DEV-001 |
| AC-009 | §2.2 `done` 事件推送好感度变化和下一节点选项 | DEV-001 |
| AC-010 | §3.2 前端 Legacy 分支使用 `useSSEStream()` composable 解析 | DEV-002 |
| AC-011 | §2.3 `POST /game/{id}/free-chat/stream` 新增端点，返回 `text/event-stream` + `X-Accel-Buffering: no` | DEV-001 |
| AC-012 | §2.4 `model_router.stream_with_fallback()` 方法签名 `AsyncGenerator[str, None]` | DEV-001 |
| AC-013 | §2.3 + §2.6 `free_chat_service.send_message_stream()` 使用 `stream_with_fallback()` 逐字输出 | DEV-001 |
| AC-014 | §2.3 `done` 事件推送好感度变化；deferred DB 写入 | DEV-001 |
| AC-015 | §7 旧 `POST /game/{id}/free-chat` 保留兼容，追加 `Deprecation: true` 响应头 | DEV-001 |
| AC-016 | §3.2 `FreeChatView.vue` 改用 `useSSEStream()` 调用流式端点 | DEV-002 |
| AC-017 | §2.4 `stream_with_fallback()` 返回 `AsyncGenerator[str, None]`，逐 token yield | DEV-001 |
| AC-018 | §2.4 主模型流式失败 → 自动切换 fallback 链下一个模型 | DEV-001 |
| AC-019 | §2.4 + §5 Q-003 所有 fallback 失败 → 一次性 yield 场景特定友好提示文本 | DEV-001 |
| AC-020 | §3.1 `useSSEStream()` composable 提取，封装 fetch + reader + SSE 解析 | DEV-002 |
| AC-021 | §3.2 三条 Legacy 路径使用 composable | DEV-002 |
| AC-022 | §3.3 Corvus 分支迁移到 composable + 回归验证（CEO 附条件 C2） | DEV-002 |
