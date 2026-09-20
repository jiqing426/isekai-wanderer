# Capability Spec

## Scope

本规格描述 Corvus-Story-Core 集成对系统能力的影响，仅描述本次变更新增或改变的能力。规格按实体和关键流程拆分，P0/P1 场景必须可测试。

---

### Requirement: REQ-CORVUS-001 — Corvus 服务可达性和安全隔离

Corvus-Story-Core 部署在 127.0.0.1:8082，systemd 守护，公网不可达，LLM 走 thoushub 网关调用 deepseek-v4-flash。

#### Scenario: 本机健康检查

- **Given** Corvus systemd 服务已启动
- **When** 本机执行 `curl http://127.0.0.1:8082/api/health`
- **Then** 返回 `{"ok": true}` 且 HTTP 200
- **Priority** P0
- **Verification** `systemctl status corvus-story` → active(running)；`curl 127.0.0.1:8082/api/health` → 200

#### Scenario: 公网不可达

- **Given** 防火墙规则已配置
- **When** 从公网访问 `服务器IP:8082`
- **Then** 连接被拒绝或超时
- **Priority** P0
- **Verification** 外部主机 `curl --connect-timeout 5 http://<server-ip>:8082/api/health` → 拒绝/超时

#### Scenario: LLM 网关连通

- **Given** Corvus 服务运行中且已配置 thoushub 网关
- **When** Corvus 内部调用 LLM（deepseek-v4-flash）
- **Then** LLM 返回正常文本，无 401/网络超时
- **Priority** P0
- **Verification** `journalctl -u corvus-story -f` 无 401/网络报错；模拟 Corvus 内部链路返回结果

#### Scenario: 无禁用进程

- **Given** 服务器运行状态
- **When** 检查进程列表
- **Then** 不存在 ollama / vLLM / Hermes-Agent 进程
- **Priority** P1
- **Verification** `ps aux | grep -E 'ollama|vllm|hermes'` 无匹配

---

### Requirement: REQ-CORVUS-002 — 候选玩家角色池管理

每个用户拥有最多 3 个候选玩家角色，开局三选一，仅选中角色送入 Corvus。

#### Scenario: 获取候选角色列表

- **Given** 用户已登录，`player_candidates` 表有种子数据
- **When** 前端调用 `GET /api/game/player/candidates?user_id={uuid}`
- **Then** 返回最多 3 个候选角色，每个角色包含 name、personality、backstory、appearance、initial_inventory
- **Priority** P0
- **Verification** API 返回 `code: 0`，`data` 数组长度 ≤ 3；用户动作：打开角色选择页面，可见 3 个角色卡片
- **Needs** Browser Interaction E2E

#### Scenario: 创建剧本会话

- **Given** 用户已登录
- **When** 前端调用 `POST /api/game/session/create`，入参 `{"user_id": "uuid-v4"}`
- **Then** 返回 `game_session_id`（UUID v4），会话状态为 `waiting_select_player`
- **Priority** P0
- **Verification** API 返回 `code: 0`，`data.game_session_id` 为 UUID v4 格式；DB `corvus_game_sessions` 表有对应记录，status = `waiting_select_player`
- **Needs** API/DB/Runtime 契约验证

#### Scenario: 选定角色进入游戏

- **Given** 已创建剧本会话，status = `waiting_select_player`
- **When** 前端调用 `POST /api/game/session/select-player`，入参 `{"game_session_id": "uuid", "player_candidate_id": "uuid"}`
- **Then** 后端更新 GameSession status = `playing`，`selected_player_candidate_id` = 选中的角色 ID；仅该角色数据送入 Corvus（另外 2 个候选角色不送入）；后端调用 Corvus `POST /api/games` 创建游戏，存储 `corvus_internal_game_id`；返回初始世界场景数据
- **Priority** P0
- **Verification** DB `corvus_game_sessions` 表 status = `playing`，`selected_player_candidate_id` 已设置，`corvus_internal_game_id` 非空；Corvus 收到的 player 数据仅含选中角色；用户动作：点击角色卡片选择，页面进入游戏界面
- **Needs** API/DB/Runtime 契约验证 + Browser Interaction E2E

