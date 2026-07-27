# S-CR2-008 召回邮件（CR-002 补充）

**MAS（最小可用标准）**：7 天未登录→mock 召回邮件。

## REQ-CR2-008: 召回邮件

### Requirement: 自动召回邮件

**ID**: REQ-CR2-008-R01
**优先级**: P1

用户连续 7 天未登录时，系统自动发送召回邮件（含游戏链接和最近游玩进度摘要，mock 实现）。

#### Scenario: 7 天未登录触发召回

- **Given** 用户 last_login > 7 天前
- **When** RecallService cron 执行
- **Then** MockEmailService 发送召回邮件，含游戏链接和进度摘要

#### Scenario: 用户近期有登录

- **Given** 用户 last_login < 7 天前
- **When** RecallService cron 执行
- **Then** 不发送召回邮件

### R/C/U/D 完整性

| 动作 | 是否包含 | 说明 |
| --- | --- | --- |
| Create | 是 | 创建召回邮件记录 |
| Read | 是 | 查询未登录用户 |
| Update | 否 | — |
| Delete | 否 | — |

### 下游约束

- 依赖：auth 模块 last_login 字段、MockEmailService（与 AC-047 共享）
- BE：RecallService cron + recall_emails 表
