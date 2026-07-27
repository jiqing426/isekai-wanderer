# CR-015 API Contract - 角色设定

## 接口定义

### 1. GET /api/v1/characters/{characterId}

**用途**：获取角色详情

**认证**：Bearer Token

**路径参数**：
- `characterId`: 角色ID（char-001/char-002/char-003）

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

**响应示例（校验通过）**：
```json
{
  "valid": true,
  "score": 95,
  "issues": [],
  "suggestions": []
}
```

**响应示例（校验失败）**：
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

## 角色列表

| 角色ID | 名称 | 性格标签 | 台词特征 |
|--------|------|---------|---------|
| char-001 | 白鳥雪乃 | 温柔、内向、善良 | 语尾带「呢」「哦」，说话缓慢 |
| char-002 | 花野美月 | 活泼、开朗、直率 | 语尾带「啦」「呀」，说话轻快 |
| char-003 | 凛 | 傲娇、强势、害羞 | 语尾带「哼」「笨蛋」，口是心非 |

## AI对话校验规则

| 规则 | 说明 | 严重级别 |
|------|------|---------|
| character_name_mismatch | 角色名一致性检查 | error |
| emotion_mismatch | 情感极性匹配检查 | warning |
| sensitive_word_detected | 敏感词过滤 | error |
| length_exceeded | 长度控制检查 | warning |
| worldview_violation | 世界观词汇检查 | warning |

## TypeScript 类型定义

```typescript
interface Character {
  characterId: string; // char-001/char-002/char-003
  name: string;
  nameEn: string;
  avatar: string;
  portrait: string;
  personality: {
    tags: string[];
    description: string;
  };
  dialogueStyle: {
    speechPattern: string;
    catchphrase: string;
    tone: string;
  };
  preferences: {
    likedGifts: string[];
    dislikedGifts: string[];
    likedTopics: string[];
  };
  affection: {
    currentLevel: number;
    currentValue: number;
    maxValue: number;
  };
  aiValidationRules: {
    characterName: string;
    emotionPolarity: string;
    sensitiveWords: string[];
    maxLength: number;
    worldviewTerms: string[];
  };
}

interface ValidateDialogueRequest {
  characterId: string;
  dialogue: string;
  context: {
    currentScene: string;
    affectionLevel: number;
  };
}

interface ValidateDialogueResponse {
  valid: boolean;
  score: number;
  issues: ValidationIssue[];
  suggestions: string[];
}

interface ValidationIssue {
  type: 'character_name_mismatch' | 'emotion_mismatch' | 'sensitive_word_detected' | 'length_exceeded' | 'worldview_violation';
  message: string;
  severity: 'error' | 'warning';
}
```

## 数据库变更

需要创建 characters 表：
- character_id (VARCHAR)
- name (VARCHAR)
- name_en (VARCHAR)
- avatar (VARCHAR)
- portrait (VARCHAR)
- personality_tags (JSON)
- personality_description (TEXT)
- dialogue_style (JSON)
- preferences (JSON)
- ai_validation_rules (JSON)
