# Spec: Frontend — Corvus Frontend Entry

## Requirements

### Requirement: REQ-FE-001: Script interface 补齐 engine_type 必填字段

**Priority**: P0

前端 `Script` interface（`stores/game.ts` 和 `api/game.ts`）必须新增 `engine_type` 字段，类型为 `'legacy' | 'corvus'`，必填（非可选）。

#### Scenario: Script interface 定义

- **Given** 前端 `Script` interface 定义
- **When** TypeScript 编译检查
- **Then** `engine_type: 'legacy' | 'corvus'` 字段存在且无 `?` 可选标记
- **And** `npm run build` 编译通过

### Requirement: REQ-FE-002: GameSession interface engine_type 改必填

**Priority**: P0

前端 `GameSession` interface 的 `engine_type` 字段从 `engine_type?: 'legacy' | 'corvus'` 改为 `engine_type: 'legacy' | 'corvus'`（去掉 `?` 可选标记）。

#### Scenario: GameSession interface 定义

- **Given** 前端 `GameSession` interface 定义
- **When** TypeScript 编译检查
- **Then** `engine_type: 'legacy' | 'corvus'` 字段存在且无 `?` 可选标记
- **And** `npm run build` 编译通过

### Requirement: REQ-FE-003: startGame() 改造 — Corvus 会话创建流程

**Priority**: P0

前端 `startGame()` 函数改造：Corvus 剧本不走 `POST /game/start`，改走 Corvus 会话创建流程。

#### Scenario: Corvus 剧本开始游戏

- **Given** 用户在剧本选择页选择一个剧本（Script.engine_type = 'corvus'）
- **When** 用户点击"开始游戏"
- **Then** 前端调用 `POST /api/v1/game/session/create` 创建 Corvus 会话
- **And** 返回 `game_session_id`（UUID v4）
- **And** 前端设置 `currentSession.engine_type = 'corvus'`
- **And** 前端写入 `currentSession.id = game_session_id`
- **And** localStorage 保存 session（包含 `engine_type: 'corvus'`）
- **And** 页面进入选角流程或游戏界面

**验证标注**：需 Browser Interaction E2E（用户点击"开始游戏" → 可观察结果：进入选角/游戏界面）

#### Scenario: Corvus 会话创建后进入选角

- **Given** Corvus 会话已创建，status = `waiting_select_player`
- **When** 前端调用 `GET /api/v1/game/scripts/{script_id}/characters` 获取预设角色列表
- **Then** 返回该剧本可扮演角色列表（Character 表 `playable=True`）
- **And** 页面展示预设角色选择界面（角色卡片：name / description / avatar_url / play_description）

**验证标注**：需 Browser Interaction E2E（用户看到角色卡片 → 可观察结果：可选择角色）

#### Scenario: 选定预设角色后进入游戏

- **Given** 用户在选角界面选择一个预设角色
- **When** 前端调用 `POST /api/v1/game/session/select-player`，传入 `game_session_id` + `character_id`（Character 表 UUID）
- **Then** 会话 status 变为 `playing`
- **And** 前端设置 `currentSession.engine_type = 'corvus'`
- **And** 页面进入游戏对话界面，开始 SSE 流式对话

**验证标注**：需 Browser Interaction E2E + API/DB/Runtime 契约验证

### Requirement: REQ-FE-004: 剧本预设角色选择 UI

**Priority**: P0

**范围变更 (2026-09-07)**：原 REQ-FE-004（角色候选管理 UI：查看/创建/选择 player_candidates）已移除创建功能。改为剧本预设角色选择 UI：展示预设角色列表、选择角色进入游戏。不再有创建表单、name 必填校验、≤3 限制。

#### Scenario: 查看预设角色列表

- **Given** 用户已创建 Corvus 会话，进入选角界面
- **When** 前端调用 `GET /api/v1/game/scripts/{script_id}/characters`
- **Then** 页面展示预设角色卡片（name / description / avatar_url / play_description）
- **And** 数据来源为 Character 表 `playable=True` 记录

**验证标注**：需 Browser Interaction E2E（用户打开选角界面 → 可观察结果：可见预设角色卡片列表）

#### Scenario: 选择预设角色进入游戏

