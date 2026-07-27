# 存档与多线路管理

## Overview

用户可管理存档、创建快照、从快照 fork 新线路、查看结局收集进度。

## Requirements

### Requirement: 存档管理器
- /saves 页面展示所有历史存档
- 支持重命名存档
- 支持删除存档
- 支持继续游戏

#### Scenario: 查看存档列表
- Given: 用户访问 /saves
- When: 页面加载
- Then: 展示所有存档（按剧本分组，显示进度和最后游玩时间）

### Requirement: 多线路并行
- 同一剧本可同时开多个存档
- 存档列表区分不同线路

#### Scenario: 同一剧本多存档
- Given: 用户已有一个《月光下的誓言》存档
- When: 再次开始该剧本
- Then: 创建新 session，存档列表显示两个独立存档

### Requirement: 存档快照
- 关键决策点自动创建快照
- 支持"回到那个选择"功能

#### Scenario: 自动快照
- Given: 用户在游戏中做出关键选择
- When: choice 提交后
- Then: save_snapshots 表自动创建记录

#### Scenario: 从快照 fork
- Given: 用户在存档管理器查看快照
- When: 点击"从这里开始"
- Then: 创建新 session，复制 choice_history 到快照点

### Requirement: 结局收集进度
- 每个剧本显示"已解锁结局 X/Y"
- 结局详情页展示解锁条件提示

#### Scenario: 查看结局进度
- Given: 用户访问存档管理器
- When: 查看某剧本
- Then: 显示"已解锁 2/5 结局"

## Data Model Impact

### New Tables
- `save_snapshots`: game_session_id, node_id, snapshot_data, label, is_auto, is_pinned
- `ending_progress`: user_id, script_id, unlocked_endings, total_endings

### Extended Tables
- `game_sessions`: snapshot_count, last_snapshot_at

## API Endpoints
- GET /api/v1/saves (存档列表)
- PUT /api/v1/saves/:id (重命名)
- DELETE /api/v1/saves/:id (删除)
- POST /api/v1/game/:sessionId/snapshot (手动快照)
- GET /api/v1/scripts/:id/ending-progress (结局进度)
- POST /api/v1/game/:sessionId/fork (从快照 fork)

## FE Components
- SaveManagerView (存档列表+重命名+删除+继续+快照时间线+结局进度)
- SaveList (存档列表)
- SaveCard (存档卡片)
- SnapshotTimeline (快照时间线)
- EndingProgress (结局进度条)
