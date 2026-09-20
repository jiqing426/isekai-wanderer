# Change: CR-038 — Corvus 前端入口接入

- **CR ID**: CR-038
- **Change Name**: corvus-frontend-entry
- **Created At**: 2026-08-17T09:00:00+08:00
- **Status**: redevelopment
- **Source**: 用户反馈 — CR-037 后端集成已完成但前端入口未接入，用户实际仍玩 legacy 内置游戏
- **范围变更 (2026-09-07)**: 用户要求移除自定义角色创建功能，改为直接使用剧本预设角色（Character 表 playable=True 的记录）。CR-038 从 RELEASE_GATE 退回 DEVELOPMENT 改造。

## 改造范围 (2026-09-07)

### 移除
- 移除 `PlayerCandidateModal.vue` 中的创建表单和"自定义角色"区域
- 移除 `POST /api/v1/game/player/candidates` 端点（标记 deprecated 或删除）
- 移除 AC-038-003/004/005/006（创建候选相关验收项）
- 移除 AC-038-013/014/015（前端创建表单相关验收项）

### 改造
- `GET /api/v1/game/player/candidates` → 改为 `GET /api/v1/game/scripts/{script_id}/characters`，返回剧本预设可扮演角色列表
- `POST /api/v1/game/session/select-player` → 改为接收 `character_id`（Character 表 UUID），后端用角色数据组装传给 Corvus
- `CorvusGameSession` 新增 `selected_character_id` 字段（关联 Character 表），保留 `selected_player_candidate_id` 向后兼容
- `PlayerCandidateModal.vue` → 改为只展示角色卡片列表，移除创建表单
- `game.ts` startGame 流程调整：选角时传 `character_id` 而非 `player_candidate_id`
- `corvus_adapter.py` create_session 改为接收 `character_id`，从 Character 表取角色数据

### 保留
- `PlayerCandidate` 表保留（向后兼容已创建的用户数据），不再写入新记录
- Legacy 引擎流程不受影响（CR-028 的角色选择保留）
- Corvus SSE 对话逻辑不变
- AC-038-001/002（engine_type 字段）、AC-038-007/008（前端类型）、AC-038-009（会话创建）、AC-038-017~020（SSE 流式）、AC-038-021/022（会话恢复）、AC-038-023~025（剧本分流）全部保留

### 新增/改写 AC
- AC-038-010 改写：选角列表来源从 player_candidates 改为剧本预设角色（Character 表 playable=True）
- AC-038-011 改写：选定角色时传 character_id 而非 player_candidate_id
- AC-038-012 改写：角色展示来源改为剧本预设角色
- AC-038-016 改写：选定预设角色进入游戏
- 新增 AC-038-026: GET /game/scripts/{script_id}/characters 返回可扮演角色列表

## 变更目标

让用户可以在前端通过 Corvus 引擎开始游戏，体验 SSE 流式叙事，而非只能玩 legacy 节点剧本。

- 目标：激活 CR-037 已投入的后端 Corvus 能力，让用户在前端选择 Corvus 剧本开始游戏，体验 SSE 流式叙事
- 成功标准：用户可在前端选剧本→选角→SSE 流式对话→自由输入→结束；engine_type 全链路必填且为 'corvus'；Legacy 分支保留不激活；Browser E2E 可验证全链路

## 影响范围

- 前端 `game.ts`：startGame 改造、Corvus 会话创建流程
- 前端 `GameView.vue` / `ScriptDetailView.vue`：Corvus 入口和选角 UI
- 前端新增组件：角色候选管理、Corvus 选角界面
- 后端可能需补充 `GET /scripts` 返回 `engine_type` 字段
- 不涉及后端 Corvus 核心逻辑（CR-037 已完成）

## 成功标准

1. 用户可以在前端选择 Corvus 剧本并开始游戏
2. 游戏过程中对话通过 SSE 流式渲染（逐步显示，非一次性返回）
3. 用户可以自由输入文字推进剧情（非预设选项模式）
4. `engine_type` 正确设置为 `'corvus'` 并持久化
5. Legacy 剧本不受影响，仍走原有节点式流程
6. Browser E2E 可验证 Corvus 全链路（选剧本→选角→SSE 对话→自由输入→结束）

## 功能清单

### F1: 剧本选择页 Corvus 入口
- 在 ScriptDetailView 或 GameView 中区分 legacy 剧本和 Corvus 剧本
- Corvus 剧本点击"开始游戏"时走 Corvus 流程

### F2: Corvus 会话创建流程
- 前端调用 `POST /game/session/create` 创建 Corvus 会话
- 前端调用 `POST /game/session/select-player` 选定角色候选
- 会话状态 `engine_type: 'corvus'` 写入 `currentSession`，持久化到 localStorage

### F3: SSE 流式叙事接入
- `submitChoice` 和 `submitCustomInput` 的 Corvus 分支被激活
- SSE 事件正确渲染到前端（text/done/affection 等）
- Corvus 自由输入模式可用（无预设选项，用户自由输入）

### F4: 剧本预设角色选择（2026-09-07 改造）
- 移除自定义角色创建功能
- 选角列表来源改为剧本预设可扮演角色（Character 表 playable=True）
- 前端展示角色卡片（name/description/avatar_url/play_description）
- 用户选择角色后调用 `POST /game/session/select-player` 传 `character_id`
- 后端从 Character 表取角色数据组装传给 Corvus
- 不再使用 `POST /game/player/candidates` 创建自定义候选

### F5: Feature Flag 联动
- 后端返回剧本列表时标记哪些剧本走 Corvus 引擎
- 前端根据标记决定走 legacy 还是 Corvus 流程

## 额外约束（2026-08-17 用户追加）

以下三条约束为本次变更的硬性要求，优先级高于上述功能清单中的冲突项：

### C1: engine_type 字段补齐
- 后端 `corvus_game_sessions` 表已有 `engine_type` 字段（String(10), default='corvus'），无需新增。
- 后端 `GET /scripts` 返回的 script 对象当前**不含** `engine_type` 字段，需新增。
- 前端 `Script` interface 当前**没有** `engine_type` 字段，需新增。
- 前端 `startGame()` 创建 session 时未写入 `engine_type`，需补齐。
- 前端 `resumeSession()` 恢复 session 时未写入 `engine_type`，需补齐。

### C2: 字段全部必填
- 前端 `GameSession.engine_type` 从可选 `?` 改为必填。
- 前端 `Script.engine_type` 新增时即为必填（非可选）。
- 后端 `GET /scripts` 每个 script 对象必须返回 `engine_type` 字段。

### C3: 全部用 Corvus 剧本
- 所有剧本的 `engine_type` 统一为 `'corvus'`。
- 前端 `startGame()` 创建 session 时写入 `engine_type: 'corvus'`。
- 前端 `resumeSession()` 恢复 session 时写入 `engine_type: 'corvus'`。
- 后端 `GET /scripts` 返回每个 script 的 `engine_type: 'corvus'`。
- 保留 SSE Corvus 分支代码；legacy 分支代码保留但不再激活（后续如需可恢复）。

## 风险

1. 前端 Corvus 会话创建流程 UI 复杂度可能超出预期（选角、初始物品等）
2. SSE 流式渲染与现有 legacy 渲染逻辑共存可能产生状态混乱
3. Feature flag 判断逻辑需要后端配合，可能需要修改 scripts API
4. localStorage 会话恢复逻辑需区分 legacy/corvus 两种引擎
