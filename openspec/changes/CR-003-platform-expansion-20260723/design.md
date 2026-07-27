# CR-003 Design Document: Platform Expansion

## Overview

CR-003 为平台补齐 6 个功能模块：剧本发现与推荐（P0）、角色卡片系统（P0）、存档与多线路管理（P0）、碎片经济可视化（P1）、成就系统（P1）、每日任务增强（P1）。

- **Scope 澄清**：CEO 2026-07-22 确认不包含社区/UGC/真实支付。碎片经济仅为可视化展示（复用现有 fragments + fragment_transactions 表），不含新支付流程。
- **数据模型**：9 张新表 + 5 张扩展表 + 种子数据
- **API**：21 个新端点（6 个模块合计）
- **前端**：6 个新页面 + 25 个新组件 + 导航栏调整
- **Wave 规划**：Wave 1（数据层+导航）→ Wave 2（P0 三模块并行）→ Wave 3（P1 三模块并行）
- **总工作量**：33 任务 / 49 人天 / 5 周
- **沿用 CR-001/CR-002 技术栈**：FastAPI + Vue 3 + PostgreSQL + Redis + Alembic + Vitest + pytest + Playwright

## Technical Approach

### D-001: 剧本发现与推荐系统（P0）

- **新增表**：`script_tags`（script_id, tag, tag_type）和 `script_stats`（script_id UNIQUE, play_count, rating, favorite_count）
- **扩展 `scripts` 表**：新增 `difficulty VARCHAR(20) DEFAULT 'normal'`、`cover_image_url TEXT`、`description TEXT`、`estimated_duration INT`
- **索引策略**：`script_tags` 上建 `(script_id)` 和 `(tag)` 索引；`script_stats` 上建 `(play_count DESC)` 和 `(rating DESC)` 索引
- **API**：`GET /api/v1/scripts/discover`（分页+筛选: genre/theme/difficulty + 排序: play_count/rating/favorite_count）、`GET /api/v1/scripts/recommendations`（基于 user.preferred_genre + affection 匹配，fallback 热度）、`GET /api/v1/scripts/ranking`（Top 10）、`GET /api/v1/game/continue`（最近未完成 session）
- **推荐算法**：规则引擎。有行为用户→preferred_genre 匹配 + 角色类型匹配；无行为用户→热度排序 fallback
- **FE**：新增 `DiscoverView`（筛选栏+排序+剧本卡片网格+推荐区+排行组件）；`HomeView` 顶部新增"继续玩"大卡片（查询 `game_sessions` 按 updated_at DESC）
- **组件**：`FilterBar`、`SortDropdown`、`ScriptCard`（增强封面+难度标签）、`RankingList`、`ContinueCard`

### D-002: 角色卡片系统（P0）

- **新增表**：`character_profiles`（character_id UNIQUE, profile_text, backstory, personality_tags JSONB, example_dialogue JSONB）和 `user_follows`（user_id, target_type='character', target_id, UNIQUE(user_id, target_type, target_id)）
- **扩展 `characters` 表**：新增 `is_featured BOOLEAN DEFAULT FALSE`、`sort_order INT DEFAULT 0`
- **API**：`GET /api/v1/characters`（列表+搜索+is_unlocked 过滤）、`GET /api/v1/characters/:id`（详情+profile+affection）、`GET /api/v1/characters/affection-rank`（好感度排行，复用 affection 表聚合）、`POST/DELETE /api/v1/follows`（关注/取关）
- **好感度等级**：<20 陌生人、20-40 认识、40-60 朋友、60-80 密友、≥80 羁绊
- **FE**：新增 `CharactersView`（卡片网格+搜索+排序）、`CharacterDetailView`（立绘+背景故事+性格标签+对话预览+好感度进度+关注按钮）
- **组件**：`CharacterCard`（彩色/灰色剪影）、`AffectionRank`、`DialoguePreview`（聊天气泡）、`FollowButton`
- **PWA 通知复用**：AC-CHAR-004.3 复用 CR-002 AC-056 的 `useNotification` composable + `sw.js`

### D-003: 存档与多线路管理（P0）

- **新增表**：`save_snapshots`（game_session_id FK ON DELETE CASCADE, node_id FK, snapshot_data JSONB, label, is_auto, is_pinned, created_at）和 `ending_progress`（user_id, script_id, unlocked_endings JSONB DEFAULT '[]', total_endings INT, UNIQUE(user_id, script_id)）
- **扩展 `game_sessions` 表**：新增 `snapshot_count INT DEFAULT 0`、`last_snapshot_at TIMESTAMPTZ`
- **索引**：`save_snapshots` 上建 `(game_session_id)` 和 `(created_at DESC)`；`ending_progress` 上建 `(user_id)`
- **API**：`GET /api/v1/saves`（存档列表，按剧本分组）、`PUT /api/v1/saves/:id`（重命名）、`DELETE /api/v1/saves/:id`（删除）、`POST /api/v1/game/:sessionId/snapshot`（手动快照）、`GET /api/v1/scripts/:id/ending-progress`（结局进度）、`POST /api/v1/game/:sessionId/fork`（从快照 fork 新 session，复制 choice_history 到快照点）
- **自动快照**：game_service 在 choice 节点提交后自动创建 save_snapshots（is_auto=true），限制 snapshot_data ≤ 64KB
- **快照清理**：定时任务（APScheduler cron）每日 UTC 03:00 清理 30 天前 is_pinned=false 的快照
- **多线路限制**：同一剧本最多 5 个并发 session，超过返回 409
- **FE**：新增 `SaveManagerView`（存档列表+重命名+删除+继续+快照时间线+结局进度）
- **组件**：`SaveList`、`SaveCard`、`SnapshotTimeline`、`EndingProgress`、`ForkButton`、`ConfirmDialog`

