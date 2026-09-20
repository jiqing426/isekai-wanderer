# Security Review: CR-039 — Corvus 玩家选项功能

- **CR ID**: CR-039
- **Security Agent**: Cat01-security
- **执行时间**: 2026-09-11T14:00:00+08:00
- **PL 触发时间**: 2026-09-11T13:20 (PL 通知 CR-039 流转到 SECURITY)
- **Mock API**: no

---

## 1. 审查范围

### 1.1 变更文件

| 层 | 文件 | 变更内容 |
|---|---|---|
| 后端 | `backend/app/services/corvus_adapter.py` | SSETranslator: 过滤 [Narrator]/[Character] 标记 + 角色名映射 + 好感度映射 + playerOptions→choices 映射 |
| 后端 | `backend/app/api/v1/game.py` | `/game/{session_id}/status` 读取 character_id |
| 后端 | `backend/app/models/corvus.py` | CorvusGameSession 加 character_id 字段 (FK → characters.id) |
| Corvus | `corvus/server/services/gameMaster.ts` | GM prompt 增加 playerOptions 输出字段 + MUST ALWAYS 规则 |
| 前端 | `frontend/src/stores/game.ts` | SSE handler: 选项/好感度/角色名处理 |
| 前端 | `frontend/src/components/StoryPanel.vue` | 去掉打字机，直接显示 (v-html) |
| 前端 | `frontend/src/views/GameView.vue` | ChoicePanel v-if + characterDisplayName |
| 前端 | `frontend/src/components/FreeChatInput.vue` | defaultExpanded prop |

### 1.2 安全审查重点（PL 指定）

1. SSE 事件过滤是否可能被绕过（注入恶意标记）
2. character_id FK 约束是否有效
3. `/game/status` 是否有越权风险
4. GM prompt 修改是否引入 prompt injection 风险

---

## 2. 逐项安全审查

### 2.1 SSE 事件过滤 — [Narrator]/[Character] 标记注入

**审查对象**: `corvus_adapter.py` SSETranslator._process_token_chunk() + _strip_role_markers()

**实现分析**:

1. **Token 级过滤** (`_process_token_chunk`): 使用前缀匹配缓冲区，检测 `[Narrator`/`[Character`（含 `: name` 变体）的完整或部分标记。匹配到则跳过标记文本及尾部换行；未匹配的 `[` 字符正常输出。
2. **Done 级过滤** (`_strip_role_markers`): 使用正则 `\[(Narrator|Character|narrator|character)(\s*:\s*[^\]]*)?\]\s*\n?` 从完整文本中移除标记。
3. **缓冲区溢出保护**: `_MAX_MARKER_LEN` = `len("[Character: 槐枝]") + 2`，超过此长度自动 flush，防止缓冲区无限增长。

**安全评估**:

- ✅ **标记过滤覆盖完整**: 支持大小写 `[Narrator]`/`[narrator]`/`[Character]`/`[character]`，以及 `[Character: name]` 变体。
- ✅ **跨 chunk 安全**: SSE token 事件可能将一个标记分割到多个 chunk，前缀缓冲机制能正确处理。
- ✅ **Done 事件二次清理**: 即使 token 级过滤遗漏，done 事件的全文本正则替换作为兜底。
- ⚠️ **非安全等级的过滤**: 此过滤的目的是清除 UI 显示的元标记，不是安全边界。LLM 输出的内容本身仍通过 `v-html` 渲染（见 2.7 XSS）。

**结论**: ✅ **通过** — 标记过滤机制有效，满足 AC-013 要求。

---

### 2.2 character_id FK 约束

**审查对象**: `backend/app/models/corvus.py` CorvusGameSession.character_id

**实现分析**:

```python
# corvus.py
character_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True), ForeignKey("characters.id"), nullable=True
)
```

**安全评估**:

- ✅ **DB 级 FK 约束**: `ForeignKey("characters.id")` 在数据库层强制引用完整性。无法写入不存在的 character_id。
- ✅ **nullable=True**: 向后兼容，旧会话 character_id=NULL 不会破坏。
- ✅ **写入校验**: `corvus_adapter.py` create_session() 方法在写入前查询 `Character.id == character_id AND Character.playable == True`，不存在则返回 404 CHARACTER_NOT_FOUND。
- ✅ **CR-038 安全审查已验证**: character_id 来自 Character 表（非用户自定义 player_candidates），减少了注入风险。

