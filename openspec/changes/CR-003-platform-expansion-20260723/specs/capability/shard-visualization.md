# 碎片经济体系可视化

## Overview

用户可查看碎片余额、消费记录、获取途径（纯展示，复用现有 fragments 表）。

## Requirements

### Requirement: 碎片用途展示
- /shards 页面展示碎片用途（解锁章节/买装扮/抽卡/送礼物）
- 每个用途有图标+文字说明

#### Scenario: 查看碎片用途
- Given: 用户访问 /shards
- When: 页面加载
- Then: 展示 4 个用途卡片（解锁章节/买装扮/抽卡/送礼物）

### Requirement: 消费记录流水
- 展示每笔碎片消费明细
- 支持按时间筛选

#### Scenario: 查看消费记录
- Given: 用户在碎片中心
- When: 点击"消费记录"tab
- Then: 展示 fragment_transactions 表最近 30 条记录

### Requirement: 碎片获取途径
- 展示碎片获取方式（签到/完成任务/邀请好友）
- 每种方式有引导按钮

#### Scenario: 查看获取途径
- Given: 用户在碎片中心
- When: 点击"获取途径"tab
- Then: 展示 3 个途径卡片（签到/任务/邀请），每个有"去完成"按钮

## Data Model Impact

### New Tables
- 无（复用现有 fragments + fragment_transactions）

### Extended Tables
- 无

## API Endpoints
- GET /api/v1/shards/summary (余额+最近交易+获取途径统计)

## FE Components
- ShardCenterView (用途展示+消费记录+获取途径+当前余额)
- UsageGrid (用途图标网格)
- TransactionList (消费记录列表)
- AcquisitionGuide (获取途径引导)
