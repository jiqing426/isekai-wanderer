# CR-008 BE 任务清单

> 分配给：`isekai-wanderer-be`
> 分配时间：2026-07-21T16:30:00Z
> 参考文档：`docs/api/api-contract-post-refactor.md`
> 优先级：全部 P0

---

## 任务概览

| # | 任务 | 类型 | 文件位置 | 状态 |
|---|------|------|----------|------|
| 1 | `GET /api/v1/ugc/posts` 500 修复 | 修复 | `backend/app/api/v1/ugc.py` | ✅ 完成 |
| 2 | `GET /api/v1/characters` 列表新增 | 新增 | `backend/app/api/v1/characters.py` | ✅ 完成 |
| 3 | `GET /api/v1/gallery/collections` 认证确认 | 确认 | `backend/app/api/v1/gallery.py` | ✅ 完成 |
| 4 | `get_free_chat_service` ImportError 修复 | 修复 | `backend/app/services/free_chat_service.py` | ✅ 完成 |
| 5 | `GET /api/v1/users/me` | 新增 | `backend/app/api/v1/users.py` | ✅ 完成 |
| 6 | `PATCH /api/v1/users/me` | 新增 | `backend/app/api/v1/users.py` | ✅ 完成 |
| 7 | `POST /api/v1/users/me/change-password` | 新增 | `backend/app/api/v1/users.py` | ✅ 完成 |
| 8 | `DELETE /api/v1/users/me` | 新增 | `backend/app/api/v1/users.py` | ✅ 完成 |
| 9 | `GET /api/v1/users/me/subscription` | 新增 | `backend/app/api/v1/users.py` | ✅ 完成 |
| 10 | `GET /api/v1/users/me/achievements` | 新增 | `backend/app/api/v1/users.py` | ✅ 完成 |

---

## 第一部分：接口修复（4 项）

### TASK-BE-001: 修复 `GET /api/v1/ugc/posts` 500 错误

**现状：**
- 路由已定义在 `backend/app/api/v1/ugc.py`
- 执行时返回 500 Internal Server Error
- 可能原因：DB 连接问题 / posts 表不存在 / MockMiddleware 干扰

**修复步骤：**
1. 检查 `backend/app/api/v1/ugc.py` 中 `GET /posts` 路由实现
2. 确认 `posts` 表是否已通过 alembic migration 创建
3. 确认 MockMiddleware 是否正确放行（当 `DISABLE_MOCK=1` 时）
4. 确保真实路由能正常返回分页数据

**验收标准：**
```bash
# DISABLE_MOCK=1 启动后端
curl -s http://localhost:8000/api/v1/ugc/posts | jq .
# 期望返回 200 + { posts: [...], page: 1, page_size: 20, total: N }
```

**响应结构（API Contract 3.2）：**
```json
{
  "posts": [
    {
      "id": "post-uuid-001",
      "user_id": "user-uuid-001",
      "title": "我的第一次异世界冒险",
      "content": "今天第一次玩了异世界之旅...",
      "image_urls": "https://cdn.example.com/img1.jpg",
      "like_count": 42,
      "comment_count": 8,
      "created_at": "2026-07-20T14:30:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 56
}
```

---

### TASK-BE-002: 新增 `GET /api/v1/characters` 列表接口

**现状：**
- 只有 `GET /api/v1/characters/{character_id}` 单个查询
- 缺少列表接口，前端无法获取全量角色

**修复步骤：**
1. 在 `backend/app/api/v1/characters.py` 新增 `GET /` 路由
2. 查询所有角色，支持 `include_main` 和 `limit` 参数
3. 返回角色列表 + 关联剧本数（`script_count`）

**验收标准：**
```bash
curl -s http://localhost:8000/api/v1/characters | jq .
# 期望返回 200 + { characters: [...], total: N }
```

**响应结构（API Contract 3.1）：**
```json
{
  "characters": [
    {
      "id": "char-uuid-001",
      "name": "樱",
      "description": "温柔的青梅竹马",
      "avatar_url": "/assets/avatars/sakura.png",
      "is_main": true,
      "age": "18",
      "height": "162cm",
      "birthday": "03-15",
      "likes": ["花", "音乐"],
      "personality": {
        "gentle": 85,
        "wisdom": 60,
        "brave": 40,
        "mysterious": 30,
        "loyal": 90
      },
      "script_count": 2
    }
  ],
  "total": 3
}
```

**Query 参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| include_main | boolean | 否 | true | 是否包含主角 |
| limit | int | 否 | 50 | 返回数量上限 |

---

### TASK-BE-003: 确认 `GET /api/v1/gallery/collections` 认证逻辑

