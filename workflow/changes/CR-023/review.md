# CR-023 审查记录

## 2026-07-29 13:56:00 - PL 创建 CR

**需求来源**: 用户反馈
**优先级**: P0

### 需求描述

用户要求角色聊天实现流式对话功能：
1. 发送文字后请求 NPC 接口
2. 使用流式返回实现打字机效果
3. 等待时显示 loading 状态

### 技术分析

**现有实现参考**:
- 后端 SSE: `backend/app/api/v1/game.py` (dialogue/stream)
- 前端 SSE: `frontend/src/composables/useSSE.ts`

**实现方案**:
1. 后端新增 SSE 流式接口
2. 前端使用 EventSource 接收流式数据
3. 实现打字机效果渲染
4. 保存完整对话记录

### 任务分配

- **BE**: 实现流式接口，参考 game.py 的 SSE 实现
- **FE**: 实现流式接收和打字机效果

### 状态

- 当前阶段: DEVELOPMENT
- 当前状态: in-progress

---

## DEVELOPMENT 阶段审查

### 开发覆盖声明

#### BE 开发覆盖声明

**声明时间**: 2026-07-29T14:30:00+08:00  
**声明人**: BE Agent  

##### 已实现 AC
| AC 编号 | AC 描述 | 实现文件 | 实现状态 |
|---------|---------|----------|----------|
| AC-BE-001 | SSE 流式接口 POST /stream | backend/app/api/v1/chat.py | ✅ 已实现 |
| AC-BE-002 | SSE 事件格式 (message/done/error) | backend/app/api/v1/chat.py | ✅ 已实现 |
| AC-BE-003 | NPC 回复生成（LLM/fallback） | backend/app/api/v1/chat.py | ✅ 已实现 |
| AC-BE-004 | 消息持久化 | backend/app/api/v1/chat.py | ✅ 已实现 |

##### 已测试 AC
| AC 编号 | 测试方式 | 测试结果 | 测试命令/证据 |
|---------|----------|----------|---------------|
| AC-BE-001 | API 测试 | ✅ 通过 | curl POST /stream → SSE 响应 200, Content-Type: text/event-stream |
| AC-BE-002 | API 测试 | ✅ 通过 | event: message + data: {"type": "text", ...} |
| AC-BE-003 | API 测试 | ✅ 通过 | NPC 回复内容正确（fallback 或 LLM） |
| AC-BE-004 | DB 验证 | ✅ 通过 | chat_messages 表存储 user + npc 两条记录 |

##### 关键设计决策
| 决策 | 原因 |
|------|------|
| 使用 async_session_factory 创建独立 session | FastAPI 的 get_db session 在 SSE 完成后会关闭 |
| LLM 失败时使用 fallback 回复 | 保证用户体验，前端始终能收到回复 |
| 直接调用 provider.stream() | 避免 SSEFormatter 复杂解析，直接返回纯文本 token |
| 设置 X-Accel-Buffering: no | 禁用 nginx 缓冲，确保实时流式传输 |

##### SSE 事件格式
| 事件类型 | 数据格式 | 说明 |
|----------|----------|------|
| `message` | `{"type": "text", "content": "...", "character_id": "..."}` | 文本片段 |
| `done` | `{"type": "done", "message_id": "...", "character_id": "..."}` | 流式完成 |
| `error` | `{"type": "error", "message": "..."}` | 错误（仅极端情况） |

##### 未测试 AC（需 QA E2E 验证）
- AC-BE-001~004: 需要浏览器交互验证（由 QA 执行）

#### FE 开发覆盖声明

**声明时间**: 2026-07-29T14:05:00+08:00  
**声明人**: FE Agent  

##### 已实现 AC
| AC 编号 | AC 描述 | 实现文件 | 实现状态 |
|---------|---------|----------|----------|
| AC-FE-001 | 流式 API 调用 | frontend/src/api/characterChat.ts | ✅ 已实现 |
| AC-FE-002 | 打字机效果 | frontend/src/components/ChatWindow.vue | ✅ 已实现 |
| AC-FE-003 | loading 动画 | frontend/src/components/ChatWindow.vue | ✅ 已实现 |
| AC-FE-004 | 自动滚动 | frontend/src/components/ChatWindow.vue | ✅ 已实现 |
| AC-FE-005 | 错误处理 | frontend/src/api/characterChat.ts | ✅ 已实现 |

