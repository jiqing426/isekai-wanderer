# S013 CG 画廊（P1）

**MAS（最小可用标准）**：解锁 CG 列表展示，不做收藏/分享功能。

## Capability: CG 画廊

### Requirement: CG 解锁与展示

系统在玩家达成特定条件（好结局/关键选择）时解锁 CG，并在画廊页面展示。

#### Scenario: 解锁 CG

**Given** 玩家达成某路线好结局
**When** 结局页面展示完毕
**Then** 系统解锁对应 CG 并提示"CG 已解锁"

#### Scenario: 查看 CG 画廊

**Given** 玩家已解锁至少 1 张 CG
**When** 玩家进入 CG 画廊页面
**Then** 展示已解锁 CG 列表（缩略图 + 来源剧本/路线）
**And** 未解锁 CG 显示为灰色锁定状态

#### Scenario: 查看 CG 大图

**Given** 玩家在 CG 画廊页面
**When** 玩家点击已解锁 CG 缩略图
**Then** 展示 CG 大图，支持左右滑动切换
