# 修复方案：6 个空 Route 补充 Nodes 数据

**CR-ID**: CR-001  
**制定时间**: 2026-07-27 09:50  
**制定人**: PM  
**状态**: 待执行

---

## 1. 问题概述

3 个 script 共 12 个 route，其中 6 个 route 缺少 nodes 数据（创建时未 seed）。
`game.py` 有 fallback 逻辑可正常运行，但用户选择空 route 时会被静默切换到其他 route，体验不一致。

## 2. 数据库现状

### 有 nodes 的 route（参考模板）

| Script | Route | Nodes | Choices | 结构 |
|--------|-------|-------|---------|------|
| 星月奇缘 | 月夜邂逅 | 11 | 6 | opening + friendly + cold + 3 endings + cg/converge/fixed/choice |
| 星辰之约 | 星夜邂逅 | 8 | 6 | 同上模式 |
| 星辰之约 | 林辰线：星光指引 | 9 | - | 同上模式 |
| 星辰之约 | 流星线：刹那永恒 | 7 | - | 同上模式 |
| 星辰之约 | 银河线：命运交汇 | 8 | - | 同上模式 |
| 樱花恋曲 | 樱花树下 | 6 | 6 | opening + friendly + cold + 3 endings |

### 空 route（需修复）

| # | Script | Route (title) | Route ID | 角色 |
|---|--------|---------------|----------|------|
| 1 | 星月奇缘 | 双星线：命运交织 | `8ff72661-2954-4665-a611-5a63ce758996` | 沈星澜 |
| 2 | 星月奇缘 | 星澜线：星辰之约 | `a41282b0-c27d-4868-aa1c-88ba08d50040` | 沈星澜 |
| 3 | 星月奇缘 | 辉夜线：月影传说 | `90cf1451-80db-45a2-968e-aa84507bb854` | 沈星澜 (辉夜人设) |
| 4 | 樱花恋曲 | 月夜线：静谧之恋 | `89424ab0-74d6-4fad-be8c-d2fd911f7323` | 藤原雪 |
| 5 | 樱花恋曲 | 阳菜线：夏日恋歌 | `55761d28-289f-445b-82ef-fa9709d5d507` | 藤原雪 (阳菜人设) |
| 6 | 樱花恋曲 | 雪乃线：樱花树下的约定 | `8bb89d32-d99e-41ee-8a93-33b1f36ff3ee` | 藤原雪 (雪乃人设) |

## 3. 修复方案

### 方案 A（推荐）：为每个空 route 创建 6 个 nodes + 6 个 choices

**结构**（与现有 route 一致）：
```
opening (preset, parent_id=NULL)
  ├── friendly_path (preset, parent_id=opening)
  │     ├── good_ending (ending, parent_id=friendly)
  │     └── normal_ending (ending, parent_id=friendly)
  └── cold_path (preset, parent_id=opening)
        └── bad_ending (ending, parent_id=cold)
```

每个 route 6 个 nodes + 6 个 choices（opening→2, friendly→2, cold→2）。

**角色适配**：
- 星月奇缘 3 条路线：使用沈星澜角色 + 不同场景/对话风格
- 樱花恋曲 3 条路线：使用藤原雪角色 + 不同场景/对话风格
- 路线名称中提到的角色名（辉夜/阳菜/雪乃）作为对话中的性格参考

**工作量**：BE 约 3 小时（6 route × 30 min）  
**风险**：低 — 纯数据插入，不改代码逻辑  
**影响**：仅影响用户直接选择空 route 时的体验

### 方案 B：不修复数据，仅保留 fallback

**现状**：game.py fallback 已覆盖  
**缺点**：用户看到的 route 列表包含无法直接游玩的 route，选择后被静默切换，体验差  
**结论**：不推荐作为长期方案

### 方案 C：前端隐藏空 route

**缺点**：需要 FE 改动，且 route 列表不完整  
**结论**：不推荐

**决策**：采用 **方案 A**。

## 4. 执行计划

| 步骤 | 负责 | 内容 | 预计时间 |
|------|------|------|----------|
| 1 | BE | 编写 seed 脚本 `seed_empty_routes.py` | 30 min |
| 2 | BE | 执行 seed 脚本，插入 36 nodes + 36 choices | 15 min |
| 3 | BE | 验证数据完整性（每个 route 6 nodes, 6 choices） | 15 min |
| 4 | QA | 验证：选择每个 route 可正常开始游戏 | 30 min |
| 5 | QA | 验证：每个 route 的对话/选择/结局流程完整 | 30 min |

## 5. 验收标准

| AC-ID | 验收项 | 验证方式 |
|-------|--------|----------|
| AC-FIX-01 | 6 个 route 各有 6 个 nodes | DB 查询 COUNT |
| AC-FIX-02 | 6 个 route 各有 6 个 choices | DB 查询 COUNT |
| AC-FIX-03 | 每个 route 有且仅有 1 个 opening node (parent_id=NULL) | DB 查询 |
| AC-FIX-04 | 每个 route 有 3 个 ending (good/normal/bad) | DB 查询 |
| AC-FIX-05 | POST /game/start 对每个 route 返回 200 + session_id | API 测试 |
| AC-FIX-06 | 选择→对话→结局流程可走通 | E2E 测试 |

## 6. 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| UUID 冲突 | 低 | 使用固定 UUID，seed 前先检查 |
| FK 约束违反 | 低 | 先插 nodes 再插 choices |
| 影响现有数据 | 极低 | 只插入新数据，不修改已有数据 |
| 回滚 | 低 | 按 route_id DELETE 即可回滚 |
