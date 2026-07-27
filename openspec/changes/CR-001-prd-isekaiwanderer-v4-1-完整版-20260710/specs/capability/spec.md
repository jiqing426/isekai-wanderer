# Capability Specs — CR-001 MVP

## REQ-OVERVIEW: MVP 能力域总览

本文件为 CR-001 MVP 各能力域的需求规格索引和总览。各能力域的详细 Requirement + Scenario 见同目录下独立文件。

### Requirement: MVP 能力域交付

**ID**: REQ-OVERVIEW-R01
**优先级**: P0

系统必须在 MVP 中交付以下全部能力域（P0 + P1），每个能力域的详细规格见独立 spec 文件。

#### Scenario: 用户完成完整的 MVP 核心循环

- **Given** 用户首次访问游戏
- **When** 用户完成注册→引导→选择剧本→进入剧情→做出选择→对话→退出→次日回归签到
- **Then** 系统提供完整的叙事体验 + 跨会话记忆 + 好感度变化 + 签到/任务奖励

#### Scenario: 用户感受到角色跨会话记忆

- **Given** 用户昨天与角色 A 对话并分享了个人信息
- **When** 用户今天继续与角色 A 对话
- **Then** 角色 A 在相关话题中自然提及昨天的信息，用户感知到"角色记得我"

## P0 核心能力域规格索引

| 文件 | 能力 | REQ 编号 |
| --- | --- | --- |
| [narrative-engine.md](./narrative-engine.md) | S001 叙事一致性引擎 | REQ-001 |
| [script-system.md](./script-system.md) | S002 结构化剧本系统（3 个剧本） | REQ-002 |
| [character-memory.md](./character-memory.md) | S003 跨会话角色记忆 | REQ-003 |
| [affection-system.md](./affection-system.md) | S004 好感度系统 | REQ-004 |
| [first-play-guarantee.md](./first-play-guarantee.md) | S005 首玩保障 | REQ-009 |
| [visual-presentation.md](./visual-presentation.md) | S006 基础视觉呈现 | REQ-005 |
| [user-account.md](./user-account.md) | S007 用户账户系统（邮箱 + OAuth mock） | REQ-006 |
| [daily-streak.md](./daily-streak.md) | S016 每日签到 Streak | REQ-007 |
| [daily-tasks.md](./daily-tasks.md) | S017 每日任务系统 | REQ-008 |
| [payment-system.md](./payment-system.md) | S024 内购系统（mock） | REQ-010 |
| [subscription-system.md](./subscription-system.md) | S025 订阅方案体系（mock） | REQ-011 |

## P1 扩展能力域规格索引

| 文件 | 能力 | REQ 编号 | MAS 定义 |
| --- | --- | --- | --- |
| [emotional-rhythm.md](./emotional-rhythm.md) | S008 情感节奏控制 | REQ-012 | 关键节点情绪标注 + 基础节奏曲线 |
| [ai-styled-dialog.md](./ai-styled-dialog.md) | S009 AI 风格化对话 | REQ-013 | 3 种预设风格（温柔/傲娇/冷静） |
| [social-sharing.md](./social-sharing.md) | S010 社交分享 | REQ-014 | 结局分享按钮（生成链接） |
| [ugc.md](./ugc.md) | S011 UGC | REQ-015 | 自定义角色名称 + 简单外观选择 |
| [internationalization.md](./internationalization.md) | S012 国际化 | REQ-016 | 英文 UI 翻译 |
| [cg-gallery.md](./cg-gallery.md) | S013 CG 画廊 | REQ-017 | 解锁 CG 列表展示 |
| [seo.md](./seo.md) | S014 SEO | REQ-018 | 基础 meta 标签 + sitemap |
| [discord-integration.md](./discord-integration.md) | S015 Discord 集成 | REQ-019 | 官方链接 + Bot 通知 |
| [push-notification.md](./push-notification.md) | S018 Push 通知 | REQ-020 | PWA 通知权限提示 |
| [email-recall.md](./email-recall.md) | 邮件召回 | REQ-021 | 7 天未登录自动发邮件 |
| [free-conversation.md](./free-conversation.md) | 自由对话 | REQ-022 | 5 个预设话题 |
| [ending-share.md](./ending-share.md) | 结局分享 | REQ-023 | 结局卡片生成（图片+文字） |

## 不在本 CR 范围

| 能力 | 排除原因 |
| --- | --- |
| Admin 管理后台 | CEO 明确排除，后续 CR 补齐 |
| 真实支付/OAuth | MVP 使用 mock 模板，架构预留真实接口，用户后续替换凭证 |
