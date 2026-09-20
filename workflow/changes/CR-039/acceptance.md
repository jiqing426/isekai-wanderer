# Acceptance: CR-039 — Corvus 玩家选项功能

| 验收编号 | 需求编号 | 优先级 | 来源规格 | 验收标准 | 设计落点 | OpenSpec Task | 实现证据 | 测试用例 / 验证命令 | 状态 | 覆盖状态 | 未覆盖原因 | PL 处理 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AC-039-001 | REQ-GM-001 | P0 | `openspec/changes/corvus-player-options/specs/capability/spec.md` | GM 输出的 JSON 中包含 `playerOptions` 字段；类型为数组；每元素含 `text`（必填，string）和 `hint`（可选，string）；数组长度 0-4 | Corvus `gameMaster.ts` GM_SYSTEM_PROMPT | T-039-GM-001 | ✅ gameMaster.ts GM_SYSTEM_PROMPT 新增 playerOptions schema + 指令规则；parseGameMasterOutput 解析 playerOptions | TC-039-001: `curl -N -X POST /api/v1/game/{id}/custom-input` → 检查 gm_update SSE 事件含 playerOptions 字段且类型正确 | Verified | covered | — | — | C1: GM 调优 ≤0.5h，已完成；Delivery E2E 验证通过 |
| AC-039-002 | REQ-GM-001 | P0 | `openspec/changes/corvus-player-options/specs/capability/spec.md` | 每轮 GM 输出 2-4 个选项（纯叙事过渡场景可为空数组）；选项文字 ≤30 字；选项之间有区分度 | Corvus `gameMaster.ts` GM_SYSTEM_PROMPT | T-039-GM-001 | ✅ GM prompt 含选项生成规则：2-4 个情境化选项、≤30 字、空场景返回空数组 | TC-039-006: 多轮对话 Delivery E2E 验证选项数量和内容情境化 | Verified | covered | — | — | 纯叙事过渡可为空数组；Delivery E2E 验证通过（测试生成 3-4 个选项） |
| AC-039-003 | REQ-SSE-001 | P0 | `openspec/changes/corvus-player-options/specs/capability/spec.md` | `gm_update` SSE 事件包含 `playerOptions` 数据字段 | Corvus `chat.ts` writeSseEvent | T-039-SSE-001 | ✅ chat.ts writeSseEvent gm-complete case 提取 event.data.playerOptions 并加入 gm_update SSE 事件 | TC-039-003: `curl -N -X POST /api/v1/game/{id}/custom-input` → 检查 SSE 事件含 playerOptions | Verified | covered | — | — | Delivery E2E 验证通过 |
| AC-039-004 | REQ-SSE-001 | P0 | `openspec/changes/corvus-player-options/specs/capability/spec.md` | 后端 SSE 透传将 `playerOptions` 映射为 `choices` 格式（`{ id: string, text: string, hint: string }`）；前端收到 `choices` 格式数据 | 后端 `game.py` SSE 透传 | T-039-BE-001 | ✅ corvus_adapter.py SSETranslator.translate gm_update case 将 playerOptions 映射为 choices: [{id, text, hint}] | TC-039-004: `curl -N -X POST /api/v1/game/{id}/custom-input` → 检查前端收到 choices 格式 `{id, text, hint}` | Verified | covered | — | — | Delivery E2E 验证通过；API/DB/Runtime 契约验证 |
| AC-039-005 | REQ-FE-001 | P0 | `openspec/changes/corvus-player-options/specs/capability/spec.md` | 对话结束后 ChoicePanel 显示 2-4 个选项；`pendingChoices` 被赋值；`hasChoices` 变为 true | 前端 `game.ts` gm_update 处理 | T-039-FE-001 | ✅ game.ts gm_update 事件处理中 player_options/choices 赋值到 pendingChoices；ChoicePanel 复用已有组件 | TC-039-005: Browser E2E `tests/e2e/cr039-player-options.spec.ts` → 对话后可见选项 | Verified | covered | — | — | Browser E2E AC-005 passed |
| AC-039-006 | REQ-FE-001 | P0 | `openspec/changes/corvus-player-options/specs/capability/spec.md` | 玩家点击选项 → 以选项文字作为 custom-input 发送 → SSE 正常流式回应；`pendingChoices` 清空 | 前端 `game.ts` 选项点击逻辑 | T-039-FE-001 | ✅ GameView.vue handleChoice 增加 Corvus 分支调用 submitCustomInput(choice.text)；done 事件清空 pendingChoices | TC-039-006: Browser E2E `tests/e2e/cr039-player-options.spec.ts` → 点击选项 → SSE 回应 | Verified | covered | — | — | Browser E2E AC-006 passed |
| AC-039-007 | REQ-FE-001 | P0 | `openspec/changes/corvus-player-options/specs/capability/spec.md` | FreeChatInput 在有选项时仍显示；玩家可自由输入文字 | 前端 `game.ts` + ChoicePanel | T-039-FE-001 | ✅ FreeChatInput v-if="!game.isEnded" 始终渲染，有选项时不隐藏 | TC-039-005: Browser E2E `tests/e2e/cr039-player-options.spec.ts` → 有选项时输入框可见 | Verified | covered | — | — | Browser E2E AC-007 passed |
| AC-039-008 | REQ-FE-002 | P0 | `openspec/changes/corvus-player-options/specs/capability/spec.md` | GM 未返回 `playerOptions` 时，`pendingChoices` 为空数组，`hasChoices` 为 false，ChoicePanel 隐藏，FreeChatInput 正常显示 | 前端 `game.ts` fallback 逻辑 | T-039-FE-001 | ✅ gm_update 事件不含 player_options 时 pendingChoices 保持空数组，hasChoices=false，ChoicePanel 隐藏 | TC-039-008: Browser E2E `tests/e2e/cr039-player-options.spec.ts` → 无选项时 fallback | Verified | covered | — | — | Browser E2E AC-008 passed |
| AC-039-009 | REQ-FE-002 | P1 | `openspec/changes/corvus-player-options/specs/capability/spec.md` | Legacy 引擎选择逻辑不受影响；`choices` 来源仍是 NodeChoice 表 | 不改动 Legacy 代码 | T-039-FE-001 | ✅ Legacy 代码未改动；CR-038 E2E 4/4 passed 无回归 | TC-039-009: Regression `tests/e2e/cr038-*.spec.ts` 不回归 | Verified | covered | — | — | Browser E2E AC-009 regression passed |
| AC-039-010 | REQ-FE-001 | P0 | `workflow/changes/CR-039/acceptance.md` | 选角后页面显示初始叙事（非"剧情正在展开..."） | 前端 `PlayerCandidateModal.vue` + `ScriptDetailView.vue` + `game.ts` + `GameView.vue` | T-039-FE-002 | ✅ PlayerCandidateModal emit initial_scene；ScriptDetailView 存 sessionStorage；game.ts resumeSession 从 sessionStorage 取 opening_text；GameView 自动发送初始消息 | TC-039-010: Browser E2E `tests/e2e/cr039-player-options.spec.ts` → 选角后验证初始叙事 | Verified | covered | — | — | Browser E2E AC-010 passed |
| AC-039-011 | REQ-FE-001 | P0 | `workflow/changes/CR-039/acceptance.md` | E2E 测试通过 UI 流程（点击开始游戏 → 选角 → 验证） | `frontend/tests/e2e/cr039-player-options.spec.ts` | T-039-FE-003 | ✅ AC-039-005 测试改为通过 UI 流程，新增 AC-039-010 测试 | TC-039-011: Browser E2E `tests/e2e/cr039-player-options.spec.ts` → UI 流程验证 | Verified | covered | — | — | Browser E2E AC-011 passed |

