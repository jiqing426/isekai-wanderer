# Design: Corvus Frontend Entry (CR-038)

## Overview

本设计文档记录 CR-038 的架构设计过程和差异。CR-038 的目标是把 CR-037 已完成的后端 Corvus-Story-Core 集成能力在前端激活，让用户可以在前端选择 Corvus 剧本 → 选角 → SSE 流式对话 → 自由输入 → 结束。

长期有效的工程事实已拆分同步到对应 `docs/` 主事实源：
- 模块边界和核心流程 → `docs/architecture/architecture.md`
- API 契约和 API/数据/Mock/Runtime 关系 → `docs/api/api.md`
- 数据模型和持久化方式 → `docs/database/database.md`
- 权限和敏感数据 → `docs/security/security.md`
- 重要取舍和不可逆决策 → `docs/decisions/decisions.md`
- 运行时配置 → `docs/runtime/runtime-contract.md`

## Technical Approach

### 1. Legacy 代码保留方式（INIT 附条件 2 决议）

**决策：条件分支保留（`if (engine_type === 'corvus') { ... } else { ... }` 原样保留，不注释、不删除）**

**理由**：
- 前端 `game.ts` 中 `submitChoice` 和 `submitCustomInput` 已有完整的 Corvus SSE 分支和 legacy 分支条件分支代码（CR-037 DEV-008 已实现）。这些条件分支代码当前是 dead code（因为 `engine_type` 永远为 `undefined`，走 else 分支），但代码结构完整。
- CR-038 的改造不是删除 legacy 分支，而是让 `engine_type` 被正确设置为 `'corvus'`，从而使现有的 Corvus 条件分支被激活。Legacy 分支自然不被执行（因为 C3 约束下所有剧本都走 Corvus），但代码保留。
- 条件分支方式比注释方式更好：
  - 注释会导致代码可读性下降，且取消注释时容易出错
  - 条件分支保留了代码的完整性和可测试性
  - 如果未来需要恢复 legacy 引擎，只需将 `engine_type` 改回 `'legacy'` 即可
  - 不需要额外的删除标记或墓碑注释
- `startGame()` 中的 legacy 路径（`POST /game/start`）也保留，但 Corvus 剧本不走该路径。Legacy `startGame` 代码分支不会被删除，只是不被 Corvus 剧本触发。

**具体影响**：
- `submitChoice()`: `if (isCorvus) { SSE 分支 }` 原样保留，`else` 块的 legacy API 调用原样保留
- `submitCustomInput()`: 同上
- `startGame()`: 新增 Corvus 会话创建流程分支，原 legacy `POST /game/start` 路径保留
- `resumeSession()`: 新增 `engine_type` 写入，旧数据兼容处理（无 `engine_type` 视为 `'legacy'`）

### 2. startGame() 改造设计

当前 `startGame()` 流程：
1. 检查 localStorage 是否有保存的会话
2. 调用 `POST /game/start` 创建会话
3. 保存到 localStorage
4. 调用 `fetchDialogue()` 获取初始对话

改造后 `startGame()` 流程（Corvus 剧本）：
1. 检查 localStorage 是否有保存的会话（不变）
2. **新路径**：调用 `POST /api/v1/game/session/create` 创建 Corvus 会话
   - 请求体：`{ script_id: string }`
   - 响应：`{ game_session_id: string (UUID v4), status: 'waiting_select_player' }`
3. 设置 `currentSession.engine_type = 'corvus'`
4. 设置 `currentSession.id = game_session_id`
5. 保存到 localStorage（包含 `engine_type: 'corvus'`）
6. 页面进入选角流程（新增）
7. 选角完成后调用 `POST /api/v1/game/session/select-player`
   - 请求体：`{ game_session_id, player_candidate_id }`
   - 响应：`{ status: 'playing', initial_scene: {...} }`
8. 页面进入游戏对话界面

**原 legacy `POST /game/start` 路径保留**，通过 `engine_type` 判断走哪个路径。C3 约束下所有剧本 `engine_type = 'corvus'`，所以实际都走 Corvus 路径。

### 3. 选角 UI 设计（Q-003 决议）

**决策：模态弹窗（Modal Dialog）**

