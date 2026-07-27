# 角色卡片系统

## Overview

用户可查看角色图鉴、好感度排行、对话预览，关注角色。

## Requirements

### Requirement: 角色图鉴
- /characters 列表页展示所有角色卡片
- /characters/:id 详情页展示立绘/描述/背景故事/性格标签

#### Scenario: 查看角色列表
- Given: 用户访问 /characters
- When: 页面加载
- Then: 展示所有角色卡片（已解锁/未解锁区分）

### Requirement: 好感度排行榜
- 展示用户与各角色的好感度进度
- 支持按好感度排序

#### Scenario: 查看好感度排行
- Given: 用户访问角色详情页
- When: 查看好感度区域
- Then: 展示当前用户与该角色的好感度等级和进度

### Requirement: 角色对话预览
- 未玩过的剧本也能看到角色示例对话

#### Scenario: 查看示例对话
- Given: 用户访问角色详情页
- When: 点击"查看对话"
- Then: 展示 3-5 条示例对话

### Requirement: 收藏/关注角色
- 点击关注按钮，角色加入关注列表
- 关注后新剧本上线时推送通知（复用 PWA AC-056）

#### Scenario: 关注角色
- Given: 用户在角色详情页
- When: 点击关注按钮
- Then: 按钮状态切换为已关注，user_follows 表记录

## Data Model Impact

### New Tables
- `character_profiles`: character_id, profile_text, backstory, personality_tags, example_dialogue
- `user_follows`: user_id, target_type, target_id

### Extended Tables
- `characters`: is_featured, sort_order

## API Endpoints
- GET /api/v1/characters (列表)
- GET /api/v1/characters/:id (详情)
- GET /api/v1/characters/affection-rank (好感度排行)
- POST/DELETE /api/v1/follows (关注/取关)

## FE Components
- CharactersView (卡片网格)
- CharacterDetailView (立绘+背景故事+性格标签+对话预览+好感度+关注)
- CharacterCard (列表卡片)
- AffectionRank (好感度排行组件)
- FollowButton (关注按钮)