### D-004: 碎片经济可视化（P1）

- **无新表**：纯读取复用现有 `fragments`（余额）+ `fragment_transactions`（交易流水）
- **API**：`GET /api/v1/shards/summary`（balance + recent_transactions LIMIT 30 + acquisition_stats）
- **FE**：新增 `ShardCenterView`（余额+用途网格+消费记录+获取途径引导）
- **组件**：`UsageGrid`（4 用途图标卡片）、`TransactionList`（分页 20/page）、`AcquisitionGuide`（4 途径 CTA 按钮）、`BalanceDisplay`
- **用途跳转**：解锁章节→`/discover`、购买装扮→`/shop`、抽卡→`/gacha`（mock）、赠送礼物→`/gifts`（mock）

### D-005: 成就系统（P1）

- **新增表**：`achievement_definitions`（code UNIQUE, name, description, category ENUM('story','active','collection','hidden'), target_count, reward_type ENUM('shards','cosmetic','title'), reward_amount, is_hidden, icon_url, sort_order）和 `user_achievements`（user_id, achievement_id FK, progress INT, unlocked_at TIMESTAMPTZ NULL, claimed_at TIMESTAMPTZ NULL, UNIQUE(user_id, achievement_id)）
- **索引**：`user_achievements` 上建 `(user_id)`；`achievement_definitions` 上建 `(category)`
- **种子数据**：20+ 成就定义（剧情类 5 个、活跃类 6 个、收集类 5 个、隐藏类 4 个）
- **API**：`GET /api/v1/achievements`（定义列表+用户进度）、`POST /api/v1/achievements/:id/claim`（领取奖励→fragments 余额增加+fragment_transactions 记录）
- **触发器服务**：`achievement_service.check_achievements(user_id, event_type, event_data)` 事件驱动检查。事件类型：`game_completed`（剧情类进度+1）、`streak_milestone`（活跃类）、`cg_unlocked`（收集类+1）、`silent_choice_3`（隐藏类 HIDDEN_SILENT_3）。Redis 缓存已检查标记（TTL 1 天）
- **防重复**：unlocked_at IS NOT NULL 时跳过，不重复发放
- **FE**：新增 `AchievementView`（4 分类 tab+成就卡片网格+进度条+领取按钮）
- **组件**：`AchievementWall`、`AchievementCard`（金色/灰色）、`ProgressBar`、`RewardPopup`

### D-006: 每日任务增强（P1）

- **新增表**：`activity_chests`（user_id, date DATE, threshold INT, reward_json JSONB, claimed BOOLEAN DEFAULT FALSE, UNIQUE(user_id, date, threshold)）
- **扩展 `daily_tasks` 表**：新增 `activity_points INT DEFAULT 0`
- **API**：`GET /api/v1/daily/activity`（活跃度进度+宝箱状态）、`POST /api/v1/daily/chest/claim`（领取宝箱→fragments 余额增加）
- **活跃度计算**：任务完成领取后累加 activity_points（签到=10、玩章节=20、送礼物=15、观看对话预览=5、完成存档操作=10），阈值 50/100/150 解锁宝箱
- **宝箱奖励**：随机 10-50 碎片，`reward_json` 记录具体值
- **UTC 日切割**：与现有 `daily_checkins` 一致，UTC 00:00 重置活跃度和宝箱状态
- **FE**：`HomeView` 内嵌 `TaskPanel`（任务列表+活跃度进度条+宝箱区域）
- **组件**：`TaskPanel`（可收起/展开）、`TaskItem`（进度+领取按钮）、`ActivityChest`（宝箱动画）

### D-007: 共享层（数据迁移+导航+通知）

- **Alembic 迁移**：分 3 批迁移（Wave 1 数据层表+扩展字段、Wave 2 无新迁移、Wave 3 无新迁移）。9 张新表 + 5 张扩展表一次性迁移
- **种子数据**：script_tags（6 个剧本 × 3-5 个标签）、character_profiles（12 个角色各含 profile+dialogue）、achievement_definitions（20+ 成就）、ending 定义（7 个结局分布）
- **导航调整**：底部 Tab Bar 从 [首页/社区/画廊/我的] 调整为 [首页/发现/角色/我的]；"我的"页面新增存档管理/成就墙/碎片中心入口
- **全局通知**：复用 CR-002 `useNotification` composable，新增成就解锁/任务完成/碎片获得 toast

