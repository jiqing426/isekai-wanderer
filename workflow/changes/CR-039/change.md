# Change: CR-039 — Corvus 玩家选项功能

- **CR ID**: CR-039
- **创建时间**: 2026-09-10T15:06:00+08:00
- **来源**: 用户要求
- 目标：在 Corvus 引擎 SSE 流式对话中增加 GM 动态生成的玩家选项，与自由输入共存
- 成功标准：每轮对话后 GM 生成 2-4 个选项；ChoicePanel 显示选项；FreeChatInput 始终可用；向后兼容；Legacy 不受影响
- **负责人**: pl
- **当前阶段**: INTAKE
- **状态**: intake-ready
- **关联 CR**: CR-037（Corvus 后端集成）、CR-038（Corvus 前端入口）

## 变更目标

在 Corvus 引擎中增加玩家选项功能：每轮 SSE 对话结束后，GM 根据当前对话上下文动态生成 2-4 个情境化选项，通过 `gm_update` 事件推送到前端，ChoicePanel 显示选项供玩家点击，同时保留自由文字输入。

## 背景与动机

CR-038 完成后，Corvus 引擎已全链路跑通。但当前 Corvus 模式下玩家只能自由输入文字，没有预设选择分支。对比 Legacy 引擎的节点选择体验，Corvus 缺少"选 A 还是选 B"的分支叙事感。用户要求改造 Corvus 加上选择功能。

## 影响范围

| 层面 | 影响 |
|---|---|
| Corvus gameMaster.ts | GM prompt 增加 `playerOptions` 输出字段 |
| Corvus chat.ts | `gm_update` SSE 事件带上 `playerOptions` |
| 后端 game.py | SSE 透传时将 `playerOptions` 映射到 `choices` |
| 前端 game.ts | `gm_update` 事件处理中赋值 `pendingChoices` |
| 前端 ChoicePanel | 已有组件复用，无需改动 |

## 成功标准

1. 每轮 Corvus 对话结束后，GM 生成 2-4 个情境化选项
2. 前端 ChoicePanel 显示选项，玩家可点击选择
3. 玩家仍可自由输入文字，选择不是强制的
4. 选项点击后等同于以选项文字作为自定义输入发送
5. 当 GM 未返回 `playerOptions` 时，前端 fallback 到纯自由输入（向后兼容）
6. Browser E2E 验证选项显示和点击功能
7. 不影响 Legacy 引擎的选择逻辑

## 功能清单

| 编号 | 功能 | 说明 |
|---|---|---|
| F1 | GM prompt 扩展 | GM 的 JSON schema 增加 `playerOptions` 字段 |
| F2 | SSE 事件扩展 | `gm_update` 事件带上 `playerOptions` 数据 |
| F3 | 后端透传 | SSE 透传时将 `playerOptions` 映射到前端期望的 `choices` 格式 |
| F4 | 前端渲染 | `gm_update` 处理中赋值 `pendingChoices`，ChoicePanel 显示选项 |
| F5 | 选项点击 | 玩家点击选项 → 以选项文字作为 custom-input 发送 |
| F6 | 向后兼容 | GM 未返回 `playerOptions` 时，`pendingChoices` 为空，FreeChatInput 始终可用 |

## 技术方案

### GM prompt 扩展

在 `gameMaster.ts` 的 `GM_SYSTEM_PROMPT` 的 JSON schema 中增加：

```json
"playerOptions": [
  { "text": "string — 选项文字", "hint": "string — 简短提示（可选）" }
]
```

GM 指令追加：
- 根据当前对话上下文和场景，生成 2-4 个情境化选项
- 选项应反映不同的态度、行动或对话方向
- 选项文字简洁（≤30 字），让玩家快速理解
- 如果当前场景不适合提供选项（如纯叙事过渡），返回空数组

### SSE 事件扩展

`chat.ts` 的 `gm_update` 事件中增加 `playerOptions` 字段。

### 后端透传

`game.py` 在 SSE 透传 Corvus 事件时，将 `gm_update` 中的 `playerOptions` 映射为前端期望的 `choices` 格式：

```python
# gm_update 事件
if data.get("playerOptions"):
    choices = [{"id": str(i), "text": opt["text"], "hint": opt.get("hint", "")} 
               for i, opt in enumerate(data["playerOptions"])]
    # 通过 SSE 推送 choices
```

### 前端处理

`game.ts` 在 `gm_update` 事件处理中：

```ts
if (data.player_options || data.choices) {
  pendingChoices.value = data.player_options || data.choices || [];
}
```

ChoicePanel 已有组件，`hasChoices=true` 时自动显示。FreeChatInput 不隐藏，玩家可选择或自由输入。

## 风险识别

| 编号 | 风险 | 等级 | 缓解 |
|---|---|---|---|
| R1 | GM 可能不遵循 schema，不输出 playerOptions | 中 | 前端 fallback 到纯自由输入（空数组） |
| R2 | 选项质量取决于 LLM | 低 | GM prompt 中加指导规则，后续可迭代 |
| R3 | GM prompt 变长增加 token 消耗 | 低 | 仅增加一个字段描述，约 100 token |
| R4 | 选项点击后与自由输入行为不一致 | 低 | 选项点击等同于以选项文字作为 custom-input 发送，逻辑一致 |

## 约束

- 不破坏 Corvus 自由输入功能
- 不影响 Legacy 引擎的选择逻辑
- 不新增数据库表或字段
- 不新增 API 端点
- Mock API=no（Delivery E2E 和 Browser E2E 必须使用真实 Corvus 服务）

## 关联文档

- `docs/runtime/runtime-contract.md` — 运行时契约
- `docs/api/api.md` — API 文档
- CR-038 `workflow/changes/CR-038/` — Corvus 前端入口
- CR-037 — Corvus 后端集成

## 追加修复（2026-09-10T17:02）

### 问题：Corvus 游戏开始后"剧情正在展开..."一直显示

**根因**：Corvus `startGame` 创建会话后直接 return，不调用 `fetchDialogue()`。`PlayerCandidateModal` 选角成功后只 `emit('selected')`，不处理 `initial_scene`。`currentDialogue` 始终为 null → StoryPanel 显示 fallback 文本"剧情正在展开..."。

**影响 AC**: AC-039-005（对话后可见选项 — 用户在发消息前看到"剧情正在展开..."而非初始叙事）

### 追加任务

| 任务 | 角色 | 范围 |
|---|---|---|
| T-039-FE-002（追加） | FE | `PlayerCandidateModal.vue` 选角完成后把 `initial_scene` 赋值到 `game.currentDialogue`；或自动触发第一次 SSE 对话 |
| T-039-FE-003（追加） | FE | E2E 测试修复：`cr039-player-options.spec.ts` 通过 UI 流程验证初始状态，不用 API 绕过 |

### 追加 AC

| AC | 验收标准 | 优先级 |
|---|---|---|
| AC-039-010 | Corvus 游戏选角完成后，页面显示初始叙事文本（非"剧情正在展开..."） | P0 |
| AC-039-011 | E2E 测试覆盖 UI 流程：开始游戏 → 选角 → 验证初始叙事显示 | P0 |