## 状态规则

- `覆盖状态` 只允许使用 `covered`、`not_covered`、`manual_pending`、`deferred_with_approval`、`out_of_scope_with_reason`。
- P0/P1 验收项不得缺少 `覆盖状态`、`未覆盖原因` 或 `PL 处理`。
- 发布关口前，P0/P1 不能是 `not_covered`。

## Q 编号

无阻塞 MVP 的待澄清问题。所有需求范围已在 CEO INIT 阶段确认，附条件 C1（GM prompt 调优 ≤0.5h 超时以 fallback 上线）已反映在 AC-039-001 备注中。

## R/C/U/D 完整性检查

本 CR 不涉及 CRUD 实体操作。`playerOptions` 是 LLM 动态生成的运行时数据，不持久化到数据库，不新增 API 端点。无需 R/C/U/D 检查。

## 下游测试和验证契约

| AC 编号 | 验证类型 | 用户动作 / 数据状态 | 可观察结果 |
| --- | --- | --- | --- |
| AC-039-001 | Delivery E2E | 发送 custom-input → 检查 gm_update SSE 事件 | playerOptions 字段存在且类型正确 |
| AC-039-002 | Delivery E2E | 多轮对话 → 检查每轮选项数量和内容 | 2-4 个选项（或纯叙事过渡为空数组），文字 ≤30 字 |
| AC-039-003 | Delivery E2E | 发送 custom-input → 检查 gm_update SSE 事件 | 事件数据包含 playerOptions 字段 |
| AC-039-004 | Delivery E2E + API 契约 | 后端 SSE 透传 → 检查前端收到数据格式 | choices 格式 `{ id, text, hint }` |
| AC-039-005 | Browser Interaction E2E | 对话结束后查看选项面板 | ChoicePanel 显示 2-4 个选项 |
| AC-039-006 | Browser Interaction E2E | 点击某个选项 | SSE 流式回应开始，pendingChoices 清空 |
| AC-039-007 | Browser Interaction E2E | 有选项时查看输入框 | FreeChatInput 可见且可输入 |
| AC-039-008 | Browser Interaction E2E | GM 无选项时查看界面 | ChoicePanel 隐藏，FreeChatInput 正常显示 |
| AC-039-009 | Browser Interaction E2E (Regression) | 使用 Legacy 引擎剧本 → 查看选择功能 | Legacy 选择逻辑不受影响 |

| AC-039-010 | REQ-FE-001 | P0 | `openspec/changes/corvus-player-options/specs/frontend/spec.md` | Corvus 游戏选角完成后，页面显示初始叙事文本（非"剧情正在展开..."） | 前端 `PlayerCandidateModal.vue` 选角后赋值 currentDialogue | T-039-FE-002 | ✅ PlayerCandidateModal emit initial_scene；game.ts resumeSession 取 opening_text；GameView 自动发送初始消息 | E2E: 选角后页面显示初始叙事 | Verified | covered | — | — | Browser E2E AC-010 passed |
| AC-039-011 | REQ-FE-001 | P0 | `openspec/changes/corvus-player-options/specs/frontend/spec.md` | E2E 测试通过 UI 流程验证：开始游戏 → 选角 → 初始叙事显示（不用 API 绕过） | E2E `cr039-player-options.spec.ts` | T-039-FE-003 | ✅ AC-039-005 测试改为通过 UI 流程，新增 AC-039-010 测试 | Browser E2E: UI 流程验证 | Verified | covered | — | — | Browser E2E AC-011 passed |
