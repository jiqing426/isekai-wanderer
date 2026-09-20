# Proposal: Corvus 玩家选项功能

## Why

- CR-038 完成后 Corvus 引擎全链路跑通，但玩家只能自由输入文字，缺少选择驱动叙事的体验
- 增加动态选项可以降低玩家"不知道说什么"的门槛，提供分支叙事感
- 保持自由输入的开放性，选项是"建议"不是强制

## What Changes

- Corvus gameMaster.ts — GM prompt JSON schema 增加 `playerOptions: [{text, hint}]` 字段
- Corvus chat.ts — `gm_update` SSE 事件带上 `playerOptions`
- 后端 game.py — SSE 透传时 `playerOptions` → `choices` 格式映射
- 前端 game.ts — `gm_update` 事件处理中赋值 `pendingChoices`，复用已有 ChoicePanel

## Non-Goals

- 不增加预设节点/分支系统（Legacy 已有）
- 不增加结局判定机制
- 不增加选项的好感度影响（GM 已有 relationshipUpdates）
- 不改数据库结构
- 不新增 API 端点
- 不做选项质量深度调优（C1 约束：≤0.5h 调优，超时以 fallback 上线）

## Success Criteria

- 每轮 Corvus 对话结束后，GM 生成 2-4 个情境化选项
- 前端 ChoicePanel 显示选项，玩家可点击选择
- 玩家仍可自由输入文字，选择不是强制的
- 选项点击后等同于以选项文字作为自定义输入发送
- 当 GM 未返回 `playerOptions` 时，前端 fallback 到纯自由输入
- Browser E2E 验证选项显示和点击功能
- 不影响 Legacy 引擎的选择逻辑

## Impact

- Corvus gameMaster.ts: GM prompt 增加 playerOptions 输出字段
- Corvus chat.ts: gm_update SSE 事件带上 playerOptions
- 后端 game.py: SSE 透传 playerOptions → choices 映射
- 前端 game.ts: gm_update 事件处理中赋值 pendingChoices
- 前端 ChoicePanel: 已有组件复用，无需改动
- 数据库: 无变更
- API: 无新增端点
- Legacy 引擎: 不受影响
