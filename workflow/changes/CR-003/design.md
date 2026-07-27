# CR-003 技术评估报告（SA Architect）

> **阶段**：PRE-DESIGN 技术评估  
> **目的**：为 PL/PM 提供技术可行性、工作量估算和 Wave 规划依据  
> **基于**：`workflow/changes/CR-003/change.md` + 现有 29 表 + 45 API + 20 路由  
> **日期**：2026-07-23  
> **范围澄清**：CR-003 不涉及真实支付、UGC 内容创作、社区功能。碎片经济仅为可视化展示（复用现有 fragments 表），不含新支付流程。

---

## 1. 数据模型评估

### 1.1 需要新建的表（6 张）

| 表名 | 所属模块 | 关键字段 | 预估行数级 |
|------|---------|---------|-----------|
| `script_tags` | 模块1 剧本发现 | `id`, `script_id FK`, `tag VARCHAR(50)`, `tag_type ENUM('genre','theme','difficulty')` | N×M (多对多) |
| `script_stats` | 模块1 剧本发现 | `id`, `script_id FK UNIQUE`, `play_count INT DEFAULT 0`, `rating DECIMAL(3,2) DEFAULT 0`, `favorite_count INT DEFAULT 0`, `updated_at` | 1:1 scripts |
| `save_snapshots` | 模块3 存档管理 | `id UUID`, `game_session_id FK`, `node_id FK`, `snapshot_data JSONB`, `label VARCHAR(100)`, `is_auto BOOLEAN DEFAULT FALSE`, `is_pinned BOOLEAN DEFAULT FALSE`, `created_at` | 高 (每 session 多个) |
| `ending_progress` | 模块3 存档管理 | `id`, `user_id FK`, `script_id FK`, `unlocked_endings JSONB DEFAULT '[]'`, `total_endings INT`, `updated_at`, `UNIQUE(user_id, script_id)` | N×M |
| `character_profiles` | 模块2 角色卡片 | `id`, `character_id FK UNIQUE`, `profile_text TEXT`, `backstory TEXT`, `personality_tags JSONB DEFAULT '[]'`, `example_dialogue JSONB DEFAULT '[]'` | 1:1 characters |
| `user_follows` | 模块2 角色关注 | `id`, `user_id FK`, `target_type ENUM('character')`, `target_id UUID`, `created_at`, `UNIQUE(user_id, target_type, target_id)` | 中 |

### 1.2 需要扩展的现有表（5 张）

| 表名 | 新增字段 | 所属模块 | 影响评估 |
|------|---------|---------|---------|
| `scripts` | `difficulty VARCHAR(20) DEFAULT 'normal'`, `cover_image_url TEXT`, `description TEXT`, `estimated_duration INT` (分钟) | 模块1 | 低风险：nullable 字段，向后兼容 |
| `characters` | `is_featured BOOLEAN DEFAULT FALSE`, `sort_order INT DEFAULT 0` | 模块2 | 低风险：默认值 |
| `game_sessions` | `snapshot_count INT DEFAULT 0`, `last_snapshot_at TIMESTAMPTZ` | 模块3 | 低风险：计数器字段 |
| `daily_tasks` | `activity_points INT DEFAULT 0` | 模块7 | 低风险：新增字段 |
| `achievements` | `category VARCHAR(20)`, `reward_type VARCHAR(20)`, `reward_amount INT DEFAULT 0`, `is_hidden BOOLEAN DEFAULT FALSE`, `icon_url TEXT`, `sort_order INT DEFAULT 0` | 模块6 | **需确认**：achievements 表当前 schema 未记录在 database.md，需先检查实际表结构 |

### 1.3 额外新表（模块6+7 补充）

