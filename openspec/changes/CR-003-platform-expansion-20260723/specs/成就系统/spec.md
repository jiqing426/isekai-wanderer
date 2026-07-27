# Spec: 成就系统（P1）

### Requirement: REQ-ACH-001 成就定义与存储

#### 需求描述
新建 `achievement_definitions` 表存储成就定义（代码、名称、描述、分类、目标数、奖励），`user_achievements` 表存储用户进度。Q1 确认：现有 29 表中无 achievements 表，直接新建。

#### Scenario: 成就定义与存储场景

| ID | Scenario | Given | When | Then |
|----|---------|-------|------|------|
| AC-ACH-001.1 | 成就种子数据存在 | 系统启动 | 查询 `achievement_definitions` | 至少 20 条成就定义，覆盖剧情/活跃/收集/隐藏四类 |
| AC-ACH-001.2 | 用户首次登录初始化 | 新用户注册 | 注册流程完成 | `user_achievements` 自动为该用户创建所有成就的进度记录（`progress=0`） |
| AC-ACH-001.3 | 成就分类正确 | 查询成就定义 | 按分类查询 | 四类均可查到：剧情类 / 活跃类 / 收集类 / 隐藏类 |

### 成就分类（Q6 确认：移除社交类，改为活跃类）

| 分类 | 示例 | 触发事件 |
|------|------|---------|
| 剧情类 | 通关 1/3/5 个剧本、解锁全部结局 | `game_completed`, `ending_unlocked` |
| 活跃类 | 连续签到 3/7/14/30 天、完成 10/30/50 个每日任务、连续 7 天游玩 | `streak_milestone`, `task_completed`, `daily_play` |
| 收集类 | 收集 5/10/20 张 CG、解锁 3/5/10 个角色 | `cg_unlocked`, `character_unlocked` |
| 隐藏类 | 特定选择触发彩蛋（如"连续选择沉默 3 次"） | `special_choice` |

### 成就定义字段约束

| 字段 | 约束 |
|------|------|
| `code` | VARCHAR(50) UNIQUE，如 `STORY_CLEAR_1`, `ACTIVE_STREAK_7` |
| `name` | VARCHAR(100)，显示名称 |
| `description` | TEXT，解锁条件说明 |
| `category` | VARCHAR(20)，四类之一 |
| `target_count` | INT，解锁所需进度 |
| `reward_type` | VARCHAR(20)，`fragments` / `title` / `cosmetic` |
| `reward_amount` | INT，碎片数量（title/cosmetic 时为 0） |
| `is_hidden` | BOOLEAN，隐藏成就在解锁前不显示详情 |
| `icon_url` | TEXT，成就图标 URL |

## REQ-ACH-002: 成就墙

### 需求描述
用户可访问 `/achievements` 查看成就墙，展示已获得和待解锁成就，每个成就显示进度条。

### Scenarios

| ID | Scenario | Given | When | Then |
|----|---------|-------|------|------|
| AC-ACH-002.1 | 查看成就墙 | 用户已登录 | 访问 `/achievements` | 显示成就分类 tab（剧情/活跃/收集/隐藏）+ 成就卡片网格 |
| AC-ACH-002.2 | 查看剧情类成就 | 用户在成就墙 | 点击"剧情"tab | 显示剧情类成就列表，已解锁显示金色 + 解锁时间，未解锁显示灰色 + 进度条 |
| AC-ACH-002.3 | 查看隐藏成就 | 用户在成就墙 | 点击"隐藏"tab | 未解锁的隐藏成就显示"???" + 锁图标，不显示名称和条件；已解锁显示完整信息 |
| AC-ACH-002.4 | 成就进度条 | 某成就目标为"通关 3 个剧本"，用户已通关 1 个 | 查看该成就卡片 | 显示进度条 1/3 (33%) |
| AC-ACH-002.5 | 成就总数统计 | 用户在成就墙顶部 | 查看总览 | 显示"已解锁 X/Y 个成就 (Z%)"总进度 |
| AC-ACH-002.6 | 空状态 | 新用户首次访问 | 访问 `/achievements` | 所有成就显示为灰色待解锁，进度 0% |

### 成就墙交互约束
- 分类 tab 切换无需页面刷新（前端 tab 组件）
- 已解锁成就排在前，未解锁排在后
- 进度条实时更新（从 API 获取最新进度）

## REQ-ACH-003: 成就触发器

