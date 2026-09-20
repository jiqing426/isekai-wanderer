# Spec: Capability — Corvus Frontend Entry

## Requirements

### Requirement: REQ-CAP-001 — GET /scripts 返回 engine_type 字段

**Priority**: P0

后端 `GET /scripts`（列表）和 `GET /scripts/{id}`（详情）返回的每个 script 对象必须包含 `engine_type` 字段，值为 `'corvus'`（C1/C3 约束）。

#### Scenario: GET /scripts 列表返回 engine_type

- **Given** 系统中有 N 个剧本
- **When** 前端调用 `GET /api/v1/scripts`
- **Then** 返回的 `scripts` 数组中每个对象包含 `engine_type: 'corvus'` 字段
- **And** 字段类型为 string，值为 `'corvus'`

#### Scenario: GET /scripts/{id} 详情返回 engine_type

- **Given** 系统中存在某个剧本
- **When** 前端调用 `GET /api/v1/scripts/{script_id}`
- **Then** 返回的 script 对象包含 `engine_type: 'corvus'` 字段

### Requirement: REQ-CAP-002 — GET /game/scripts/{script_id}/characters 预设角色列表端点

**Priority**: P0

后端提供 `GET /api/v1/game/scripts/{script_id}/characters` 端点，返回剧本预设可扮演角色列表（Character 表 `playable=True` 记录）。

**范围变更 (2026-09-07)**：原 REQ-CAP-002（POST /game/player/candidates 创建端点）已移除。改为预设角色列表查询端点。

#### Scenario: 获取剧本预设角色列表

- **Given** 系统中存在某个剧本，且 Character 表有 `playable=True` 的角色关联到该剧本
- **When** 前端调用 `GET /api/v1/game/scripts/{script_id}/characters`
- **Then** 返回 `{"code": 0, "data": [{"id": "<uuid>", "name": "...", "description": "...", "avatar_url": "...", "play_description": "..."}, ...]}`
- **And** 数据来源为 Character 表 `playable=True` 记录

#### Scenario: 剧本无预设角色

- **Given** 某剧本在 Character 表中没有 `playable=True` 的角色
- **When** 前端调用 `GET /api/v1/game/scripts/{script_id}/characters`
- **Then** 返回 `{"code": 0, "data": []}`

### Requirement: REQ-CAP-003 — Legacy 分支保留但不激活

**Priority**: P1

前端 legacy 代码路径（`POST /game/start`、节点式对话、`submitChoice` legacy 分支）保留在代码库中，但所有剧本统一走 Corvus 流程，legacy 分支不被激活。

#### Scenario: Legacy 代码保留

- **Given** 前端代码库包含 legacy 游戏路径代码
- **When** 用户选择任意剧本开始游戏
- **Then** 走 Corvus 流程（`POST /game/session/create` + `select-player`）
- **And** Legacy 代码路径不被执行
- **And** Legacy 代码不被删除，保留在代码库中