- **Given** 用户在选角界面
- **When** 用户点击某个角色卡片
- **Then** 该角色高亮选中
- **And** 用户点击"确认"进入游戏
- **And** 前端调用 `POST /api/v1/game/session/select-player` 传 `character_id`

**验证标注**：需 Browser Interaction E2E（用户点击角色 → 点击确认 → 可观察结果：进入游戏界面）

### Requirement: REQ-FE-005: SSE 流式叙事分支激活

**Priority**: P0

前端 `submitChoice` / `submitCustomInput` 的 Corvus 分支激活，SSE 事件正确渲染。

#### Scenario: Corvus 自由输入 SSE 流式渲染

- **Given** 用户在 Corvus 游戏对话界面，engine_type = 'corvus'
- **When** 用户在输入框输入文字 → 点击发送
- **Then** 前端走 Corvus SSE 分支（不走 legacy `POST /game/choice`）
- **And** SSE 事件 `text` 逐步渲染到 StoryPanel（逐字/逐段显示，非一次性返回）
- **And** SSE `done` 事件到达后，流式渲染结束
- **And** `pendingChoices` 清空（或设置为 Corvus 返回的选项，如有）

**验证标注**：需 Browser Interaction E2E（用户输入文字 → 点击发送 → 可观察结果：文字逐步渲染）

#### Scenario: Corvus SSE gm_update 事件处理

- **Given** Corvus SSE 流中
- **When** 收到 `gm_update` 事件，包含 `affection_delta` 和 `inventory_changes`
- **Then** 前端更新对应 NPC 好感度显示
- **And** 前端更新道具列表
- **And** 不阻塞文本流式渲染

**验证标注**：需 API/DB/Runtime 契约验证

#### Scenario: Corvus SSE error 事件处理

- **Given** Corvus SSE 流中
- **When** 收到 `error` 事件或连接中断
- **Then** 前端显示错误提示
- **And** 用户可点击重试

**验证标注**：需 Browser Interaction E2E（模拟断连 → 可观察结果：错误提示显示，重试可用）

#### Scenario: Corvus 无预设选项降级

- **Given** Corvus 返回的 SSE done 事件不含 player_options
- **When** done 事件到达
- **Then** ChoicePanel 隐藏
- **And** FreeChatInput 始终显示
- **And** 用户可自由输入文字推进剧情

**验证标注**：需 Browser Interaction E2E（完成一轮对话 → 可观察结果：输入框可见可用）

### Requirement: REQ-FE-006: resumeSession() 补齐 engine_type

**Priority**: P0

前端 `resumeSession()` 恢复 session 时写入 `engine_type`。

#### Scenario: 恢复 Corvus 会话

- **Given** localStorage 中存在 Corvus 会话（含 engine_type: 'corvus'）
- **When** 前端调用 `resumeSession(sessionId)`
- **Then** `currentSession.engine_type` 设置为 `'corvus'`
- **And** 后续对话走 Corvus SSE 分支

**验证标注**：需 API/DB/Runtime 契约验证

#### Scenario: 旧数据兼容（无 engine_type）

- **Given** localStorage 中存在旧会话（无 engine_type 字段）
- **When** 前端恢复该会话
- **Then** 默认 `engine_type` 视为 `'legacy'`（Q-004 暂缓建议）
- **And** 走 legacy 分支

**验证标注**：需 Browser Interaction E2E

### Requirement: REQ-FE-007: 剧本选择页区分引擎类型

**Priority**: P1

前端剧本选择页根据 `Script.engine_type` 区分 Corvus 和 legacy 剧本（C3 约束下全部为 Corvus，但 UI 逻辑需读取该字段决定流程）。

#### Scenario: 剧本列表展示 engine_type

- **Given** 前端加载剧本列表 `GET /scripts`
- **When** 返回数据包含 `engine_type` 字段
- **Then** 每个 Script 对象的 `engine_type` 被正确解析
- **And** 点击"开始游戏"时根据 `engine_type` 走对应流程

**验证标注**：需 Browser Interaction E2E

#### Scenario: Legacy 剧本保留不激活

- **Given** C3 约束下全部剧本 engine_type = 'corvus'
- **When** 用户选择任意剧本
- **Then** 走 Corvus 流程
- **And** Legacy 代码路径不被执行

**验证标注**：需 Browser Interaction E2E