### D-008: 错误码设计

| 错误码 | HTTP | 场景 |
|--------|------|------|
| `SAVE_LIMIT_EXCEEDED` | 409 | 同一剧本已有 5 个存档，拒绝创建第 6 个 |
| `SAVE_NOT_OWNED` | 403 | 用户操作他人存档 |
| `SNAPSHOT_NOT_FOUND` | 404 | 快照 ID 不存在 |
| `SNAPSHOT_TOO_LARGE` | 413 | snapshot_data 超过 64KB |
| `FORK_CONFLICT` | 409 | 同一 session 并发 fork（乐观锁 version 冲突） |
| `ACHIEVEMENT_NOT_UNLOCKED` | 400 | 尝试领取未解锁成就 |
| `ACHIEVEMENT_ALREADY_CLAIMED` | 400 | 重复领取成就奖励 |
| `CHEST_NOT_UNLOCKED` | 400 | 活跃度未达阈值时尝试领取宝箱 |
| `CHEST_ALREADY_CLAIMED` | 400 | 重复领取宝箱 |
| `FOLLOW_ALREADY_EXISTS` | 409 | 重复关注同一角色 |
| `SCRIPT_NOT_FOUND` | 404 | 剧本 ID 不存在 |

### D-009: 安全设计

- **存档权限**：所有存档操作（GET/PUT/DELETE/snapshot/fork）校验 `game_sessions.user_id == current_user.id`，不匹配返回 403 `SAVE_NOT_OWNED`
- **成就领取**：`POST /achievements/:id/claim` 校验 `user_achievements.user_id == current_user.id`
- **碎片操作**：宝箱/成就领取使用数据库事务 + 乐观锁，防止并发重复发放
- **关注通知**：PWA 推送内容不含敏感信息，仅角色名+剧本名
- **snapshot_data 大小限制**：BE 层校验 ≤ 64KB，超过返回 413

## Technology Decisions

| Decision | Selected | Status | Evidence |
|----------|----------|--------|----------|
| 推荐算法 | 规则引擎（preferred_genre + affection 匹配，fallback 热度） | Accepted | MVP 无需 ML；CEO 2026-07-22 澄清无 ML 预算；PL 确认规则引擎足够 MVP |
| 快照存储 | JSONB（复用 PostgreSQL） | Accepted | 快照数据 < 64KB；CEO 2026-07-22 确认复用现有 PG 不引入新存储；PL 确认 |
| 成就触发 | 事件驱动（业务逻辑回调 achievement_service） | Accepted | 解耦业务逻辑和成就检查；CEO 2026-07-22 确认事件驱动方案；PL 确认 |
| 碎片可视化 | 纯展示（复用现有 fragments + fragment_transactions） | Accepted | CEO 2026-07-22 澄清不含支付流程；PL 确认纯展示方案；读取现有数据即可 |
| 活跃度日切割 | UTC 00:00 | Accepted | 与现有 daily_checkins 一致；CEO 2026-07-22 确认统一时区策略；PL 确认 |

## Document Sync

| Target Doc | Status | 同步说明 |
|------------|--------|---------|
| `docs/architecture/architecture.md` | Synced | 新增 recommendation_service、snapshot_service、achievement_service、activity_service 模块；新增 6 路由；新增 21 API 端点 |
| `docs/api/api.md` | Synced | 新增 21 个 API 端点（discover/recommendations/ranking/continue/characters/affection-rank/follows/saves/snapshot/ending-progress/fork/shards-summary/achievements/claim/daily-activity/chest-claim），总计 66 端点；引用 docs/runtime/runtime-contract.md 说明 API base /api/v1 |
| `docs/database/database.md` | Synced | 新增 9 张表（script_tags/script_stats/character_profiles/user_follows/save_snapshots/ending_progress/achievement_definitions/user_achievements/activity_chests）+ 5 张扩展表（scripts/characters/game_sessions/daily_tasks/achievements）；总计 38 表；引用 docs/runtime/runtime-contract.md 说明 PG 持久化配置 |
| `docs/security/security.md` | Synced | 存档权限校验 SAVE_NOT_OWNED、碎片并发防重复乐观锁、snapshot_data 大小限制 64KB、成就/宝箱领取事务 + 防重复发放 |
| `docs/decisions/decisions.md` | Synced | 推荐算法选型（规则引擎）、快照存储（JSONB）、成就触发（事件驱动）已 Accepted；无新 ADR（沿用 CR-002 技术栈） |
| `docs/runtime/runtime-contract.md` | Synced | 新增 6 路由（/discover /characters /characters/:id /saves /shards /achievements）+ Browser E2E 用户动作（发现筛选、角色图鉴、存档管理、成就墙、碎片中心、活跃度宝箱） |