**现状：**
- 路由已定义且需要 Bearer 认证（`Depends(get_current_user_id)`）
- MockMiddleware 也拦截了该路径
- 前端可能未正确传递 Authorization header 导致 401

**修复步骤：**
1. 确认路由实现正确，Bearer Token 认证逻辑无误
2. 确认 MockMiddleware 在 `DISABLE_MOCK=1` 时放行
3. 确认前端 http interceptor 会自动注入 Bearer token（FE 侧确认）
4. 用真实 token 测试路由返回正常数据

**验收标准：**
```bash
# 获取 token 后请求
curl -s -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/gallery/collections | jq .
# 期望返回 200 + { collections: [...] }
```

**响应结构（API Contract 3.3）：**
```json
{
  "collections": [
    {
      "id": "col-uuid-001",
      "item_type": "cg",
      "item_id": "cg-001",
      "item_name": "初次相遇",
      "image_url": "/assets/cg/1_thumb.jpg",
      "unlocked_at": "2026-07-15T10:00:00Z"
    }
  ]
}
```

---

### TASK-BE-004: 修复 `get_free_chat_service` ImportError

**现状：**
- `game.py` 第 287/324/343 行 `from app.services.free_chat_service import get_free_chat_service`
- 但 `free_chat_service.py` 只定义了 `class FreeChatService`，没有工厂函数
- 第 374 行 `from app.services.free_chat_service import free_chat_service`（模块级实例）

**修复步骤：**
1. 在 `backend/app/services/free_chat_service.py` 末尾添加工厂函数和模块级实例
2. 确保两种 import 方式都能工作

**代码修复：**
```python
# 在 free_chat_service.py 末尾添加：

# 单例工厂（兼容旧 import）
_free_chat_service_instance: Optional[FreeChatService] = None

def get_free_chat_service() -> FreeChatService:
    """获取 FreeChatService 单例。"""
    global _free_chat_service_instance
    if _free_chat_service_instance is None:
        _free_chat_service_instance = FreeChatService()
    return _free_chat_service_instance

# 模块级实例（兼容 from app.services.free_chat_service import free_chat_service）
free_chat_service = FreeChatService()
```

**验收标准：**
```bash
cd backend && python -c "from app.services.free_chat_service import get_free_chat_service, free_chat_service; print('OK')"
# 期望输出：OK
```

---

## 第二部分：新增用户 API（6 项）— ✅ 已完成

> 所有 `/users/me/*` 接口需 Bearer Token 认证。
> 建议新建 `backend/app/api/v1/users.py`，注册到 v1 router。
> 内部复用现有 user service 逻辑，不重复代码。

### ~~TASK-BE-005: 新增 `GET /api/v1/users/me`~~ ✅

**用途：** 获取当前用户信息（设置页面消费）
**认证：** Bearer

