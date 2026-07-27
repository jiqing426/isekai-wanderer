# S-CR2-006 Discord 集成（CR-002 补充）

**MAS（最小可用标准）**：mock webhook 通知结局解锁。

## REQ-CR2-006: Discord 集成

### Requirement: Discord 通知

**ID**: REQ-CR2-006-R01
**优先级**: P1

新结局解锁时 Discord Bot 发送通知到指定频道（mock webhook 实现）。

#### Scenario: 结局解锁触发 Discord 通知

- **Given** 玩家达成某路线好结局
- **When** 结局解锁事件触发
- **Then** DiscordService 通过 mock webhook 发送通知到指定频道

#### Scenario: Discord 链接展示

- **Given** 用户在设置页
- **When** 页面加载
- **Then** 展示官方 Discord 邀请链接

### R/C/U/D 完整性

| 动作 | 是否包含 | 说明 |
| --- | --- | --- |
| Create | 是 | 创建 Discord 配置 |
| Read | 是 | 读取配置 |
| Update | 否 | — |
| Delete | 否 | — |

### 下游约束

- 依赖：结局解锁系统（已存在）
- BE：DiscordService（mock webhook）
- 新增：discord_configs 表
