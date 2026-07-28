# Design: CR-018 用户复测问题修复

> 创建时间：2026-07-26 | 状态：已完成 | 关联 CR: CR-018

---

## 1. 修复方案概述

本次变更为用户复测阶段的问题修复，涉及三大类工作：

### 1.1 BE 修复（11 项）
- **P0 接口修复**：送礼接口 400（gift.py 参数校验/余额查询）、自由对话 401（chat.py 鉴权依赖）、头像上传 AUTH_TOKEN_EXPIRED（users.py multipart token 处理 + nginx 静态路径兼容）
- **P1 逻辑修复**：好感度实时更新（narrative_engine.py process_choice 返回 affection_change）、自由对话历史持久化（free_chat_service.py session 复用）、剧本流程过短（节点流转深度不足）、进度记录（ending_progress.py 写入逻辑）、完成剧本统计（COUNT DISTINCT script_id）、累计碎片为 0（FragmentTransaction 创建逻辑）、对话额度重置确认
- **额外修复**：碎片交易明细中文映射（shards.py 前缀匹配）、帖子浏览量（community.py view_count +1）、会员账单全类型查询

### 1.2 FE 修复（14 项）
- **P2 UI/展示**：AI 叙事 loading 状态、成就卡片 JSON 解析渲染、碎片商城 Tab 样式、AI 记忆 Invalid Date 容错、角色详情页 personality 展示、语音试听 UI 占位、封面图/头像自适应
- **P1 i18n**：性格特质中英映射（loyal→忠诚）、好感等级中文映射（acquaintance→相识）、账单类型中文映射、碎片收支明细中文化
- **交互修复**：好感度实时更新前端响应、碎片获取"成就奖励"跳转成就页

### 1.3 数据迁移（UUID v4）
- 将 7 张表中的硬编码非 v4 UUID 替换为随机 UUID v4
- 同步更新所有外键引用和 JSON 字段中的 UUID 值

---

## 2. 关键文件变更清单

### Backend (`backend/app/`)
| 文件 | 变更内容 |
|------|----------|
| `api/v1/gift.py` | 修复 session_id 参数校验、碎片余额查询逻辑 |
| `api/v1/chat.py` | 修复 free_chat 鉴权依赖，确保 get_current_user_id 正确解析 |
| `api/v1/users.py` | 修复 upload_avatar multipart token 处理；修正统计逻辑 COUNT DISTINCT |
| `api/v1/shards.py` | 修复 total_earned 查询；碎片交易明细前缀匹配 |
| `api/v1/characters.py` | 确保 API 返回 personality 字段 |
| `api/v1/community.py` | 帖子详情 view_count +1（防刷） |
| `api/v1/subscription.py` | 账单查询返回所有交易类型 |
| `services/narrative_engine.py` | process_choice 返回 affection_change；修复节点流转深度 |
| `services/free_chat_service.py` | session 复用逻辑修复 |
| `services/ending_progress.py` | 选择后正确写入 route_progress |
| `services/sign.py` | 签到碎片 FragmentTransaction 创建逻辑 |
| `routers/mock_router.py` | condition 字段结构化返回 |

### Frontend (`frontend/src/`)
| 文件 | 变更内容 |
|------|----------|
| `views/GameView.vue` | 自由对话 session_id 传递；loading 状态；好感度响应更新 |
| `views/CharacterDetailView.vue` | personality 展示；语音试听 UI；好感等级中文映射 |
| `views/PersonalCenterView.vue` | Invalid Date 容错；对话次数展示；记忆列表最大高度 |
| `views/FragmentMallView.vue` | Tab 顶部样式；收支明细中文化 |
| `views/AchievementView.vue` | 成就卡片 JSON 解析渲染 |
| `views/SettingsView.vue` | 账单中文映射 |
| `locales/zh-CN.ts` | 补全性格特质、好感等级、账单类型、碎片交易类型映射 |
| `components/affection-display.vue` | 响应 affection_change 数据更新 |
| `components/progress-row.vue` | 绑定进度数据并响应更新 |

