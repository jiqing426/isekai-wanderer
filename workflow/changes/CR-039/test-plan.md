# Test Plan: CR-039 — Corvus 玩家选项功能

## Test-First Scope

本 CR 为小改造（4 文件，~1.5h），测试先行策略：
- BE 任务（GM/SSE/透传）先写 Delivery E2E 验证命令，再改代码
- FE 任务先写 Browser E2E 测试用例，再改代码
- Red 记录在 DEVELOPMENT 阶段写业务代码前补

## Test Case Artifacts

| 任务编号 | 测试用例产物 | 覆盖验收项 | 状态 |
|---|---|---|---|
| T-039-GM-001 | `curl -N -X POST /api/v1/game/{id}/custom-input` → 检查 gm_update SSE 事件含 playerOptions 字段且类型正确 | AC-039-001, AC-039-002 | Ready |
| T-039-SSE-001 | `curl -N -X POST /api/v1/game/{id}/custom-input` → 检查 gm_update SSE 事件包含 playerOptions 数据字段 | AC-039-003 | Ready |
| T-039-BE-001 | `curl -N -X POST /api/v1/game/{id}/custom-input` → 检查前端收到 choices 格式 `{id, text, hint}` | AC-039-004 | Ready |
| T-039-FE-001 | `tests/e2e/cr039-player-options.spec.ts` → 对话后 ChoicePanel 显示 2-4 个选项 + FreeChatInput 可见 + 点击选项发送 + 无 playerOptions 时 fallback | AC-039-005, AC-039-006, AC-039-007, AC-039-008 | Ready |
| T-039-FE-001 | `tests/e2e/cr039-*.spec.ts` → Legacy 引擎选择功能回归 | AC-039-009 | Ready |
| T-039-GM-001 | 多轮对话 Delivery E2E → 验证选项数量 2-4 个、文字 ≤30 字、情境化 | AC-039-002 | Ready |
| T-039-FE-001 | `cd frontend && npm run build` → vue-tsc + vite build exit 0 | AC-039-005, AC-039-006, AC-039-007, AC-039-008 | Ready |
| T-039-BE-001 | API 契约验证 → SSE 透传后 choices 格式与 api.md 一致 | AC-039-004 | Ready |
| T-039-FE-002 | `tests/e2e/cr039-player-options.spec.ts` → 选角后验证页面显示初始叙事（非"剧情正在展开..."） | AC-039-010 | Ready |
| T-039-FE-003 | `tests/e2e/cr039-player-options.spec.ts` → 通过 UI 流程验证（点击开始游戏 → 选角 → 验证） | AC-039-011 | Ready |
| T-039-FE-004 | `tests/e2e/cr039-player-options.spec.ts` → 选项出现后持续显示 3 秒不被覆盖 | AC-039-012 | Ready |
| T-039-FE-005 | `tests/e2e/cr039-player-options.spec.ts` → SSE 文字不含 [Narrator]/[Character] 元标记 | AC-039-013 | Ready |
| T-039-FE-006 | `tests/e2e/cr039-player-options.spec.ts` → 好感度在对话后更新（禁止 `\|\| true` 绕过） | AC-039-014 | Ready |

## Red Failure Records

| 任务编号 | 命令 | Red 记录 | 补录时间 |
|---|---|---|---|
| T-039-GM-001 | Delivery E2E: `curl -N -X POST .../custom-input` → 检查 playerOptions | 待 DEVELOPMENT 阶段补 | — |
| T-039-SSE-001 | Delivery E2E: 同上 → 检查 SSE 事件格式 | 待 DEVELOPMENT 阶段补 | — |
| T-039-BE-001 | Delivery E2E: 同上 → 检查 choices 映射 | 待 DEVELOPMENT 阶段补 | — |
| T-039-FE-001 | Browser E2E: `npx playwright test tests/e2e/cr039-*.spec.ts` | 待 DEVELOPMENT 阶段补 | — |
| T-039-FE-001 | CI/CD: `cd frontend && npm run build` | 待 DEVELOPMENT 阶段补 | — |
| T-039-FE-002 | Browser E2E: `npx playwright test tests/e2e/cr039-player-options.spec.ts` → 选角后初始叙事 | 待 DEVELOPMENT 阶段补 | — |
| T-039-FE-003 | Browser E2E: `npx playwright test tests/e2e/cr039-player-options.spec.ts` → UI 流程验证 | 待 DEVELOPMENT 阶段补 | — |
| T-039-FE-004 | Browser E2E: `npx playwright test tests/e2e/cr039-player-options.spec.ts` → 选项持续显示 3 秒 | 待 DEVELOPMENT 阶段补 | — |
| T-039-FE-005 | Browser E2E: `npx playwright test tests/e2e/cr039-player-options.spec.ts` → SSE 文字不含元标记 | 待 DEVELOPMENT 阶段补 | — |
| T-039-FE-006 | Browser E2E: `npx playwright test tests/e2e/cr039-player-options.spec.ts` → 好感度对话后更新 | 待 DEVELOPMENT 阶段补 | — |

