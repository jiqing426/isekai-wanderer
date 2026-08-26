# Review: CR-038 — Corvus 前端入口接入

- **CR ID**: CR-038
- **Created At**: 2026-08-17T09:00:00+08:00
- **PL**: isekai-wanderer-pl

## INTAKE 审查记录

### 变更目标

CR-037 完成了 Corvus-Story-Core 的后端全链路集成（BE 端点、SSE 透传、DB 同步、向量记忆、feature flag），但前端入口未接入。当前前端 `startGame()` 只调用 legacy `POST /game/start`，从不创建 Corvus 会话，`engine_type` 永远为 `undefined`，所有 Corvus SSE 分支代码成为 dead code。用户实际体验仍是内置节点式剧本游戏。

本 CR 目标：让用户可以在前端通过 Corvus 引擎开始游戏，体验 SSE 流式叙事。

### 影响范围

| 层面 | 影响 |
|---|---|
| 前端 game.ts | startGame 改造、Corvus 会话创建流程、SSE 分支激活 |
| 前端视图 | GameView.vue / ScriptDetailView.vue 需区分引擎类型，新增选角 UI |
| 前端新增组件 | 角色候选管理、Corvus 选角界面 |
| 后端 | 可能需补充 GET /scripts 返回 engine_type 字段 |
| 后端 Corvus 核心 | 不涉及（CR-037 已完成） |

### 成功标准

1. 用户可以在前端选择 Corvus 剧本并开始游戏
2. 游戏过程中对话通过 SSE 流式渲染
3. 用户可以自由输入文字推进剧情
4. `engine_type` 正确设置为 `'corvus'` 并持久化
5. Legacy 剧本不受影响
6. Browser E2E 可验证 Corvus 全链路

### 功能清单

| 编号 | 功能 | 说明 |
|---|---|---|
| F1 | 剧本选择页 Corvus 入口 | 区分 legacy/corvus 剧本，Corvus 剧本走 Corvus 流程 |
| F2 | Corvus 会话创建流程 | 调用 /game/session/create + /game/session/select-player |
| F3 | SSE 流式叙事接入 | submitChoice/submitCustomInput 的 Corvus 分支激活 |
| F4 | 角色候选管理 | 查看/创建/选择 player_candidates |
| F5 | Feature Flag 联动 | 后端标记剧本引擎类型，前端按标记分流 |

### 风险识别

| 编号 | 风险 | 等级 |
|---|---|---|
| R1 | 前端 Corvus 会话创建 UI 复杂度可能超预期 | 中 |
| R2 | SSE 流式渲染与 legacy 渲染逻辑共存可能状态混乱 | 中 |
| R3 | Feature flag 判断需后端配合，可能需改 scripts API | 低 |
| R4 | localStorage 会话恢复需区分 legacy/corvus | 低 |

### 额外约束（2026-08-17 用户追加）

用户在 INTAKE 阶段追加三条硬性约束：

| 编号 | 约束 | 排查结论 |
|---|---|---|
| C1 | engine_type 字段补齐 | 后端 Model/Migration/API 创建会话已有；前端 Interface/startGame/resumeSession 缺失；后端 GET /scripts 缺失 |
| C2 | 字段全部必填 | 前端 GameSession.engine_type 改为必填（去掉 ?）；Script interface 新增 engine_type 必填 |
| C3 | 全部用 Corvus 剧本 | 所有剧本 engine_type 统一 'corvus'；startGame/resumeSession 写入 'corvus'；GET /scripts 返回 'corvus' |

### 缺口

- ~~需确认：Corvus 剧本列表从哪里来？后端 GET /scripts 是否已有 engine_type 字段，还是需要新增？~~→ 已确认：GET /scripts 当前不含 engine_type，需新增（C1/C3）
- 需确认：角色候选创建流程中，用户需要填写哪些字段（name/personality/backstory/appearance）？哪些必填？
- 需确认：Corvus 剧本和 legacy 剧本在 UI 上如何区分展示？（C3 已约束全部用 Corvus，此问题降级为后续优化）

### 关联 CR

- CR-037: Corvus-Story-Core 集成（后端已完成，本 CR 是前端补完）

## 通信台账

| 时间 | from | to | 阶段 | 状态 | 说明 |
|---|---|---|---|---|---|
| 2026-08-17T09:00 | pl | - | INTAKE | created | CR-038 PRD 自动入口完成，等待用户确认推进 |

## Stage Pause Confirmations

| Stage | Action | Next Stage | Deliverables | Summary Shown | User Confirmation | Recorded At |
|---|---|---|---|---|---|---|
| INTAKE | accept | INIT | change.md（含 C1/C2/C3 硬性约束）、docs/prd/cr-038-corvus-frontend-entry.md、review.md INTAKE 审查记录 | 变更目标：前端接入 Corvus 引擎；三条硬性约束 C1(engine_type 补齐) C2(全部必填) C3(全部 Corvus)；影响范围 2 文件；4 条风险；2 个缺口待后续细化 | 用户于 2026-08-17 15:41 回复「推进」，明确同意从 INTAKE 推进到 INIT | 2026-08-18T11:26:00+08:00 |
