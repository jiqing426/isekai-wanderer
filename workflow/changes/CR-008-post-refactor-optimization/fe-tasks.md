# CR-008 FE 对接任务清单

> 分配给：`isekai-wanderer-fe`
> 分配时间：2026-07-23
> 参考文档：`docs/api/api-contract-post-refactor.md`
> 状态：等待 PL 分配

---

## 任务概览

BE 已完成全部 **18 个后端接口**，FE 需对接以下接口：

| 批次 | 数量 | 用途 |
|------|------|------|
| 第一批 | 10 个 | 设置页面 + 社区 + 角色 + 收藏馆 |
| 第二批 | 9 个 | 个人中心（统计/资产/签到/存档/记忆/羁绊/结局） |

---

## 第一批：设置页面 + 社区 + 角色 + 收藏馆（10 个）

### 设置页面（5 个接口）

| # | 接口 | 方法 | 用途 | 认证 |
|---|------|------|------|------|
| 1 | `/api/v1/users/me` | GET | 获取用户信息 | Bearer |
| 2 | `/api/v1/users/me` | PATCH | 修改用户信息 | Bearer |
| 3 | `/api/v1/users/me/change-password` | POST | 修改密码 | Bearer |
| 4 | `/api/v1/users/me` | DELETE | 注销账号 | Bearer |
| 5 | `/api/v1/users/me/subscription` | GET | 获取订阅状态 | Bearer |

**前端消费组件：** `SettingsView.vue` / `ProfileSection`

### 收藏馆（2 个接口）

| # | 接口 | 方法 | 用途 | 认证 |
|---|------|------|------|------|
| 6 | `/api/v1/gallery/collections` | GET | 收藏品列表 | Bearer |
| 7 | `/api/v1/users/me/achievements` | GET | 成就列表（卡片式） | Bearer |

**前端消费组件：** `CollectionView.vue` → `CollectionsTab` / `AchievementTab`

### 社区（1 个接口）

| # | 接口 | 方法 | 用途 | 认证 |
|---|------|------|------|------|
| 8 | `/api/v1/ugc/posts` | GET | 帖子列表 | 无 |

**前端消费组件：** `CommunityView.vue` / `PostList`

### 角色（1 个接口）

| # | 接口 | 方法 | 用途 | 认证 |
|---|------|------|------|------|
| 9 | `/api/v1/characters` | GET | 角色列表 | 无 |

**前端消费组件：** `CharacterListView.vue` / `DiscoverView.vue`

### 其他

| # | 接口 | 说明 |
|---|------|------|
| 10 | `get_free_chat_service` | BE 已修复 ImportError，FE 无需改动 |

---

## 第二批：个人中心（9 个接口）

全部需 Bearer Token 认证。

| # | 接口 | 方法 | 用途 | 前端卡片 |
|---|------|------|------|----------|
| 11 | `/api/v1/users/me/stats` | GET | 游玩统计 | `StatsCard` |
| 12 | `/api/v1/users/me/asset` | GET | 碎片余额 | `AssetCard` |
| 13 | `/api/v1/sign/info` | GET | 签到信息 | `CheckinCard` |
| 14 | `/api/v1/users/me/latest-save` | GET | 继续游玩 | `ContinuePlayCard` |
| 15 | `/api/v1/users/me/memory/summary` | GET | AI 记忆摘要 | `MemoryCard` |
| 16 | `/api/v1/users/me/characters/bond` | GET | 角色羁绊 | `BondCard` |
| 17 | `/api/v1/users/me/endings` | GET | 结局追踪 | `EndingTrackerCard` |
| 18 | `/api/v1/users/me/endings/recent` | GET | 新解锁结局（分享用） | 弹窗/Toast |
| 19 | `/api/v1/users/me/memory/full` | GET | 完整 AI 记忆（会员） | `MemoryFullView` |

**前端消费组件：** `PersonalCenterView.vue`

---

## FE 对接清单

### API 层新增（`frontend/src/api/`）

```typescript
// api/user.ts — 设置页面
export function getMe()
export function updateMe(data: ProfileUpdateRequest)
export function changePassword(data: ChangePasswordRequest)
export function deleteAccount()
export function getMySubscription()
export function getMyAchievements()

// api/personal-center.ts — 个人中心
export function getUserStats()
export function getUserAsset()
export function getLatestSave()
export function getMemorySummary()
export function getCharacterBond()
export function getEndings()
export function getRecentEndings()
export function getFullMemory()

// api/sign.ts — 签到
export function getSignInfo()

// api/characters.ts — 已有，新增
export function getCharacters()

// api/ugc.ts — 已有，确认
export function getPosts()

// api/gallery.ts — 已有，确认 token 注入
export function getCollections()
```

### TypeScript Interfaces

参考 `docs/api/api-contract-post-refactor.md` 中每个接口的"前端消费方"部分。

