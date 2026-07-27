# CR-013 API Contract - 剧本详情页面渲染

## 接口定义

### GET /api/v1/scripts/{scriptId}/detail

**用途**：获取剧本详情（含章节和节点数据）

**认证**：Bearer Token

**路径参数**：
- `scriptId`: 剧本ID（UUID v4格式）

**响应示例**：
```json
{
  "scriptId": "550e8400-e29b-41d4-a716-446655440000",
  "title": "樱花纷飞的季节",
  "cover": "https://cdn.example.com/covers/sakura.jpg",
  "description": "一个关于青春和爱情的故事...",
  "author": "剧本作者",
  "chapters": [
    {
      "chapterId": "550e8400-e29b-41d4-a716-446655440001",
      "title": "第一章：相遇",
      "nodes": [
        {
          "nodeId": "550e8400-e29b-41d4-a716-446655440010",
          "type": "fixed_scene",
          "title": "樱花树下",
          "content": "春天，樱花树下...",
          "background": "https://cdn.example.com/bg/sakura_tree.jpg",
          "isUnlocked": true
        },
        {
          "nodeId": "550e8400-e29b-41d4-a716-446655440011",
          "type": "ai_dialog",
          "title": "与樱的对话",
          "characterId": "char-001",
          "characterName": "樱",
          "dialogueOptions": ["你好", "今天天气不错"],
          "isUnlocked": true
        },
        {
          "nodeId": "550e8400-e29b-41d4-a716-446655440012",
          "type": "choice_point",
          "title": "重要选择",
          "choices": [
            {"text": "接受邀请", "nextNodeId": "550e8400-e29b-41d4-a716-446655440013"},
            {"text": "婉拒", "nextNodeId": "550e8400-e29b-41d4-a716-446655440014"}
          ],
          "isUnlocked": true
        },
        {
          "nodeId": "550e8400-e29b-41d4-a716-446655440013",
          "type": "converge_node",
          "title": "故事汇聚",
          "description": "无论选择什么，故事都会在这里汇聚",
          "isUnlocked": false
        },
        {
          "nodeId": "550e8400-e29b-41d4-a716-446655440014",
          "type": "cg_trigger",
          "title": "特殊CG",
          "cgId": "cg-001",
          "cgUrl": "https://cdn.example.com/cg/special.jpg",
          "isUnlocked": false
        },
        {
          "nodeId": "550e8400-e29b-41d4-a716-446655440015",
          "type": "ending_node",
          "title": "结局：永远的约定",
          "endingType": "good",
          "description": "两人约定永远在一起",
          "isUnlocked": false
        }
      ]
    }
  ],
  "totalNodes": 6,
  "unlockedNodes": 3,
  "completionRate": 50
}
```

## 节点类型定义

| 类型 | 说明 | 特殊字段 |
|------|------|---------|
| fixed_scene | 固定场景 | background |
| ai_dialog | AI对话 | characterId, characterName, dialogueOptions |
| choice_point | 选择点 | choices[] |
| converge_node | 汇聚节点 | description |
| cg_trigger | CG触发 | cgId, cgUrl |
| ending_node | 结局节点 | endingType, description |

## TypeScript 类型定义

```typescript
interface ScriptDetail {
  scriptId: string; // UUID v4
  title: string;
  cover: string;
  description: string;
  author: string;
  chapters: Chapter[];
  totalNodes: number;
  unlockedNodes: number;
  completionRate: number;
}

interface Chapter {
  chapterId: string; // UUID v4
  title: string;
  nodes: ScriptNode[];
}

interface ScriptNode {
  nodeId: string; // UUID v4
  type: 'fixed_scene' | 'ai_dialog' | 'choice_point' | 'converge_node' | 'cg_trigger' | 'ending_node';
  title: string;
  content?: string;
  isUnlocked: boolean;
  // 类型特定字段
  background?: string; // fixed_scene
  characterId?: string; // ai_dialog
  characterName?: string; // ai_dialog
  dialogueOptions?: string[]; // ai_dialog
  choices?: Choice[]; // choice_point
  description?: string; // converge_node, ending_node
  cgId?: string; // cg_trigger
  cgUrl?: string; // cg_trigger
  endingType?: 'good' | 'normal' | 'bad'; // ending_node
}

interface Choice {
  text: string;
  nextNodeId: string; // UUID v4
}
```

## 数据库变更

需要确保以下字段使用 UUID v4：
- scripts.script_id
- chapters.chapter_id
- nodes.node_id
