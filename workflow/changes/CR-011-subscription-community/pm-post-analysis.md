# PM 分析：帖子页面功能完善

> 分析时间：2026-07-24
> 分析人：PM

---

## 一、问题根因分析

### 1.1 点赞功能 Bug

**根因：前后端字段名不匹配 + unlike 无返回体**

| 项目 | 前端期望 | 后端实际 | 问题 |
|------|----------|----------|------|
| like 响应字段 | `response.likes_count` | `{"like_count": N}` | 字段名不匹配 |
| unlike 响应 | `response.likes_count` | 204 No Content（无 body） | 前端访问 undefined 报错 |

**代码位置：**
- 前端：`frontend/src/components/LikeButton.vue` 第 42-45 行
- 后端：`backend/app/api/v1/community.py` 第 203 行（like）、第 237 行（unlike）

**修复方案：**
- 后端 like 返回字段改为 `likes_count`（与前端对齐）
- 后端 unlike 改为返回 200 + `{"likes_count": N}`（与 like 一致）

### 1.2 评论功能缺失

**根因：后端缺少评论 API 端点**

| 项目 | 状态 | 说明 |
|------|------|------|
| Comment 模型 | ✅ 已有 | `backend/app/models/ugc.py` — Comment 类 |
| comments 表 | ✅ 已有 | id, post_id, user_id, content, is_deleted, created_at |
| 评论 API | ❌ 缺失 | community.py 无 GET/POST/DELETE comments 端点 |
| 前端 submitComment | ❌ TODO | CommunityView.vue 第 314 行 `// TODO: 实现提交评论的 API` |
| 前端 loadComments | ❌ 缺失 | 无加载评论的 API 调用 |

### 1.3 帖子详情页

**根因：前端已有 UI 但缺少数据加载逻辑**

| 项目 | 状态 |
|------|------|
| 详情页 UI | ✅ 已有（selectedPost 逻辑） |
| 评论区 UI | ✅ 已有（comment-list + comment-input） |
| 加载评论 | ❌ 缺失 |
| 提交评论 | ❌ TODO |

---

## 二、BE 任务清单

| # | 任务 | 优先级 | 工时 | 验收标准 |
|---|------|--------|------|----------|
| BE-P01 | 修复 like_post 返回字段 | P0 | 0.5h | 返回 `{"likes_count": N}` |
| BE-P02 | 修复 unlike_post 返回体 | P0 | 0.5h | 返回 200 + `{"likes_count": N}` |
| BE-P03 | 新增 GET /community/posts/{id}/comments | P0 | 1.5h | 返回评论列表+作者信息+分页 |
| BE-P04 | 新增 POST /community/posts/{id}/comments | P0 | 1.5h | 创建评论+更新 post.comment_count |
| BE-P05 | 新增 DELETE /community/posts/{id}/comments/{cid} | P1 | 1h | 软删除+更新 comment_count |

**BE 总工时：5h**

### API Contract

#### GET /community/posts/{post_id}/comments

```json
{
  "comments": [
    {
      "id": "uuid",
      "post_id": "uuid",
      "user_id": "uuid",
      "author_name": "用户名",
      "author_avatar": "url|null",
      "content": "评论内容",
      "created_at": "2026-07-24T10:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

#### POST /community/posts/{post_id}/comments

请求：`{"content": "评论内容"}`
响应：201 + 创建的评论对象

#### DELETE /community/posts/{post_id}/comments/{comment_id}

响应：204（仅评论作者可删除）

---

## 三、FE 任务清单

| # | 任务 | 优先级 | 工时 | 验收标准 |
|---|------|--------|------|----------|
| FE-P01 | 修复 LikeButton 响应字段处理 | P0 | 0.5h | 点赞/取消点赞后正确更新计数 |
| FE-P02 | 新增 getComments API 函数 | P0 | 0.5h | 调用 GET /comments 接口 |
| FE-P03 | 新增 createComment API 函数 | P0 | 0.5h | 调用 POST /comments 接口 |
| FE-P04 | 详情页加载评论 | P0 | 1h | 打开帖子自动加载评论列表 |
| FE-P05 | submitComment 对接 API | P0 | 1h | 提交评论后刷新列表+更新计数 |
| FE-P06 | 新增 deleteComment API + UI | P1 | 1h | 仅作者可见删除按钮 |

**FE 总工时：4.5h**

---

## 四、执行顺序

```
阶段 1（并行）：
  BE: BE-P01 + BE-P02（修复点赞）→ BE-P03 + BE-P04（评论 API）
  FE: FE-P01（修复 LikeButton）→ FE-P02 + FE-P03（API 函数）

阶段 2（BE 完成后）：
  FE: FE-P04 + FE-P05（加载+提交评论）→ FE-P06（删除评论）
```

---

## 五、联调测试

| # | 测试用例 | 验收标准 |
|---|----------|----------|
| TC-01 | 点赞帖子 | like_count +1，前端正确显示 |
| TC-02 | 取消点赞 | like_count -1，前端正确显示 |
| TC-03 | 加载评论列表 | 显示评论+作者+时间 |
| TC-04 | 发表评论 | 评论出现在列表，comment_count +1 |
| TC-05 | 删除评论（作者） | 评论消失，comment_count -1 |
| TC-06 | 删除评论（非作者） | 403 拒绝 |
| TC-07 | 游客点赞 | 提示登录 |
| TC-08 | 游客评论 | 提示登录 |
