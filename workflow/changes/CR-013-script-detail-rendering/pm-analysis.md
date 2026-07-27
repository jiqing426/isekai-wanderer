# CR-013 PM 分析报告 — 剧本详情页面渲染

> 分析时间：2026-07-23T23:00:00Z
> 分析人：PM

---

## 一、现状分析

### 1.1 现有数据库表（已存在）

| 表名 | 字段 | 说明 |
|------|------|------|
| `scripts` | id(UUID), slug, title, description, genre, cover_image_url | ✅ 已有 |
| `routes` | id(UUID), script_id, title, description, branch_type | ✅ 已有 |
| `nodes` | id(UUID), route_id, parent_id, node_type, content(JSON), background | ✅ 已有 |
| `node_choices` | id(UUID), node_id, text, next_node_id, affection_delta | ✅ 已有 |
| `characters` | id(UUID), script_id, name, description, dialogue_style, portraits, age, height, birthday, likes, personality, avatar_url, is_main | ✅ 已有 |
| `game_sessions` | id, user_id, script_id, route_id, current_node_id, status, choice_history(JSON) | ✅ 已有 |
| `cg_assets` | 已存在 | ✅ CG 资源表 |
| `unlocked_cgs` | 已存在 | ✅ 用户解锁 CG |
| `unlocked_scripts` | 已存在 | ✅ 用户解锁剧本 |

### 1.2 缺失的表（seed_script_detail.sql 引用但不存在）

| 表名 | seed SQL 中的用途 | PM 判断 |
|------|-------------------|---------|
| `endings` | 结局定义（title, type, description, unlock_condition） | **需要创建** — 当前 API 用 mock 数据 |
| `chapters` | 章节定义（title, order_number） | **可选** — 当前 API 用 route 模拟章节 |
| `cgs` | CG 定义（title, url, thumbnail, trigger_node_id） | **需要创建** — 当前 API 用 mock 数据 |
| `user_script_progress` | 用户进度（unlocked_nodes, unlocked_endings, unlocked_cgs） | **可选** — 可用 game_sessions 替代 |

### 1.3 现有 API 实现（scripts.py）

已实现的端点：
- `GET /scripts` — 列表（公开）
- `GET /scripts/{id}` — 详情（含 routes + characters）
- `GET /scripts/{id}/characters` — 角色列表
- `GET /scripts/{id}/routes` — 路线探索树（需认证）
- `GET /scripts/{id}/endings` — 结局列表（需认证，**mock 数据**）
- `GET /scripts/{id}/cg-preview` — CG 预览（需认证，**mock 数据**）
- `GET /scripts/{id}/detail` — CR-013 详情（需认证，**基于 route→node 结构**）

### 1.4 API Contract 与实现的差异

| 项目 | API Contract 定义 | 当前实现 | 差异 |
|------|-------------------|----------|------|
| 章节结构 | `chapters[]` 独立表 | route 模拟章节 | Contract 用 chapterId，实现用 route 分组 |
| 节点类型 | 6 种（fixed_scene/ai_dialog/choice_point/converge_node/cg_trigger/ending_node） | node_type 字段 + content JSON | 基本一致 |
| 结局数据 | 从 nodes 中 ending_node 返回 | mock 数据 | **需要真实数据** |
| CG 数据 | 从 nodes 中 cg_trigger 返回 | mock 数据 | **需要真实数据** |
| 字段命名 | scriptId / chapterId / nodeId（camelCase） | id（snake_case） | 实现已转 camelCase |

---

## 二、数据库表设计方案

### 2.1 需要创建的表

#### `endings` 表

```sql
CREATE TABLE IF NOT EXISTS endings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    script_id UUID NOT NULL REFERENCES scripts(id),
    title VARCHAR(255) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('good', 'normal', 'bad')),
    description TEXT,
    unlock_condition TEXT,
    route_id UUID REFERENCES routes(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_endings_script_id ON endings(script_id);
```

#### `cgs` 表（剧本 CG 定义）

```sql
CREATE TABLE IF NOT EXISTS script_cgs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    script_id UUID NOT NULL REFERENCES scripts(id),
    title VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    thumbnail TEXT,
    trigger_node_id UUID REFERENCES nodes(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_script_cgs_script_id ON script_cgs(script_id);
```