#### Scenario: 换角色必须创建新会话

- **Given** 用户已有一个 status = `playing` 的 Corvus 会话
- **When** 用户选择另一个候选角色
- **Then** 必须创建全新 `game_session_id`，旧会话记忆不影响新会话
- **Priority** P1
- **Verification** 旧会话 `selected_player_candidate_id` 不变；新会话有不同的 `game_session_id` 和 `corvus_internal_game_id`；旧会话的向量记忆不会错误注入新会话（通过 user_id + character_id 隔离）

---

### Requirement: REQ-CORVUS-003 — SSE 流式游戏回合

用户在游戏中输入文本，后端通过 SSE 流式透传 Corvus 回合结果，逐字渲染到前端。

#### Scenario: SSE 流式文本渲染

- **Given** Corvus 会话 status = `playing`，用户在游戏界面
- **When** 用户输入文本并提交（前端 `submitCustomInput` 发起 SSE 请求 `POST /game/{id}/custom-input`）
- **Then** 后端 CorvusAdapter 先执行向量记忆召回（pgvector KNN → NPC knownInfo 注入），然后 POST Corvus `/api/games/{game_id}/messages`，SSE 事件流逐条透传前端；前端 StoryPanel 逐字渲染 `assistant-delta` 事件
- **Priority** P0
- **Verification** 用户动作：在输入框输入文本 → 点击发送 → 观察文字逐字出现；可观察结果：文字逐步渲染到 StoryPanel，非一次性出现
- **Needs** Browser Interaction E2E + API/DB/Runtime 契约验证

#### Scenario: SSE 事件翻译映射

- **Given** 后端收到 Corvus SSE 事件
- **When** Corvus 发出 `assistant-delta` / `assistant-complete` / `gm-complete` / `done` / `error` 事件
- **Then** 后端翻译为前端期望格式：`text`（逐字内容）/ `done`（完整文本 + character_id + node_id）/ `gm_update`（好感/道具/标记变化）/ `stream_end`（关闭连接）/ `error`（错误信息）
- **Priority** P0
- **Verification** 前端收到的事件格式与映射表一致；`done` 事件包含完整文本和 character_id；`gm_update` 事件包含好感/道具/标记变化数据
- **Needs** API/DB/Runtime 契约验证

#### Scenario: SSE 中断错误处理

- **Given** SSE 流式传输进行中
- **When** Corvus 连接中断或超时
- **Then** 前端 `onError` 回调触发，显示错误提示；用户可重试
- **Priority** P1
- **Verification** 模拟 Corvus 断开连接，前端显示错误提示而非白屏；用户点击重试后可重新发送消息
- **Needs** Browser Interaction E2E

---

### Requirement: REQ-CORVUS-004 — world_state 数据持久化

Corvus 返回的 world_state（好感、道具、剧情标记）必须同步到业务数据库。

#### Scenario: 好感度同步

- **Given** Corvus 返回 `gm_update` 事件，包含 `affinity_delta`
- **When** 后端 CorvusAdapter 处理事件
- **Then** `session_npcs` 表对应 NPC 的 `affinity` 字段更新；异步执行，不阻塞 SSE 文本流
- **Priority** P0
- **Verification** DB `session_npcs` 表 `affinity` 值与 Corvus 返回一致；SSE 文本流不受 DB 写入阻塞（asyncio.create_task）
- **Needs** API/DB/Runtime 契约验证

#### Scenario: 道具同步

- **Given** Corvus 返回 `gm_update` 事件，包含 `inventory_changes`
- **When** 后端 CorvusAdapter 处理事件
- **Then** `inventory_items` 表对应记录创建/更新/删除
- **Priority** P0
- **Verification** DB `inventory_items` 表与 Corvus 返回的道具列表一致；刷新页面后道具仍存在
- **Needs** API/DB/Runtime 契约验证

#### Scenario: 剧情标记同步

- **Given** Corvus 返回 `gm_update` 事件，包含 `story_flags`
- **When** 后端 CorvusAdapter 处理事件
- **Then** `story_flags` 表对应记录创建/更新（`flag_key` 唯一约束）
- **Priority** P0
- **Verification** DB `story_flags` 表与 Corvus 返回的标记列表一致；`flag_key` 重复时更新而非插入
- **Needs** API/DB/Runtime 契约验证

