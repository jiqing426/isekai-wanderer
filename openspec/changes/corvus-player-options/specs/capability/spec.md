# Spec: Corvus 玩家选项 — 能力规格

### Requirement: REQ-GM-001 — GM prompt 扩展

GM 的 JSON 输出 schema 增加 `playerOptions` 字段，根据对话上下文动态生成 2-4 个情境化选项。

#### Scenario: GM 输出 playerOptions

- **Given** Corvus 引擎运行中，玩家发送一条消息
- **When** narrator 生成叙事完成，GM 执行状态提取
- **Then** GM 输出的 JSON 中包含 `playerOptions` 字段
- **And** `playerOptions` 是数组类型
- **And** 每个元素包含 `text`（必填，string）和 `hint`（可选，string）
- **And** 数组长度为 0-4

#### Scenario: 选项内容情境化

- **Given** 当前对话是林辰介绍自己是占星师
- **When** GM 生成 playerOptions
- **Then** 选项应反映不同的态度/行动/对话方向
- **And** 选项文字简洁（≤30 字）
- **And** 选项之间有区分度

#### Scenario: 纯叙事过渡不生成选项

- **Given** 当前对话是纯场景描述过渡
- **When** GM 判断不适合提供选项
- **Then** `playerOptions` 返回空数组

### Requirement: REQ-SSE-001 — SSE 透传

`gm_update` SSE 事件带上 `playerOptions`，后端透传时映射为前端期望的 `choices` 格式。

#### Scenario: gm_update 事件包含 playerOptions

- **Given** GM 输出包含 `playerOptions`
- **When** Corvus chat.ts 发送 `gm_update` SSE 事件
- **Then** 事件数据中包含 `playerOptions` 字段

#### Scenario: 后端 SSE 透传映射

- **Given** 后端收到 Corvus 的 `gm_update` 事件包含 `playerOptions`
- **When** 后端透传给前端
- **Then** `playerOptions` 被映射为 `choices` 格式
- **And** 每个选项格式为 `{ id: string, text: string, hint: string }`

### Requirement: REQ-FE-001 — 前端选项渲染

前端 `gm_update` 事件处理中赋值 `pendingChoices`，ChoicePanel 显示选项，FreeChatInput 始终可用。

#### Scenario: ChoicePanel 显示选项

- **Given** Corvus 对话结束，`gm_update` 事件包含 `playerOptions`
- **When** 前端处理 `gm_update` 事件
- **Then** `pendingChoices` 被赋值为选项列表
- **And** `hasChoices` 变为 true
- **And** ChoicePanel 显示 2-4 个选项

#### Scenario: 玩家点击选项

- **Given** ChoicePanel 显示选项
- **When** 玩家点击某个选项
- **Then** 以选项文字作为 custom-input 发送
- **And** SSE 正常流式回应

#### Scenario: FreeChatInput 始终可用

- **Given** ChoicePanel 显示选项
- **When** 玩家查看输入框
- **Then** FreeChatInput 仍可见
- **And** 玩家可自由输入文字

### Requirement: REQ-FE-002 — 向后兼容

GM 未返回 `playerOptions` 时，前端 fallback 到纯自由输入；Legacy 引擎不受影响。

#### Scenario: GM 未返回 playerOptions

- **Given** GM 输出不含 `playerOptions` 字段
- **When** 前端处理 `gm_update` 事件
- **Then** `pendingChoices` 为空数组
- **And** `hasChoices` 变为 false
- **And** ChoicePanel 隐藏
- **And** FreeChatInput 正常显示

#### Scenario: Legacy 引擎不受影响

- **Given** 使用 Legacy 引擎的剧本
- **When** 玩家开始游戏
- **Then** Legacy 的预设节点和选择逻辑不受影响
- **And** `choices` 来源仍是 NodeChoice 表