| 表名 | 所属模块 | 关键字段 |
|------|---------|---------|
| `achievement_definitions` | 模块6 成就系统 | `id`, `code VARCHAR(50) UNIQUE`, `name VARCHAR(100)`, `description TEXT`, `category VARCHAR(20)`, `target_count INT`, `reward_type VARCHAR(20)`, `reward_amount INT DEFAULT 0`, `is_hidden BOOLEAN DEFAULT FALSE`, `icon_url TEXT` |
| `user_achievements` | 模块6 成就系统 | `id UUID`, `user_id FK`, `achievement_id FK`, `unlocked_at TIMESTAMPTZ DEFAULT NOW()`, `progress INT DEFAULT 0`, `UNIQUE(user_id, achievement_id)` |
| `activity_chests` | 模块7 活跃度宝箱 | `id`, `user_id FK`, `date DATE`, `threshold INT`, `reward_json JSONB`, `claimed BOOLEAN DEFAULT FALSE`, `UNIQUE(user_id, date, threshold)` |

### 1.4 数据模型总结

| 类别 | 数量 | 说明 |
|------|------|------|
| 新建表 | **9 张** | script_tags, script_stats, save_snapshots, ending_progress, character_profiles, user_follows, achievement_definitions, user_achievements, activity_chests |
| 扩展现有表 | **5 张** | scripts, characters, game_sessions, daily_tasks, achievements(需确认) |
| 高风险迁移 | 1 | `achievements` 表结构需先确认；其余均为 nullable/default 扩展 |
| **不涉及** | — | 无支付表、无 UGC 表、无评论表 |

---

## 2. 前后端工作量估算

### 2.1 按模块估算

| 模块 | BE API 数 | BE 复杂度 | FE 页面数 | FE 组件数 | FE 复杂度 | BE 人天 | FE 人天 | 合计 |
|------|----------|----------|----------|----------|----------|---------|---------|------|
| **1. 剧本发现与推荐** | 4 | 中 (推荐算法) | 1 (DiscoverView) | 5 (FilterBar, SortDropdown, ContinueCard, ScriptCard增强, RankingList) | 高 (筛选+排序交互) | 4 | 5 | **9** |
| **2. 角色卡片系统** | 3 | 低 | 2 (CharactersView, CharacterDetailView) | 4 (CharacterCard, AffectionRank, DialoguePreview, FollowButton) | 中 | 2 | 4 | **6** |
| **3. 存档与多线路** | 5 | 高 (快照+并发) | 1 (SaveManagerView) | 4 (SaveList, SaveCard, SnapshotTimeline, EndingProgress) | 高 (状态管理复杂) | 5 | 4 | **9** |
| **4. 碎片经济可视化** | 2 | 低 (只读查询) | 1 (ShardCenterView) | 3 (UsageGrid, TransactionList, AcquisitionGuide) | 低 (纯展示) | 1 | 2 | **3** |
| **6. 成就系统** | 3 | 中 (触发器) | 1 (AchievementView) | 4 (AchievementWall, AchievementCard, ProgressBar, RewardPopup) | 中 | 3 | 3 | **6** |
| **7. 每日任务增强** | 2 | 低 | 0 (HomeView 内嵌) | 3 (TaskPanel, TaskItem, ActivityChest) | 低 | 1 | 2 | **3** |
| **共享层** | 2 (DB迁移+种子数据) | 中 | 0 | 2 (导航增强, 全局badge) | 低 | 2 | 1 | **3** |
| **合计** | **21** | — | **6** | **25** | — | **18** | **21** | **39** |

### 2.2 总工作量

| 角色 | 人天 | 说明 |
|------|------|------|
| BE | 18 | 含 API + service + migration + 单元测试 |
| FE | 21 | 含页面 + 组件 + store + E2E |
| QA | 8 | E2E 测试集 + 回归测试 |
| SA | 2 | 设计评审 + 文档同步 |
| **总计** | **49 人天** | 按 1 BE + 1 FE 并行 ≈ 25 个工作日（5 周） |

### 2.3 与初版对比（移除 UGC/社区/支付后）