---

### Requirement: REQ-CORVUS-005 — 向量记忆系统（pgvector 语义召回）

跨会话语义记忆：对话结束 → 向量化写入 pgvector；回合开始 → KNN 召回 Top-5 → 注入 Corvus NPC knownInfo。

#### Scenario: 对话结束写入向量记忆

- **Given** Corvus SSE `assistant-complete` 事件到达（完整对话文本）
- **When** 后端 CorvusAdapter 触发记忆写入流程
- **Then** 调用现有 MemoryService.extract_and_store()（LLM 提取关键记忆）→ bge-small-zh 生成 512 维 embedding → 写入 `character_memories` 表（user_id, character_id, memory_text, embedding, source_session_id）
- **Priority** P0
- **Verification** DB `character_memories` 表有新记录，`embedding` 非 NULL，维度 512；异步执行，不阻塞 SSE 文本流
- **Needs** API/DB/Runtime 契约验证

#### Scenario: 回合开始向量召回

- **Given** 用户输入文本，Corvus 会话 status = `playing`
- **When** 后端 CorvusAdapter 执行召回流程
- **Then** bge-small-zh 生成用户输入的 embedding → pgvector KNN 搜索 `character_memories`（`WHERE user_id = X AND character_id = Y AND 1 - (embedding <=> query_embedding) > 0.7 LIMIT 5`）→ 召回 Top-5 相关记忆文本
- **Priority** P0
- **Verification** 召回结果按相似度排序；相似度阈值 0.7；最多返回 5 条
- **Needs** API/DB/Runtime 契约验证

#### Scenario: NPC knownInfo 注入与恢复

- **Given** 召回的向量记忆文本
- **When** 后端读取 Corvus NPC `characters/{npc_id}.json`，将召回记忆追加到 NPC `knownInfo` 字段，POST Corvus `/api/games/{game_id}/messages`
- **Then** Corvus 自动把 NPC knownInfo 带入 LLM 上下文；回合结束后恢复 NPC knownInfo 原始值（避免污染）
- **Priority** P0
- **Verification** 回合期间 NPC knownInfo 包含召回记忆；回合结束后 NPC knownInfo 恢复为原始值；加锁保证恢复在下次注入前完成
- **Needs** API/DB/Runtime 契约验证

#### Scenario: 跨会话记忆隔离

- **Given** 同一用户同一角色在不同 game_session 的对话
- **When** 新会话回合开始时执行向量召回
- **Then** `character_memories` 按 `user_id + character_id` 检索，自然跨会话召回旧记忆；不同用户/不同角色的记忆不互相检索
- **Priority** P1
- **Verification** 用户 A 角色 1 的记忆不会出现在用户 B 或角色 2 的召回结果中

---

### Requirement: REQ-CORVUS-006 — 新旧引擎共存 feature flag 切换

通过 engine_type 字段区分旧引擎和 Corvus 引擎，旧引擎路径完全不变。

#### Scenario: 旧引擎路径不受影响

- **Given** game_session 的 `engine_type` = `legacy`（或字段为空）
- **When** 前端调用现有 API（`/game/start`、`/game/{id}/custom-input`、`/game/{id}/choice`、`/game/{id}/dialogue`）
- **Then** 走现有 NarrativeEngine 路径，行为与 CR-037 前完全一致
- **Priority** P0
- **Verification** 现有剧本功能回归测试通过；无回归 bug
- **Needs** Browser Interaction E2E

#### Scenario: Corvus 引擎路径切换

- **Given** game_session 的 `engine_type` = `corvus`
- **When** 前端调用现有 API
- **Then** 后端 Engine Dispatcher 切换到 CorvusAdapter 路径，走 Corvus 流程
- **Priority** P0
- **Verification** Corvus 会话走 CorvusAdapter；旧剧本走 NarrativeEngine；两者互不干扰
- **Needs** API/DB/Runtime 契约验证

---

### Requirement: REQ-CORVUS-007 — 数据库 UUID v4 强制规范