### Database Migration
| 文件 | 变更内容 |
|------|----------|
| `migrations/uuid_v4_migration.sql` | UUID v4 数据迁移脚本 |

---

## 3. UUID v4 迁移方案

### 3.1 迁移范围

| 表 | 迁移内容 | 影响记录数 |
|----|----------|-----------|
| `characters` | id 字段：`22222222-...` → 随机 UUID v4 | ~3 条 |
| `scripts` | id 字段：`a1111111-...`、`66666666-...` → 随机 UUID v4 | ~3 条 |
| `script_nodes` | script_id 外键 + node id | ~36 条 |
| `script_choices` | node_id 外键 + choice id | ~36 条 |
| `user_scripts` | script_id 外键 | ~12 条 |
| `fragment_transactions` | 关联 JSON 字段中的 UUID | 若干 |
| `ending_progress` | script_id 外键 | 若干 |

### 3.2 迁移策略

1. **生成映射表**：为每个旧 UUID 生成对应的 UUID v4，记录到临时映射表
2. **外键级联更新**：按依赖顺序更新（先子表后主表，或禁用外键约束后批量更新）
3. **JSON 字段更新**：对包含旧 UUID 的 JSON 字段做字符串替换
4. **验证**：迁移后校验所有外键引用完整性，确保无悬挂引用
5. **回滚**：迁移前备份相关表，回滚时恢复备份

### 3.3 执行顺序

```
BEGIN;
-- 1. 创建映射表
CREATE TEMPORARY TABLE uuid_mapping (old_id UUID, new_id UUID);
-- 2. 生成 UUID v4 映射
INSERT INTO uuid_mapping SELECT id, uuid_generate_v4() FROM characters WHERE id IN ('22222222-...');
-- 3. 更新子表外键（script_nodes, script_choices, user_scripts, ending_progress）
-- 4. 更新主表主键
-- 5. 更新 JSON 字段
-- 6. 验证完整性
COMMIT;
```

### 3.4 林辰 UUID 修复

角色"林辰"单独迁移至新 UUID `26917e16-...`，同步更新所有引用（nodes/choices/user_scripts 中的 route JSON）。

---

## 4. 前后端数据契约

### 4.1 送礼接口
```
POST /api/v1/game/{session_id}/gift
Request: { character_id: UUID, gift_id: string }
Response: { success: true, affection_change: number, remaining_shards: number }
```

### 4.2 自由对话
```
POST /api/v1/chat/free
Request: { session_id?: UUID, message: string, character_id: UUID }
Response: { reply: string, session_id: UUID }
```

### 4.3 好感度实时更新
```
process_choice 响应新增字段:
{ ..., affection_change: { character_id: UUID, delta: number, new_level: string } }
```

### 4.4 碎片交易明细
```
GET /api/v1/shards/transactions
Response: { items: [{ type: string, type_label: string(中文), amount: number, created_at: datetime }] }
```

### 4.5 剧本进度
```
process_choice 响应新增字段:
{ ..., progress: { current_node: string, total_nodes: number, visited: number } }
```

### 4.6 会员账单
```
GET /api/v1/subscription/bills
Response: { items: [{ type: string, type_label: string(中文), amount: number, created_at: datetime }] }
```

---

## 5. Document Sync

| 目标文档 | 状态 | 说明 |
|----------|------|------|
| `docs/architecture/architecture.md` | Not Required | 本次为 bugfix，无架构变更 |
| `docs/api/api.md` | Synced | 接口响应字段变更（affection_change、progress、type_label）已在 api.md 更新 |
| `docs/database/database.md` | Synced | UUID v4 迁移方案已记录 |
| `docs/security/security.md` | Not Required | 无安全相关变更 |
| `docs/decisions/decisions.md` | Not Required | 无重大架构决策 |
| `docs/runtime/runtime-contract.md` | Synced | 运行时无变更（端口/代理/健康检查不变） |
