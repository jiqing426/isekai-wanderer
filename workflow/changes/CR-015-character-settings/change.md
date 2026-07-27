# CR-015 角色设定

## 变更概述

实现3个角色的完整设定，包含性格标签、台词特征、好感度偏好和AI对话校验规则。

## 需求分析

### 一、角色数据 [P0] [BE]

**3个角色：**
1. 白鳥雪乃（Shiratori Yukino）
2. 花野美月（Hanano Mitsuki）
3. 凛（Rin）

**每个角色包含：**
- 性格标签（如：温柔、傲娇、活泼）
- 台词特征（如：语尾、口头禅）
- 好感度偏好（喜欢的礼物、话题）

### 二、AI对话校验 [P0] [BE]

**5项校验规则：**
1. 角色名一致性 - 确保AI回复中使用正确的角色名
2. 情感极性匹配 - 确保情感表达与角色性格一致
3. 敏感词过滤 - 过滤不当内容
4. 长度控制 - 控制回复长度在合理范围
5. 世界观词汇 - 确保使用符合世界观的词汇

### 三、角色展示 [P0] [FE]

**角色详情页：**
- 展示角色立绘
- 显示性格标签
- 显示台词特征示例
- 显示好感度偏好

## API约定

### 1. GET /api/v1/characters/{characterId}

**用途**：获取角色详情

**认证**：Bearer Token

**响应示例**：
```json
{
  "characterId": "char-001",
  "name": "白鳥雪乃",
  "nameEn": "Shiratori Yukino",
  "avatar": "https://cdn.example.com/characters/yukino_avatar.png",
  "portrait": "https://cdn.example.com/characters/yukino_portrait.png",
  "personality": {
    "tags": ["温柔", "内向", "善良"],
    "description": "温柔内向的少女，说话轻声细语"
  },
  "dialogueStyle": {
    "speechPattern": "语尾常带「呢」「哦」",
    "catchphrase": "那个...我可以这样说吗？",
    "tone": "温柔、缓慢"
  },
  "preferences": {
    "likedGifts": ["书籍", "花束", "手写信"],
    "dislikedGifts": ["吵闹的玩具", "辛辣食物"],
    "likedTopics": ["文学", "自然", "音乐"]
  },
  "affection": {
    "currentLevel": 3,
    "currentValue": 450,
    "maxValue": 1000
  },
  "aiValidationRules": {
    "characterName": "白鳥雪乃",
    "emotionPolarity": "gentle",
    "sensitiveWords": ["粗鲁", "暴力"],
    "maxLength": 150,
    "worldviewTerms": ["学院", "图书馆", "樱花"]
  }
}
```

**字段说明**：
- `personality.tags`: 性格标签数组
- `dialogueStyle`: 台词风格
- `preferences`: 好感度偏好
- `affection`: 当前好感度状态
- `aiValidationRules`: AI对话校验规则

### 2. POST /api/v1/ai/validate-dialogue

**用途**：校验AI对话内容

**认证**：Bearer Token

**请求示例**：
```json
{
  "characterId": "char-001",
  "dialogue": "那个...我觉得今天的樱花很美呢",
  "context": {
    "currentScene": "樱花树下",
    "affectionLevel": 3
  }
}
```

**响应示例**：
```json
{
  "valid": true,
  "score": 95,
  "issues": [],
  "suggestions": []
}
```

**校验失败响应**：
```json
{
  "valid": false,
  "score": 60,
  "issues": [
    {
      "type": "character_name_mismatch",
      "message": "角色名不一致",
      "severity": "error"
    },
    {
      "type": "emotion_mismatch",
      "message": "情感极性不匹配",
      "severity": "warning"
    }
  ],
  "suggestions": [
    "建议使用更温柔的语气",
    "可以添加语尾词「呢」"
  ]
}
```

## 任务分配

### BE任务（8小时）

1. **角色数据模型**（3小时）
   - 创建characters表
   - 定义3个角色数据
   - 存储性格标签、台词特征、偏好

2. **AI对话校验引擎**（5小时）
   - 实现5项校验规则
   - 校验API接口
   - 校验结果评分

### FE任务（6小时）

1. **角色详情页**（3小时）
   - 展示角色立绘
   - 显示性格标签
   - 显示台词特征
   - 显示好感度偏好

2. **角色列表页**（2小时）
   - 展示3个角色卡片
   - 快速预览性格标签

3. **好感度进度条**（1小时）
   - 显示当前好感度
   - 进度条动画

## 验收标准

- 3个角色数据完整
- 性格标签正确显示
- AI对话校验准确
- 角色详情页渲染正常

## 时间估算

- BE：8小时
- FE：6小时
- 联调：2小时
- **总计：16小时（2天）**