## CI/CD Evidence Plan

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 记录位置 | 状态 |
|---|---|---|---|---|---|---|
| 前端编译 | DEVELOPMENT 写完 FE 代码后 | `cd frontend && npm run build` (vue-tsc + vite build) | AC-039-005, AC-039-006, AC-039-007, AC-039-008 | FE | `workflow/changes/CR-039/test-report.md` | Ready |
| 后端无新增单元测试 | DEVELOPMENT 完成后 | GM prompt 改动通过 Delivery E2E 验证（无新增自动化单元测试） | AC-039-001, AC-039-002, AC-039-003, AC-039-004 | BE | `workflow/changes/CR-039/test-report.md` | Ready |

## Delivery E2E / Runtime Smoke Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---|---|---|---|---|---|---|---|---|
| T-039-GM-001 | `curl -N -X POST http://localhost:8081/api/v1/game/{id}/custom-input -H "Accept: text/event-stream" -d '{"text":"你好"}'` → 检查 gm_update 事件含 playerOptions 字段且类型为数组 | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | /api/v1/game/{id}/custom-input (SSE) | no | AC-039-001 | `workflow/changes/CR-039/test-report.md` | Ready |
| T-039-GM-001 | 多轮对话 `curl -N -X POST .../custom-input` → 检查每轮选项数量 2-4 个、文字 ≤30 字 | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | /api/v1/game/{id}/custom-input (SSE) | no | AC-039-002 | `workflow/changes/CR-039/test-report.md` | Ready |
| T-039-SSE-001 | `curl -N -X POST .../custom-input` → 检查 gm_update 事件数据包含 playerOptions | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | /api/v1/game/{id}/custom-input (SSE) | no | AC-039-003 | `workflow/changes/CR-039/test-report.md` | Ready |
| T-039-BE-001 | `curl -N -X POST .../custom-input` → 检查前端收到的 choices 格式 `{id, text, hint}` | http://localhost:8081 | http://localhost:8000 | /api/v1/game/{id}/custom-input (SSE) | no | AC-039-004 | `workflow/changes/CR-039/test-report.md` | Ready |

## Browser Interaction E2E Plan

### 断言质量要求（强制）

以下规则适用于 Browser Interaction E2E Plan 的所有 AC 测试用例，在 DESIGN_GATE 前必须满足：

#### 必须通过的硬断言（不可绕过）

| AC 编号 | 硬断言 | 说明 |
|---|---|---|
| AC-039-005 | 1. `choice-panel` 元素必须 visible（`await expect(choicePanel).toBeVisible()`，不允许 `.catch(() => false)` 绕过）<br>2. `.choice-card` 数量必须 ≥ 2（`expect(count).toBeGreaterThanOrEqual(2)`）<br>3. 每个 `.choice-card` 必须有非空 `text` 内容（遍历断言 `textContent.length > 0`）<br>4. 每个 `.choice-card` 必须有 `data-id` 或可点击属性 | 选项面板必须出现且内容完整 |
| AC-039-006 | 1. 必须存在 ≥ 1 个 `.choice-card`（`expect(choiceCount).toBeGreaterThan(0)`，不允许 if/else 绕过）<br>2. 点击选项前记录 `storyText.textContent` 作为 `beforeText`<br>3. 点击选项后等待 SSE 响应完成（监听网络空闲或 `.story-text` 文本变化，不得用固定 `waitForTimeout`）<br>4. 点击后 `afterText !== beforeText`（`expect(afterText).not.toEqual(beforeText)`）<br>5. 点击后 `pendingChoices` 清空 → `.choice-card` 数量为 0 | 选项点击必须触发实质性对话推进 |
| AC-039-008 | 1. `choice-panel` 元素必须 **不可见** 或 **不存在于 DOM**（`await expect(choicePanel).not.toBeVisible()` 或 `await expect(choicePanel).toHaveCount(0)`）<br>2. `FreeChatInput` 输入框必须 visible 且 `enabled`（`await expect(inputArea).toBeVisible()` + `await expect(inputArea).toBeEnabled()`）<br>3. 输入框可 fill 且 inputValue 反映填充值 | 无选项时必须走 fallback 路径 |
| AC-039-010 | 1. `.story-text` 元素必须 visible（不允许只检查 `#app` 可见）<br>2. `textContent` 必须非空且长度 > 10（`expect(text.length).toBeGreaterThan(10)`）<br>3. `textContent` 不得包含 `"剧情正在展开"` | 选角后必须有实质叙事内容 |
| AC-039-007 | 1. `inputArea` 必须 visible 且 enabled（`await expect(inputArea).toBeVisible()` + `await expect(inputArea).toBeEnabled()`）<br>2. 如果 `choice-panel` visible，仍必须断言 `inputArea` visible（不允许走 if/else 跳过）<br>3. `inputArea.fill('test')` 后 `inputValue` 包含 `test` | 有选项时输入框仍可见可用 |

