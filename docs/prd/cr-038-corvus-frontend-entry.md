# PRD: CR-038 — Corvus 前端入口接入

## 背景

CR-037 完成了 Corvus-Story-Core 的后端集成（BE 端点、SSE 透传、DB 同步、向量记忆、feature flag），但前端入口未接入。当前前端 `startGame()` 只调用 legacy `POST /game/start`，从不创建 Corvus 会话，导致 `engine_type` 永远为 `undefined`，所有 Corvus SSE 分支代码成为 dead code。用户实际体验仍是内置节点式剧本游戏。

## 问题陈述

- `frontend/src/stores/game.ts` 的 `startGame()` 调用 `POST /game/start`（legacy），不设置 `engine_type`
- Corvus 后端端点 `POST /game/session/create` 和 `POST /game/session/select-player` 已实现但前端无调用
- 前端 SSE 流式分支（game.ts L265、L393）因 `engine_type` 永远非 `'corvus'` 而永远不执行
- 用户无法在 UI 中选择 Corvus 引擎或进入 Corvus 游戏流程

## 目标

让用户可以在前端通过 Corvus 引擎开始游戏，体验 SSE 流式叙事，而非只能玩 legacy 节点剧本。

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

## 成功标准

1. 用户可以在前端选择 Corvus 剧本并开始游戏
2. 游戏过程中对话通过 SSE 流式渲染（逐步显示，非一次性返回）
3. 用户可以自由输入文字推进剧情（非预设选项模式）
4. `engine_type` 正确设置为 `'corvus'` 并持久化
5. Legacy 剧本不受影响，仍走原有节点式流程
6. Browser E2E 可验证 Corvus 全链路（选剧本→选角→SSE 对话→自由输入→结束）

## 影响范围

- 前端 `game.ts`：startGame 改造、Corvus 会话创建流程
- 前端 `GameView.vue` / `ScriptDetailView.vue`：Corvus 入口和选角 UI
- 前端新增组件：角色候选管理、Corvus 选角界面
- 后端可能需补充 `GET /scripts` 返回 `engine_type` 字段
- 不涉及后端 Corvus 核心逻辑（CR-037 已完成）

## 风险

1. 前端 Corvus 会话创建流程 UI 复杂度可能超出预期（选角、初始物品等）
2. SSE 流式渲染与现有 legacy 渲染逻辑共存可能产生状态混乱
3. Feature flag 判断逻辑需要后端配合，可能需要修改 scripts API
4. localStorage 会话恢复逻辑需区分 legacy/corvus 两种引擎