### 需求描述
后端事件驱动触发器：当特定游戏事件发生时，检查相关成就条件，更新 `user_achievements.progress`。

### Scenarios

| ID | Scenario | Given | When | Then |
|----|---------|-------|------|------|
| AC-ACH-003.1 | 通关剧本触发 | 用户完成一个剧本 | 结局展示时 | `user_achievements` 中剧情类 `STORY_CLEAR_N` 进度 +1；若达到 `target_count` 则标记 `unlocked_at` |
| AC-ACH-003.2 | 签到里程碑触发 | 用户连续签到 7 天 | 签到成功时 | `user_achievements` 中 `ACTIVE_STREAK_7` 标记解锁 |
| AC-ACH-003.3 | CG 解锁触发 | 用户解锁一张 CG | CG 解锁事件 | `user_achievements` 中收集类进度 +1 |
| AC-ACH-003.4 | 隐藏成就触发 | 用户在游戏中连续选择"沉默"3 次 | 第 3 次选择后 | 隐藏成就 `HIDDEN_SILENT_3` 解锁 |
| AC-ACH-003.5 | 成就解锁通知 | 某成就解锁 | 触发器执行 | FE 显示全局 toast/popup："🎉 成就解锁：XXX！奖励 N 碎片" |
| AC-ACH-003.6 | 重复事件不重复解锁 | 成就已解锁 | 再次触发同一事件 | `user_achievements.unlocked_at` 不变，不重复发放奖励 |

### 触发器性能约束
- 成就检查异步执行（不阻塞主游戏流程）
- 按 `category` 分批检查（每次事件只检查相关分类）
- 单次事件处理延迟 < 200ms

## REQ-ACH-004: 成就奖励领取

### 需求描述
解锁成就后用户可领取奖励（碎片/称号/装扮）。领取操作将奖励写入用户账户。

### Scenarios

| ID | Scenario | Given | When | Then |
|----|---------|-------|------|------|
| AC-ACH-004.1 | 领取碎片奖励 | 成就已解锁且未领取 | 在成就墙点击"领取"按钮 | 碎片余额增加 `reward_amount`，`fragment_transactions` 新增一条 `type=achievement_reward` 记录 |
| AC-ACH-004.2 | 领取称号奖励 | 成就奖励类型为 `title` | 点击"领取" | 用户 `titles` 列表新增该称号（可扩展 `users` 表或独立 `user_titles` 表） |
| AC-ACH-004.3 | 已领取状态 | 成就奖励已领取 | 查看成就卡片 | 显示"已领取"标签，按钮禁用 |
| AC-ACH-004.4 | 批量领取 | 用户有多个未领取成就 | 点击"一键领取" | 所有未领取成就的奖励一次性发放，余额累加 |
| AC-ACH-004.5 | 领取失败 | 网络异常 | 点击领取 | 显示"领取失败，请重试"，不扣减奖励 |

### 奖励领取约束
- 解锁后奖励不会过期
- 碎片奖励写入 `fragment_transactions` 时需注明 `description` 为成就名
- 称号/装扮奖励的具体存储方式由 BE 设计（PM 不规定表结构）

## 数据模型需求

| 表 | 用途 | 关键字段 |
|----|------|---------|
| `achievement_definitions`（新建） | 成就定义 | `id`, `code UNIQUE`, `name`, `description`, `category`, `target_count`, `reward_type`, `reward_amount`, `is_hidden`, `icon_url` |
| `user_achievements`（新建） | 用户进度 | `id UUID`, `user_id FK`, `achievement_id FK`, `progress INT`, `unlocked_at TIMESTAMPTZ`, `claimed BOOLEAN DEFAULT FALSE`, `UNIQUE(user_id, achievement_id)` |

## 路由需求

| 路由 | 用途 | Auth |
|------|------|------|
| `/achievements` | 成就墙 | Required |

## 验收动作标注

- **Browser Interaction E2E**：成就墙 tab 切换、进度条显示、领取按钮点击、toast 通知展示，需 Playwright E2E 验证
- **API/DB 验证**：成就触发后 `user_achievements` 进度更新、领取后 `fragment_transactions` 新增记录，需真实后端状态验证
- **事件驱动验证**：游戏事件（通关/签到/CG 解锁）触发后成就进度异步更新，需验证延迟 < 200ms
- **幂等性验证**：重复事件不重复解锁，需 BE 单元测试覆盖