---

## 已知限制

| 项目 | 说明 |
|------|------|
| 成就进度 | 当前返回 0%，未对接业务数据，FE 可正常渲染进度条 |
| `/users/me/memory/full` | 免费用户返回 403，FE 需处理权限提示 |
| DELETE `/users/me` | BE 未执行真实删除（保留测试数据），FE 需做二次确认弹窗 |

---

## 完成标准

- [ ] 18 个接口全部对接
- [ ] 设置页面渲染用户信息 + 订阅状态
- [ ] 个人中心 9 个卡片全部渲染
- [ ] 收藏馆成就卡片式展示
- [ ] 社区帖子列表正常加载
- [ ] 角色列表正常加载
- [ ] http interceptor 自动注入 Bearer token

---

## 第二阶段：阶段二 P1 任务（15h）— 2026-07-24 启动

### 缺陷修复（3h）

| # | 任务 | 优先级 | 工作量 | 状态 |
|---|------|--------|--------|------|
| FE-BUG-012 | 签到"累计获得"数据修复 | P1 | 1h | ⏳ 待开始 |
| FE-BUG-014 | 性格数据 JSON 解析 | P1 | 1h | ⏳ 待开始 |
| FE-BUG-015 | 好感度 NaN 修复 | P1 | 1h | ⏳ 待开始 |

### 功能实现（12h）

| # | 任务 | 优先级 | 工作量 | 状态 |
|---|------|--------|--------|------|
| FE-FEAT-020 | 对话页面历史展示（加载历史 + 倒序 + 滚动加载） | P1 | 3h | ⏳ 待开始 |
| FE-FEAT-021 | 对话标题显示剧本和角色 | P1 | 1h | ⏳ 待开始 |
| FE-FEAT-023 | 剧本详情完整数据展示 | P1 | 3h | ⏳ 待开始 |
| FE-FEAT-025 | AI 记忆展示（偏好/羁绊/事件列表） | P1 | 3h | ⏳ 待开始 |
| FE-FEAT-030 | 性格分析展示（标签+描述） | P1 | 2h | ⏳ 待开始 |

### 验收标准

#### FE-BUG-012: 签到累计获得
- AC-012-1: 签到后"累计获得"字段显示正确数值
- AC-012-2: 数据来源：`GET /users/me/sign/info` 返回 `total_fragments` 字段

#### FE-BUG-014: 性格数据 JSON 解析
- AC-014-1: 性格数据不再显示原始 JSON
- AC-014-2: 解析 JSON 后展示为标签列表

#### FE-BUG-015: 好感度 NaN 修复
- AC-015-1: "距离下一个"显示正确数值或隐藏
- AC-015-2: 当好感度已满时显示"已满级"
- AC-015-3: 数据缺失时不显示 NaN

#### FE-FEAT-020: 对话页面历史展示
- AC-020-1: 进入自由对话页面时加载历史对话
- AC-020-2: 历史对话按时间倒序显示
- AC-020-3: 支持滚动加载更多

#### FE-FEAT-021: 对话标题显示剧本和角色
- AC-021-1: 标题下方显示剧本名称（非"未知剧本"）
- AC-021-2: 标题下方显示角色名称（非"旁白"）
- AC-021-3: 数据来源：`GET /game/{id}/status`

#### FE-FEAT-023: 剧本详情完整数据
- AC-023-1: 展示剧本名称、描述、封面图片
- AC-023-2: 展示角色列表、路线数量、结局数量
- AC-023-3: 无图片时显示默认占位图（展示已有 image_url）

#### FE-FEAT-025: AI 记忆展示
- AC-025-1: 展示用户偏好记忆（列表）
- AC-025-2: 展示角色羁绊记忆（列表）
- AC-025-3: 展示重要事件记忆（列表）
- AC-025-4: 每条记忆包含描述和创建时间

#### FE-FEAT-030: 性格分析展示
- AC-030-1: 展示性格标签（如"温柔"、"傲娇"）
- AC-030-2: 每个标签附带描述说明
- AC-030-3: 数据来源：`GET /characters/{id}` 的 `personality_tags`

### 依赖关系

- BE-BUG-013 → FE-FEAT-028（收支明细依赖后端接口）
- BE-FEAT-027 → FE-BUG-012（签到阶梯奖励依赖后端逻辑）
- BE-FEAT-025 → FE-FEAT-025（AI 记忆展示依赖后端接口）
- BE-FEAT-023 → FE-FEAT-023（剧本详情依赖后端数据）

### 完成标准

- [ ] 8 个任务全部完成
- [ ] 所有缺陷修复通过验收
- [ ] 所有功能实现通过验收
- [ ] 无 UI 显示错误
- [ ] 无 NaN/undefined 显示

**启动时间：** 2026-07-24
**预计完成：** 2026-07-25（Day 3）
