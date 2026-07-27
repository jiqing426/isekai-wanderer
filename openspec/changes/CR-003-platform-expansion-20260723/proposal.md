# CR-003: 平台功能扩展（剧本发现 / 角色卡片 / 存档管理 / 碎片可视化 / 成就系统 / 每日任务增强）

## Why

- 为什么做：CR-001/CR-002 完成了核心游戏体验。当前平台缺少留存和发现机制：用户无法按类型筛选剧本、无法查看角色图鉴、无法管理存档、无法追踪成就进度。CEO 2026-07-22 指令：补齐 6 个功能模块，提升留存率和发现效率。

## What Changes

- 变更内容：补齐 6 个功能模块（剧本发现/角色卡片/存档管理/碎片可视化/成就系统/每日任务增强），不含社区/UGC/支付。

### 包含（6 个模块）

1. **剧本发现与推荐系统（P0）** — DiscoverView + 分类筛选 + 热度排行 + 首页继续玩
2. **角色卡片系统（P0）** — 角色图鉴 + 好感度排行 + 对话预览 + 关注
3. **存档与多线路管理（P0）** — 存档管理器 + 快照 + 多线路并行 + 结局收集进度
4. **碎片经济可视化（P1）** — 用途展示 + 消费记录 + 获取途径（纯展示，复用现有 fragments 表）
5. **成就系统（P1）** — 成就墙 + 剧情/活跃/收集/隐藏 + 奖励领取
6. **每日任务增强（P1）** — 活跃度积分 + 宝箱

### 不包含（CEO 澄清 2026-07-22）

- 社区与 UGC 功能（剧本创作工坊 / 同人作品 / 评论讨论区 / 创作者认证）
- 真实支付 / 首充奖励 / 限时礼包
- 碎片购买新流程

## PM Q1-Q6 决策（2026-07-23）

| # | 问题 | SA 建议 | PM 决策 |
|---|------|---------|---------|
| Q1 | achievements 表当前 schema？ | 检查 Alembic 迁移历史 | **不存在**。database.md 29 表清单无 achievements 表，后端 model 无 Achievement 类。直接新建 `achievement_definitions` + `user_achievements` 两张表，无需迁移旧表。 |
| Q2 | 多存档时"继续玩"显示哪个？ | 最近更新的 session | **确认 SA 建议**：显示 `game_sessions.updated_at` 最大的那条 session；若该 session 状态为 `completed`（已到达结局节点），则不显示继续玩卡片，改为显示"重新开始"入口。 |
| Q3 | 角色关注通知复用 PWA？ | 复用 CR-002 AC-056 | **确认复用**。复用 PWA Notification（CR-002 AC-056），触发事件：新剧本上线且包含用户关注角色时，推送 PWA 通知。通知内容由 BE 模板生成，FE 展示标题+摘要。 |
| Q4 | 存档快照保留策略？ | 30 天清理 + pinned 保留 | **确认**：自动快照 30 天自动清理；用户手动 pin 的快照永久保留；清理由 BE 定时任务执行（每日 UTC 00:30）；清理前在存档管理器给出"即将清理"提示（7 天内）。 |
| Q5 | 碎片中心需要获取途径引导？ | 是 | **确认需要**。展示以下获取途径及引导按钮：①每日签到（跳转签到页）②每日任务（跳转任务面板）③邀请好友（分享链接，复用 PWA share）④充值（跳转 /shop，mock 支付）。每个途径配图标+简短说明+CTA 按钮。 |
| Q6 | 成就"社交类"改为"活跃类"？ | 是（移除社交类） | **确认**。四类成就：剧情类 / 活跃类 / 收集类 / 隐藏类。活跃类示例：连续签到 3/7/14/30 天、完成 X 个每日任务、连续 X 天游玩。社交类（发帖/点赞）移出 CR-003 范围，留待 CR-004。 |

## Success Criteria

- 成功标准：用户可从发现页筛选剧本；首页展示继续玩卡片；角色图鉴和好感度排行；存档管理；碎片余额/消费/获取途径；成就墙和奖励；每日任务活跃度和宝箱。

| # | 标准 | 验证方式 |
|---|------|---------|
| SC-1 | 用户可从发现页按类型/标签/难度筛选剧本 | Playwright E2E |
| SC-2 | 首页展示最近未完成剧本的继续玩卡片 | Playwright E2E |
| SC-3 | 用户可查看角色图鉴和好感度排行 | Playwright E2E |
| SC-4 | 用户可管理存档（重命名/删除/继续/快照/fork） | Playwright E2E |
| SC-5 | 用户可查看碎片余额、消费记录和获取途径 | Playwright E2E |
| SC-6 | 用户可查看成就墙和进度，领取奖励 | Playwright E2E |
| SC-7 | 每日任务面板展示活跃度进度和宝箱 | Playwright E2E |

## Non-Goals

- 社区/UGC（留待 CR-004）
- 真实支付集成
- 管理后台
- 第 3 个剧本

## Impact

- **新表**: 9 张 (script_tags, script_stats, save_snapshots, ending_progress, character_profiles, user_follows, achievement_definitions, user_achievements, activity_chests)
- **扩展表**: 5 张 (scripts, characters, game_sessions, daily_tasks, achievements→新建替代)
- **新 API**: 21 个端点
- **新页面**: 6 个 (DiscoverView, CharactersView, CharacterDetailView, SaveManagerView, ShardCenterView, AchievementView)
- **新路由**: /discover, /characters, /characters/:id, /saves, /shards, /achievements
- **导航调整**: Tab Bar 增加发现和角色入口

## 待澄清问题（PM 视角）

| Q 编号 | 问题 | 阻塞 MVP | 状态 |
|--------|------|---------|------|
| Q1 | achievements 表 schema | 否 | ✅ 已确认：不存在，新建两表 |
| Q2 | 继续玩显示策略 | 否 | ✅ 已确认：最近 updated_at + completed 不显示 |
| Q3 | 角色关注通知方案 | 否 | ✅ 已确认：复用 PWA AC-056 |
| Q4 | 快照保留策略 | 否 | ✅ 已确认：30 天 + pinned 永久 |
| Q5 | 碎片获取引导 | 否 | ✅ 已确认：4 种途径 + CTA |
| Q6 | 成就分类命名 | 否 | ✅ 已确认：剧情/活跃/收集/隐藏 |

所有 Q 均为非阻塞，已给出明确决策，可进入正式 DESIGN 阶段。
