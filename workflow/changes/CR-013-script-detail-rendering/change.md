# CR-013 剧本详情页面渲染

## 变更概述

实现剧本详情页面的分层渲染，支持6种节点类型，强制使用UUID v4标准。

## 需求分析

### 一、节点类型定义 [P0] [BE+FE]

**6种节点类型：**
1. `fixed_scene` - 固定场景节点
2. `ai_dialog` - AI对话节点
3. `choice_point` - 选择点节点
4. `converge_node` - 汇聚节点
5. `cg_trigger` - CG触发节点
6. `ending_node` - 结局节点

### 二、页面分层渲染 [P0] [FE]

**渲染层次：**
1. 头部信息（剧本标题、封面、简介）
2. 章节折叠面板（按章节分组）
3. 节点卡片（6种类型不同样式）

### 三、UUID v4标准 [P0] [BE]

**强制要求：**
- 所有剧本ID使用UUID v4格式
- 节点ID使用UUID v4格式
- 章节ID使用UUID v4格式

## API约定

### 1. GET /api/v1/scripts/{scriptId}/detail

**用途**：获取剧本详情（含节点数据）

**认证**：Bearer Token

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

**字段说明**：
- `scriptId`: 剧本ID（UUID v4）
- `chapters`: 章节列表
  - `chapterId`: 章节ID（UUID v4）
  - `nodes`: 节点列表
    - `nodeId`: 节点ID（UUID v4）
    - `type`: 节点类型（6种之一）
    - `isUnlocked`: 是否已解锁

## 任务分配

### BE任务（10小时）

1. **剧本详情API**（4小时）
   - 实现 GET /scripts/{scriptId}/detail
   - 返回完整剧本数据（含章节和节点）

2. **UUID v4生成**（2小时）
   - 确保所有ID使用UUID v4格式
   - 数据库字段类型检查

3. **节点数据查询**（4小时）
   - 按章节分组查询节点
   - 计算解锁状态和完成率

### FE任务（12小时）

1. **节点卡片组件**（6小时）
   - 6种节点类型组件
   - 不同样式和图标
   - 解锁/未解锁状态

2. **分层渲染逻辑**（3小时）
   - 头部信息组件
   - 章节折叠面板
   - 节点列表渲染

3. **进度显示**（3小时）
   - 完成率计算
   - 进度条展示

## 验收标准

- 6种节点类型正确渲染
- 页面分层显示正常
- UUID v4格式正确
- 解锁状态正确显示

## 时间估算

- BE：10小时
- FE：12小时
- 联调：2小时
- **总计：24小时（3天）**
