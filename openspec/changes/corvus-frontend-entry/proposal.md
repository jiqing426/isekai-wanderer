# OpenSpec Change: corvus-frontend-entry

## Why

- CR-037 已完成后端 Corvus-Story-Core 全链路集成，但前端入口未接入，用户仍玩 legacy 节点式剧本
- 前端 startGame() 从不创建 Corvus 会话，engine_type 永远为 undefined，所有 Corvus SSE 分支代码成为 dead code
- CR-037 的业务价值为零，~18h 后端投入为沉没成本
- 本 CR 让用户可以在前端通过 Corvus 引擎开始游戏，体验 SSE 流式叙事，激活已投入的后端能力

### 背景和动机

CR-037 已完成后端 Corvus-Story-Core 全链路集成（SSE 透传、DB 同步、向量记忆、feature flag、5 张表、28 条 AC 全部 covered），但前端入口未接入。当前前端 `startGame()` 只调用 legacy `POST /game/start`，从不创建 Corvus 会话，`engine_type` 永远为 `undefined`，所有 Corvus SSE 分支代码成为 dead code。用户实际体验仍是 legacy 节点式剧本游戏，CR-037 的业务价值为零。

本 CR 目标：让用户可以在前端通过 Corvus 引擎开始游戏，体验 SSE 流式叙事。

### 业务价值

激活 CR-037 已投入的后端能力（~18h 工程量），交付用户可感知的流式叙事体验。不做本 CR，CR-037 的投入即为沉没成本。

## What Changes

### 变更内容

1. **前端 `startGame()` 改造**：不再只调 `POST /game/start`；Corvus 剧本走 `POST /game/session/create` → 选角 → `POST /game/session/select-player` 流程，写入 `engine_type: 'corvus'`
2. **前端 SSE 分支激活**：`submitChoice` / `submitCustomInput` 的 Corvus 分支可用，SSE 事件（text/done/gm_update/stream_end/error）正确渲染到 StoryPanel
3. **前端 Interface 补齐（C1/C2）**：
   - `Script` interface 新增 `engine_type: 'legacy' | 'corvus'`（必填，不可选）
   - `GameSession` interface 的 `engine_type` 从 `?` 可选改为必填
4. **前端 `resumeSession()` 补齐**：恢复 session 时写入 `engine_type`，localStorage 旧数据兼容处理
5. **后端 `GET /scripts` 补充 `engine_type` 字段（C1/C3）**：每个 script 对象返回 `engine_type: 'corvus'`
6. **角色候选管理 UI（F4）**：前端可查看/创建/选择 player_candidates，与后端 `GET /game/player/candidates` 和 `POST /game/session/select-player` 对接
7. **Legacy 分支保留但不激活（C3）**：legacy 代码路径保留，但全部剧本统一走 Corvus

### 角色候选字段定义（INIT 附条件 1 必答）

基于 CR-037 后端 `PlayerCandidate` 模型和 PRD §3.1 定义，角色候选创建时用户需填写的字段：

| 字段 | 类型 | 必填 | 说明 | 建议默认值 |
| --- | --- | --- | --- | --- |
| name | string (≤100) | ✅ 必填 | 角色名字，用户自定义 | 无，必须由用户填写 |
| personality | string | ❌ 可选 | 角色性格描述 | 空 string |
| backstory | string | ❌ 可选 | 角色完整背景故事 | 空 string |
| appearance | string | ❌ 可选 | 角色外貌描述 | 空 string |

**设计依据**：后端 `PlayerCandidate` model 中 `name` 为 `nullable=False`，其余三个字段为 `nullable=True`。PRD §3.1 的 JSON 结构包含 `initial_inventory` 字段，但该字段由后端管理（剧本初始道具），用户创建时不填写。

**UI 约束**：
- name 必填，前端表单需校验非空
- personality / backstory / appearance 可选但建议填写，UI 需展示输入框并标注"可选"
- 用户最多 3 个候选角色（PRD §6 强制业务规则），前端需限制创建数量
- 创建接口为 `POST /game/player/candidates`（本 CR 新增后端端点，当前后端只有 GET）

> 注意：后端当前只有 `GET /game/player/candidates`（查询），缺少 `POST /game/player/candidates`（创建）。本 CR 需要 BE 新增创建端点。见 specs/frontend/spec.md REQ-FE-004。

## Non-Goals

### 不做范围

