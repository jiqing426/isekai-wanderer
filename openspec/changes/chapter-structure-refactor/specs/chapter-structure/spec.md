# Spec: 章节结构 (chapter-structure)

## 概述

本规格定义剧本 4 章节结构（相遇/日常/冲突/收束）的数据模型、API 契约和前端展示规则。

---

### Requirement: REQ-CHAP-001 — routes 表新增章节字段

**优先级**: P0  
**来源**: change.md §1, design.md §1

#### Scenario: 数据库迁移成功执行

**Given**: routes 表存在且无 chapter_number、chapter_type 字段  
**When**: 执行 `alembic upgrade head`  
**Then**:
- routes 表新增 `chapter_number` (INTEGER, nullable) 字段
- routes 表新增 `chapter_type` (VARCHAR(50), nullable) 字段
- 现有数据不受影响（字段默认为 NULL）

**验证方式**: 数据库 schema 查询、`alembic current` 显示正确版本

#### Scenario: 数据库迁移回滚

**Given**: 已完成数据库迁移  
**When**: 执行 `alembic downgrade -1`  
**Then**:
- chapter_number 和 chapter_type 字段被移除
- 现有数据恢复原状

**验证方式**: 数据库 schema 查询确认字段不存在

---

### Requirement: REQ-CHAP-002 — 现有 route 数据迁移到章节

**优先级**: P0  
**来源**: change.md §2, design.md §2

#### Scenario: 星月奇缘 route 映射到章节

**Given**: 星月奇缘剧本包含 3 条 route  
**When**: 执行数据迁移脚本  
**Then**:
- "第一章：月夜邂逅" → chapter_number=1, chapter_type='encounter'
- "第二章：星辰之约" → chapter_number=2, chapter_type='daily'
- "第三章：命运交织" → chapter_number=3, chapter_type='conflict'

**验证方式**: SQL 查询 `SELECT title, chapter_number, chapter_type FROM routes WHERE script_id='星月奇缘'`

#### Scenario: 星辰之约 route 映射到章节

**Given**: 星辰之约剧本包含 4 条 route  
**When**: 执行数据迁移脚本  
**Then**:
- "星夜邂逅" → chapter_number=1, chapter_type='encounter'
- "林辰线：星光指引" → chapter_number=2, chapter_type='daily'
- "流星线：刹那永恒" → chapter_number=3, chapter_type='conflict'
- "银河线：命运交汇" → chapter_number=4, chapter_type='convergence'

**验证方式**: SQL 查询验证

#### Scenario: 樱花恋曲 route 映射到章节

**Given**: 樱花恋曲剧本包含 4 条 route  
**When**: 执行数据迁移脚本  
**Then**:
- "樱花树下" → chapter_number=1, chapter_type='encounter'
- "月夜线：静谧之恋" → chapter_number=2, chapter_type='daily'
- "阳菜线：夏日恋歌" → chapter_number=3, chapter_type='conflict'
- "雪乃线：樱花树下的约定" → chapter_number=4, chapter_type='convergence'

**验证方式**: SQL 查询验证

#### Scenario: 数据迁移回滚

**Given**: 已完成数据迁移  
**When**: 执行数据回滚脚本  
**Then**:
- 所有 route 的 chapter_number 和 chapter_type 恢复为 NULL

**验证方式**: SQL 查询验证所有字段为 NULL

---

### Requirement: REQ-CHAP-003 — 游戏状态 API 返回章节信息

**优先级**: P0  
**来源**: change.md §3, design.md §3.1

#### Scenario: 新 session 查询游戏状态返回章节信息

**Given**: 用户处于星月奇缘剧本的第 2 章（日常）  
**When**: 调用 `GET /api/v1/game/{session_id}/status`  
**Then**: 响应包含以下字段：
```json
{
  "session_id": "xxx",
  "chapter_number": 2,
  "chapter_type": "daily",
  "chapter_title": "日常",
  ...
}
```

**验证方式**: API 测试验证响应 schema 和字段值

#### Scenario: 章节切换后 API 返回新章节信息

**Given**: 用户从第 1 章进入第 2 章  
**When**: 调用 `GET /api/v1/game/{session_id}/status`  
**Then**: 响应中 `chapter_number` 从 1 变为 2，`chapter_type` 从 'encounter' 变为 'daily'

**验证方式**: API 测试验证状态变化

---

### Requirement: REQ-CHAP-004 — 剧本章节列表 API

**优先级**: P1  
**来源**: change.md §3, design.md §3.1

#### Scenario: 查询剧本章节列表

**Given**: 星辰之约剧本包含 4 个章节  
**When**: 调用 `GET /api/v1/scripts/{script_id}/chapters`  
**Then**: 响应包含章节列表：
```json
{
  "chapters": [
    {
      "chapter_number": 1,
      "chapter_type": "encounter",
      "title": "相遇",
      "routes": [...]
    },
    {
      "chapter_number": 2,
      "chapter_type": "daily",
      "title": "日常",
      "routes": [...]
    },
    ...
  ]
}
```

**验证方式**: API 测试验证章节数量和顺序

---

### Requirement: REQ-CHAP-005 — 前端进度条展示章节信息

**优先级**: P1  
**来源**: change.md §4, design.md §4

#### Scenario: 进度条显示当前章节名

**Given**: 用户处于星月奇缘第 2 章（日常）  
**When**: 用户打开游戏界面  
**Then**: 进度条上方显示"第 2 章：日常"

**验证方式**: Browser E2E 测试验证文本内容

#### Scenario: 章节切换时显示过渡动画

**Given**: 用户从第 1 章进入第 2 章  
**When**: 章节切换发生  
**Then**: 显示过渡动画"进入第 2 章"（可选功能，不阻塞 MVP）

**验证方式**: Browser E2E 测试验证动画元素

---

### Requirement: REQ-CHAP-006 — 向后兼容旧 session

**优先级**: P1  
**来源**: CEO 条件, design.md §5

#### Scenario: 旧 session 查询游戏状态返回 null 章节信息

**Given**: 存在迁移前创建的旧 session（无章节信息）  
**When**: 调用 `GET /api/v1/game/{session_id}/status`  
**Then**: 响应包含：
```json
{
  "session_id": "old-xxx",
  "chapter_number": null,
  "chapter_type": null,
  "chapter_title": null,
  ...
}
```

**验证方式**: API 测试验证旧 session 返回 null 且不报错

#### Scenario: 旧 session 游戏流程不受影响

**Given**: 用户继续使用旧 session 进行游戏  
**When**: 用户执行游戏操作（选择选项、推进剧情）  
**Then**: 游戏正常运行，无报错

**验证方式**: E2E 测试验证旧 session 完整游戏流程

---

## 数据约束

### chapter_type 枚举值

| 值 | 含义 | 对应章节 |
|----|------|----------|
| `encounter` | 相遇 | 第 1 章 |
| `daily` | 日常 | 第 2 章 |
| `conflict` | 冲突 | 第 3 章 |
| `convergence` | 收束 | 第 4 章 |

### chapter_number 范围

- 最小值：1
- 最大值：4
- 允许 NULL（向后兼容）

---

## 测试策略

| 层级 | 测试内容 | 验证方式 |
|------|----------|----------|
| 数据库 | 字段存在、数据迁移正确性 | SQL 查询、alembic 命令 |
| API | 返回章节信息、向后兼容 | API 测试（pytest） |
| 前端 | 进度条展示、章节切换 | Browser E2E（Playwright） |

---

## 创建时间

2026-08-04