**理由**：
- 选角是进入游戏前的必要步骤，模态弹窗可以聚焦用户注意力
- 不需要独立路由页面，选角完成后自动进入游戏界面
- 与现有 Naive UI 的 `n-modal` 组件一致
- 触发时机：`startGame()` 创建会话成功后 → 弹出选角 Modal → 用户选择/创建角色 → 确认 → 进入游戏

**流程**：
1. `startGame()` 创建 Corvus 会话成功
2. 选角 Modal 弹出，展示候选角色列表（`GET /game/player/candidates`）
3. 用户可选择已有角色，或在 Modal 内创建新角色
4. 用户点击"确认" → 调用 `POST /game/session/select-player`
5. Modal 关闭，进入游戏对话界面

### 4. 角色候选管理 UI 设计

**独立组件**：`PlayerCandidateModal.vue`
- 嵌套在选角 Modal 内，支持两种模式：
  - 选择模式：展示已有候选列表，点击选择
  - 创建模式：表单（name 必填，personality/backstory/appearance 可选），提交后刷新列表
- 已有候选 < 3 时显示"创建角色"按钮
- 已有候选 = 3 时按钮禁用，显示"已达上限"
- name 为空时前端表单校验失败，显示"name 必填"，不发送 API 请求

### 5. localStorage 旧数据兼容处理（Q-004 决议）

**决策：旧数据（无 engine_type）默认视为 'legacy'**

**处理逻辑**：
```typescript
// resumeSession() 中
const engineType = sessionData.engine_type || 'legacy';
currentSession.value.engine_type = engineType;
```

- 旧 localStorage 数据无 `engine_type` 字段 → 视为 `'legacy'` → 走 legacy 分支
- 新 Corvus 会话数据有 `engine_type: 'corvus'` → 走 Corvus SSE 分支
- 不清除旧数据，不影响旧会话恢复

### 6. POST /game/player/candidates 创建端点（Q-002 决议）

**决策：创建时不接受 initial_inventory 字段**

**请求体**：
```json
{
  "name": "string (≤100, required)",
  "personality": "string (optional)",
  "backstory": "string (optional)",
  "appearance": "string (optional)"
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "id": "uuid-v4",
    "name": "星野",
    "personality": null,
    "backstory": null,
    "appearance": null,
    "initial_inventory": []
  }
}
```

**理由**：`initial_inventory` 由剧本/后端管理，用户创建角色候选时不填写。后端 `PlayerCandidate` model 的 `initial_inventory` 字段默认为空数组。

### 7. 后端 GET /scripts 补充 engine_type

**改动范围**：`backend/app/api/v1/scripts.py` 的 `list_scripts()` 和 `get_script()` 函数。

**实现方式**：在返回的 script 对象中硬编码 `engine_type: 'corvus'`（C3 约束下所有剧本统一为 Corvus）。

**不改动**：`scripts` 表不加 `engine_type` 列（表结构不变）。engine_type 是运行时返回的虚拟字段，值固定为 `'corvus'`。如果未来需要数据库级别区分，再走迁移。

### 8. 前端 Script interface 补齐（C1/C2）

**stores/game.ts 的 `Script` interface**：
```typescript
export interface Script {
  id: string;
  slug: string;
  title: string;
  description: string;
  genre: string;
  cover_image_url?: string;
  engine_type: 'legacy' | 'corvus';  // C1: 新增；C2: 必填（无 ?）
}
```

**api/game.ts 的 `Script` interface**：
```typescript
export interface Script {
  id: string;
  title: string;
  description: string;
  genre: string;
  cover_url?: string;
  cover_image_url?: string;
  is_premium?: boolean;
  tag_list?: string[];
  slug?: string;
  route_count?: number;
  tags?: string[];
  play_count_7d?: number;
  engine_type: 'legacy' | 'corvus';  // C1: 新增；C2: 必填（无 ?）
}
```

### 9. 前端 GameSession interface 补齐（C1/C2）

**stores/game.ts 的 `GameSession` interface**：
```typescript
export interface GameSession {
  id: string;
  script_id: string;
  current_node_id: string;
  status: 'active' | 'completed' | 'abandoned';
  character_id?: string;
  route_id?: string;
  affection_value?: number;
  engine_type: 'legacy' | 'corvus';  // C2: 去掉 ?，改必填
}
```

