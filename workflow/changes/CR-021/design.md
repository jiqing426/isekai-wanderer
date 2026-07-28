# CR-021 DESIGN阶段 - 技术设计文档

## 设计时间
2026-07-28T20:25:00+08:00

## 设计人
Architect (PL代理)

## 1. 系统架构设计

### 1.1 整体架构
```
┌─────────────────────────────────────────────────────────┐
│                    前端应用 (Vue3)                        │
├─────────────────────────────────────────────────────────┤
│  Header组件                                              │
│  ├─ 导航Tab列表                                          │
│  └─ 角色聊天Tab (新增)                                   │
├─────────────────────────────────────────────────────────┤
│  CharacterChatView (新增页面)                            │
│  ├─ 左侧：角色列表组件                                   │
│  │   ├─ 角色卡片                                         │
│  │   └─ 好感度进度条                                     │
│  ├─ 右侧：聊天窗口组件                                   │
│  │   ├─ 角色信息头部                                     │
│  │   ├─ 消息列表区                                       │
│  │   ├─ 推荐话题区                                       │
│  │   └─ 输入栏组件                                       │
│  │       ├─ 加号按钮                                     │
│  │       ├─ 文本输入框                                   │
│  │       ├─ 发送按钮                                     │
│  │       └─ 功能菜单弹窗                                 │
│  └─ 弹窗组件                                             │
│      ├─ 送礼弹窗                                         │
│      └─ 送礼记录弹窗                                     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    后端API (FastAPI)                      │
├─────────────────────────────────────────────────────────┤
│  复用API:                                                │
│  ├─ GET /api/v1/affection (获取角色好感度)               │
│  ├─ POST /api/v1/gifts/send (送礼)                     │
│  └─ GET /api/v1/gifts/history (送礼记录)               │
├─────────────────────────────────────────────────────────┤
│  新增API:                                                │
│  ├─ GET /api/v1/character-chat/{character_id}/messages  │
│  ├─ POST /api/v1/character-chat/{character_id}/messages │
│  └─ GET /api/v1/character-chat/{character_id}/topics    │
└─────────────────────────────────────────────────────────┘
```

### 1.2 技术栈
- **前端框架**: Vue3 + TypeScript
- **UI组件库**: Naive UI
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios
- **样式**: CSS + Naive UI主题

## 2. 组件设计

### 2.1 页面结构
```
CharacterChatView.vue (主页面)
├─ CharacterList.vue (角色列表组件)
│  └─ CharacterCard.vue (角色卡片)
├─ ChatWindow.vue (聊天窗口组件)
│  ├─ ChatHeader.vue (聊天头部)
│  ├─ MessageList.vue (消息列表)
│  │  └─ MessageBubble.vue (消息气泡)
│  ├─ TopicList.vue (推荐话题)
│  │  └─ TopicTag.vue (话题标签)
│  └─ ChatInput.vue (输入栏)
│     ├─ PlusButton.vue (加号按钮)
│     ├─ MessageInput.vue (文本输入)
│     ├─ SendButton.vue (发送按钮)
│     └─ FunctionMenu.vue (功能菜单弹窗)
└─ 弹窗组件
   ├─ GiftModal.vue (送礼弹窗)
   └─ GiftHistoryModal.vue (送礼记录弹窗)
```

### 2.2 组件职责

#### CharacterChatView.vue
- **职责**: 页面容器，管理整体状态和布局
- **状态**: 
  - 当前选中角色ID
  - 角色列表数据
  - 聊天消息数据
  - 弹窗显示状态

#### CharacterList.vue
- **职责**: 展示角色列表，处理角色选择
- **Props**: 
  - `characters`: 角色列表
  - `selectedCharacterId`: 当前选中角色ID
- **Events**: 
  - `select-character`: 选择角色事件

#### ChatWindow.vue
- **职责**: 展示聊天窗口，管理消息发送
- **Props**: 
  - `character`: 当前角色信息
  - `messages`: 消息列表
  - `topics`: 推荐话题
- **Events**: 
  - `send-message`: 发送消息事件
  - `select-topic`: 选择话题事件

#### ChatInput.vue
- **职责**: 输入栏组件，管理输入状态
- **Props**: 
  - `disabled`: 是否禁用
- **Events**: 
  - `send`: 发送消息事件
  - `open-gift`: 打开送礼弹窗
  - `open-history`: 打开送礼记录

## 3. API设计

### 3.1 获取聊天消息
```typescript
GET /api/v1/character-chat/{character_id}/messages

请求参数:
- page: number (页码，默认1)
- page_size: number (每页数量，默认20)

响应:
{
  "messages": [
    {
      "message_id": "string",
      "sender_type": "npc" | "user",
      "content": "string",
      "created_at": "datetime"
    }
  ],
  "total": number,
  "page": number,
  "page_size": number
}
```

### 3.2 发送聊天消息
```typescript
POST /api/v1/character-chat/{character_id}/messages

请求体:
{
  "content": "string"
}

响应:
{
  "message_id": "string",
  "sender_type": "user",
  "content": "string",
  "created_at": "datetime"
}
```

### 3.3 获取推荐话题
```typescript
GET /api/v1/character-chat/{character_id}/topics

响应:
{
  "topics": [
    {
      "topic_id": "string",
      "topic_text": "string"
    }
  ]
}
```

## 4. 数据模型设计

### 4.1 角色数据 (复用现有)
```typescript
interface Character {
  character_id: string;
  character_name: string;
  avatar_url: string;
  affection_level: string;
  affection_value: number;
}
```

### 4.2 聊天消息 (新增)
```typescript
interface ChatMessage {
  message_id: string;
  character_id: string;
  sender_type: 'npc' | 'user';
  content: string;
  created_at: Date;
}
```