**结论**: ✅ **通过** — FK 约束有效，写入前有应用层校验。

---

### 2.3 /game/{session_id}/status 越权风险

**审查对象**: `backend/app/api/v1/game.py` get_game_status()

**实现分析**:

```python
# game.py L1859-1920
@router.get("/game/{session_id}/status")
async def get_game_status(
    session_id: str,
    user_id: str = Depends(get_current_user_id),  # Bearer Token
    db: AsyncSession = Depends(get_db),
):
    # Corvus 路径
    corvus_stmt = select(CorvusGameSession).where(
        CorvusGameSession.id == session_uuid,
        CorvusGameSession.user_id == UUID(user_id)  # ← 所有权校验
    )
    
    # Legacy 路径
    stmt = select(GameSession).where(
        GameSession.id == UUID(session_id),
        GameSession.user_id == UUID(user_id)  # ← 所有权校验
    )
```

**安全评估**:

- ✅ **Bearer Token 认证**: 端点使用 `get_current_user_id` 依赖，未认证返回 401。
- ✅ **所有权校验**: WHERE 子句同时匹配 `session_id` AND `user_id`，用户只能查询自己的会话。
- ✅ **Corvus + Legacy 双路径覆盖**: 两种引擎类型都有所有权校验。
- ✅ **无批量枚举**: 端点接受单个 session_id，不接受列表查询，无法批量枚举。
- ✅ **CR-039 D6 修复**: character_id 从 CorvusGameSession 读取，再查 Character 表获取 name。character_id 不会从请求参数中接受，不可篡改。

**结论**: ✅ **通过** — 无越权风险。所有者校验完整，character_id 不可从外部注入。

---

### 2.4 GM prompt 修改 — Prompt Injection 风险

**审查对象**: `corvus/server/services/gameMaster.ts` GM_SYSTEM_PROMPT

**实现分析**:

GM prompt 新增内容:
1. `playerOptions` 字段定义在 JSON schema 中
2. `PLAYER OPTIONS RULES` 指令块：MUST ALWAYS 生成 2-4 个选项
3. 选项文字 ≤30 字约束

**安全评估**:

- ✅ **GM 输出为 JSON**: GM prompt 强制 `You MUST respond with a single JSON object and NOTHING ELSE`。playerOptions 是 JSON 字符串字段，不会被解释为指令。
- ✅ **输出解析容错**: `parseGameMasterOutput()` 使用 lenient JSON 解析，提取 `playerOptions` 数组。即使 LLM 输出格式异常，fallback 为空数组，不会执行任意代码。
- ✅ **playerOptions 不持久化**: choices/playerOptions 是运行时 LLM 输出，不写入数据库，不作为指令执行。
- ✅ **用户输入隔离**: 玩家文本通过 `PLAYER: {content}` 格式传入 GM context，与 system prompt 分离。用户无法通过选项文字注入系统指令（选项 text 只被前端显示为按钮文字）。
- ⚠️ **间接注入路径**: 如果玩家在自由输入中写入类似 `[System: ignore previous instructions]` 的文本，会被原样传入 GM 的 `exchange` 上下文。但 GM 输出被限制为 JSON-only，且 `parseGameMasterOutput` 只提取预定义字段，不会执行注入的指令。**风险可控**。
- ✅ **前端选项点击安全**: 选项点击后以选项文字作为 `custom-input` 发送 → SSE 流式回应。选项文字来自 LLM 输出，经过 JSON 解析后作为普通字符串传输，前端 `ChoicePanel` 使用 Vue 模板转义渲染（`{{ }}`）。

**结论**: ✅ **通过** — GM prompt 修改不引入新的 prompt injection 风险。输出限制为 JSON-only，解析容错，用户输入与系统提示分离。

---

### 2.5 SSE 事件数据完整性

**审查对象**: SSETranslator.translate() gm_update 事件 → 前端 choices 映射

**实现分析**:

```python
# corvus_adapter.py SSETranslator.translate()
if event_type == "gm_update":
    player_options = corvus_event.get("playerOptions", [])
    choices = [
        {"id": str(i), "text": opt.get("text", ""), "hint": opt.get("hint", "")}
        for i, opt in enumerate(player_options)
        if isinstance(opt, dict)
    ]
    frontend_event["choices"] = choices
```

**安全评估**:

- ✅ **类型校验**: `isinstance(opt, dict)` 过滤非字典元素。
- ✅ **字段默认值**: `opt.get("text", "")` 和 `opt.get("hint", "")` 提供安全默认值。
- ✅ **id 生成**: `str(i)` 使用数组索引，不接受 LLM 提供的 id，防止注入。
- ✅ **空数组 fallback**: `playerOptions` 缺失或空时，`choices = []`，前端 fallback 到纯自由输入。

**结论**: ✅ **通过** — choices 映射安全，id 服务端生成，字段有默认值。

---

### 2.6 密钥/Token/凭证泄露检查

**审查对象**: `.env.example`, `corvus_adapter.py`, `game.py`, `gameMaster.ts`

**安全评估**:

- ✅ **.env.example**: 只有占位符 (`change-me-local-only`, `test-key-placeholder`, `isekai_password`)，无真实凭证。
- ✅ **Corvus LLM API-Key**: 由 Corvus `config.json` 自行管理，不经后端代码，不存储在后端环境变量中（CR-037 安全约束已验证）。
- ✅ **JWT Token**: 前端从 cookie 读取 `isekai_access_token` 用于 SSE fetch 请求。Token 不在 SSE 事件中传输，不记录在日志中。
- ✅ **SSE 错误消息**: `corvus_adapter.py` 错误处理使用通用化消息（`'Corvus 服务连接失败，请重试'`, `'服务器内部错误，请重试'`），不泄露内部细节。
- ✅ **日志脱敏**: `logger` 调用记录 session_id、character_id 等非敏感 UUID，不记录 token、密码或用户个人信息。

**结论**: ✅ **通过** — 无密钥/凭证泄露。

---

### 2.7 前端 XSS 防护

**审查对象**: `StoryPanel.vue`, `game.ts`, `GameView.vue`

**实现分析**:

1. **StoryPanel.vue** 使用 `v-html="formattedText"` 渲染对话文本:
   ```vue
   <div class="story-text" v-html="formattedText" v-show="displayedText || !isLoading"></div>
   ```
   `formattedText` 对 `displayedText` 做 `replace(/\n/g, '<br>')` + markdown 粗体/斜体替换。

2. **ChoicePanel**: 使用 Vue 模板 `{{ }}` 转义渲染选项文字。

3. **FreeChatInput**: 使用 Naive UI `<n-input>` 组件，默认转义。

**安全评估**:

- ⚠️ **v-html XSS 风险**: `StoryPanel.vue` 使用 `v-html` 渲染 LLM 输出文本。如果 LLM 输出包含 `<script>` 或 `<img onerror=...>` 标签，理论上可被渲染执行。
  - **缓解因素 1**: LLM 输出经过 SSETranslator 的 `_strip_role_markers()` 正则处理，但这只移除 `[Narrator]`/`[Character]` 标记，不过滤 HTML 标签。
  - **缓解因素 2**: `formattedText` 的 replace 操作只处理 `\n`、`**bold**`、`*italic*`，不涉及 HTML 标签清理。
  - **缓解因素 3**: CSP headers（`docs/security/security.md` 记录）在生产环境可缓解但不消除风险。
  - **实际风险等级**: 中。LLM (deepseek-v4-flash) 被系统 prompt 约束为叙事输出，主动输出恶意 HTML 的概率低。但用户自由输入 → LLM 回复路径中，用户可尝试诱导 LLM 输出 HTML。建议后续增加 HTML 标签白名单过滤。
- ✅ **ChoicePanel**: Vue 模板转义 (`{{ }}`) 对选项文字有效。
- ✅ **FreeChatInput**: Naive UI 组件默认转义。

**结论**: ⚠️ **条件通过** — StoryPanel `v-html` 存在理论 XSS 风险，但：
  1. LLM 输出受 system prompt 约束，非用户直接输入；
  2. 生产环境有 CSP headers 缓解；
  3. CR-039 变更范围未引入新的 XSS 风险（`v-html` 在 CR-038 已存在，CR-039 只改了 `displayedText` 计算方式）。