| 项 | 初版 | 修订版 | 差异 |
|---|------|--------|------|
| 新建表 | 10 | 9 | -1 (无 ugc_posts) |
| API 数 | 28 | 21 | -7 (无 UGC CRUD/评论/点赞/审核) |
| FE 页面 | 9 | 6 | -3 (无 Community/CreatePost/Creator) |
| 总人天 | 68 | 49 | **-19 (减少 28%)** |

---

## 3. 任务拆分

### 模块 1：剧本发现与推荐系统（P0）

| 任务编号 | 描述 | 优先级 | 依赖 | BE/FE | 工时 |
|---------|------|--------|------|-------|------|
| CR3-T01 | scripts 表扩展 (difficulty, cover_image, description, estimated_duration) + script_stats 新表 + seed 数据 | P0 | 无 | BE | 1.5d |
| CR3-T02 | script_tags 表 + 种子标签数据 (恋爱/奇幻/悬疑/科幻, HE/BE/多结局, 难度) | P0 | CR3-T01 | BE | 1d |
| CR3-T03 | GET /api/v1/scripts/discover (分页+筛选: tag/genre/difficulty +排序: play_count/rating/favorite_count) | P0 | CR3-T01, T02 | BE | 2d |
| CR3-T04 | GET /api/v1/scripts/recommendations (基于 user.preferred_genre + affection 角色类型匹配，fallback 热度排序) | P0 | CR3-T01 | BE | 2d |
| CR3-T05 | DiscoverView 页面 (筛选栏+排序+剧本卡片网格+推荐区) | P0 | CR3-T03, T04 | FE | 3d |
| CR3-T06 | HomeView "继续玩" 大卡片 (GET /api/v1/game/continue → 最近未完成 session) | P0 | 无 (复用 game_sessions) | FE | 1.5d |
| CR3-T07 | 热度排行组件 (Top 10 列表, 嵌入 DiscoverView) | P1 | CR3-T03 | FE | 1d |

### 模块 2：角色卡片系统（P0）

| 任务编号 | 描述 | 优先级 | 依赖 | BE/FE | 工时 |
|---------|------|--------|------|-------|------|
| CR3-T08 | character_profiles 表 + 种子数据 (profile_text, backstory, personality_tags, example_dialogue) | P0 | 无 | BE | 1.5d |
| CR3-T09 | GET /api/v1/characters (列表, 含 is_unlocked 过滤) + GET /api/v1/characters/:id (详情+example_dialogue) | P0 | CR3-T08 | BE | 1.5d |
| CR3-T10 | GET /api/v1/characters/affection-rank (角色好感度排行, 复用 affection 表) | P0 | 无 | BE | 0.5d |
| CR3-T11 | user_follows 表 + POST/DELETE /api/v1/follows API (角色关注) | P0 | 无 | BE | 1d |
| CR3-T12 | CharactersView 页面 (卡片网格, 已解锁/未解锁区分, 搜索) | P0 | CR3-T09 | FE | 2d |
| CR3-T13 | CharacterDetailView 页面 (立绘+背景故事+性格标签+对话预览+好感度进度+关注按钮) | P0 | CR3-T09, T10, T11 | FE | 2d |

### 模块 3：存档与多线路管理（P0）