### 4.3 推荐话题 (新增)
```typescript
interface ChatTopic {
  topic_id: string;
  character_id: string;
  topic_text: string;
}
```

## 5. 状态管理设计

### 5.1 Pinia Store
```typescript
// stores/characterChat.ts
interface CharacterChatState {
  characters: Character[];
  selectedCharacterId: string | null;
  messages: Map<string, ChatMessage[]>; // character_id -> messages
  topics: Map<string, ChatTopic[]>; // character_id -> topics
  loading: boolean;
  error: string | null;
}

// Actions
- fetchCharacters(): 获取角色列表
- selectCharacter(characterId: string): 选择角色
- fetchMessages(characterId: string): 获取聊天消息
- sendMessage(characterId: string, content: string): 发送消息
- fetchTopics(characterId: string): 获取推荐话题
```

## 6. 路由设计

### 6.1 新增路由
```typescript
// router/index.ts
{
  path: '/character-chat',
  name: 'CharacterChat',
  component: () => import('@/views/CharacterChatView.vue'),
  meta: { requiresAuth: true }
}
```

### 6.2 Header导航更新
```typescript
// components/Header.vue
const navItems = [
  { label: '首页', path: '/' },
  { label: '剧本', path: '/scripts' },
  { label: '角色', path: '/characters' },
  { label: '角色聊天', path: '/character-chat' } // 新增
];
```

## 7. 样式设计

### 7.1 布局结构
```css
.character-chat-container {
  display: flex;
  height: calc(100vh - 60px); /* 减去Header高度 */
}

.character-list {
  width: 280px;
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
}

.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
}
```

### 7.2 弹窗层级管理
```css
/* z-index层级定义 */
.function-menu { z-index: 1000; }
.gift-modal { z-index: 1100; }
.gift-history-modal { z-index: 1100; }
```

## 8. 性能优化

### 8.1 消息加载优化
- 分页加载，每次加载20条
- 虚拟滚动（消息数量>100时启用）
- 消息缓存（已加载的消息缓存在内存中）

### 8.2 好感度更新优化
- 轮询间隔：5秒
- 仅更新当前选中角色的好感度
- 使用防抖避免频繁请求

### 8.3 图片加载优化
- 角色头像懒加载
- 图片缓存策略

## 9. 任务分解

### 9.1 前端任务
| 任务ID | 任务名称 | 优先级 | 预估时间 |
|--------|---------|--------|----------|
| DEV-FE-001 | 创建CharacterChatView页面 | P0 | 2h |
| DEV-FE-002 | 实现CharacterList组件 | P0 | 2h |
| DEV-FE-003 | 实现ChatWindow组件 | P0 | 3h |
| DEV-FE-004 | 实现MessageList和MessageBubble组件 | P0 | 2h |
| DEV-FE-005 | 实现ChatInput组件 | P0 | 2h |
| DEV-FE-006 | 实现FunctionMenu弹窗 | P1 | 1h |
| DEV-FE-007 | 实现GiftModal弹窗 | P1 | 2h |
| DEV-FE-008 | 实现GiftHistoryModal弹窗 | P1 | 1h |
| DEV-FE-009 | 实现TopicList组件 | P1 | 1h |
| DEV-FE-010 | 创建Pinia Store | P0 | 2h |
| DEV-FE-011 | 集成API调用 | P0 | 2h |
| DEV-FE-012 | Header导航更新 | P0 | 0.5h |
| DEV-FE-013 | 路由配置 | P0 | 0.5h |
| DEV-FE-014 | 样式优化和响应式适配 | P1 | 2h |
| DEV-FE-015 | 弹窗层级管理 | P1 | 1h |

### 9.2 后端任务
| 任务ID | 任务名称 | 优先级 | 预估时间 |
|--------|---------|--------|----------|
| DEV-BE-001 | 创建聊天消息数据模型 | P0 | 1h |
| DEV-BE-002 | 实现获取聊天消息API | P0 | 1h |
| DEV-BE-003 | 实现发送聊天消息API | P0 | 1h |
| DEV-BE-004 | 创建推荐话题数据模型 | P1 | 0.5h |
| DEV-BE-005 | 实现获取推荐话题API | P1 | 0.5h |
| DEV-BE-006 | 数据库迁移脚本 | P0 | 0.5h |

## 10. 测试策略

### 10.1 单元测试
- 组件单元测试（Vue Test Utils）
- Store单元测试
- API调用测试

### 10.2 集成测试
- 页面加载测试
- 角色选择测试
- 消息发送测试
- 弹窗交互测试

### 10.3 E2E测试
- 完整用户流程测试
- 跨浏览器兼容性测试

## 11. 部署策略

### 11.1 部署步骤
1. 后端数据库迁移
2. 后端API部署
3. 前端代码部署
4. 功能验证测试

### 11.2 回滚方案
- 数据库回滚脚本
- 前端版本回退
- API版本控制

## 12. 风险评估

| 风险ID | 风险描述 | 影响 | 概率 | 缓解措施 |
|--------|---------|------|------|----------|
| R-001 | 弹窗层级管理复杂度 | 中 | 中 | 使用Naive UI Modal组件，统一管理z-index |
| R-002 | 好感度实时更新性能 | 低 | 低 | 轮询间隔5秒，仅更新当前角色 |
| R-003 | 移动端适配问题 | 中 | 中 | 响应式布局，优先保证PC端 |
| R-004 | 消息历史加载性能 | 低 | 低 | 分页加载，虚拟滚动 |

## 设计结论

✅ **设计完成** - 技术方案可行，任务分解清晰，风险可控

---
设计时间: 2026-07-28T20:25:00+08:00
设计人: Architect (PL代理)
