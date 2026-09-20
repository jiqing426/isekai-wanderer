# Design: CR-039 — Corvus 玩家选项功能

## Overview

- CR-039 在 Corvus 引擎 SSE 流式对话中增加 GM 动态生成的玩家选项，每轮对话后 GM 生成 2-4 个情境化选项
- 改动范围小（4 文件，~1.5h），不新增端点/端口/DB 表/API，复用已有 ChoicePanel 组件
- 长期有效的工程事实已拆分同步到对应 `docs/` 主事实源

## Technical Approach

### 1. Corvus gameMaster.ts — GM prompt 扩展

在 `GM_SYSTEM_PROMPT` 的 JSON schema 中增加 `playerOptions` 字段：

```json
"playerOptions": [
  { "text": "string — 选项文字（≤30字）", "hint": "string — 简短提示（可选）" }
]
```

GM 指令追加：
- 根据当前对话上下文和场景，生成 2-4 个情境化选项
- 选项应反映不同的态度、行动或对话方向
- 选项文字简洁（≤30 字），让玩家快速理解
- 如果当前场景不适合提供选项（如纯叙事过渡），返回空数组 `[]`

**C1 附条件落实**：GM prompt 调优 ≤0.5h。如果超时，GM prompt 中 `playerOptions` 字段保持不完善，前端 fallback 到空数组 = 纯自由输入。选项质量后续迭代。此约束已写入 T-039-GM-001 任务单。

### 2. Corvus chat.ts — SSE 事件扩展

在 `writeSseEvent` 的 `gm_update` case 中，将 `playerOptions` 加入推送数据。GM JSON 输出中 `playerOptions` 字段直接透传到 SSE 事件数据中。

### 3. 后端 game.py — SSE 透传映射

在 Corvus SSE 透传逻辑中，将 `gm_update` 事件中的 `playerOptions` 映射为前端期望的 `choices` 格式：

```python
if data.get("playerOptions"):
    choices = [{"id": str(i), "text": opt["text"], "hint": opt.get("hint", "")}
               for i, opt in enumerate(data["playerOptions"])]
    # 通过 SSE 推送 choices
```

映射规则：
- `playerOptions` 数组 → `choices` 数组
- 每个选项 `text` → `text`（保持不变）
- 每个选项 `hint` → `hint`（默认空字符串）
- 生成 `id` = 数组索引字符串（"0", "1", ...）
- `playerOptions` 为空数组或不存在时，`choices` 为空数组

### 4. 前端 game.ts — gm_update 事件处理

在 `gm_update` 事件处理中增加：

```ts
if (data.player_options || data.choices) {
  pendingChoices.value = data.player_options || data.choices || [];
}
```

选项点击后调用 `submitCustomInput(option.text)`，清空 `pendingChoices`。

**向后兼容**：
- GM 未返回 `playerOptions` 时，`pendingChoices` 保持空数组，`hasChoices` 为 false，ChoicePanel 隐藏，FreeChatInput 正常显示
- Legacy 引擎的 `choices` 来源仍是 NodeChoice 表，不受影响

### 模块依赖方向

```txt
gameMaster.ts (GM prompt) ──> chat.ts (SSE 事件) ──> game.py (后端透传映射) ──> game.ts (前端处理)
```

- T-039-GM-001 必须先完成（GM 输出格式定义）
- T-039-SSE-001 和 T-039-BE-001 可并行（SSE 事件扩展 + 后端透传映射）
- T-039-FE-001 依赖 T-039-BE-001（前端需要后端透传的 `choices` 格式）

## Technology Decisions

| 选型项 | 选择 | 状态 | 确认依据 |
|---|---|---|---|
| 新增技术选型 | Not Required | Not Required | 本 CR 不引入新框架/语言/数据库/云服务/工具链；复用已有 Corvus+FastAPI+Vue3 技术栈；无不可逆架构取舍 |

## Document Sync

| 目标文档 | 状态 | 说明 |
|---|---|---|
| docs/architecture/architecture.md | Not Required | 无新增模块/组件边界变更；playerOptions 是已有 gm_update SSE 事件的字段扩展，不改变模块职责 |
| docs/api/api.md | Synced | 已在 SSE 事件映射说明中补充 gm_update 事件带 playerOptions → choices 映射；无新增端点 |
| docs/database/database.md | Not Required | 无 DB 变更；playerOptions 是 LLM 动态生成的运行时数据，不持久化 |
| docs/security/security.md | Not Required | 无新增权限/敏感数据/审计变更；playerOptions 是游戏内容数据，不涉及安全边界 |
| docs/decisions/decisions.md | Not Required | 无重要取舍或不可逆决策；C1 附条件已在任务单和 design.md 落实，不属于 ADR 级别 |
| docs/runtime/runtime-contract.md | Synced | 已追加 CR-039 段，声明无新增端点/端口/proxy 变更；Browser E2E 命令和 user actions 已追加 CR-039 条目 |