### 10. SSE 流式渲染设计

现有 `submitChoice()` 和 `submitCustomInput()` 中已有 Corvus SSE 分支代码。激活条件是 `currentSession.engine_type === 'corvus'`。

**SSE 事件处理**（已在 game.ts 中实现，无需改动）：
- `text` → `fullText += data.content`，逐步渲染到 `currentDialogue.text`
- `done` → 更新 `currentDialogue`，设置 `current_node_id`，清空 `pendingChoices`
- `gm_update` → 好感度/道具/标记更新（异步处理，不阻塞文本流）
- `error` → 显示错误提示，用户可重试
- `stream_end` → 关闭 SSE 连接

**新增**：`gm_update` 事件需要更新 NPC 好感度显示和道具列表 UI。当前代码中 `gm_update` 分支为空注释 `// 好感度/道具/标记更新 - 异步处理`。需要补齐实际 UI 更新逻辑。

### 11. choices 为空降级（REQ-FE-005 Scenario 4）

当 Corvus SSE `done` 事件不含 `player_options` 时：
- `pendingChoices` 清空为 `[]`
- `ChoicePanel` 组件根据 `hasChoices` computed 隐藏
- `FreeChatInput` 始终显示
- 用户可自由输入文字推进剧情

现有代码已在 `done` 事件处理中设置 `pendingChoices.value = []`，`hasChoices` computed 返回 `false`。无需额外改动。

## Technology Decisions

| Decision | Selected | Status | Evidence |
|---|---|---|---|
| Legacy 代码保留方式 | 条件分支保留 | Accepted | ADR-0012 (`docs/decisions/decisions.md`); INIT 附条件 2 委托 SA 决定；Architect 确认 |
| 选角 UI 形态 | 模态弹窗 (Modal) | Accepted | ADR-0013 (`docs/decisions/decisions.md`); Q-003 暂缓到设计阶段，SA 决定 |
| POST /game/player/candidates 请求体 | 不含 initial_inventory | Accepted | Q-002 暂缓到设计阶段，SA 决定：由后端管理 initial_inventory；PL 确认 |
| localStorage 旧数据兼容 | 默认视为 'legacy' | Accepted | Q-004 暂缓到设计阶段，SA 决定：默认 'legacy'；PL 确认 |
| GET /scripts engine_type 实现方式 | 运行时虚拟字段，不改表结构 | Accepted | C3 约束下所有剧本统一 'corvus'，无需数据库迁移；Architect 确认 |
| 角色候选创建 UI 富文本编辑器 | 不做，使用 textarea | Not Required | Q-001 已 resolved：暂缓到后续迭代，使用普通 textarea |

## Document Sync

| Target Doc | Status | Summary / Evidence |
|---|---|---|
| `docs/architecture/architecture.md` | Synced | 新增 CR-038 模块依赖：前端 startGame Corvus 分支、选角 Modal、PlayerCandidateModal 组件、SSE gm_update UI 更新；Engine Dispatcher 条件分支保留策略 |
| `docs/api/api.md` | Synced | 新增 POST /game/player/candidates 端点（1 new, total 67）；扩展 GET /scripts 和 GET /scripts/{id} 返回 engine_type 字段；API/数据/Mock/Runtime 关系更新 |
| `docs/database/database.md` | Synced | Not Required: 无新增表或列变更。player_candidates 表已在 CR-037 创建，本 CR 不改表结构。GET /scripts 的 engine_type 为运行时虚拟字段，不持久化 |
| `docs/security/security.md` | Synced | 新增 CR-038 安全：角色候选创建数量限制（后端 ≤3 校验）、前端表单校验（name 必填）、localStorage 旧数据兼容安全（默认 legacy 不影响 Corvus 流程） |
| `docs/decisions/decisions.md` | Synced | 新增 ADR-0012: Legacy 条件分支保留策略；ADR-0013: 选角 UI 模态弹窗决策 |
| `docs/runtime/runtime-contract.md` | Synced | 新增 CR-038 Additions：browser_e2e_command 扩展 cr038 测试文件、browser_e2e_user_actions 新增 14 条用户动作、POST /game/player/candidates 端点、GET /scripts engine_type 字段 |
