# Proposal: 章节结构重构 (CR-030)

## 变更 ID

CR-030

## 变更名称

chapter-structure-refactor

## 为什么做

- 当前剧本使用纯 route 结构组织内容，与剧本设计文档中的 4 章节结构（相遇/日常/冲突/收束）不一致
- 用户无法直观感知当前处于哪个章节，进度展示不清晰
- 章节级别的统计、分析、解锁等后续功能无法实现

## 变更内容

### 1. 数据库层

- `routes` 表新增 `chapter_number` (INTEGER) 和 `chapter_type` (VARCHAR(50)) 字段
- `chapter_type` 枚举值：`encounter` / `daily` / `conflict` / `convergence`

### 2. 数据迁移

将现有 11 条 route 按剧本映射到章节：

| 剧本 | 现有 route | 章节 |
|------|-----------|------|
| 星月奇缘 | 第一章：月夜邂逅 | ch1/encounter |
| 星月奇缘 | 第二章：星辰之约 | ch2/daily |
| 星月奇缘 | 第三章：命运交织 | ch3/conflict |
| 星辰之约 | 星夜邂逅 | ch1/encounter |
| 星辰之约 | 林辰线：星光指引 | ch2/daily |
| 星辰之约 | 流星线：刹那永恒 | ch3/conflict |
| 星辰之约 | 银河线：命运交汇 | ch4/convergence |
| 樱花恋曲 | 樱花树下 | ch1/encounter |
| 樱花恋曲 | 月夜线：静谧之恋 | ch2/daily |
| 樱花恋曲 | 阳菜线：夏日恋歌 | ch3/conflict |
| 樱花恋曲 | 雪乃线：樱花树下的约定 | ch4/convergence |

### 3. API 层

- `GET /game/{session_id}/status` 响应新增 `chapter_number`、`chapter_type`、`chapter_title` 字段
- 新增 `GET /scripts/{script_id}/chapters` 返回剧本章节列表

### 4. 前端层

- 进度条展示"第 X 章：章节名"
- 章节切换时显示过渡动画（可选）

## 不做范围

- ❌ 章节解锁逻辑（后续迭代）
- ❌ 章节选择界面（可选功能，不在 MVP）
- ❌ 章节级别的统计/分析功能
- ❌ 修改现有 route 的业务逻辑，仅新增字段

## 成功标准

- 数据库字段：routes 表包含 chapter_number 和 chapter_type 字段，可通过数据库查询验证
- 数据迁移：所有 11 条现有 route 正确映射到章节，可通过数据完整性检查验证
- API 返回：游戏状态 API 包含章节信息，可通过 API 测试验证
- 前端展示：进度条显示章节名，可通过 Browser E2E 验证
- 向后兼容：旧 session 正常运行且返回 null 章节信息，可通过 API 兼容性测试验证

## 影响范围

- **后端 (BE)**：数据库迁移、API 改动、向后兼容处理
- **前端 (FE)**：进度条展示、章节信息消费
- **数据库 (DB)**：routes 表结构变更
- **运维 (Ops)**：无直接影响

## 依赖与约束

- **CEO 条件**：
  1. BE 必须产出数据迁移回滚脚本
  2. API 向后兼容旧 session（过渡期双格式支持）
  3. CR-029 与 CR-030 无冲突（PL 已确认）

- **技术约束**：
  - 使用 alembic 进行数据库迁移
  - 回滚方案：`alembic downgrade -1` + 数据回滚脚本

## 待澄清问题

**无阻塞 MVP 的 Open 问题。**

所有关键问题已在 change.md 和 design.md 中明确：
- 章节类型枚举值已确定（encounter/daily/conflict/convergence）
- 数据映射规则已确定（11 条 route → 章节）
- API 向后兼容策略已确定（旧 session 返回 null）

## 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| 影响现有游戏逻辑 | 高 | 充分测试 + 回滚方案 |
| 数据迁移失败 | 中 | 回滚脚本 + 迁移前备份 |
| 前端展示异常 | 中 | 向后兼容 + 降级展示 |

## 验收追踪

见 `workflow/changes/CR-030/acceptance.md`

## 创建时间

2026-08-04