所有业务实体 ID 统一使用 UUID v4，禁止自增数字 ID。

#### Scenario: 新建表主键 UUID v4

- **Given** 5 张新表 DDL 已执行
- **When** 插入新记录
- **Then** `player_candidates.id`、`corvus_game_sessions.id`、`session_npcs.id`、`inventory_items.id`、`story_flags.id` 均为 UUID v4 格式（`DEFAULT gen_random_uuid()`）
- **Priority** P0
- **Verification** `SELECT id FROM player_candidates LIMIT 1` → UUID v4 格式；无自增数字 ID
- **Needs** API/DB/Runtime 契约验证

#### Scenario: Corvus game_id slug 类型

- **Given** Corvus 返回的 `game_id` 为 slug 格式（非 UUID v4）
- **When** 存储 `corvus_internal_game_id`
- **Then** `corvus_game_sessions.corvus_internal_game_id` 字段类型为 VARCHAR(100)，非 UUID
- **Priority** P1
- **Verification** DB 字段类型为 VARCHAR(100)；存储的值为 slug 格式

---

### Requirement: REQ-CORVUS-008 — 前端兼容性（不改 Vue 组件/样式）

前端仅改 game.ts 数据层 ~40 行，Vue 组件/样式/交互逻辑全部不动。

#### Scenario: 页面路由不变

- **Given** 用户访问游戏页面
- **When** 打开 `/game?script={game_session_id}`
- **Then** 页面正常打开，路由格式不变，`script` 参数等价 `game_session_id`（UUID v4）
- **Priority** P0
- **Verification** 用户动作：浏览器输入 URL → 页面正常加载；可观察结果：游戏界面正常显示
- **Needs** Browser Interaction E2E

#### Scenario: choices 为空时降级

- **Given** Corvus 不返回 player_options
- **When** 前端收到 `done` 事件，`pendingChoices` 为空数组
- **Then** `ChoicePanel` 的 `v-if` 已处理空数组，`FreeChatInput` 始终显示，用户可自由输入
- **Priority** P1
- **Verification** 用户动作：完成一轮对话后 → 无选项按钮 → 可在输入框自由输入；可观察结果：输入框可见可用
- **Needs** Browser Interaction E2E

---

### Requirement: REQ-CORVUS-009 — Corvus API 真实接口适配

Corvus 实际为 Node.js + Express + tsx，API 路径与 PRD 文档不同，以执行方案 v3 为准。

#### Scenario: 创建游戏

- **Given** 后端 CorvusClient 调用 Corvus
- **When** `POST http://127.0.0.1:8082/api/games`，入参 player_name、backstory、appearance、world_setting
- **Then** 返回 game_id（slug 格式），后端存入 `corvus_internal_game_id`
- **Priority** P0
- **Verification** API 调用成功，返回 game_id；DB 记录 `corvus_internal_game_id` 非空
- **Needs** API/DB/Runtime 契约验证

#### Scenario: 发送消息（SSE 流式）

- **Given** 后端 CorvusClient 调用 Corvus
- **When** `POST http://127.0.0.1:8082/api/games/{gameId}/messages`，入参 content
- **Then** 返回 SSE 事件流（`assistant-delta` / `assistant-complete` / `gm-complete` / `done` / `error`）
- **Priority** P0
- **Verification** SSE 事件流格式正确；事件类型与映射表一致
- **Needs** API/DB/Runtime 契约验证

#### Scenario: 获取 NPC 信息

- **Given** 后端 CorvusClient 调用 Corvus
- **When** `GET http://127.0.0.1:8082/api/games/{gameId}/characters/{npcId}`
- **Then** 返回 NPC JSON（含 memory[] 字段、knownInfo 字段）
- **Priority** P1
- **Verification** 返回 JSON 格式正确；包含 knownInfo 字段

#### Scenario: 更新 NPC knownInfo

- **Given** 后端 CorvusClient 调用 Corvus
- **When** `PATCH http://127.0.0.1:8082/api/games/{gameId}/characters/{npcId}`，入参 knownInfo
- **Then** NPC knownInfo 字段更新成功
- **Priority** P1
- **Verification** 再次 GET NPC 信息，knownInfo 已更新