| 任务编号 | 描述 | 优先级 | 依赖 | BE/FE | 工时 |
|---------|------|--------|------|-------|------|
| CR3-T14 | save_snapshots 表 + game_sessions 扩展 (snapshot_count, last_snapshot_at) | P0 | 无 | BE | 1d |
| CR3-T15 | ending_progress 表 + 剧本结局种子数据 (total_endings per script) | P0 | 无 | BE | 1d |
| CR3-T16 | GET /api/v1/saves (存档列表) + PUT /api/v1/saves/:id (重命名) + DELETE /api/v1/saves/:id | P0 | CR3-T14 | BE | 1.5d |
| CR3-T17 | POST /api/v1/game/:sessionId/snapshot (手动快照) + 自动快照触发器 (关键决策节点 type=choice 时自动创建) | P0 | CR3-T14 | BE | 2d |
| CR3-T18 | GET /api/v1/scripts/:id/ending-progress (已解锁结局 X/Y) | P0 | CR3-T15 | BE | 0.5d |
| CR3-T19 | POST /api/v1/game/:sessionId/fork (从存档创建分支 session, 复制 choice_history 到快照点) | P0 | CR3-T14, T16 | BE | 2d |
| CR3-T20 | SaveManagerView 页面 (存档列表+重命名+删除+继续+快照时间线+结局进度) | P0 | CR3-T16~T19 | FE | 3d |

### 模块 4：碎片经济体系可视化（P1）— 仅展示层

| 任务编号 | 描述 | 优先级 | 依赖 | BE/FE | 工时 |
|---------|------|--------|------|-------|------|
| CR3-T21 | GET /api/v1/shards/summary (碎片余额 + 最近交易 + 获取途径统计，复用 fragments + fragment_transactions) | P1 | 无 | BE | 1d |
| CR3-T22 | ShardCenterView 页面 (用途图标展示 + 消费记录流水 + 获取途径说明 + 当前余额) | P1 | CR3-T21 | FE | 2d |

### 模块 6：成就系统（P1）

| 任务编号 | 描述 | 优先级 | 依赖 | BE/FE | 工时 |
|---------|------|--------|------|-------|------|
| CR3-T23 | achievement_definitions 表 + user_achievements 表 + 种子成就数据 (20+ 个: 剧情/社交/收集/隐藏) | P1 | 无 | BE | 1.5d |
| CR3-T24 | GET /api/v1/achievements (定义列表+用户进度) + POST /api/v1/achievements/:id/claim (领取奖励→碎片) | P1 | CR3-T23 | BE | 1.5d |
| CR3-T25 | 成就触发器服务 (事件驱动: game_completed, cg_unlocked, streak_milestone 等事件→检查成就条件→更新 user_achievements) | P1 | CR3-T23 | BE | 2d |
| CR3-T26 | AchievementView 页面 (成就墙+分类 tab: 剧情/社交/收集/隐藏+进度条+已解锁/待解锁) | P1 | CR3-T24 | FE | 2d |
| CR3-T27 | RewardPopup 组件 (解锁动画+碎片/称号奖励展示) | P1 | CR3-T24 | FE | 1d |

### 模块 7：每日任务系统增强（P1）

| 任务编号 | 描述 | 优先级 | 依赖 | BE/FE | 工时 |
|---------|------|--------|------|-------|------|
| CR3-T28 | daily_tasks 表扩展 (activity_points) + activity_chests 表 | P1 | 无 | BE | 0.5d |
| CR3-T29 | 活跃度计算服务 (任务完成→累加 activity_points→检查宝箱阈值→创建 activity_chests 记录) | P1 | CR3-T28 | BE | 1d |
| CR3-T30 | TaskPanel 组件 (HomeView 内嵌: 任务列表+进度条+活跃度宝箱领取) | P1 | CR3-T29 | FE | 1.5d |

### 共享层

| 任务编号 | 描述 | 优先级 | 依赖 | BE/FE | 工时 |
|---------|------|--------|------|-------|------|
| CR3-T31 | Alembic 迁移整合 (9 新表 + 5 扩展表, 分批迁移) | P0 | 所有表变更任务 | BE | 1.5d |
| CR3-T32 | 导航栏增强 (新增 Discover/Characters/Saves/Achievements 入口, badge 通知) | P0 | 无 | FE | 1d |
| CR3-T33 | 全局 badge/toast 组件 (成就解锁/任务完成/碎片获得通知) | P1 | 无 | FE | 0.5d |

---

## 4. Wave 规划

### Wave 1：数据层 + 导航基础（Week 1-2, 8 个工作日）

