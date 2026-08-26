# Proposal

## Why

- 用户需要在现有异世界漫游项目中集成 Corvus-Story-Core（Node.js AI 叙事引擎），获得 AI 自由叙事能力，突破现有剧本系统的线性对话限制。
- 现有 NarrativeEngine 为规则驱动的节点跳转，无法生成自由文本剧情；Corvus 负责 GM 游戏主循环、剧情生成、会话内记忆管理，LLM 走 thoushub 网关调用 deepseek-v4-flash。
- 新旧引擎共存，通过 feature flag（engine_type 字段）切换，不废弃旧剧本系统，降低风险。
- 用户已确认急需此能力（P1），且已自行完成 Corvus 部署（systemd + 防火墙 + LLM 配置）。

## What Changes

- 新增 Corvus 引擎路径：后端新增 CorvusClient（HTTP + SSE 流式调用 Corvus 127.0.0.1:8082）、CorvusAdapter（SSE 翻译 + world_state DB 同步 + 向量记忆写入/召回）、EmbeddingService（bge-small-zh 本地推理 + pgvector 语义召回）。
- 现有 API feature flag 改造：`/game/start`、`/game/{id}/custom-input`、`/game/{id}/choice`、`/game/{id}/dialogue` 增加 engine_type 切换，旧引擎路径完全不变。
- 新增 4 个 API：`POST /api/game/session/create`、`GET /api/game/player/candidates`、`POST /api/game/session/select-player`、`POST /api/game/game-turn`。
- 前端 game.ts 微调 ~40 行：`submitCustomInput` 改 SSE 流式读取，`GameSession` 接口新增 `engine_type` 字段，`GameView` initGame 增加 Corvus 分支。
- 数据库新建 5 张表：`player_candidates`、`corvus_game_sessions`、`session_npcs`、`inventory_items`、`story_flags`；`character_memories` embedding 维度 1536→512（适配 bge-small-zh）。
- 向量记忆：对话结束 → LLM 提取关键记忆 → bge-small-zh 向量化 → pgvector 存储；回合开始 → pgvector KNN 召回 Top-5 → 注入 Corvus NPC knownInfo → 回合结束恢复。
- 所有业务实体 ID 统一 UUID v4。

## Non-Goals

- 不部署 ollama / vLLM / Hermes-Agent。
- 不修改 Corvus 内部 GM 逻辑 / 提示词体系。
- 不修改 Vue 前端组件 / 样式 / 交互逻辑（仅 game.ts 数据层 ~40 行 SSE 改造 + GameView ~5 行分支）。
- 不废弃旧剧本系统（Script / Route / Node）。
- 不新增基础设施费用（LLM 复用 thoushub 网关，embedding 用开源 bge-small-zh）。
- 不引入独立向量数据库服务（复用 PostgreSQL + pgvector）。
- 不做公共 API 破坏性变更（对外 API 入参、返回 JSON 字段名保持现有协议）。

## Success Criteria

- 前端 `/game?script={game_session_id}` 正常打开，SSE 流式逐字渲染。
- 候选角色三选一，仅选中角色送入 Corvus。
- game-turn 返回 scene_desc / npc_dialogues / player_options，页面渲染正常。
- world_state 变更正确落库（好感 / 道具 / 剧情标记）。
- 跨会话记忆隔离；向量记忆可语义召回。
- 8082 端口公网不可达。
- 所有主键 UUID v4。
- 无 ollama / vLLM / Hermes-Agent 进程。

## Impact

- **后端**：新增 CorvusClient / CorvusAdapter / EmbeddingService，现有 4 个 API 增加 feature flag 切换，新增 4 个 API 端点。
- **前端**：game.ts `submitCustomInput` 改 SSE 流式读取（~40 行），`GameSession` 接口新增 `engine_type` 字段，`GameView` initGame 增加 Corvus 分支（~5 行）。
- **数据库**：新建 5 张表，`character_memories` embedding 维度 1536→512（不可逆迁移，需人工确认，见 Q-001），删除 6 张无用 backup 表。
- **基础设施**：Corvus 127.0.0.1:8082 systemd 守护（已完成），防火墙 8082 公网 DROP（已完成）。
- **安全**：Corvus 仅本机访问，前端不可直接请求 8082；LLM 网关 API-Key 存储在 Corvus config.json，不经过我方后端。
- **旧系统**：完全保留，feature flag 隔离，旧引擎路径无任何改动。

## Open Questions

| ID | Question | Blocks MVP | Status | Shown to User | User Answer | Resolution |
| --- | --- | --- | --- | --- | --- | --- |
| Q-001 | `character_memories` embedding 维度 1536→512 属不可逆 DB 迁移，需人工确认后方可执行。现有 119 条记忆 embedding 全为 NULL，不影响迁移。 | 是 | open | PRD 自动入口已记录，需 PL 在 DESIGN_GATE 前向用户确认 | 待用户确认 | CEO INIT 附条件1：PL 在 DESIGN_GATE 前取得人工确认；Architect 在 DESIGN 阶段需设计迁移方案和回滚预案 |
| Q-002 | 生产环境变更（systemd 服务、防火墙规则）需人工确认。PRD 自动入口不授权自动通过。TRIAGE 已确认 systemd 和防火墙已执行，需用户事后追认。 | 否 | closed | PRD 自动入口已记录，PL 在 DEPLOY 前向用户确认 | TRIAGE 记录：systemd 和防火墙已执行，Corvus 服务 active running，health 200，公网 8082 DROP | 非阻塞 MVP；已执行，待 DEPLOY 前追认 |
| Q-003 | Corvus 实际 API 与 PRD 文档存在差异（Node.js vs Python，config.json vs .env，API 路径不同），执行方案 v3 已记录真实 API。是否以执行方案 v3 为准？ | 否 | closed | PRD 自动入口已记录，执行方案 v3 已记录真实 API 差异 | 执行方案 v3 已记录真实 API，用户确认以实际 API 为准 | 非阻塞 MVP；以执行方案 v3 为准 |
| Q-004 | Corvus game_id 是 slug 格式（非 UUID v4），`corvus_internal_game_id` 字段需用 VARCHAR 而非 UUID 类型。是否允许？ | 否 | closed | PRD 自动入口已记录，执行方案 v3 已记录此差异 | 用户确认接受 slug 格式的 game_id | 非阻塞 MVP；corvus_internal_game_id 用 VARCHAR(100) |
| Q-005 | bge-small-zh 模型首次加载需下载 ~400MB，服务启动时预加载预热。是否在应用启动时执行？ | 否 | closed | PRD 自动入口已记录 | 用户确认预热方案 | 非阻塞 MVP；启动时预加载模型 |
| Q-006 | 现有 119 条旧记忆无 embedding 数据，上线后需跑批量补量脚本。是否允许上线后异步补量？ | 否 | closed | PRD 自动入口已记录 | 用户确认上线后批量补量 | 非阻塞 MVP；上线后跑批量补量脚本，不阻塞发布 |
