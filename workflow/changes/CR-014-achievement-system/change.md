# CR-014 成就设定

## 变更概述

实现15个成就的完整系统，包含3种稀有度、碎片奖励、自动解锁和全屏动画。

## 需求分析

### 一、成就列表 [P0] [BE]

**15个成就：**
- ACH-001 ~ ACH-015
- 3种稀有度：普通（绿）、稀有（蓝）、史诗（紫）
- 碎片奖励：30~300不等

### 二、解锁规则 [P0] [BE+FE]

**自动解锁：**
- 监听游戏事件（对话次数、选择次数、CG收集等）
- 满足条件自动触发解锁

**全屏动画：**
- 解锁时播放全屏动画
- 显示成就名称、稀有度、碎片奖励

### 三、碎片发放 [P0] [BE]

**即时发放：**
- 解锁成就后立即发放碎片
- 记录碎片流水

## API约定

### 1. GET /api/v1/achievements

**用途**：获取成就列表

**认证**：Bearer Token

**响应示例**：
```json
{
  "achievements": [
    {
      "id": "ACH-001",
      "name": "初次相遇",
      "description": "完成第一次对话",
      "rarity": "common",
      "icon": "achievement_001.png",
      "reward": 30,
      "condition": {
        "type": "dialogue_count",
        "value": 1
      },
      "isUnlocked": true,
      "unlockedAt": "2026-07-23T10:00:00Z"
    },
    {
      "id": "ACH-002",
      "name": "选择大师",
      "description": "做出100次选择",
      "rarity": "rare",
      "icon": "achievement_002.png",
      "reward": 100,
      "condition": {
        "type": "choice_count",
        "value": 100
      },
      "isUnlocked": false,
      "progress": 45
    }
  ],
  "total": 15,
  "unlockedCount": 3,
  "totalReward": 1490
}
```

**字段说明**：
- `id`: 成就ID（ACH-001 ~ ACH-015）
- `rarity`: 稀有度（common/rare/epic）
- `reward`: 碎片奖励（30~300）
- `condition`: 解锁条件
  - `type`: 条件类型（dialogue_count/choice_count/cg_count等）
  - `value`: 目标值
- `isUnlocked`: 是否已解锁
- `progress`: 当前进度（仅未解锁时显示）

### 2. POST /api/v1/achievements/{id}/unlock

**用途**：手动解锁成就（测试用）

**认证**：Bearer Token

**响应示例**：
```json
{
  "success": true,
  "achievement": {
    "id": "ACH-001",
    "name": "初次相遇",
    "rarity": "common",
    "reward": 30
  },
  "fragmentsAdded": 30,
  "newBalance": 530
}
```

## 任务分配

### BE任务（10小时）

1. **成就数据模型**（3小时）
   - 创建achievements表
   - 定义15个成就数据

2. **解锁检测引擎**（4小时）
   - 监听游戏事件
   - 检查解锁条件
   - 触发解锁逻辑

3. **碎片发放**（3小时）
   - 解锁后发放碎片
   - 记录流水

### FE任务（9小时）

1. **成就列表页面**（4小时）
   - 展示15个成就
   - 按稀有度分类
   - 显示解锁状态和进度

2. **解锁动画**（3小时）
   - 全屏动画效果
   - 碎片飞入动画
   - 音效播放

3. **成就详情弹窗**（2小时）
   - 显示成就详情
   - 显示解锁时间

## 验收标准

- 15个成就正确显示
- 3种稀有度样式正确
- 解锁动画流畅
- 碎片发放正确

## 时间估算

- BE：10小时
- FE：9小时
- 联调：2小时
- **总计：21小时（3天）**