**响应 200（API Contract 1.1）：**
```json
{
  "id": "bd7f90f9-1234-5678-abcd-ef0123456789",
  "email": "user@example.com",
  "display_name": "夜行者",
  "avatar_url": "https://cdn.example.com/avatars/user001.png",
  "email_verified": true,
  "subscription_tier": "standard",
  "preferred_genre": "romance",
  "locale": "zh-CN",
  "onboarding_completed": true,
  "created_at": "2026-06-01T10:00:00Z"
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| AUTH_TOKEN_EXPIRED | 401 | Token 过期 |
| USER_NOT_FOUND | 404 | 用户不存在 |

---

### ~~TASK-BE-006: 新增 `PATCH /api/v1/users/me`~~ ✅

**用途：** 修改用户信息（部分更新）
**认证：** Bearer

**请求 Body：**
```json
{
  "display_name": "新名字",
  "avatar_url": "https://cdn.example.com/avatars/new.png",
  "locale": "zh-CN"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| display_name | string | 否 | 2-100 字符 |
| avatar_url | string | 否 | 新头像 URL |
| locale | string | 否 | 语言偏好 |

**响应 200：** 同 TASK-BE-005 结构（更新后的用户信息）

**错误码：**
| code | status | 说明 |
|------|--------|------|
| AUTH_TOKEN_EXPIRED | 401 | Token 过期 |
| USER_NOT_FOUND | 404 | 用户不存在 |
| VALIDATION_ERROR | 422 | 参数校验失败 |

---

### ~~TASK-BE-007: 新增 `POST /api/v1/users/me/change-password`~~ ✅

**用途：** 修改密码
**认证：** Bearer

**请求 Body：**
```json
{
  "old_password": "oldPass123",
  "new_password": "newPass456!"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 当前密码 |
| new_password | string | 是 | ≥8 字符 |

**响应 200：**
```json
{
  "status": "ok",
  "message": "Password changed successfully"
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| AUTH_TOKEN_EXPIRED | 401 | Token 过期 |
| AUTH_INVALID_CREDENTIALS | 401 | 旧密码错误 |
| VALIDATION_ERROR | 422 | 新密码格式不合规 |
| USER_NOT_FOUND | 404 | 用户不存在 |

---

### ~~TASK-BE-008: 新增 `DELETE /api/v1/users/me`~~ ✅

**用途：** 注销账号（MVP 阶段硬删除）
**认证：** Bearer

**响应 200：**
```json
{
  "status": "deleted",
  "message": "Account deleted successfully"
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| AUTH_TOKEN_EXPIRED | 401 | Token 过期 |
| USER_NOT_FOUND | 404 | 用户不存在 |

---

### ~~TASK-BE-009: 新增 `GET /api/v1/users/me/subscription`~~ ✅

**用途：** 获取订阅状态（设置页面 / 订阅页面）
**认证：** Bearer
**注意：** 已有 `/user/subscription`，需新增 `/users/me/subscription` 别名，内部复用同一逻辑。

**响应 200（API Contract 1.5）：**
```json
{
  "tier": "standard",
  "status": "active",
  "trial_started_at": "2026-06-01T10:00:00Z",
  "trial_ends_at": "2026-07-01T10:00:00Z",
  "renew_at": "2026-08-01T10:00:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| tier | string | `free` / `standard` / `premium` |
| status | string | `active` / `inactive` / `cancelled` / `trialing` |
| trial_started_at | string\|null | 试用开始时间 |
| trial_ends_at | string\|null | 试用结束时间 |
| renew_at | string\|null | 下次续费时间（仅 active 时有值） |

**错误码：**
| code | status | 说明 |
|------|--------|------|
| AUTH_TOKEN_EXPIRED | 401 | Token 过期 |
| USER_NOT_FOUND | 404 | 用户不存在 |

---

### ~~TASK-BE-010: 新增 `GET /api/v1/users/me/achievements`~~ ✅

**用途：** 收藏馆 → 成就 Tab 卡片式展示
**认证：** Bearer
**注意：** 整合 `achievements-v2` 和 `gallery/achievements` 的数据。

**响应 200（API Contract 2.1）：**
```json
{
  "achievements": [
    {
      "id": "ach_first_dialogue",
      "name": "初见",
      "description": "完成第一次对话",
      "icon": "🎭",
      "icon_url": "/assets/achievements/first_dialogue.png",
      "is_unlocked": true,
      "unlocked_at": "2026-07-15T10:00:00Z",
      "progress": {
        "current": 1,
        "target": 1,
        "percentage": 100
      },
      "reward": {
        "type": "fragments",
        "amount": 20,
        "claimed": true
      }
    }
  ],
  "total": 8,
  "unlocked_count": 4,
  "claimed_count": 3
}
```

**字段说明（单个 achievement）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 成就唯一标识 |
| name | string | 成就名称 |
| description | string | 成就描述 |
| icon | string | Emoji 图标（备用） |
| icon_url | string\|null | 图标资源 URL |
| is_unlocked | boolean | 是否已解锁 |
| unlocked_at | string\|null | 解锁时间 |
| progress.current | number | 当前进度值 |
| progress.target | number | 目标值 |
| progress.percentage | number | 0-100 百分比 |
| reward.type | string | `fragments` |
| reward.amount | number | 奖励数量 |
| reward.claimed | boolean | 是否已领取 |

**错误码：**
| code | status | 说明 |
|------|--------|------|
| AUTH_TOKEN_EXPIRED | 401 | Token 过期 |

---

## 实现建议

### 文件结构

```
backend/app/api/v1/
├── users.py          # 新建：TASK-BE-005 ~ 010
├── characters.py     # 修改：TASK-BE-002
├── ugc.py            # 修改：TASK-BE-001
└── gallery.py        # 确认：TASK-BE-003

backend/app/services/
└── free_chat_service.py  # 修改：TASK-BE-004
```

### 认证依赖

所有 `/users/me/*` 路由使用现有认证依赖：
```python
from app.api.deps import get_current_user_id

@router.get("/users/me")
async def get_me(user_id: str = Depends(get_current_user_id)):
    ...
```

### 执行顺序建议

1. **TASK-BE-004**（ImportError 修复）— 最基础，解除启动阻塞
2. **TASK-BE-001**（ugc/posts 500 修复）— 解除社区页面阻塞
3. **TASK-BE-002**（characters 列表新增）— 解除角色页面阻塞
4. **TASK-BE-003**（gallery/collections 确认）— 解除收藏馆阻塞
5. **TASK-BE-005 ~ 010**（用户 API 系列）— 解除设置页面阻塞

## 第三部分：个人中心接口（9 项）— ✅ 已完成

> 所有接口需 Bearer Token 认证。
> 参考 API Contract 第 2 节。

| # | 任务 | 状态 |
|---|------|------|
| TASK-BE-011 | `GET /api/v1/users/me/stats` 游玩统计 | ✅ |
| TASK-BE-012 | `GET /api/v1/users/me/asset` 碎片余额 | ✅ |
| TASK-BE-013 | `GET /api/v1/sign/info` 签到信息 | ✅ |
| TASK-BE-014 | `GET /api/v1/users/me/latest-save` 继续游玩 | ✅ |
| TASK-BE-015 | `GET /api/v1/users/me/memory/summary` AI 记忆摘要 | ✅ |
| TASK-BE-016 | `GET /api/v1/users/me/characters/bond` 角色羁绊 | ✅ |
| TASK-BE-017 | `GET /api/v1/users/me/endings` 结局追踪 | ✅ |
| TASK-BE-018 | `GET /api/v1/users/me/endings/recent` 新解锁结局 | ✅ |
| TASK-BE-019 | `GET /api/v1/users/me/memory/full` 完整记忆 | ✅ |

---

### 完成标准

- [x] 18 个接口全部实现并可访问
- [x] 无 500/404 错误
- [x] 响应结构与 API Contract 一致
- [x] `python -c "from app.services.free_chat_service import get_free_chat_service"` 通过
- [x] 所有 `/users/me/*` 接口带 Bearer Token 可正常返回
- [x] 所有公开接口不带 Token 可正常返回

**完成时间：** 2026-07-23

---

## 第四部分：阶段二 P1 任务（8h）— 2026-07-24 启动

### 缺陷修复（5h）

| # | 任务 | 优先级 | 工作量 | 状态 |
|---|------|--------|--------|------|
| BE-BUG-013 | 实现 `GET /users/me/transactions` 收支明细 | P1 | 3h | ⏳ 待开始 |
| BE-BUG-016 | 帖子预览数增加（点击后 view_count +1） | P1 | 2h | ⏳ 待开始 |

### 功能增强（3h）

| # | 任务 | 优先级 | 工作量 | 状态 |
|---|------|--------|--------|------|
| BE-FEAT-027 | 签到阶梯奖励逻辑（3/7/30天阶梯 + 断签重置） | P1 | 3h | ⏳ 待开始 |
| BE-FEAT-025 | AI 记忆接口补全（返回偏好/羁绊/事件列表） | P1 | 2h | ⏳ 待开始 |
| BE-FEAT-023 | 剧本详情数据补全（返回完整角色/路线/结局数据） | P1 | 2h | ⏳ 待开始 |

### 验收标准

#### BE-BUG-013: 收支明细
- AC-013-1: 调用 `GET /users/me/transactions` 返回 200
- AC-013-2: 响应包含 `transactions: Transaction[]` 数组
- AC-013-4: 支持分页加载（page, page_size 参数）

#### BE-BUG-016: 帖子预览数
- AC-016-1: 点击帖子后 `view_count` 字段 +1
- AC-016-3: 并发访问时预览数正确累加（使用数据库原子操作）

#### BE-FEAT-027: 签到阶梯奖励
- AC-027-1: 连续签到 3 天奖励 +10 碎片
- AC-027-2: 连续签到 7 天奖励 +30 碎片
- AC-027-3: 连续签到 30 天奖励 +200 碎片
- AC-027-4: 断签后连续天数重置为 0
- AC-027-5: 累计签到里程碑奖励正确发放

#### BE-FEAT-025: AI 记忆接口
- 返回用户偏好记忆列表
- 返回角色羁绊记忆列表
- 返回重要事件记忆列表
- 每条记忆包含描述和创建时间

#### BE-FEAT-023: 剧本详情数据
- 返回剧本名称、描述、封面图片（cover_image_url）
- 返回角色列表（关联 characters 表）
- 返回路线数量（关联 routes 表）
- 返回结局数量（关联 endings 表）

### 依赖关系

- BE-BUG-013 → FE-FEAT-028（收支明细依赖后端接口）
- BE-FEAT-027 → FE-BUG-012（签到阶梯奖励依赖后端逻辑）
- BE-FEAT-025 → FE-FEAT-025（AI 记忆展示依赖后端接口）
- BE-FEAT-023 → FE-FEAT-023（剧本详情依赖后端数据）

### 完成标准

- [ ] 5 个任务全部完成
- [ ] 所有接口返回正确数据结构
- [ ] 签到阶梯奖励逻辑正确（3/7/30天）
- [ ] 帖子预览数正确累加
- [ ] 无 500/404 错误

**启动时间：** 2026-07-24
**预计完成：** 2026-07-24（Day 2）