**目标**：所有表结构就绪，导航可跳转

```
CR3-T01  scripts 扩展 + script_stats         [BE, 1.5d]
CR3-T02  script_tags 表                      [BE, 1d]
CR3-T08  character_profiles 表               [BE, 1.5d]
CR3-T14  save_snapshots 表                   [BE, 1d]
CR3-T15  ending_progress 表                  [BE, 1d]
CR3-T11  user_follows 表 + API               [BE, 1d]
CR3-T31  Alembic 迁移整合                     [BE, 1.5d]
CR3-T32  导航栏增强                           [FE, 1d]
```

**里程碑**：`alembic upgrade head` 成功，全部 P0 表可查询，导航栏可跳转到新页面骨架

### Wave 2：P0 三模块并行（Week 2-4, 12 个工作日）

**目标**：剧本发现、角色卡片、存档管理功能完成

```
Track A - 剧本发现 (BE+FE):
  CR3-T03  discover API                      [BE, 2d]
  CR3-T04  recommendations API               [BE, 2d]
  CR3-T05  DiscoverView                      [FE, 3d]
  CR3-T06  HomeView "继续玩"                  [FE, 1.5d]
  CR3-T07  热度排行                           [FE, 1d]

Track B - 角色卡片 (BE+FE):
  CR3-T09  characters API                    [BE, 1.5d]
  CR3-T10  affection-rank API                [BE, 0.5d]
  CR3-T12  CharactersView                    [FE, 2d]
  CR3-T13  CharacterDetailView               [FE, 2d]

Track C - 存档管理 (BE+FE):
  CR3-T16  saves CRUD API                    [BE, 1.5d]
  CR3-T17  snapshot API + 自动触发器          [BE, 2d]
  CR3-T18  ending-progress API               [BE, 0.5d]
  CR3-T19  session fork API                  [BE, 2d]
  CR3-T20  SaveManagerView                   [FE, 3d]
```

**里程碑**：Discover / Characters / Saves 三个 P0 页面可完整使用

### Wave 3：P1 模块 + 集成（Week 4-5, 10 个工作日）

**目标**：成就/碎片/任务增强 + 全量回归

```
Track D - 成就系统:
  CR3-T23  成就表 + 种子数据                   [BE, 1.5d]
  CR3-T24  成就 API                           [BE, 1.5d]
  CR3-T25  成就触发器                          [BE, 2d]
  CR3-T26  AchievementView                    [FE, 2d]
  CR3-T27  RewardPopup                        [FE, 1d]

Track E - 碎片可视化 + 任务增强:
  CR3-T21  碎片 summary API                    [BE, 1d]
  CR3-T22  ShardCenterView                     [FE, 2d]
  CR3-T28  活跃度表扩展                         [BE, 0.5d]
  CR3-T29  活跃度计算服务                       [BE, 1d]
  CR3-T30  TaskPanel                           [FE, 1.5d]
  CR3-T33  全局 badge                          [FE, 0.5d]
```

**里程碑**：全部 6 个模块可用，集成测试通过

### Wave 总览

| Wave | 周期 | 目标 | 任务数 | BE 工时 | FE 工时 |
|------|------|------|--------|---------|---------|
| Wave 1 | Week 1-2 | 数据层 + 导航 | 8 | 9.5d | 1d |
| Wave 2 | Week 2-4 | P0 三模块 (发现/角色/存档) | 13 | 9.5d | 13.5d |
| Wave 3 | Week 4-5 | P1 三模块 (成就/碎片/任务) + 集成 | 12 | 7.5d | 7.5d |
| **总计** | **5 周** | **全部 6 模块** | **33 任务** | **26.5d** | **22d** |

---

## 5. 技术风险识别

### 5.1 按模块风险

