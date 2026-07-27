# S015 Discord 集成（P1）

**MAS（最小可用标准）**：官方 Discord 链接 + 简单 Bot 通知（里程碑通知），不做深度集成。

## Capability: Discord 集成

### Requirement: Discord 社区链接

系统在游戏设置页面提供官方 Discord 服务器邀请链接。

#### Scenario: 用户访问 Discord 链接

**Given** 用户在游戏设置页面
**When** 用户点击"加入 Discord"按钮
**Then** 新标签页打开 Discord 服务器邀请页面

### Requirement: Discord Bot 通知

系统在玩家达成特定里程碑时通过 Discord Bot 发送通知到指定频道。

#### Scenario: 里程碑通知发送

**Given** 玩家达成首个好结局
**When** 结局页面展示完毕
**Then** 系统通过 Discord Bot 向配置的通知频道发送消息（含玩家名称和成就描述）
**And** 若 Bot 未配置则静默跳过，不影响用户体验