> 注：已有 `cg_assets` 表，需确认其结构。如果 cg_assets 已覆盖 CG 定义，可复用而不新建。

#### `chapters` 表（可选）

```sql
CREATE TABLE IF NOT EXISTS chapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    script_id UUID NOT NULL REFERENCES scripts(id),
    route_id UUID REFERENCES routes(id),
    title VARCHAR(255) NOT NULL,
    order_number INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_chapters_script_id ON chapters(script_id);
```

> PM 建议：**暂不创建 chapters 表**。当前实现用 route→nodes 结构模拟章节，API Contract 中的 chapterId 可以用 `{scriptId}-{routeIdx}` 格式生成。如果后续需要更复杂的章节管理再添加。

#### `user_script_progress` 表（可选）

> PM 建议：**暂不创建**。当前 `game_sessions` + `game_progress` 已能追踪用户进度。`unlocked_scripts` 和 `unlocked_cgs` 表也已存在。无需额外进度表。

### 2.2 最终建议：只创建 `endings` 表

| 表 | 决策 | 理由 |
|----|------|------|
| `endings` | ✅ 创建 | 结局是剧本核心数据，不应 mock |
| `script_cgs` | ⚠️ 先检查 cg_assets | 如 cg_assets 已覆盖则复用 |
| `chapters` | ❌ 暂不创建 | route 结构可模拟 |
| `user_script_progress` | ❌ 暂不创建 | game_sessions 已覆盖 |

---

## 三、API Contract 调整建议

### 3.1 字段命名统一

现有实现已使用 camelCase（scriptId/chapterId/nodeId），与 Contract 一致。**无需调整。**

### 3.2 结局数据来源调整

**当前 Contract**：结局数据从 `ending_node` 类型节点返回
**建议调整**：结局数据从 `endings` 表查询，`ending_node` 节点关联 ending_id

```json
// 调整后的 ending_node
{
  "nodeId": "...",
  "type": "ending_node",
  "title": "结局：永远的约定",
  "endingId": "ending-uuid-001",  // 新增：关联 endings 表
  "endingType": "good",
  "description": "两人约定永远在一起",
  "isUnlocked": true
}
```

### 3.3 CG 数据来源调整

**当前 Contract**：CG 数据从 `cg_trigger` 类型节点返回 cgId/cgUrl
**建议调整**：cg_trigger 节点关联 script_cgs 表，API 返回时查询真实 URL

### 3.4 author 字段

**当前问题**：API 返回 `"author": "剧本作者"` 硬编码
**建议**：Script 模型暂无 author 字段。MVP 阶段保持硬编码，后续迭代添加。

---

## 四、BE 任务清单

### P0 — 核心任务

| # | 任务 | 描述 | 工时 | 验收标准 |
|---|------|------|------|----------|
| BE-013-1 | 创建 `endings` 表 | DDL 见上方 | 1h | 表创建成功，有索引 |
| BE-013-2 | 插入结局测试数据 | 每个剧本 3 个结局（good/normal/bad） | 1h | 至少 1 个剧本有完整结局数据 |
| BE-013-3 | 修改 `GET /scripts/{id}/endings` | 从 endings 表查询替代 mock | 2h | 返回真实结局数据+解锁状态 |
| BE-013-4 | 修改 `GET /scripts/{id}/detail` | ending_node 关联 endings 表 | 2h | ending_node 返回 endingId+真实数据 |
| BE-013-5 | 检查 cg_assets 表结构 | 确认是否可复用 | 0.5h | 输出 cg_assets 字段清单 |
| BE-013-6 | 修改 `GET /scripts/{id}/cg-preview` | 从 cg_assets/script_cgs 查询替代 mock | 2h | 返回真实 CG 数据+解锁状态 |

### P1 — 增强任务

| # | 任务 | 描述 | 工时 | 验收标准 |
|---|------|------|------|----------|
| BE-013-7 | 节点解锁状态优化 | 基于 game_sessions 精确计算 | 2h | 已玩节点 isUnlocked=true |
| BE-013-8 | completionRate 精确计算 | unlocked_nodes / total_nodes | 1h | 百分比与实际进度一致 |

---

## 五、FE 任务清单

### P0 — 核心任务