| 模块 | 技术难点 | 风险级 | 缓解方案 |
|------|---------|--------|---------|
| **1. 剧本发现** | 推荐算法冷启动（新用户无行为数据） | 中 | MVP 用规则推荐 (preferred_genre + 热度排序)，不做 ML；fallback 为热度排序 |
| **2. 角色卡片** | 立绘资源加载性能（大量高清立绘同屏） | 低 | 列表页用缩略图 (300px webp)，详情页加载原图；懒加载 + CDN |
| **3. 存档管理** | 存档快照数据量大 (JSONB)；多分支并发冲突 | **高** | snapshot_data 限制 64KB；fork 时用乐观锁 (version 字段)；定期清理 30 天未活跃 + 非 pinned 快照 |
| **4. 碎片可视化** | 无特殊风险（只读查询） | 低 | 复用现有 fragments/fragment_transactions 表 |
| **6. 成就系统** | 事件驱动触发器的性能（每次游戏事件都检查所有成就） | 中 | 成就条件预编译为规则表；按 category 分批检查；Redis 缓存已检查标记 |
| **7. 每日任务** | 跨时区日期计算 | 低 | 统一 UTC+0 日切割（与现有 daily_checkins 一致） |

### 5.2 可复用现有代码

| 现有代码 | 复用于 | 复用程度 |
|---------|--------|---------|
| `scripts` 表 + ScriptService | 模块1 剧本发现 | 高：扩展字段即可 |
| `characters` 表 + 现有立绘系统 | 模块2 角色卡片 | 高：扩展 profile 字段 |
| `game_sessions` 表 + choice_history | 模块3 存档管理 | 中：扩展 snapshot 关联 |
| `affection` 表 | 模块2 好感度排行 | 高：直接查询聚合 |
| `fragments` + `fragment_transactions` | 模块4 碎片可视化 | 高：纯读取，无需改表 |
| `daily_tasks` 表 | 模块7 每日任务 | 高：扩展 activity_points |
| `achievements` 表 (待确认) | 模块6 成就系统 | 中：可能需重建 |
| Pinia stores + API client | 全部模块 | 高：复用现有模式 |
| PWA Notification (CR-002) | 角色关注通知 | 高：复用 Service Worker |

### 5.3 需新引入的技术/工具

| 技术/工具 | 用于 | 是否需要 ADR |
|----------|------|-------------|
| `vue-draggable-plus` (可选) | 模块3 存档拖拽排序 | 否：轻量库，可选 |
| `@vueuse/core` (已有) | 模块1+3+7 各种 composable | 否：已使用 |
| **无需新引入** | — | UGC 富文本编辑器已移除，无新技术依赖 |

### 5.4 性能瓶颈预测

| 瓶颈点 | 影响 | 阈值 | 优化方案 |
|--------|------|------|---------|
| DiscoverView 剧本列表加载 | 首屏慢 | >50 个剧本 | 分页 (20/page) + 骨架屏 + 图片懒加载 |
| save_snapshots JSONB 查询 | 存档列表慢 | >100 快照/用户 | 索引 (user_id, created_at)；列表只返回元数据不含 snapshot_data |
| 成就触发器 | 游戏事件处理延迟 | >50 个成就定义 | 按 category 分批；Redis 缓存进度；异步检查 |
| 角色卡片立绘 | 列表页内存 | >30 个角色同屏 | 虚拟滚动 + 缩略图 (webp 300px) |

---

## 6. 建议路由结构

### 6.1 新增路由

| 路由 | View 组件 | Auth | 说明 |
|------|----------|------|------|
| `/discover` | DiscoverView | Optional | 剧本发现页（未登录可浏览，操作需登录） |
| `/characters` | CharactersView | Optional | 角色图鉴列表 |
| `/characters/:characterId` | CharacterDetailView | Optional | 角色详情 |
| `/saves` | SaveManagerView | Required | 存档管理器 |
| `/shards` | ShardCenterView | Required | 碎片经济可视化（只读） |
| `/achievements` | AchievementView | Required | 成就墙 |

