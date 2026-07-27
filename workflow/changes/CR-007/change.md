# CR-007: v4.4 双 Agent 架构实现

## 基本信息
- **CR ID**: CR-007
- **变更名称**: v4.4-dual-agent
- **创建时间**: 2026-07-21T22:00:00Z
- **发起人**: CEO（通过 main session 转达）
- **负责人**: PL
- **当前阶段**: INTAKE

## 变更目标

实现 v4.4 双 Agent 架构（剧情 Agent + 陪伴 Agent），支持 3 角色 × 3 集合点剧情走向系统，每角色 2 个结局，14 个 AI 模型自动降级，手动存档机制，CG 图像解锁系统，用户数据完全隔离。

## 页面范围（共 8 页）

| 页面 | 路由 | 优先级 | 操作 |
|------|------|--------|------|
| LandingView | `/` | P0-2 | 移动端适配完成 |
| LoginView | `/login` | P0-1 | 增强：Google/Discord OAuth 按钮（mock） |
| RegisterView | `/register` | P0-1 | 增强：Google/Discord OAuth 按钮（mock） |
| ScriptDetailView | `/script/:id` | P0-4 | 增强 + 移动端适配 |
| GameView | `/play/:id/:session` | P0-5 | ★重构：整合所有组件 + 移动端适配 |
| GalleryView | `/gallery` | P1-1 | 保留 + 移动端适配 |
| SubscriptionView | `/subscribe` | P1-2 | 增强 + 移动端适配 |
| About&Legal | `/about` | P1-3 | 新增 + 移动端适配 |

**删除**：HomeView（首页）

## 技术架构

以 `docs/v4.4-完整需求与实现方案-v4.0.md` 为准：
- ✅ 集合点机制：保留
- ✅ 好感度 5 级：保留
- ✅ 14 个模型路由器：保留
- ✅ 记忆回溯：保留

## OAuth 方案

- Google OAuth：先用 mock 数据，等老大配好 key 替换
- Discord OAuth：同上，mock 先行
- 登录/注册页：保持两个页面（Login + Register），不合并

## 优先级排序

### P0-1：登录/注册页（W02）
- 增强现有 LoginView.vue + RegisterView.vue
- 添加 Google OAuth 按钮（mock）
- 添加 Discord OAuth 按钮（mock）
- 邮箱密码登录保持
- redirect 回跳机制

### P0-2：LandingView（W01）
- 移动端适配完成

### P0-3：剧本大厅（W04/DiscoverView）
- 增强 + 移动端适配

### P0-4：剧本详情（W05/ScriptDetailView）
- 增强 + 移动端适配

### P0-5：游戏交互页 ★（W06/GameView）
- BE 先补完：ConvergenceService + API 路由注册 + AffectionHistory
- FE 重构 GameView.vue 整合所有组件
- 移动端适配

### P1-1：CG 画廊（W08/GalleryView）
### P1-2：订阅页（W11/SubscriptionView）
### P1-3：关于&法律（W14）

## 数据库迁移状态

✅ 已完成：v44_dual_agent (head) — 6 张表迁移全部到位

## 立即行动

### BE 任务（5 个）
1. 创建 AffectionHistory 模型（好感度历史记录表）
2. 创建 ConvergenceService（集合点服务，包含检测逻辑）
3. 注册 /api/v1/chat/free 路由（自由对话 API）
4. 注册 /api/v1/game/convergence/check 路由（集合点检测）
5. 注册 /api/v1/affection/history 路由（好感度历史）

**说明**：数据库迁移已完成，ConvergencePoint 和 UserPersona 模型已创建，AffectionHistory 模型文件缺失需要补。

### FE 任务
从 W02 登录页开始：
1. 增强 LoginView.vue：添加 Google OAuth 按钮（mock）+ Discord OAuth 按钮（mock）
2. 增强 RegisterView.vue：同上
3. OAuth 用 mock 数据，不接真实 API

完成后等后续页面分配。

## 成功标准

- [ ] 8 个页面全部实现并移动端适配
- [ ] OAuth mock 登录/注册流程正常
- [ ] GameView 整合所有组件（集合点、好感度、自由对话）
- [ ] BE 5 个 API 全部可用
- [ ] 数据库迁移无回滚

## 风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| OAuth key 未配置 | 无法真实登录 | mock 先行，后续替换 |
| GameView 重构复杂 | 可能影响现有功能 | 分步整合，逐步验证 |
| 移动端适配工作量 | 可能超时 | 优先 P0 页面 |

## 下一步

1. 确认群集状态
2. 分配 BE 任务（5 个）
3. 分配 FE 任务（W02 登录页）
4. 跟踪进度