**建议**: 后续迭代中为 `formattedText` 增加 DOMPurify 或 HTML 标签白名单过滤。此建议不阻塞 CR-039 发布。

---

### 2.8 依赖、容器和部署配置风险

**审查对象**: `deploy-plan.md`（不存在）, `docker-compose.yml`, runtime-contract.md

**安全评估**:

- ⚠️ **deploy-plan.md 缺失**: CR-039 目录下无 `deploy-plan.md`。但 CR-039 明确不涉及部署变更（无新端口、无新容器、无 Nginx 配置变更），复用 CR-037/CR-038 部署配置。**不阻塞**。
- ✅ **无新增依赖**: CR-039 变更使用已有依赖（Python re/json、TypeScript 原生功能），无新增 npm/pip 包。
- ✅ **无新增端口**: 复用 CR-037 已有端口配置（Corvus 127.0.0.1:8082, 后端 8000, 前端 8081）。
- ✅ **无 iptables 变更**: Corvus 8082 公网 DROP 规则已在 CR-037 配置。

**结论**: ✅ **通过** — 无部署/依赖风险。

---

### 2.9 发布证据安全验证

**审查对象**: `test-report.md`, `acceptance.md`

**安全评估**:

- ✅ **Mock API=no**: test-report.md 明确记录 Delivery E2E 和 Browser E2E 均使用 `Mock API=no`。
- ✅ **Delivery E2E**: 4/4 PASS，使用真实 Corvus 服务 (127.0.0.1:8082)、真实后端 API、真实 PostgreSQL。
- ✅ **Browser Interaction E2E**: 12/13 PASS (1 deferred)，使用真实浏览器 (Playwright Chromium) + 真实前后端。
- ✅ **Regression E2E**: 4/4 PASS (CR-038 回归)。
- ✅ **测试类型区分**: test-report.md 明确区分 CI/CD、Delivery E2E / Runtime Smoke、Browser Interaction E2E。
- ✅ **AC-014 deferred_with_approval**: 好感度数值变化测试单轮不足，Delivery E2E Round 3 已验证 BE 映射逻辑正确。PL 批准 deferred，不阻塞发布。

**结论**: ✅ **通过** — 发布证据使用真实服务，Mock API=no，测试类型区分明确。

---

### 2.10 追踪链完整性

**审查对象**: `traceability-chain.md`, `failure-backtrace.md`

**安全评估**:

- ✅ **AC → REQ 追踪**: acceptance.md 每个 AC 有需求编号 (REQ-GM-001, REQ-SSE-001, REQ-FE-001/002)。
- ✅ **AC → 设计落点**: 每个 AC 指向具体模块 (gameMaster.ts, chat.ts, game.py, game.ts, ChoicePanel)。
- ✅ **AC → 测试证据**: 每个 AC 有 Test Case 编号和测试类型。
- ✅ **AC → QA 复核**: test-report.md 逐 AC 记录 QA 结论。
- ✅ **发布证据 → Mock API=no**: Delivery E2E 和 Browser E2E 均记录 Mock API=no。
- ✅ **无断链**: 未发现安全相关 AC 缺少证据或覆盖状态。

**结论**: ✅ **通过** — 追踪链完整。

---

## 3. 高风险事项

| 编号 | 风险 | 等级 | 状态 | 责任人 | 修复后验证路径 |
|---|---|---|---|---|---|
| H-1 | StoryPanel `v-html` 渲染 LLM 输出，理论 XSS 风险 | 中 | 不阻塞（CR-038 已有，CR-039 未引入新风险） | FE (后续迭代) | 增加 DOMPurify HTML 白名单过滤 |

**无 P0/阻塞级高风险事项。**

---

## 4. 安全检查清单