### 6.2 扩展现有路由

| 路由 | 扩展内容 |
|------|---------|
| `/home` | 顶部增加"继续玩"大卡片 + 每日任务面板 (TaskPanel) + 活跃度宝箱 |
| `/scripts/:scriptId` | 增加结局收集进度条 + 标签/难度显示 |

### 6.3 导航结构调整

```
底部 Tab Bar (现有):
  [首页] [社区] [画廊] [我的]

调整为:
  [首页] [发现] [角色] [我的]

"我的"页面内入口:
  存档管理 | 成就墙 | 碎片中心 | 设置 | 画廊(保留)
```

### 6.4 与现有路由兼容性

| 检查项 | 结果 |
|--------|------|
| `/scripts/:scriptId` 现有 ScriptDetailView | ✅ 兼容：扩展内容，不改路由 |
| `/community` 现有 CommunityView | ✅ 不影响：保留原样，不在 CR-003 范围 |
| `/game/:sessionId/free-chat` (CR-002) | ✅ 兼容：无变更 |
| `/game/:sessionId/route-map` (CR-002) | ✅ 兼容：无变更 |
| 所有 `meta: { requiresAuth }` 路由 | ✅ 兼容：新路由遵循相同 auth guard |

---

## 7. 待确认事项（提交 PL/PM）

| # | 问题 | 影响范围 | 建议默认值 |
|---|------|---------|-----------|
| Q1 | `achievements` 表当前实际 schema 是什么？database.md 未记录 | 模块6 成就系统 | 检查 Alembic 迁移历史，可能需要新建 achievement_definitions 替代 |
| Q2 | "继续玩" 模块：同一剧本多存档时显示哪个？ | 模块1 API 逻辑 | 显示最近更新的 session |
| Q3 | 角色关注后推送通知：复用 PWA Notification (CR-002 AC-056)？ | 模块2 通知逻辑 | 复用 PWA Notification |
| Q4 | 存档快照保留策略：永久 or 30 天自动清理？ | 模块3 存储成本 | 30 天自动清理 + 用户手动 pinned 保留 |
| Q5 | 碎片中心是否需要展示"获取途径"引导（如签到/任务入口链接）？ | 模块4 FE 工作量 | 是：增加 0.5d FE 引导组件 |
| Q6 | 成就"社交类"（发布帖子/获赞）是否从 CR-003 移除？因 UGC 不在范围 | 模块6 成就分类 | 移除社交类，改为"活跃类"（签到/连续游玩等） |

---

## 8. 与现有文档的关系

| 文档 | CR-003 影响 |
|------|------------|
| `docs/database/database.md` | +9 新表 + 5 扩展表 schema |
| `docs/api/api.md` | +21 新 API endpoint (总计 66) |
| `docs/architecture/architecture.md` | +recommendation_service, +snapshot_service, +achievement_service, +activity_service |
| `docs/security/security.md` | 存档权限校验 (用户只能操作自己的存档) |
| `docs/runtime/runtime-contract.md` | 新增 6 路由、Browser E2E 用户动作 |
| `docs/decisions/decisions.md` | 无新 ADR（无新技术选型） |

---

## 9. 排除项记录

| 排除项 | 原因 | 后续 |
|--------|------|------|
| 社区与 UGC 功能 | CEO 澄清：CR-003 不涉及 UGC | 可列入 CR-004 |
| 剧本创作工坊 | CEO 澄清：CR-003 不涉及 UGC | 可列入 CR-004 |
| 评论与讨论区 | CEO 澄清：CR-003 不涉及社区 | 可列入 CR-004 |
| 创作者认证 | CEO 澄清：CR-003 不涉及 UGC | 可列入 CR-004 |
| 真实支付/首充奖励 | CEO 澄清：不涉及支付 | 沿用 mock 支付 |
| 碎片礼包购买 | 不在 CR-003 范围 | 碎片中心仅做展示 |
