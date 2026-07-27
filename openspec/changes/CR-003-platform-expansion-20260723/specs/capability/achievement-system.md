# 成就系统

## Overview

用户可查看成就墙、进度、领取奖励。成就分 4 类：剧情/活跃/收集/隐藏。

## Requirements

### Requirement: 成就墙
- /achievements 页面展示已获得和待解锁成就
- 每个成就显示进度条

#### Scenario: 查看成就墙
- Given: 用户访问 /achievements
- When: 页面加载
- Then: 展示 4 个分类 tab（剧情/活跃/收集/隐藏），每个 tab 下展示成就列表

### Requirement: 成就类型
- 剧情类：通关 X 个剧本、解锁全部结局
- 活跃类：连续签到 X 天、完成 X 个每日任务
- 收集类：收集 X 张 CG、解锁 X 个角色
- 隐藏成就：特定选择触发的彩蛋

#### Scenario: 查看成就进度
- Given: 用户在成就墙
- When: 查看某成就
- Then: 显示"已通关 2/5 个剧本"进度条

### Requirement: 成就奖励
- 解锁成就获得碎片奖励
- 解锁成就获得装扮/称号

#### Scenario: 领取成就奖励
- Given: 用户完成某成就条件
- When: 点击"领取"按钮
- Then: 碎片余额增加，user_achievements 标记为 claimed

## Data Model Impact

### New Tables
- `achievement_definitions`: code, name, description, category, target_count, reward_type, reward_amount, is_hidden, icon_url
- `user_achievements`: user_id, achievement_id, unlocked_at, progress

### Extended Tables
- `achievements` (现有表，需确认 schema): category, reward_type, reward_amount, is_hidden, icon_url, sort_order

## API Endpoints
- GET /api/v1/achievements (定义列表+用户进度)
- POST /api/v1/achievements/:id/claim (领取奖励)

## FE Components
- AchievementView (成就墙+分类 tab+进度条)
- AchievementWall (成就墙容器)
- AchievementCard (成就卡片)
- ProgressBar (进度条)
- RewardPopup (奖励弹窗)

## Achievement Trigger Service
- 事件驱动：game_completed, cg_unlocked, streak_milestone 等事件触发成就检查
- 按 category 分批检查，Redis 缓存已检查标记
