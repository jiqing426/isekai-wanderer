# Change: CR-038 — Corvus 前端入口接入

- **CR ID**: CR-038
- **Change Name**: corvus-frontend-entry
- **Created At**: 2026-08-17T09:00:00+08:00
- **Status**: intake
- **Source**: 用户反馈 — CR-037 后端集成已完成但前端入口未接入，用户实际仍玩 legacy 内置游戏

## 变更目标

让用户可以在前端通过 Corvus 引擎开始游戏，体验 SSE 流式叙事，而非只能玩 legacy 节点剧本。

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

### F4: 角色候选管理
- 前端可查看/创建/选择角色候选（player_candidates）
- 与后端 `GET/POST /game/session/{id}/player-candidates` 对接

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