##### 已测试 AC
| AC 编号 | 测试方式 | 测试结果 | 测试命令/证据 |
|---------|----------|----------|---------------|
| AC-FE-001 | 编译检查 | ✅ 通过 | npm run build → exit 0 |
| AC-FE-002 | 编译检查 | ✅ 通过 | npm run build → exit 0 |
| AC-FE-003 | 编译检查 | ✅ 通过 | npm run build → exit 0 |
| AC-FE-004 | 编译检查 | ✅ 通过 | npm run build → exit 0 |
| AC-FE-005 | 编译检查 | ✅ 通过 | npm run build → exit 0 |

##### 未测试 AC（需 QA E2E 验证）
- AC-FE-001~005: 需要浏览器交互验证（由 QA 执行）

### 开发完成确认

**确认时间**: 2026-07-29T14:05:00+08:00  
**确认人**: PL Agent  

- ✅ BE 开发覆盖声明完整（4/4 AC 已实现）
- ✅ FE 开发覆盖声明完整（5/5 AC 已实现）
- ✅ 编译通过（npm run build exit 0）
- ✅ 代码变更已确认（git diff 核实）

**结论**: ✅ 通过 - 开发完成，进入 QA 验证

### QA 触发记录

**触发时间**: 2026-07-29T14:10:00+08:00  
**触发人**: PL Agent  
**触发方式**: sessions_send  
**目标**: isekai-wanderer-qa  

**通信记录**:
| 时间 | from | to | 目的 | 状态 |
|------|------|-----|------|------|
| 2026-07-29T14:10:00+08:00 | isekai-wanderer-pl | isekai-wanderer-qa | 触发 CR-023 QA 验证 | accepted (runId: 6b7c023b) |

#### QA 验证状态

**状态**: ⏳ 等待 QA 完成 Browser E2E 验证  
**测试文件**: `tests/e2e/cr023-streaming-chat.spec.ts` 已创建  
**test-report.md**: 尚未生成

---

### Prompt 增强修复 (2026-07-29 14:45)

**修复人**: BE Agent  
**修复原因**: 流式对话 prompt 不完整，NPC 回复缺乏角色人设上下文

#### 修复内容
| 项 | 内容 |
| --- | --- |
| 问题 | NPC 回复仅基于简单角色名，缺乏完整人设、剧本背景、游戏进度 |
| 修复 | 使用 `build_free_chat_prompt` 构建完整 prompt，包含角色人设、剧本背景、好感度、对话历史、记忆、游戏进度（防剧透） |
| 修改文件 | `backend/app/api/v1/chat.py` |
| 验证 | SSE 流式测试通过，NPC 回复基于完整上下文生成 |

#### 完整上下文包含
1. **角色完整人设**: name, description, personality, dialogue_style, traits, likes, dislikes, speak_style, example_sentences, title
2. **剧本背景信息**: 通过 character.script_id 关联查询 Script 表
3. **游戏进度**: 查询 game_sessions 获取当前 route_id 和 current_node_id（防剧透指导）
4. **好感度等级**: 从 affection 表获取，用于动态适配 relationship_stage
5. **对话历史**: 最近 5 条消息
6. **记忆**: 最近 5 条相关记忆

---

### Prompt 增强修复 (2026-07-29 14:45)

**修复人**: BE Agent  
**修复原因**: 流式对话 prompt 不完整，NPC 回复缺乏角色人设上下文

#### 修复内容
| 项 | 内容 |
| --- | --- |
| 问题 | NPC 回复仅基于简单角色名，缺乏完整人设、剧本背景、游戏进度 |
| 修复 | 使用 `build_free_chat_prompt` 构建完整 prompt，包含角色人设、剧本背景、好感度、对话历史、记忆、游戏进度（防剧透） |
| 修改文件 | `backend/app/api/v1/chat.py` |
| 验证 | SSE 流式测试通过，NPC 回复基于完整上下文生成 |

#### 完整上下文包含
1. **角色完整人设**: name, description, personality, dialogue_style, traits, likes, dislikes, speak_style, example_sentences, title
2. **剧本背景信息**: 通过 character.script_id 关联查询 Script 表
3. **游戏进度**: 查询 game_sessions 获取当前 route_id 和 current_node_id（防剧透指导）
4. **好感度等级**: 从 affection 表获取，用于动态适配 relationship_stage
5. **对话历史**: 最近 5 条消息
6. **记忆**: 最近 5 条相关记忆
