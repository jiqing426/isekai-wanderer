# 每日任务系统增强

## Overview

在现有每日任务基础上增加活跃度积分和宝箱机制。

## Requirements

### Requirement: 每日任务列表
- HomeView 内嵌任务面板
- 展示当日任务（玩一个章节/签到/查看角色）

#### Scenario: 查看每日任务
- Given: 用户访问首页
- When: 查看任务面板
- Then: 展示 3-5 个当日任务及完成状态

### Requirement: 任务进度条
- 显示完成 X/Y 个任务
- 全部完成获额外碎片奖励

#### Scenario: 查看任务进度
- Given: 用户在任务面板
- When: 查看进度条
- Then: 显示"已完成 2/5 个任务"

### Requirement: 活跃度宝箱
- 活跃度到阈值解锁宝箱
- 宝箱随机获得碎片/道具

#### Scenario: 领取宝箱
- Given: 用户完成 3 个任务，活跃度达 60
- When: 点击宝箱
- Then: 随机获得 10-50 碎片，activity_chests 记录领取

## Data Model Impact

### New Tables
- `activity_chests`: user_id, date, threshold, reward_json, claimed

### Extended Tables
- `daily_tasks`: activity_points

## API Endpoints
- GET /api/v1/daily/tasks (已有，扩展 activity_points 字段)
- POST /api/v1/daily/tasks/:taskId/claim (已有)
- GET /api/v1/daily/activity (活跃度进度+宝箱状态)
- POST /api/v1/daily/chest/claim (领取宝箱)

## FE Components
- TaskPanel (HomeView 内嵌：任务列表+进度条+活跃度宝箱)
- TaskItem (任务项)
- ActivityChest (活跃度宝箱)