#### 禁止的弱断言

以下断言模式在 Browser E2E 中被 **严格禁止**。代码审查和 QA 执行时发现任何一条即判定对应 AC 不通过：

| 禁止模式 | 原因 | 替代方案 |
|---|---|---|
| `expect(x >= 0).toBeTruthy()` | `0 >= 0` 永真，不检查任何实质内容 | `expect(x).toBeGreaterThan(0)` 或具体数值断言 |
| `expect(x \|\| true).toBeTruthy()` | `\|\| true` 使整个表达式永真 | 移除 `\|\| true`，对 `x` 做直接断言 |
| `expect(page.locator('#app')).toBeVisible()` 作为唯一通过断言 | 只检查页面未崩溃，不检查业务功能 | 必须断言业务元素（`.story-text`、`.choice-card` 等） |
| `if(condition) { 断言 } else { 不断言或弱断言 }` | if/else 绕过关键断言路径 | 移除 if/else，对关键元素做无条件断言；如条件不成立应直接 fail |
| `await page.waitForTimeout(N)` 等待业务结果 | 固定 sleep 不检查中间过程，结果可能未到位 | 使用 `expect(locator).toBeVisible({ timeout })` 或 `expect.poll(() => ...)` 等待条件满足 |
| `.catch(() => false)` 吞掉 `isVisible()` 失败 | 将失败静默转为 false，绕过断言 | 直接 `await expect(locator).toBeVisible()`，让失败抛出 |

#### 新增测试用例

| AC 编号 | 测试描述 | 硬断言 | 用户动作 | 覆盖验收项 | 状态 |
|---|---|---|---|---|---|
| AC-039-012 | 选项出现后持续显示 3 秒不被覆盖 | 1. `.choice-panel` visible 后，等待 3 秒再次断言 `.choice-panel` 仍 visible<br>2. `.choice-card` 数量不变<br>3. 期间不应出现新的 `.story-text` 内容覆盖选项（`storyText` 文本不变） | 对话后选项出现 → 等待 3 秒 → 验证选项仍存在 | AC-039-005 补充 | Ready |
| AC-039-013 | SSE 文字不含元标记 | 1. 遍历 `.story-text` 的全部 textContent<br>2. 断言不包含 `[Narrator]`、`[Character]`、`[GM]`、`[System]` 标记<br>3. 断言不包含 JSON 大括号 `{` 或 `playerOptions` 字面量 | 对话发送 → 等待 SSE 完成 → 检查故事文本 | AC-039-003 补充 | Ready |
| AC-039-014 | 好感度在对话后更新 | 1. 对话前记录 `[class*="affection"]` 区域的 textContent 作为 `beforeAffection`<br>2. 发送对话 → 等待 SSE 完成<br>3. 对话后再次读取 affection 区域 textContent 作为 `afterAffection`<br>4. `expect(afterAffection).not.toEqual(beforeAffection)` 或如果 affection 区域首次出现则 `expect(affectionArea).toBeVisible()`<br>5. 如果 affection 区域不存在，断言失败（不允许 `\|\| true` 绕过） | 对话前记录好感度 → 发送对话 → 对话后验证好感度变化 | AC-038-018 修复 | Ready |

