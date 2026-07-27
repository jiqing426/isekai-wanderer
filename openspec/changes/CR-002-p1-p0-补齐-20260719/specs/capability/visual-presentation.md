# Visual Presentation — CR-002 测试补齐

> 本规格覆盖 CR-001 已有视觉呈现功能的 P0 测试补齐。功能已在 CR-001 实现，本 CR 仅补齐自动化测试。

## Background

CR-001 已实现基础视觉呈现：角色立绘表情切换、场景背景淡入、BGM 跟随切换、打字效果和页面加载优化。但 5 项 P0 性能/交互测试未运行，需要在 Phase 2 补齐自动化验证。

## Requirements

### Requirement: 立绘表情切换 ≤200ms

AI 输出带情绪标签时，角色立绘必须在 200ms 内切换到对应表情。

#### Scenario: 情绪标签触发立绘切换

- Given: 用户正在游玩剧本对话
- When: AI 输出包含 `[emotion:happy]` 标签
- Then: CharacterSprite 在 200ms 内完成表情切换
- And: `performance.now()` 测量的切换延迟 ≤200ms

### Requirement: 背景图淡入 ≤500ms

剧情推进到新场景时，背景图必须在 500ms 内完成淡入切换。

#### Scenario: 场景切换背景淡入

- Given: 用户正在游玩剧本
- When: 剧情推进到新场景节点
- Then: SceneBackground 在 500ms 内完成淡入
- And: CSS transition duration ≤500ms

### Requirement: BGM 跟随切换

场景切换时 BGM 必须跟随切换（淡出旧曲 + 淡入新曲）；用户点击静音后 BGM 停止。

#### Scenario: 场景切换 BGM 跟随

- Given: 用户正在游玩剧本且 BGM 开启
- When: 剧情推进到新场景
- Then: 旧 BGM 淡出，新 BGM 淡入
- And: 过渡期间无音频中断

#### Scenario: 静音按钮停止 BGM

- Given: BGM 正在播放
- When: 用户点击静音按钮
- Then: BGM 立即停止

### Requirement: 打字效果 ≥30fps

对话文本以流式打字效果展示，帧率不低于 30fps；用户点击后全部文本立即显示。

#### Scenario: 流式打字帧率

- Given: 对话界面正在接收 SSE 流式文本
- When: 文本逐字渲染
- Then: requestAnimationFrame 帧率 ≥30fps
- And: 无卡顿或跳帧

#### Scenario: 点击跳过打字

- Given: 打字效果进行中
- When: 用户点击对话区域
- Then: 全部文本立即显示，无动画延迟

### Requirement: 页面首次加载 <3s（3G Fast）

3G Fast 网络条件下，页面首次加载（URL 到可交互）小于 3 秒。

#### Scenario: Lighthouse 性能评分

- Given: 浏览器 3G Fast 网络模拟
- When: 加载游戏首页
- Then: Lighthouse Performance 评分显示 FCP <3s
- And: TTI <3.5s

## Implementation Notes

- 所有功能已在 CR-001 实现（CharacterSprite、SceneBackground、AudioPlayer、useTypewriter、Vite code splitting）
- 本 CR Phase 2 仅补齐测试：Playwright + performance.now()、CSS transition 验证、rAF 帧率统计、Lighthouse CI
- 不需要新增代码，只需新增测试用例

## R/C/U/D Matrix

| Action | User | System | Notes |
|---|---|---|---|
| Create | — | — | CR-001 已创建 |
| Read | user | system | 用户观察视觉效果 |
| Update | system | system | 情绪/场景切换触发 |
| Delete | — | — | — |

## Downstream Constraints

| Consumer | Contract |
|---|---|
| DEV-CR2-011 ~ DEV-CR2-015 | 测试用例产物必须验证上述 5 项性能指标 |
| QA Phase 2 | Playwright + Lighthouse CI 必须 Mock API=no |
