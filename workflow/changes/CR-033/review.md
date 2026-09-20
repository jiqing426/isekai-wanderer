# CR-033 Review

## 开发覆盖声明: T-033-BE-001

### 任务信息

| 字段 | 值 |
|------|-----|
| 任务编号 | T-033-BE-001 |
| 任务名称 | 修复剧本详情章节解锁逻辑 |
| 负责人 | be (isekai-wanderer-be) |
| 关联 AC | AC-033-001 |
| 实际工时 | 0.5h |
| 完成时间 | 2026-08-05T14:35:00+08:00 |

### 已实现 AC

| AC | 描述 | 实现状态 | 测试状态 | 证据 |
|----|------|----------|----------|------|
| AC-033-001 | 章节解锁逻辑正确 | ✅ 已实现 | ✅ 逻辑验证 | `backend/app/api/v1/scripts.py` |

### 已测试 AC

| 测试项 | 结果 |
|--------|------|
| 新用户：第一章解锁，后续章节锁定 | ✅ PASSED |
| 完成第一章：第二章解锁 | ✅ PASSED |
| 进行中的章节保持解锁 | ✅ PASSED |
| 未完成的后续章节锁定 | ✅ PASSED |

### 未实现 AC

无

### 未测试 AC

无

### 已运行命令

- 逻辑验证脚本: Python 单元测试通过

### 失败命令

无

### 需要人工验收

- 实际环境中验证剧本详情页章节解锁状态
- 新用户进入剧本详情，第一章应显示为解锁状态

### 已知风险

1. 如果 `chapter_number` 为 NULL，视为 0，排在最前面
2. 如果有多个 route 的 `chapter_number` 相同，按 `created_at` 排序

---

## 代码变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `backend/app/api/v1/scripts.py` | Modified | 重写 `explored_route_ids` 计算逻辑 |

---

## 变更详情

### 问题分析

原代码存在以下问题：
1. 嵌套循环遍历 `script.routes` 和 `r.nodes` 来查找 `current_node_id` 所属的 route，效率低且逻辑混乱
2. `session` 变量在循环外部被引用，可能导致 `UnboundLocalError`
3. 逻辑过于复杂，没有清晰的顺序解锁规则

### 修复方案

重写解锁逻辑，遵循清晰的规则：
1. 按 `chapter_number` 排序所有路线（NULL 视为 0）
2. 第一个章节默认解锁（游戏入口）
3. 前置章节 `completed` → 解锁下一个章节
4. 正在进行的章节（`active`）保持解锁

### 代码对比

**修改前**（约 80 行复杂逻辑）:
```python
# 嵌套循环，逻辑混乱
for i, route in enumerate(sorted_routes):
    for session in user_sessions:
        ...
    for session in user_sessions:
        if session.status in ['active', 'completed'] and session.current_node_id:
            for r in script.routes:
                for node in r.nodes:
                    if node.id == session.current_node_id:
                        ...
    if session.choice_history:  # ❌ session 可能未定义
        ...
```

**修改后**（约 40 行清晰逻辑）:
```python
# 1. 按 chapter_number 排序
sorted_routes = sorted(script.routes, key=lambda r: (r.chapter_number or 0, r.created_at))

# 2. 第一个章节默认解锁
explored_route_ids.add(str(sorted_routes[0].id))

# 3. 构建 route_id → session status 映射
route_session_status = {}
for session in user_sessions:
    rid = str(session.route_id)
    # 优先级: active > completed > abandoned
    ...

# 4. 顺序遍历，应用解锁规则
for i, route in enumerate(sorted_routes):
    status = route_session_status.get(route_id_str)
    if status == 'active':
        explored_route_ids.add(route_id_str)
    elif status == 'completed':
        explored_route_ids.add(route_id_str)
        if i + 1 < len(sorted_routes):
            explored_route_ids.add(str(sorted_routes[i + 1].id))
```

---

## QA 覆盖复核

| AC | 描述 | 开发覆盖 | QA 复核 | 测试证据 | 状态 |
|----|------|----------|---------|----------|------|
| AC-033-001 | 章节解锁逻辑正确 | ✅ 已实现 | ❌ FAILED | DEFECT-033-001: API 返回 500 | 🔄 RETURNED TO BE |

### QA 复核详情

**复核时间**: 2026-08-05 11:20 CST  
**复核人**: isekai-wanderer-qa

**复核方法**:
1. ✅ Delivery E2E / Runtime Smoke: 健康检查通过（环境可达）
2. ❌ API 集成测试: `GET /api/v1/scripts/{script_id}` 返回 500 Internal Server Error
3. ⏸️ Browser Interaction E2E: 全部阻塞（依赖 API 修复）

**发现的问题**:
- **DEFECT-033-001**: 剧本详情 API 返回 500 错误（P0 阻塞性缺陷）
- 影响范围: 所有剧本详情页功能
- 复现步骤: 注册新用户 → 调用 `GET /api/v1/scripts/{script_id}` → 返回 500
- 责任归属: BE（isekai-wanderer-be）

**退回原因**:
- CR-033 修复的代码部署后引入新的 P0 缺陷
- 可能原因：
  1. 新代码中的边界条件未正确处理（如空列表访问、KeyError）
  2. 数据库查询返回异常数据
  3. 异常处理缺失
- 需要 BE 检查后端日志，定位异常堆栈并修复

**下一步行动**:
1. BE 检查后端日志，定位 500 错误的根因
2. 修复 `backend/app/api/v1/scripts.py` 中的 `get_script()` 函数
3. 部署修复版本到测试环境
4. QA 重新执行 API 测试和 Browser E2E

**测试结论**: ❌ BLOCKED - P0 缺陷阻塞测试