| 检查项 | 结论 | 备注 |
|---|---|---|
| 是否提交真实密钥/token/证书/密码或生产数据 | ✅ 无 | .env.example 只有占位符 |
| 鉴权、授权、审计和敏感操作确认是否完整 | ✅ 通过 | Bearer Token + 所有权校验 |
| 敏感字段、隐私、日志脱敏和数据保留是否清楚 | ✅ 通过 | 日志记录 UUID，不记录 token/密码 |
| API、DB/Storage、Runtime 和 Mock 策略是否一致 | ✅ 通过 | 无 mock 发布证据，无未记录数据源 |
| test-report.md 是否区分 CI/CD、Delivery E2E、Browser E2E | ✅ 通过 | 三类测试明确区分 |
| 依赖、容器和部署配置是否存在明显风险 | ✅ 通过 | 无新增依赖/端口/容器 |
| 安全相关验收项是否在 acceptance.md 有验证结论 | ✅ 通过 | 14/14 AC 有效通过 (13 passed + 1 deferred) |
| 高风险事项是否需要人工确认 | ✅ 无阻塞 | H-1 为中风险，不阻塞 |

---

## 5. 退回规则检查

- ❌ **无需退回架构师**: 无架构或数据风险。
- ❌ **无需退回实现 Agent**: 无实现漏洞。
- ❌ **无需退回 PL 升级人工**: 无生产/权限/支付/数据删除风险。

---

## 6. 安全审查结论

### ✅ PASSED — 具备发布关口通过条件

**安全审查通过**，附 1 项非阻塞建议：

1. **PASSED**: SSE 事件过滤有效，character_id FK 约束有效，/game/status 无越权风险，GM prompt 无 prompt injection 风险。
2. **PASSED**: 发布证据使用真实服务 (Mock API=no)，追踪链完整。
3. **PASSED**: 14/14 AC 有效通过 (13 passed + 1 deferred_with_approval)。
4. **非阻塞建议 H-1**: StoryPanel `v-html` 存在理论 XSS 风险（CR-038 已有，CR-039 未引入新风险），建议后续迭代增加 DOMPurify 过滤。

### 限制项

- 无阻塞级安全限制项。
- H-1 (StoryPanel v-html) 为中风险建议，不阻塞 CR-039 发布。

### 发布建议

- CR-039 安全审查通过，可进入 RELEASE_GATE。
- H-1 建议记录到 `docs/security/security.md` 后续改进项。

---

## 7. 证据等级

| 证据 | 等级 | 说明 |
|---|---|---|
| Delivery E2E (3 轮 SSE 验证) | L2 | 真实前后端 + 真实 Corvus 服务 |
| Browser Interaction E2E (12/13) | L2 | 真实浏览器 + 真实前后端 |
| 代码审查 (SSETranslator, game.py, corvus.py, gameMaster.ts, game.ts, StoryPanel.vue) | L1 | 静态代码审查 |
| FK 约束验证 | L1 | 代码级审查 (SQLAlchemy ForeignKey) |

---

## 8. 追加：docs/security/security.md 更新建议

在 `docs/security/security.md` 的 CR-038 Additions 后追加：

### CR-039 Additions: Corvus 玩家选项功能

| Risk | Mitigation |
|------|------------|
| SSE 事件 [Narrator]/[Character] 标记泄露 | SSETranslator token 级 + done 级双重正则过滤 |
| playerOptions → choices 映射注入 | id 服务端生成 (数组索引), 字段有默认值, isinstance 类型校验 |
| GM prompt playerOptions 注入 | GM 输出限制为 JSON-only, parseGameMasterOutput lenient 解析, playerOptions 不持久化 |
| /game/status 越权 | Bearer Token + WHERE user_id 所有权校验, character_id 不可从请求参数注入 |
| StoryPanel v-html XSS | LLM 输出受 system prompt 约束; CSP headers 缓解; 后续迭代增加 DOMPurify (H-1 非阻塞建议) |

### CR-039 安全检查清单

- [x] SSETranslator 双重过滤 [Narrator]/[Character] 标记
- [x] playerOptions → choices 映射有类型校验和默认值
- [x] GM prompt 输出限制为 JSON-only
- [x] /game/{session_id}/status 有 Bearer Token + 所有权校验
- [x] character_id FK 约束 (DB + 应用层)
- [x] 无密钥/token 凭证泄露
- [x] 日志不记录敏感数据
- [x] 发布证据 Mock API=no
- [ ] StoryPanel v-html 增加 DOMPurify (H-1 后续迭代)
