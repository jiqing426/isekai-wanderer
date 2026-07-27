# CR-014 API Contract - 成就设定

## 接口定义

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
    },
    {
      "id": "ACH-015",
      "name": "传说之旅",
      "description": "解锁所有结局",
      "rarity": "epic",
      "icon": "achievement_015.png",
      "reward": 300,
      "condition": {
        "type": "all_endings",
        "value": 1
      },
      "isUnlocked": false,
      "progress": 3
    }
  ],
  "total": 15,
  "unlockedCount": 3,
  "totalReward": 1490
}
```

### 2. POST /api/v1/achievements/{id}/unlock

**用途**：手动解锁成就（测试用）

**认证**：Bearer Token

**路径参数**：
- `id`: 成就ID（ACH-001 ~ ACH-015）

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

## 成就列表

| ID | 名称 | 稀有度 | 碎片奖励 | 解锁条件 |
|----|------|--------|---------|---------|
| ACH-001 | 初次相遇 | common | 30 | 完成1次对话 |
| ACH-002 | 选择大师 | rare | 100 | 做出100次选择 |
| ACH-003 | CG收藏家 | common | 50 | 收集10张CG |
| ACH-004 | 剧情探索者 | rare | 150 | 解锁5个结局 |
| ACH-005 | 社交达人 | common | 40 | 添加5个好友 |
| ACH-006 | 连续登录 | common | 60 | 连续登录7天 |
| ACH-007 | 月度玩家 | rare | 120 | 连续登录30天 |
| ACH-008 | 礼物大师 | common | 45 | 送出20个礼物 |
| ACH-009 | 剧情分支 | rare | 130 | 探索10条剧情分支 |
| ACH-010 | 全角色解锁 | epic | 250 | 解锁所有角色 |
| ACH-011 | 对话专家 | common | 55 | 完成50次对话 |
| ACH-012 | 选择困难 | common | 35 | 做出50次选择 |
| ACH-013 | CG全收集 | epic | 280 | 收集所有CG |
| ACH-014 | 完美结局 | rare | 180 | 获得3个完美结局 |
| ACH-015 | 传说之旅 | epic | 300 | 解锁所有结局 |

## TypeScript 类型定义

```typescript
interface Achievement {
  id: string; // ACH-001 ~ ACH-015
  name: string;
  description: string;
  rarity: 'common' | 'rare' | 'epic';
  icon: string;
  reward: number; // 30~300
  condition: {
    type: 'dialogue_count' | 'choice_count' | 'cg_count' | 'endings_unlocked' | 'friends_count' | 'login_streak' | 'gifts_sent' | 'branches_explored' | 'characters_unlocked' | 'all_endings';
    value: number;
  };
  isUnlocked: boolean;
  unlockedAt?: string; // ISO timestamp
  progress?: number; // 当前进度（仅未解锁时显示）
}

interface AchievementListResponse {
  achievements: Achievement[];
  total: number;
  unlockedCount: number;
  totalReward: number;
}

interface UnlockAchievementResponse {
  success: boolean;
  achievement: {
    id: string;
    name: string;
    rarity: string;
    reward: number;
  };
  fragmentsAdded: number;
  newBalance: number;
}
```

## 数据库变更

需要创建 achievements 表：
- achievement_id (VARCHAR)
- user_id (UUID)
- unlocked_at (TIMESTAMP)
- progress (INTEGER)