- 不改后端 Corvus 核心逻辑（CR-037 已完成）
- 不做 Corvus/Legacy 双引擎 UI 切换（C3 已约束全部用 Corvus，双引擎展示降级为后续优化）
- 不做新剧本内容创作
- 不做性能优化 / 压测
- 不做角色候选的编辑和删除（本期只做查看/创建/选择，编辑/删除留后续迭代）
- 不做 initial_inventory 的前端管理（由后端/剧本配置管理）

## Success Criteria

- 用户可以在前端选择剧本并开始 Corvus 游戏（选剧本 → 选角 → SSE 对话 → 自由输入 → 结束）
- 游戏过程中对话通过 SSE 流式渲染（逐步显示，非一次性返回）
- 用户可以自由输入文字推进剧情（非预设选项模式）
- engine_type 在前后端全链路必填且为 'corvus'（C1/C2/C3）
- Legacy 分支代码保留但不激活，不影响 Corvus 流程
- Browser E2E 可验证 Corvus 全链路（选剧本 → 选角 → SSE 对话 → 自由输入 → 结束）
- 角色候选管理：用户可查看已有候选（≤3）、创建新候选、选择候选进入游戏

## Impact

### 影响范围

| 层面 | 影响 |
| --- | --- |
| 前端 `stores/game.ts` | `Script` interface 新增 `engine_type` 必填；`GameSession.engine_type` 改必填；`startGame()` 新增 Corvus 会话创建分支；`resumeSession()` 补 `engine_type` |
| 前端 `api/game.ts` | `Script` interface 同步新增 `engine_type`；新增 Corvus 会话/选角/候选管理 API 调用 |
| 前端视图 | `ScriptDetailView.vue` / `GameView.vue` 需区分引擎类型，新增选角 UI |
| 前端新增组件 | 角色候选管理界面、Corvus 选角界面 |
| 后端 `scripts.py` | `GET /scripts` 和 `GET /scripts/{id}` 返回 `engine_type: 'corvus'` |
| 后端 `game.py` | 新增 `POST /game/player/candidates` 创建端点（当前只有 GET） |
| 后端 Corvus 核心 | 不涉及（CR-037 已完成） |
| localStorage | 会话恢复需区分 `engine_type`，旧数据兼容处理 |

### 硬性约束影响

| 约束 | 影响 |
| --- | --- |
| C1: engine_type 字段补齐 | 前端 Script/GameSession interface 补字段；后端 GET /scripts 补字段 |
| C2: 字段全部必填 | 前端 Script.engine_type 和 GameSession.engine_type 去掉 `?` 可选标记 |
| C3: 全部用 Corvus | startGame/resumeSession 写入 'corvus'；GET /scripts 返回 'corvus'；legacy 分支保留不激活 |

## Open Questions

### 待澄清问题

| Q 编号 | Question | Blocks MVP | Status | User Answer | Resolution | Shown to User |
| --- | --- | --- | --- | --- | --- | --- |
| Q-001 | 角色候选创建 UI 是否需要富文本编辑器（personality/backstory 可能较长）？ | 否 | resolved | 暂缓：使用普通 textarea，富文本编辑器留后续迭代 | PRD 自动入口已记录，暂缓到后续迭代 | PRD 自动入口已记录，暂缓到后续迭代/设计阶段 |
| Q-002 | 后端 `POST /game/player/candidates` 创建端点的请求体格式：是否需要 `initial_inventory` 字段？ | 否 | resolved | 暂缓：创建时不接受 initial_inventory（由剧本/后端管理），只接受 name/personality/backstory/appearance | 非阻塞，SA 在 DESIGN 阶段最终确定 API 契约 | PRD 自动入口已记录，暂缓到设计阶段 |
| Q-003 | 前端选角 UI 是模态弹窗还是独立页面？ | 否 | resolved | 暂缓：建议模态弹窗（进入游戏前的选角步骤） | 非阻塞，SA 在 DESIGN 阶段决定 | PRD 自动入口已记录，暂缓到设计阶段 |
| Q-004 | localStorage 中旧会话数据（无 engine_type 字段）如何兼容？默认视为 'legacy' 还是清除？ | 否 | resolved | 暂缓：默认视为 'legacy'，不影响旧会话恢复 | 非阻塞 | PRD 自动入口已记录，暂缓到设计阶段 |

**结论**：无阻塞 MVP 的待澄清问题。Q-001~Q-004 均为非阻塞，已记录暂缓依据。角色候选字段定义（INIT 附条件 1）已在 What Changes 章节明确回答。
