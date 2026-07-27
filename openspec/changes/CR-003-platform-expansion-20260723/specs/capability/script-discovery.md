# 剧本发现与推荐系统

## Overview

用户可通过发现页按类型/标签/难度筛选剧本，查看热度排行，首页展示继续玩卡片。

## Requirements

### Requirement: 智能推荐
- 首页顶部显示"继续玩"大卡片，展示用户最近未完成的剧本
- 推荐列表根据用户已玩剧本类型和角色偏好排序
- 推荐算法可解释（如"因为你玩了《XX》"）

#### Scenario: 新用户无行为数据
- Given: 用户首次登录，无游玩记录
- When: 访问首页
- Then: 展示热度排行前 10 的剧本

#### Scenario: 有行为数据用户
- Given: 用户已玩过 2 个恋爱类剧本
- When: 访问首页
- Then: 推荐列表优先展示恋爱类剧本

### Requirement: 分类筛选
- 按类型筛选：恋爱/奇幻/悬疑/科幻
- 按标签筛选：HE/BE/多结局
- 按难度筛选：新手/进阶/硬核

#### Scenario: 按类型筛选
- Given: 用户在发现页
- When: 选择"恋爱"类型
- Then: 列表仅展示恋爱类剧本

### Requirement: 热度排行
- 按游玩人数排序
- 按评分排序
- 按收藏数排序

#### Scenario: 按游玩人数排序
- Given: 用户在发现页
- When: 选择"热度"排序
- Then: 列表按 play_count 降序排列

## Data Model Impact

### New Tables
- `script_tags`: script_id, tag, tag_type (genre/theme/difficulty)
- `script_stats`: script_id, play_count, rating, favorite_count

### Extended Tables
- `scripts`: difficulty, cover_image_url, description, estimated_duration

## API Endpoints
- GET /api/v1/scripts/discover (分页+筛选+排序)
- GET /api/v1/scripts/recommendations (个性化推荐)
- GET /api/v1/game/continue (最近未完成 session)

## FE Components
- DiscoverView (筛选栏+排序+剧本卡片网格+推荐区)
- HomeView 继续玩大卡片
- RankingList (热度排行组件)