| # | 任务 | 描述 | 工时 | 验收标准 |
|---|------|------|------|----------|
| FE-013-1 | ScriptDetailView 页面框架 | 头部信息+章节折叠+节点列表 | 3h | 页面正确渲染剧本标题/封面/描述 |
| FE-013-2 | 章节折叠面板 | Accordion 组件，按章节分组 | 2h | 展开/折叠正常，显示节点数 |
| FE-013-3 | 6 种节点卡片组件 | fixed_scene/ai_dialog/choice_point/converge_node/cg_trigger/ending_node | 4h | 每种类型独立样式和图标 |
| FE-013-4 | 节点解锁/未解锁状态 | 未解锁灰显+锁图标 | 2h | 状态正确，未解锁不可点击 |
| FE-013-5 | 结局展示 | ending_node 显示结局类型+描述 | 1h | good/normal/bad 不同颜色标识 |
| FE-013-6 | CG 预览 | cg_trigger 显示缩略图 | 1h | 未解锁 CG 显示模糊/锁定遮罩 |
| FE-013-7 | 进度条/完成率 | 显示 completionRate | 1h | 百分比与 API 一致 |

### P1 — 增强任务

| # | 任务 | 描述 | 工时 | 验收标准 |
|---|------|------|------|----------|
| FE-013-8 | 路线探索可视化 | 节点连接图/树形结构 | 3h | 节点间连线，分支可视化 |
| FE-013-9 | 结局收集面板 | 列出所有结局+解锁状态 | 2h | 未解锁结局显示"???" |
| FE-013-10 | CG 收集画廊 | 网格展示所有 CG | 2h | 未解锁 CG 模糊处理 |

---

## 六、优先级和工时评估

### 总工时

| 角色 | P0 | P1 | 总计 |
|------|-----|-----|------|
| BE | 8.5h | 3h | 11.5h |
| FE | 14h | 7h | 21h |
| **总计** | **22.5h** | **10h** | **32.5h** |

### 执行顺序

```
阶段 1（并行）：
  BE: BE-013-1 → BE-013-2 → BE-013-5（建表+数据+检查CG）
  FE: FE-013-1 → FE-013-2 → FE-013-3（页面框架+章节+节点卡片）

阶段 2（BE 完成后 FE 对接）：
  BE: BE-013-3 → BE-013-4 → BE-013-6（真实数据替代 mock）
  FE: FE-013-4 → FE-013-5 → FE-013-6 → FE-013-7（状态+结局+CG+进度）

阶段 3（增强）：
  BE: BE-013-7 → BE-013-8
  FE: FE-013-8 → FE-013-9 → FE-013-10
```

---

## 七、联调测试计划

| # | 测试用例 | 验收标准 |
|---|----------|----------|
| TC-001 | GET /scripts/{id}/detail 返回完整数据 | scriptId/title/cover/chapters 全部正确 |
| TC-002 | 6 种节点类型正确渲染 | 每种类型有对应卡片样式 |
| TC-003 | 结局数据来自真实表 | endings 表数据正确返回，非 mock |
| TC-004 | CG 数据来自真实表 | cg_assets 数据正确返回，非 mock |
| TC-005 | 节点解锁状态正确 | 已玩游戏节点 isUnlocked=true |
| TC-006 | 章节折叠正常 | 展开/折叠交互正确 |
| TC-007 | 完成率计算正确 | completionRate 与实际一致 |
| TC-008 | UUID v4 格式 | 所有 ID 符合 UUID v4 |

---

## 八、风险识别

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| seed_script_detail.sql 字段与现有表不匹配 | 高 | SQL 中的字段名（script_id/character_id）需映射到现有表字段（id） |
| cg_assets 表结构未知 | 中 | BE-013-5 先检查再决定 |
| 节点解锁状态依赖 game_sessions.choice_history | 中 | 需要真实游戏数据才能验证 |

---

## 九、PM 建议

1. **只创建 `endings` 表**，不创建 chapters/user_script_progress
2. **先检查 cg_assets 表结构**，再决定是否需要 script_cgs
3. **seed_script_detail.sql 需要重写**，字段名与现有表不匹配
4. **API Contract 基本正确**，只需微调 ending_node 增加 endingId
5. **建议 BE 先完成数据层（建表+种子数据），再改 API；FE 可并行开发组件**
