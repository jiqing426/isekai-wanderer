# CR-030 Design: 章节结构重构

## Overview

- routes 表新增 chapter_number (INTEGER) 和 chapter_type (VARCHAR(50)) 字段，nullable 确保向后兼容
- 11 条现有 route 按剧本 title 映射到 4 章节结构（相遇/日常/冲突/收束）
- 扩展 GET /game/{session_id}/status 和 GET /game/{session_id}/dialogue 返回章节信息
- 新增 GET /scripts/{script_id}/chapters 返回剧本章节列表
- 前端进度条显示"第X章：章节名"，旧 session 降级显示 route.title
- Alembic 迁移 + 数据迁移在同一 upgrade() 中完成，downgrade -1 回滚

## Technical Approach

- 数据层：Alembic 迁移脚本，routes 表加 chapter_number (INTEGER nullable) 和 chapter_type (VARCHAR(50) nullable)，创建 3 个索引（chapter_number, chapter_type, script_id+chapter_number）
- 数据迁移：在 Alembic upgrade() 中通过 scripts.title + routes.title 联合匹配执行 11 条 UPDATE，未匹配保持 NULL
- API 层：game status/dialogue 通过 session.route_id → route 读取 chapter_number/chapter_type，映射 chapter_type → chapter_title 中文名称；新增 /scripts/{id}/chapters 端点按 chapter_number 分组查询
- 前端层：ChapterProgress 组件消费 chapter_number/chapter_title，null 时降级显示 route.title
- 向后兼容：旧 session route 的 chapter 字段为 NULL → API 返回 null → 前端 fallback 到旧 chapter 字段
- 回滚方案：alembic downgrade -1 移除字段（数据自动回滚）+ git revert 代码

## Technology Decisions

| Decision | Selected | Status | Evidence |
|----------|----------|--------|----------|
| 章节数据存储方式 | routes 表新增 nullable 字段（非新建 chapters 表） | Not Required | 已有架构自然延伸，复用 routes 表避免 JOIN，PL 确认 |
| chapter_type 字段类型 | VARCHAR(50)（非 PostgreSQL ENUM） | Not Required | 已有架构自然延伸，便于扩展，PL 确认 |
| 数据迁移方式 | Alembic upgrade() 内 op.execute() UPDATE | Not Required | 标准 Alembic 模式，PL 确认 |
| API 兼容策略 | nullable 字段 + 旧字段保留（双格式） | Not Required | 向后兼容已有模式，PL 确认 |

## Document Sync

| Target Doc | Status | Summary / Evidence |
|------------|--------|-------------------|
| `docs/architecture/architecture.md` | Synced | CR-030 新增 routes chapter 字段依赖、ScriptService/GameService 章节查询 |
| `docs/api/api.md` | Synced | CR-030 新增 1 端点 GET /scripts/{id}/chapters + 扩展 2 端点响应字段 |
| `docs/database/database.md` | Synced | CR-030 routes 表新增 chapter_number/chapter_type + 3 索引 + 数据迁移 SQL |
| `docs/security/security.md` | Not Required | 无安全相关变更，章节字段为只读展示 |
| `docs/decisions/decisions.md` | Not Required | 无不可逆架构决策，均为已有架构自然延伸 |
| `docs/runtime/runtime-contract.md` | Synced | CR-030 更新 browser_e2e_user_actions、api_contract_doc、database_contract_doc |

---

## 1. 数据库设计

### 1.1 routes 表新增字段

```sql
ALTER TABLE routes ADD COLUMN chapter_number INTEGER;
ALTER TABLE routes ADD COLUMN chapter_type VARCHAR(50);
CREATE INDEX ix_routes_chapter_number ON routes(chapter_number);
CREATE INDEX ix_routes_chapter_type ON routes(chapter_type);
CREATE INDEX ix_routes_script_chapter ON routes(script_id, chapter_number);
```

| 字段 | 类型 | 可空 | 说明 |
|------|------|------|------|
| `chapter_number` | INTEGER | YES | 章节编号（1-4），NULL = 向后兼容旧数据 |
| `chapter_type` | VARCHAR(50) | YES | 章节类型：encounter/daily/conflict/convergence，NULL = 向后兼容 |

### 1.2 数据迁移映射

| 剧本 | route title | chapter_number | chapter_type |
|------|-------------|----------------|--------------|
| 星月奇缘 | 第一章：月夜邂逅 | 1 | encounter |
| 星月奇缘 | 第二章：星辰之约 | 2 | daily |
| 星月奇缘 | 第三章：命运交织 | 3 | conflict |
| 星辰之约 | 星夜邂逅 | 1 | encounter |
| 星辰之约 | 林辰线：星光指引 | 2 | daily |
| 星辰之约 | 流星线：刹那永恒 | 3 | conflict |
| 星辰之约 | 银河线：命运交汇 | 4 | convergence |
| 樱花恋曲 | 樱花树下 | 1 | encounter |
| 樱花恋曲 | 月夜线：静谧之恋 | 2 | daily |
| 樱花恋曲 | 阳菜线：夏日恋歌 | 3 | conflict |
| 樱花恋曲 | 雪乃线：樱花树下的约定 | 4 | convergence |

## 2. API 设计

### 2.1 扩展 GET /game/{session_id}/status

新增响应字段：`chapter_number` (INT|null), `chapter_type` (string|null), `chapter_title` (string|null)

chapter_title 映射：encounter→相遇, daily→日常, conflict→冲突, convergence→收束, null→null

### 2.2 新增 GET /scripts/{script_id}/chapters

响应：`{ "chapters": [{ "chapter_number": 1, "chapter_type": "encounter", "title": "相遇", "routes": [...] }] }`

逻辑：WHERE script_id = ? AND chapter_number IS NOT NULL，按 chapter_number 升序分组。

### 2.3 扩展 GET /game/{session_id}/dialogue

新增 chapter_number, chapter_type, chapter_title 字段，与 game status 一致。

## 3. 前端设计

进度条组件消费 chapter_number/chapter_title，null 时降级显示 route.title。

## 4. 向后兼容

| 场景 | 行为 |
|------|------|
| 旧 session 查询 game status | 返回 chapter_number: null, chapter_type: null, chapter_title: null |
| 旧 session 继续游戏 | 正常运行，无报错 |
| 前端展示 | null → 降级显示 route.title（现有 chapter 字段保留） |

## 5. 回滚方案

1. Schema 回滚：`alembic downgrade -1`（移除字段，数据自动回滚）
2. 代码回滚：`git revert <commit-hash>`

## 6. 与 CR-029 的关系

PL 已确认无冲突。CR-029 改 nodes.character_id，CR-030 改 routes.chapter_number/chapter_type，无共享字段。

---

**创建时间**: 2026-08-04
**Architect**: sa
**状态**: DESIGN in-progress