### E2E 用例表

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---|---|---|---|---|---|---|---|---|---|---|
| T-039-FE-001 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr039-player-options.spec.ts --project=chromium --trace on` → 对话后查看选项面板 | Playwright (Chromium) | Corvus 对话结束后 → 查看 ChoicePanel → 可见 ≥2 个选项 + 每个选项有非空 text + FreeChatInput 仍可见可输入 | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | /api/v1/game/{id}/custom-input (SSE) | no | AC-039-005, AC-039-007 | `workflow/changes/CR-039/test-report.md` | Ready |
| T-039-FE-001 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr039-player-options.spec.ts --project=chromium --trace on` → 点击选项 | Playwright (Chromium) | 必须存在 ≥1 个选项 → 记录 beforeText → 点击选项 → 等待 story-text 变化 → 验证 afterText ≠ beforeText + choice-card 数量归 0 | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | /api/v1/game/{id}/custom-input (SSE) | no | AC-039-006 | `workflow/changes/CR-039/test-report.md` | Ready |
| T-039-FE-001 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr039-player-options.spec.ts --project=chromium --trace on` → 无选项时 fallback | Playwright (Chromium) | GM 无 playerOptions 时查看界面 → ChoicePanel 不可见或不存在 + FreeChatInput visible + enabled + 可 fill | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | /api/v1/game/{id}/custom-input (SSE) | no | AC-039-008 | `workflow/changes/CR-039/test-report.md` | Ready |
| T-039-FE-001 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr038-*.spec.ts --project=chromium --trace on` → Legacy 回归 | Playwright (Chromium) | 使用 Legacy 引擎剧本 → 正常分支选择 → Legacy 选择逻辑不受影响 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/{id}/dialogue (SSE) | no | AC-039-009 | `workflow/changes/CR-039/test-report.md` | Ready |
| T-039-FE-002 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr039-player-options.spec.ts --project=chromium --trace on` → 选角后验证初始叙事 | Playwright (Chromium) | 选角完成后 → 查看页面 → 显示初始叙事文本（非"剧情正在展开..."）→ textContent 长度 > 10 | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | /api/v1/game/session/select-player (POST) | no | AC-039-010 | `workflow/changes/CR-039/test-report.md` | Ready |
| T-039-FE-003 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr039-player-options.spec.ts --project=chromium --trace on` → UI 流程验证 | Playwright (Chromium) | 通过 UI 点击开始游戏 → 选角 → 验证进入游戏界面（createCorvusSessionViaUI，不用 API 绕过） | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | /api/v1/game/session/create (POST) + /api/v1/game/session/select-player (POST) | no | AC-039-011 | `workflow/changes/CR-039/test-report.md` | Ready |
| T-039-FE-004 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr039-player-options.spec.ts --project=chromium --trace on` → 选项持续显示 3 秒不被覆盖 | Playwright (Chromium) | 对话后选项出现 → 等待 3 秒 → 验证选项面板仍 visible + choice-card 数量不变 + story-text 文本不变 | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | /api/v1/game/{id}/custom-input (SSE) | no | AC-039-012 | `workflow/changes/CR-039/test-report.md` | Ready |
| T-039-FE-005 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr039-player-options.spec.ts --project=chromium --trace on` → SSE 文字不含元标记 | Playwright (Chromium) | 对话发送 → 等待 SSE 完成 → 遍历 story-text → 断言不含 [Narrator]/[Character]/[GM]/[System] 标记和 JSON 大括号 | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | /api/v1/game/{id}/custom-input (SSE) | no | AC-039-013 | `workflow/changes/CR-039/test-report.md` | Ready |
| T-039-FE-006 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr039-player-options.spec.ts --project=chromium --trace on` → 好感度对话后更新 | Playwright (Chromium) | 对话前记录 affection 区域 textContent → 发送对话 → 等待 SSE 完成 → 断言 affection 区域 textContent 变化或首次出现；禁止 \|\| true 绕过 | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | /api/v1/game/{id}/custom-input (SSE) | no | AC-039-014 | `workflow/changes/CR-039/test-report.md` | Ready |

## Browser E2E Command

```bash
SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr039-*.spec.ts tests/e2e/cr038-*.spec.ts --project=chromium --trace on
```
