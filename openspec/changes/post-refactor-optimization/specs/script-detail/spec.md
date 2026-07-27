# Script Detail Spec — CR-008 V3（FEAT-023 最终版）

## 需求概述

用户原话："在数据库加上数据，前端页面要展示"。

剧本详情页面需要展示完整数据：基本信息、角色、路线、结局、CG、章节节点。数据从数据库读取，前端渲染。

## 当前状态分析

### 已有数据库模型
- `scripts` - 剧本（title, description, cover_image_url, genre, hot_value）
- `routes` - 路线（title, description, script_id）
- `nodes` - 节点（node_type, content, background, route_id）
- `node_choices` - 选择项（text, next_node_id, node_id）
- `characters` - 角色（name, description, avatar_url, personality, likes, age, height, birthday, script_id）
- `character_sprites` - 角色表情（emotion, image_url, character_id）
- `scenes` - 场景（name, background_url, bgm_url, script_id）

### 已有 API 端点
| 端点 | 认证 | 返回内容 | 状态 |
|------|------|----------|------|
| `GET /scripts/{id}` | 无 | 基本信息 + routes + characters | ✅ 可用 |
| `GET /scripts/{id}/detail` | 需要 | chapters + nodes | ⚠️ 缺 characters/endings/cgs |
| `GET /scripts/{id}/characters` | 无 | characters 列表 | ✅ 可用 |
| `GET /scripts/{id}/routes` | 需要 | 路线树 | ✅ 可用 |
| `GET /scripts/{id}/endings` | 需要 | 结局列表 | ⚠️ 需确认 endings 表数据 |
| `GET /scripts/{id}/cg-preview` | 需要 | CG 列表 | ⚠️ 需确认 cg_assets 表数据 |

### 前端期望（ScriptDetailView.vue）
前端调用 `GET /scripts/{id}/detail`，期望响应包含：
- `title`, `cover`, `description`, `author` - 基本信息
- `characters[]` - 角色列表
- `endings[]` - 结局列表（含 unlocked 状态）
- `cgs[]` - CG 列表（含 unlocked 状态）
- `chapters[]` - 章节列表（含 nodes[]）
- `completionRate`, `totalNodes`, `unlockedNodes` - 进度数据

### 缺口
1. `/detail` 接口不返回 characters、endings、cgs
2. Script 模型无 author 字段（API 硬编码 "剧本作者"）
3. endings 表和 cg_assets 表可能无数据

## 需求列表

### REQ-FEAT-023-BE: 后端补全 `/scripts/{id}/detail` 响应

**修改内容**：
在 `backend/app/api/v1/scripts.py` 的 `get_script_detail` 函数中：

1. **添加 characters**：查询 `characters` 表，返回角色列表
2. **添加 endings**：查询 `endings` 表，返回结局列表（含用户解锁状态）
3. **添加 cgs**：查询 `cg_assets` 表，返回 CG 列表（含用户解锁状态）
4. **添加 author**：从 Script 模型读取或返回默认值

**接口响应结构**：
```json
{
  "scriptId": "uuid",
  "title": "剧本标题",
  "cover": "封面图片 URL",
  "description": "剧本描述",
  "author": "作者名",
  "characters": [
    {
      "id": "uuid",
      "name": "角色名",
      "description": "角色描述",
      "avatar_url": "头像 URL",
      "personality": {},
      "likes": [],
      "age": 20,
      "height": 170,
      "birthday": "07-07",
      "is_main": true
    }
  ],
  "endings": [
    {
      "id": "uuid",
      "title": "结局标题",
      "type": "good/normal/bad",
      "description": "结局描述",
      "unlocked": true/false,
      "unlockDate": "2026-07-24"
    }
  ],
  "cgs": [
    {
      "id": "uuid",
      "name": "CG 名称",
      "imageUrl": "图片 URL",
      "unlocked": true/false
    }
  ],
  "chapters": [
    {
      "chapterId": "ch1",
      "title": "第一章",
      "nodes": [...]
    }
  ],
  "totalNodes": 50,
  "unlockedNodes": 10,
  "completionRate": 20
}
```

### REQ-FEAT-023-DATA: 数据库补全种子数据

**需要确认/补全的数据**：

1. **endings 表**：每个剧本至少有 3 个结局（good/normal/bad）
2. **cg_assets 表**：每个剧本至少有 5 个 CG
3. **characters 表**：每个剧本至少有 3 个角色（已有数据）
4. **author 字段**：Script 模型添加 author 字段，或从 seed 数据填充

**种子数据 SQL**（示例）：
```sql
-- 为星月奇缘添加结局
INSERT INTO endings (id, script_id, title, type, description, route_id) VALUES
  (uuid_generate_v4(), '66666666-...', '星月永恒', 'good', '...', '88888888-...'),
  (uuid_generate_v4(), '66666666-...', '月缺星沉', 'bad', '...', '88888888-...'),
  (uuid_generate_v4(), '66666666-...', '擦肩而过', 'normal', '...', '88888888-...');

-- 为星月奇缘添加 CG
INSERT INTO cg_assets (id, script_id, name, image_url, route_id) VALUES
  (uuid_generate_v4(), '66666666-...', '星空下的约定', '/assets/cg/sm-01.jpg', '88888888-...'),
  ...;
```

### REQ-FEAT-023-FE: 前端展示已有数据

**前端已实现**（ScriptDetailView.vue）：
- ✅ Hero Section：封面、标题、描述、作者
- ✅ 角色选择：CharacterDetailCard 组件
- ✅ 路线探索：RouteTree 组件
- ✅ 结局收集：EndingList 组件
- ✅ CG 预览：CGPreviewGrid 组件
- ✅ 章节内容：ScriptNodeCard 组件

**前端需要修复**：
- 确认 `loadScript()` 函数正确解析 API 响应
- 确认各组件正确接收 props

## 验收标准

### AC-023-1: 基本信息展示
- 剧本标题、描述、封面图片正确显示
- 作者名正确显示（非"剧本作者"硬编码）
- 无封面时显示占位图

### AC-023-2: 角色列表展示
- 展示该剧本所有角色
- 每个角色显示头像、名称、描述
- 数据来源：`characters` 表

### AC-023-3: 结局列表展示
- 展示该剧本所有结局
- 显示解锁/未解锁状态
- 数据来源：`endings` 表

### AC-023-4: CG 预览展示
- 展示该剧本所有 CG
- 显示解锁/未解锁状态
- 数据来源：`cg_assets` 表

### AC-023-5: 章节节点展示
- 展示章节列表和节点
- 显示解锁/未解锁状态
- 数据来源：`routes` + `nodes` 表

### AC-023-6: 统计数据展示
- 路线数量、结局数量、角色数量正确
- 完成进度百分比正确

## 依赖

- BE: 修改 `get_script_detail` 函数
- BE: 确认 endings/cg_assets 表有数据
- FE: 确认前端解析逻辑正确

## 任务分配

| 角色 | 任务 | 工作量 |
|------|------|--------|
| BE | 修改 `/scripts/{id}/detail` 接口 | 2h |
| BE | 补全 endings/cg_assets 种子数据 | 1h |
| FE | 验证前端展示逻辑 | 1h |
