# Tasks — CR-004 移动端适配

| 项 | 内容 |
| --- | --- |
| 变更 ID | CR-004 |
| 变更名称 | mobile-responsive |
| 任务状态 | Ready |
| 负责人 | fe (Frontend) |
| 创建时间 | 2026-07-19 |
| 前置条件 | DESIGN passed |

---

## CEO 附加约束（DESIGN 阶段必须遵循）

| # | 约束 | 执行方式 |
|---|------|----------|
| C1 | **GameView 单独处理** | TASK-MOB-005 不与其他 P0 页面并行；单独分配 + 充分测试后再进入其余 P0 |
| C2 | **Naive UI 覆盖冲突风险** | TASK-MOB-010 中如 `:deep()` 方案不可行，立即上报 PL，不硬啃；标记为 Blocked 并记录具体组件 |
| C3 | **PC 端零影响是硬约束** | 每个任务的验证方式必须包含 `≥1024px 视口回归验证`；违反即回滚 |

---

## 执行策略

**Demo 先行 → GameView 单独 → P0 其余 → P1 → P2**：

| 阶段 | 内容 | 预估 | 前置条件 |
|------|------|------|----------|
| Demo | LandingView + HomeView + 基础设施（mobile.css + TabBar） | 1 天 | DESIGN passed |
| GameView 单独 | GameView 单独适配 + 充分测试 | 1 天 | Demo 用户确认 |
| P0 其余 | DiscoverView + CharacterListView + CharacterDetailView + CommunityView + Naive UI 覆盖 | 1-2 天 | GameView 验收通过 |
| P1 | 18 个功能页面 | 3-4 天 | P0 完成 |
| P2 | 3 个辅助页面 + 公共组件 + 回归 | 1-2 天 | P1 完成 |
| **合计** | | **7-10 天** | |

---

## 紧急修复任务（优先级最高）

### BUG-MOB-001: 移动端导航栏不可见

| 项 | 内容 |
| --- | --- |
| 任务 ID | BUG-MOB-001 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 AppHeader 移动端样式） |
| 关联验收项 | AC-MOB-009 |
| 验证方式 | 1. ≤767px 视口下 AppHeader 隐藏或简化<br>2. 仅显示底部 TabBar<br>3. 导航功能正常 |
| 回滚方案 | 删除 `mobile.css` 中 AppHeader 移动端样式 |

**任务描述**：
- 在 `mobile.css` 中添加 AppHeader 移动端样式
- 移动端隐藏顶部导航栏（`.header-nav`）
- 保留 Logo 和工具按钮（语言切换、主题切换、用户头像）
- 确保底部 TabBar 正常显示和导航

---

### BUG-MOB-002: hero-banner 上下留空过多

| 项 | 内容 |
| --- | --- |
| 任务 ID | BUG-MOB-002 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（调整 hero-banner 移动端样式） |
| 关联验收项 | AC-MOB-002 |
| 验证方式 | 1. ≤767px 视口下 hero-banner 间距紧凑<br>2. 内容不拥挤<br>3. 视觉效果良好 |
| 回滚方案 | 恢复 `mobile.css` 中 hero-banner 原始样式 |

**任务描述**：
- 调整 `mobile.css` 中 hero-banner 的 padding 和 margin
- 减少上下间距，让内容更紧凑
- 保持视觉效果良好

---

## Demo 任务（基础设施 + LandingView + HomeView）

### TASK-MOB-001: 创建 mobile.css 基础架构

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-001 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（新建）, `frontend/src/main.ts`（仅添加 import） |
| 关联验收项 | AC-MOB-013, AC-MOB-015 |
| 验证方式 | 1. `git diff frontend/src/styles/global.css` 为空<br>2. `mobile.css` 存在且包含 `@media (max-width: 767px)`<br>3. 全局 `overflow-x: hidden` 生效<br>4. **≥1024px 视口下页面视觉无变化** |
| 回滚方案 | 删除 `mobile.css`，移除 `main.ts` 中的 import |

**任务描述**：
- 新建 `frontend/src/styles/mobile.css`
- 添加全局移动端基础样式：
  - `html, body { overflow-x: hidden; }`（仅在 `@media (max-width: 767px)` 内）
  - `.page-bg { padding: 12px; }`（单列布局基础）
  - iOS 安全区域支持 `@supports (padding-bottom: env(safe-area-inset-bottom))`
- 在 `main.ts` 中添加 `import './styles/mobile.css'`
- 添加布局工具类：`.mobile-full-width`, `.mobile-single-column`
- **所有规则必须在 `@media (max-width: 767px)` 内，确保 PC 端零影响**

---

### TASK-MOB-002: 创建 MobileTabBar 组件

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-002 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/components/MobileTabBar.vue`（新建）, `frontend/src/App.vue`（仅添加组件引入）, `frontend/src/styles/mobile.css`（添加 TabBar 样式） |
| 关联验收项 | AC-MOB-009, AC-MOB-010, AC-MOB-011 |
| 验证方式 | 1. ≤767px 视口下 TabBar 固定显示，包含 5 个入口<br>2. 点击 Tab 可正常导航<br>3. 当前 Tab 高亮<br>4. **≥1024px 视口下 TabBar 不显示（`display: none`）**<br>5. iOS 设备底部 safe-area 生效 |
| 回滚方案 | 删除 `MobileTabBar.vue`，移除 `App.vue` 中的组件引入 |

**任务描述**：
- 新建 `frontend/src/components/MobileTabBar.vue`
- 实现 5 个入口：🏠 首页、🔍 发现、🎮 游戏、👥 社区、👤 我的
- 实现路由导航和高亮逻辑
- GameView 隐藏 TabBar（沉浸模式）
- 在 `mobile.css` 中添加 TabBar 样式（全部在 `@media (max-width: 767px)` 内）：
  - `position: fixed; bottom: 0`
  - `height: 56px`
  - `padding-bottom: env(safe-area-inset-bottom)`
  - `z-index: 1000`
- 在 `App.vue` 中引入组件
- **PC 端：TabBar 组件在 ≥1024px 必须完全不可见、不占空间**

---

### TASK-MOB-003: LandingView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-003 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 LandingView 样式） |
| 关联验收项 | AC-MOB-001 |
| 验证方式 | 1. ≤767px 视口下页面单列布局<br>2. 无横向滚动<br>3. CTA 按钮 ≥44px<br>4. 图片/视频自适应宽度<br>5. 文字 ≥14px<br>6. **≥1024px 视口下 LandingView 视觉无变化** |
| 回滚方案 | 删除 `mobile.css` 中 LandingView 相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 LandingView 移动端样式
- 单列全宽布局
- CTA 按钮 `width: 100%; min-height: 44px`
- 图片/视频 `max-width: 100%; height: auto`
- 文字 `font-size: ≥14px`

---

### TASK-MOB-004: HomeView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-004 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 HomeView 样式） |
| 关联验收项 | AC-MOB-002 |
| 验证方式 | 1. ≤767px 视口下卡片单列全宽<br>2. 卡片间距 12-16px<br>3. 底部 TabBar「首页」高亮<br>4. 无横向滚动<br>5. 无内容溢出/错位<br>6. **≥1024px 视口下 HomeView 视觉无变化** |
| 回滚方案 | 删除 `mobile.css` 中 HomeView 相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 HomeView 移动端样式
- 卡片单列全宽 `width: 100%`
- 卡片间距 `gap: 12-16px`
- 底部预留 TabBar 高度 `padding-bottom: 72px`
- 验证 TabBar「首页」高亮

---

### Demo 阶段验收检查点

完成以上 4 个任务后，进行 Demo 验收：

1. **视觉验收**：LandingView + HomeView 在 ≤767px 视口下布局正常
2. **功能验收**：TabBar 5 入口导航正常，高亮状态正确
3. **回归验收**：≥1024px 视口下 PC 端完全不受影响（截图对比）
4. **用户确认**：提交用户确认，通过后进入 GameView 单独阶段

---

## GameView 单独阶段（CEO 要求：不与其他 P0 并行）

### TASK-MOB-005: GameView 移动端适配（单独处理）

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-005 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 GameView 样式） |
| 关联验收项 | AC-MOB-003, AC-MOB-004 |
| 验证方式 | 1. ≤767px 视口下对话区域全宽，字号 ≥14px<br>2. 选择面板按钮 ≥44px 全宽单列<br>3. 场景图片自适应宽度<br>4. TabBar 隐藏（沉浸模式）<br>5. 点击选项按钮能正常触发剧情推进，无 JS 报错<br>6. **≥1024px 视口下 GameView 视觉与交互完全无变化**<br>7. **GameView 单独测试通过后才进入其余 P0** |
| 回滚方案 | 删除 `mobile.css` 中 GameView 相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 GameView 移动端样式
- 对话区域全宽 `width: 100%`
- 选择面板按钮单列全宽 `min-height: 44px`
- 场景图片 `max-width: 100%`
- 确保 TabBar 在 GameView 隐藏
- 验证点击选项能正常触发剧情推进（不改业务逻辑，仅验证 CSS 不影响交互）

**CEO 约束执行**：
- ⚠️ 此任务**必须单独执行**，不得与 TASK-MOB-006~009 并行
- ⚠️ 此任务**必须充分测试**：至少覆盖 3 种场景（对话显示、选择分支、场景切换）
- ⚠️ 测试通过后，PL 确认方可进入 P0 其余页面

---

### GameView 阶段验收检查点

1. **GameView 单独验收**：≤767px 视口下对话/选择/场景全部正常
2. **交互验证**：选择分支能正常触发剧情推进
3. **回归验证**：≥1024px 视口下 GameView 完全不受影响
4. **PL 确认**：PL 确认 GameView 验收通过，批准进入 P0 其余页面

---

## P0 其余任务（GameView 验收通过后执行）

### TASK-MOB-006: DiscoverView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-006 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 DiscoverView 样式） |
| 关联验收项 | AC-MOB-005 |
| 验证方式 | 1. ≤767px 视口下内容列表单列全宽<br>2. TabBar「发现」高亮<br>3. 卡片/列表项触摸区域 ≥44px<br>4. **≥1024px 视口下 DiscoverView 视觉无变化** |
| 回滚方案 | 删除 `mobile.css` 中 DiscoverView 相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 DiscoverView 移动端样式
- 内容列表单列全宽
- 列表项 `min-height: 44px`
- 验证 TabBar「发现」高亮

---

### TASK-MOB-007: CharacterListView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-007 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 CharacterListView 样式） |
| 关联验收项 | AC-MOB-006 |
| 验证方式 | 1. ≤767px 视口下多列网格转为单列全宽<br>2. 每个角色卡片 ≥44px 可点击<br>3. 无横向滚动<br>4. **≥1024px 视口下 CharacterListView 视觉无变化** |
| 回滚方案 | 删除 `mobile.css` 中 CharacterListView 相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 CharacterListView 移动端样式
- 网格转单列 `grid-template-columns: 1fr`
- 角色卡片 `min-height: 44px`

---

### TASK-MOB-008: CharacterDetailView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-008 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 CharacterDetailView 样式） |
| 关联验收项 | AC-MOB-007 |
| 验证方式 | 1. ≤767px 视口下图文混排呈单列布局<br>2. 图片自适应宽度<br>3. 交互按钮 ≥44px<br>4. **≥1024px 视口下 CharacterDetailView 视觉无变化** |
| 回滚方案 | 删除 `mobile.css` 中 CharacterDetailView 相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 CharacterDetailView 移动端样式
- 单列布局
- 图片 `max-width: 100%`
- 交互按钮 `min-height: 44px`

---

### TASK-MOB-009: CommunityView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-009 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 CommunityView 样式） |
| 关联验收项 | AC-MOB-008 |
| 验证方式 | 1. ≤767px 视口下帖子列表单列全宽<br>2. TabBar「社区」高亮<br>3. 列表项 ≥44px<br>4. 评论/点赞交互正常<br>5. **≥1024px 视口下 CommunityView 视觉无变化** |
| 回滚方案 | 删除 `mobile.css` 中 CommunityView 相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 CommunityView 移动端样式
- 帖子列表单列全宽
- 列表项 `min-height: 44px`
- 验证 TabBar「社区」高亮
- 验证评论/点赞交互正常（CSS 不影响交互）

---

### TASK-MOB-010: Naive UI 组件覆盖 + 触摸目标检查

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-010 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 Naive UI 覆盖样式） |
| 关联验收项 | AC-MOB-014 |
| 验证方式 | 1. ≤767px 视口下所有按钮、链接、输入框 bounding box ≥44×44px<br>2. Naive UI 组件样式覆盖生效<br>3. **≥1024px 视口下所有 Naive UI 组件视觉无变化** |
| 回滚方案 | 删除 `mobile.css` 中 Naive UI 覆盖样式 |

**任务描述**：
- 在 `mobile.css` 中添加 Naive UI 组件覆盖样式：
  - `:deep(.n-button) { min-height: 44px; min-width: 44px; }`
  - `:deep(.n-input) { min-height: 44px; }`
  - `:deep(.n-card) { width: 100%; }`
  - 其他组件覆盖
- 验证所有交互元素 ≥44×44px

**CEO 约束执行（风险 R1 缓解）**：
- ⚠️ 如果 `:deep()` 方案对某个 Naive UI 组件不可行，**立即上报 PL**，标记为 Blocked
- ⚠️ 记录具体组件名、尝试方案、失败原因
- ⚠️ 不得硬啃超过 2 小时；超时即上报
- ⚠️ 备选方案：如 `:deep()` 不行，尝试 `:global()` 或组件级 `class` 覆盖

---

### P0 阶段验收检查点

完成以上 5 个任务后，进行 P0 全面验收：

1. **7 个 P0 页面**在 ≤767px 视口下全部可用
2. **TabBar** 导航正常，高亮正确
3. **PC 端回归** ≥1024px 视口完全不受影响（截图对比）
4. **触摸目标** 全部 ≥44×44px
5. **无横向滚动**
6. **Naive UI 覆盖** 无未解决的 Blocked 项

---

### TASK-MOB-031: HomeView 羁绊概览轮播图

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-031 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 HomeView 羁绊概览轮播图样式） |
| 关联验收项 | AC-MOB-039 |
| 验证方式 | 1. ≤767px 视口下羁绊概览显示为轮播图<br>2. 支持触摸滑动<br>3. 自动播放，鼠标移入暂停<br>4. 指示器显示当前位置<br>5. ≥768px 视口保持原有网格布局 |
| 回滚方案 | 删除 `mobile.css` 中 HomeView 羁绊概览轮播图相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 HomeView 羁绊概览轮播图样式
- 将 `.affection-grid` 改为轮播图布局
- 实现触摸滑动、自动播放、暂停逻辑
- 添加指示器
- PC 端保持原有 3 列网格布局

---

### TASK-MOB-032: HomeView 剧本列表轮播图

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-032 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 HomeView 剧本列表轮播图样式） |
| 关联验收项 | AC-MOB-040 |
| 验证方式 | 1. ≤767px 视口下剧本列表显示为轮播图<br>2. 支持触摸滑动<br>3. 自动播放，鼠标移入暂停<br>4. 指示器显示当前位置<br>5. ≥768px 视口保持原有网格布局 |
| 回滚方案 | 删除 `mobile.css` 中 HomeView 剧本列表轮播图相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 HomeView 剧本列表轮播图样式
- 将 `.script-grid` 改为轮播图布局
- 实现触摸滑动、自动播放、暂停逻辑
- 添加指示器
- PC 端保持原有 3 列网格布局

---

### TASK-MOB-033: DiscoverView 热门剧本轮播图

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-033 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 DiscoverView 热门剧本轮播图样式） |
| 关联验收项 | AC-MOB-041 |
| 验证方式 | 1. ≤767px 视口下热门剧本显示为轮播图<br>2. 支持触摸滑动<br>3. 自动播放，鼠标移入暂停<br>4. 指示器显示当前位置<br>5. ≥768px 视口保持原有水平滚动布局 |
| 回滚方案 | 删除 `mobile.css` 中 DiscoverView 热门剧本轮播图相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 DiscoverView 热门剧本轮播图样式
- 将 `.trending-scroll` 优化为轮播图布局
- 实现触摸滑动、自动播放、暂停逻辑
- 添加指示器
- PC 端保持原有水平滚动布局

---

### TASK-MOB-034: DiscoverView 推荐剧本轮播图

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-034 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 DiscoverView 推荐剧本轮播图样式） |
| 关联验收项 | AC-MOB-042 |
| 验证方式 | 1. ≤767px 视口下推荐剧本显示为轮播图<br>2. 支持触摸滑动<br>3. 自动播放，鼠标移入暂停<br>4. 指示器显示当前位置<br>5. ≥768px 视口保持原有网格布局 |
| 回滚方案 | 删除 `mobile.css` 中 DiscoverView 推荐剧本轮播图相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 DiscoverView 推荐剧本轮播图样式
- 将推荐剧本网格改为轮播图布局
- 实现触摸滑动、自动播放、暂停逻辑
- 添加指示器
- PC 端保持原有网格布局

---

### TASK-MOB-035: CharacterListView 角色网格轮播图

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-035 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 CharacterListView 角色网格轮播图样式） |
| 关联验收项 | AC-MOB-043 |
| 验证方式 | 1. ≤767px 视口下角色网格显示为轮播图<br>2. 支持触摸滑动<br>3. 自动播放，鼠标移入暂停<br>4. 指示器显示当前位置<br>5. ≥768px 视口保持原有网格布局 |
| 回滚方案 | 删除 `mobile.css` 中 CharacterListView 角色网格轮播图相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 CharacterListView 角色网格轮播图样式
- 将 `.character-grid` 改为轮播图布局
- 实现触摸滑动、自动播放、暂停逻辑
- 添加指示器
- PC 端保持原有网格布局

---

## P1 任务（18 个功能页面）

### TASK-MOB-011: 表单类页面适配（Login, Register, ForgotPassword, ResetPassword）

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-011 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加表单页面样式） |
| 关联验收项 | AC-MOB-016, AC-MOB-017, AC-MOB-032, AC-MOB-033 |
| 验证方式 | 1. 表单全宽，padding 16px<br>2. 输入框 ≥44px<br>3. 提交按钮 ≥44px 全宽<br>4. 无横向滚动<br>5. **≥1024px 视口下 4 个表单页视觉无变化** |
| 回滚方案 | 删除 `mobile.css` 中表单页面相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 4 个表单页面样式
- 统一模式：表单容器 `width: 100%; padding: 16px`
- 输入框 `width: 100%; min-height: 44px`
- 提交按钮 `width: 100%; min-height: 44px`

---

### TASK-MOB-012: OnboardingView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-012 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 OnboardingView 样式） |
| 关联验收项 | AC-MOB-018 |
| 验证方式 | 1. 步骤内容单列全宽<br>2. 下一步/跳过按钮 ≥44px<br>3. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 OnboardingView 相关样式 |

---

### TASK-MOB-013: ProfileView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-013 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 ProfileView 样式） |
| 关联验收项 | AC-MOB-019 |
| 验证方式 | 1. 用户信息单列显示<br>2. TabBar「我的」入口可达<br>3. 菜单项 ≥44px<br>4. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 ProfileView 相关样式 |

---

### TASK-MOB-014: SettingsView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-014 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 SettingsView 样式） |
| 关联验收项 | AC-MOB-020 |
| 验证方式 | 1. 设置项列表全宽单列<br>2. 每个设置项 ≥44px<br>3. 开关/选择器可正常操作<br>4. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 SettingsView 相关样式 |

---

### TASK-MOB-015: SaveManagerView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-015 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 SaveManagerView 样式） |
| 关联验收项 | AC-MOB-021 |
| 验证方式 | 1. 存档列表单列全宽<br>2. 操作按钮 ≥44px<br>3. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 SaveManagerView 相关样式 |

---

### TASK-MOB-016: ShardCenterView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-016 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 ShardCenterView 样式） |
| 关联验收项 | AC-MOB-022 |
| 验证方式 | 1. 碎片中心单列全宽<br>2. 购买按钮 ≥44px<br>3. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 ShardCenterView 相关样式 |

---

### TASK-MOB-017: AchievementView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-017 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 AchievementView 样式） |
| 关联验收项 | AC-MOB-023 |
| 验证方式 | 1. 成就网格转为单列或双列<br>2. 每个成就卡片 ≥44px 可点击<br>3. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 AchievementView 相关样式 |

---

### TASK-MOB-018: SubscriptionView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-018 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 SubscriptionView 样式） |
| 关联验收项 | AC-MOB-024 |
| 验证方式 | 1. 套餐卡片单列全宽<br>2. 订阅按钮 ≥44px<br>3. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 SubscriptionView 相关样式 |

---

### TASK-MOB-019: GalleryView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-019 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 GalleryView 样式） |
| 关联验收项 | AC-MOB-025 |
| 验证方式 | 1. 图片网格转为单列或双列<br>2. 图片自适应宽度<br>3. 点击图片可正常预览<br>4. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 GalleryView 相关样式 |

---

### TASK-MOB-020: GiftView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-020 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 GiftView 样式） |
| 关联验收项 | AC-MOB-026 |
| 验证方式 | 1. 礼物列表单列全宽<br>2. 送礼按钮 ≥44px<br>3. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 GiftView 相关样式 |

---

### TASK-MOB-021: ScriptDetailView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-021 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 ScriptDetailView 样式） |
| 关联验收项 | AC-MOB-027 |
| 验证方式 | 1. 剧本内容全宽可读<br>2. 开始游戏按钮 ≥44px<br>3. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 ScriptDetailView 相关样式 |

---

### TASK-MOB-022: EndingView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-022 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 EndingView 样式） |
| 关联验收项 | AC-MOB-028 |
| 验证方式 | 1. 结局内容单列全宽<br>2. 操作按钮 ≥44px<br>3. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 EndingView 相关样式 |

---

### TASK-MOB-023: RecapView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-023 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 RecapView 样式） |
| 关联验收项 | AC-MOB-029 |
| 验证方式 | 1. 剧情回顾内容单列全宽<br>2. 文字可读，图片自适应<br>3. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 RecapView 相关样式 |

---

### TASK-MOB-024: RouteMap 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-024 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 RouteMap 样式） |
| 关联验收项 | AC-MOB-030 |
| 验证方式 | 1. 节点图自适应宽度，无横向滚动<br>2. 节点可点击 ≥44px<br>3. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 RouteMap 相关样式 |

---

### TASK-MOB-025: FreeChatView 移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-025 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 FreeChatView 样式） |
| 关联验收项 | AC-MOB-031 |
| 验证方式 | 1. 聊天消息全宽显示<br>2. 输入框固定底部 ≥44px<br>3. 发送按钮 ≥44px<br>4. **≥1024px 视口下无变化** |
| 回滚方案 | 删除 `mobile.css` 中 FreeChatView 相关样式 |

---

### P1 阶段验收检查点

完成以上 15 个任务后，进行 P1 验收：

1. **18 个 P1 页面**在 ≤767px 视口下全部可用
2. **表单类页面**统一模式：全宽、padding 16px、输入框/按钮 ≥44px
3. **列表类页面**单列全宽，操作项 ≥44px
4. **内容类页面**全宽可读，交互按钮 ≥44px
5. **PC 端回归** ≥1024px 视口完全不受影响

---

## P2 任务（3 个辅助页面 + 公共组件 + 回归）

### TASK-MOB-026: P2 页面适配（ShareView, OAuthCallbackView, NotFoundView）

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-026 |
| 负责人 | fe |
| 优先级 | P2 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加 P2 页面样式） |
| 关联验收项 | AC-MOB-036, AC-MOB-037, AC-MOB-038 |
| 验证方式 | 1. ShareView 分享内容单列全宽，CTA 按钮 ≥44px<br>2. OAuthCallbackView 加载中居中，无横向滚动<br>3. NotFoundView 提示居中，返回按钮 ≥44px<br>4. **≥1024px 视口下 3 个页面视觉无变化** |
| 回滚方案 | 删除 `mobile.css` 中 P2 页面相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加 3 个 P2 页面样式
- ShareView：单列全宽，CTA 按钮 `min-height: 44px`
- OAuthCallbackView：加载中居中，无横向滚动
- NotFoundView：提示居中，返回按钮 `min-height: 44px`

---

### TASK-MOB-027: 公共组件移动端适配

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-027 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/styles/mobile.css`（添加公共组件样式） |
| 关联验收项 | AC-MOB-034, AC-MOB-035 |
| 验证方式 | 1. PaymentModal 转底部抽屉或全屏，支付按钮 ≥44px<br>2. DialogueBox、ChoicePanel、AudioPlayer 等组件布局正常，无溢出/错位/重叠<br>3. **≥1024px 视口下所有公共组件视觉无变化** |
| 回滚方案 | 删除 `mobile.css` 中公共组件相关样式 |

**任务描述**：
- 在 `mobile.css` 中添加公共组件移动端样式：
  - PaymentModal：转底部抽屉或全屏
  - DialogueBox：全宽，字号 ≥14px
  - ChoicePanel：按钮全宽单列，≥44px
  - AudioPlayer：控件 ≥44px
  - BalanceDisplay：文字可读
  - AffectionMeter/AffectionBar：进度条自适应
  - MemoryCard：全宽单列
  - TaskPanel：列表单列全宽
  - ScriptCard：全宽单列
  - EndingCard：全宽单列
- 验证所有组件无溢出/错位/重叠

---

### TASK-MOB-028: PC 端回归测试 + 最终验收

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-028 |
| 负责人 | fe |
| 优先级 | P0 |
| 允许写入范围 | 无（仅测试） |
| 关联验收项 | AC-MOB-012, AC-MOB-013, AC-MOB-014, AC-MOB-015 |
| 验证方式 | 1. ≥1024px 视口下所有 28 个页面视觉与适配前完全一致（截图对比）<br>2. `git diff frontend/src/styles/global.css` 为空<br>3. 所有交互元素 ≥44×44px<br>4. 所有页面无横向滚动条 |
| 回滚方案 | N/A（测试任务） |

**任务描述**：
- PC 端回归测试：≥1024px 视口下验证所有 28 个页面
- CSS 隔离检查：`git diff frontend/src/styles/global.css` 为空
- 触摸目标检查：所有按钮、链接、输入框 ≥44×44px
- 横向滚动检查：所有页面无横向滚动条

---

## 任务依赖关系（含 CEO 约束）

```
TASK-MOB-001 (mobile.css 基础)
    ↓
TASK-MOB-002 (TabBar 组件)
    ↓
TASK-MOB-003, TASK-MOB-004 (LandingView, HomeView)  [可并行]
    ↓
[Demo 验收 + 用户确认]
    ↓
TASK-MOB-005 (GameView)  ⚠️ 单独执行，不并行
    ↓
[GameView 验收 + PL 确认]
    ↓
TASK-MOB-0006 ~ TASK-MOB-009 (P0 其余 4 页面)  [可并行]
    ↓
TASK-MOB-010 (Naive UI 覆盖)  ⚠️ 遇阻即上报 PL
    ↓
[P0 全面验收]
    ↓
TASK-MOB-011 ~ TASK-MOB-025 (P1 页面)  [可按模块并行]
    ↓
[P1 验收]
    ↓
TASK-MOB-026, TASK-MOB-027 (P2 页面 + 公共组件)  [可并行]
    ↓
TASK-MOB-028 (PC 端回归 + 最终验收)
    ↓
[RELEASE_GATE]
```

---

## 任务统计

| 阶段 | 任务数 | 预估工时 | 备注 |
|------|--------|----------|------|
| Demo | 4 | 1 天 | mobile.css + TabBar + Landing + Home |
| GameView 单独 | 1 | 1 天 | ⚠️ 不与其他 P0 并行 |
| P0 其余 | 5 | 1-2 天 | 4 页面 + Naive UI 覆盖 |
| P1 | 15 | 3-4 天 | 18 个功能页面 |
| P2 | 3 | 1-2 天 | 3 辅助页面 + 公共组件 + 回归 |
| **合计** | **28** | **7-10 天** | |

---

## 验收追踪

| AC 编号 | 关联任务 | 覆盖状态 |
|---------|----------|----------|
| AC-MOB-001 | TASK-MOB-003 | not_covered |
| AC-MOB-002 | TASK-MOB-004 | not_covered |
| AC-MOB-003 | TASK-MOB-005 | not_covered |
| AC-MOB-004 | TASK-MOB-005 | not_covered |
| AC-MOB-005 | TASK-MOB-006 | not_covered |
| AC-MOB-006 | TASK-MOB-007 | not_covered |
| AC-MOB-007 | TASK-MOB-008 | not_covered |
| AC-MOB-008 | TASK-MOB-009 | not_covered |
| AC-MOB-009 | TASK-MOB-002 | not_covered |
| AC-MOB-010 | TASK-MOB-002 | not_covered |
| AC-MOB-011 | TASK-MOB-002 | not_covered |
| AC-MOB-012 | TASK-MOB-028 | not_covered |
| AC-MOB-013 | TASK-MOB-001, TASK-MOB-028 | not_covered |
| AC-MOB-014 | TASK-MOB-010, TASK-MOB-028 | not_covered |
| AC-MOB-015 | TASK-MOB-001, TASK-MOB-028 | not_covered |
| AC-MOB-016 | TASK-MOB-011 | not_covered |
| AC-MOB-017 | TASK-MOB-011 | not_covered |
| AC-MOB-018 | TASK-MOB-012 | not_covered |
| AC-MOB-019 | TASK-MOB-013 | not_covered |
| AC-MOB-020 | TASK-MOB-014 | not_covered |
| AC-MOB-021 | TASK-MOB-015 | not_covered |
| AC-MOB-022 | TASK-MOB-016 | not_covered |
| AC-MOB-023 | TASK-MOB-017 | not_covered |
| AC-MOB-024 | TASK-MOB-018 | not_covered |
| AC-MOB-025 | TASK-MOB-019 | not_covered |
| AC-MOB-026 | TASK-MOB-020 | not_covered |
| AC-MOB-027 | TASK-MOB-021 | not_covered |
| AC-MOB-028 | TASK-MOB-022 | not_covered |
| AC-MOB-029 | TASK-MOB-023 | not_covered |
| AC-MOB-030 | TASK-MOB-024 | not_covered |
| AC-MOB-031 | TASK-MOB-025 | not_covered |
| AC-MOB-032 | TASK-MOB-011 | not_covered |
| AC-MOB-033 | TASK-MOB-011 | not_covered |
| AC-MOB-034 | TASK-MOB-027 | not_covered |
| AC-MOB-035 | TASK-MOB-027 | not_covered |
| AC-MOB-036 | TASK-MOB-026 | not_covered |
| AC-MOB-037 | TASK-MOB-026 | not_covered |
| AC-MOB-038 | TASK-MOB-026 | not_covered |

## Implementation Tasks

| Task ID | Owner Agent | Requirement / AC | Excluded AC | Allowed Write Scope | Test Case Artifact | Verification | Rollback / Revert Plan | Status |
|---------|-------------|------------------|-------------|---------------------|-------------------|--------------|------------------------|--------|
| TASK-MOB-001 | fe | AC-MOB-013, AC-MOB-015 | 无 | `frontend/src/styles/mobile.css`（新建）, `frontend/src/main.ts`（仅添加 import） | `tests/e2e/mobile-basic.spec.ts` | 1. `git diff frontend/src/styles/global.css` 为空<br>2. `mobile.css` 存在且包含 `@media (max-width: 767px)`<br>3. 全局 `overflow-x: hidden` 生效<br>4. **≥1024px 视口下页面视觉无变化** | 删除 `mobile.css`，移除 `main.ts` 中的 import | Ready |
| TASK-MOB-002 | fe | AC-MOB-009, AC-MOB-010, AC-MOB-011 | 无 | `frontend/src/components/MobileTabBar.vue`（新建）, `frontend/src/App.vue`（仅添加组件引入）, `frontend/src/styles/mobile.css`（添加 TabBar 样式） | `tests/e2e/mobile-tabbar.spec.ts` | 1. ≤767px 视口下 TabBar 固定显示，包含 5 个入口<br>2. 点击 Tab 可正常导航<br>3. 当前 Tab 高亮<br>4. ≥1024px 视口下 TabBar 不显示<br>5. iOS 设备底部 safe-area 生效 | 删除 `MobileTabBar.vue`，移除 `App.vue` 中的组件引入 | Ready |
| TASK-MOB-003 | fe | AC-MOB-001 | 无 | `frontend/src/styles/mobile.css`（添加 LandingView 样式） | `tests/e2e/mobile-landing.spec.ts` | 1. ≤767px 视口下页面单列布局<br>2. 无横向滚动<br>3. CTA 按钮 ≥44px<br>4. 图片/视频自适应宽度<br>5. 文字 ≥14px | 删除 `mobile.css` 中 LandingView 相关样式 | Ready |
| TASK-MOB-004 | fe | AC-MOB-002 | 无 | `frontend/src/styles/mobile.css`（添加 HomeView 样式） | `tests/e2e/mobile-home.spec.ts` | 1. ≤767px 视口下卡片单列全宽<br>2. 卡片间距 12-16px<br>3. 底部 TabBar「首页」高亮<br>4. 无横向滚动<br>5. 无内容溢出/错位 | 删除 `mobile.css` 中 HomeView 相关样式 | Ready |
| TASK-MOB-005 | fe | AC-MOB-003, AC-MOB-004 | 无 | `frontend/src/styles/mobile.css`（添加 GameView 样式） | `tests/e2e/mobile-game.spec.ts` | 1. ≤767px 视口下对话区域全宽，字号 ≥14px<br>2. 选择面板按钮 ≥44px 全宽单列<br>3. 场景图片自适应宽度<br>4. TabBar 隐藏（沉浸模式）<br>5. 点击选项按钮能正常触发剧情推进 | 删除 `mobile.css` 中 GameView 相关样式 | Ready |
| TASK-MOB-006 | fe | AC-MOB-005 | 无 | `frontend/src/styles/mobile.css`（添加 DiscoverView 样式） | `tests/e2e/mobile-discover.spec.ts` | 1. ≤767px 视口下内容列表单列全宽<br>2. TabBar「发现」高亮<br>3. 卡片/列表项触摸区域 ≥44px | 删除 `mobile.css` 中 DiscoverView 相关样式 | Ready |
| TASK-MOB-007 | fe | AC-MOB-006 | 无 | `frontend/src/styles/mobile.css`（添加 CharacterListView 样式） | `tests/e2e/mobile-characters.spec.ts` | 1. ≤767px 视口下多列网格转为单列全宽<br>2. 每个角色卡片 ≥44px 可点击<br>3. 无横向滚动 | 删除 `mobile.css` 中 CharacterListView 相关样式 | Ready |
| TASK-MOB-008 | fe | AC-MOB-007 | 无 | `frontend/src/styles/mobile.css`（添加 CharacterDetailView 样式） | `tests/e2e/mobile-character-detail.spec.ts` | 1. ≤767px 视口下图文混排呈单列布局<br>2. 图片自适应宽度<br>3. 交互按钮 ≥44px | 删除 `mobile.css` 中 CharacterDetailView 相关样式 | Ready |
| TASK-MOB-009 | fe | AC-MOB-008 | 无 | `frontend/src/styles/mobile.css`（添加 CommunityView 样式） | `tests/e2e/mobile-community.spec.ts` | 1. ≤767px 视口下帖子列表单列全宽<br>2. TabBar「社区」高亮<br>3. 列表项 ≥44px<br>4. 评论/点赞交互正常 | 删除 `mobile.css` 中 CommunityView 相关样式 | Ready |
| TASK-MOB-010 | fe | AC-MOB-014 | 无 | `frontend/src/styles/mobile.css`（添加 Naive UI 覆盖样式） | `tests/e2e/mobile-touch-targets.spec.ts` | 1. ≤767px 视口下所有按钮、链接、输入框 bounding box ≥44×44px<br>2. Naive UI 组件样式覆盖生效 | 删除 `mobile.css` 中 Naive UI 覆盖样式 | Ready |
| TASK-MOB-011 | fe | AC-MOB-016, AC-MOB-017, AC-MOB-032, AC-MOB-033 | 无 | `frontend/src/styles/mobile.css`（添加表单页面样式） | `tests/e2e/mobile-forms.spec.ts` | 1. 表单全宽，padding 16px<br>2. 输入框 ≥44px<br>3. 提交按钮 ≥44px 全宽<br>4. 无横向滚动 | 删除 `mobile.css` 中表单页面相关样式 | Ready |
| TASK-MOB-012 | fe | AC-MOB-018 | 无 | `frontend/src/styles/mobile.css`（添加 OnboardingView 样式） | `tests/e2e/mobile-onboarding.spec.ts` | 1. 步骤内容单列全宽<br>2. 下一步/跳过按钮 ≥44px | 删除 `mobile.css` 中 OnboardingView 相关样式 | Ready |
| TASK-MOB-013 | fe | AC-MOB-019 | 无 | `frontend/src/styles/mobile.css`（添加 ProfileView 样式） | `tests/e2e/mobile-profile.spec.ts` | 1. 用户信息单列显示<br>2. TabBar「我的」入口可达<br>3. 菜单项 ≥44px | 删除 `mobile.css` 中 ProfileView 相关样式 | Ready |
| TASK-MOB-014 | fe | AC-MOB-020 | 无 | `frontend/src/styles/mobile.css`（添加 SettingsView 样式） | `tests/e2e/mobile-settings.spec.ts` | 1. 设置项列表全宽单列<br>2. 每个设置项 ≥44px<br>3. 开关/选择器可正常操作 | 删除 `mobile.css` 中 SettingsView 相关样式 | Ready |
| TASK-MOB-015 | fe | AC-MOB-021 | 无 | `frontend/src/styles/mobile.css`（添加 SaveManagerView 样式） | `tests/e2e/mobile-saves.spec.ts` | 1. 存档列表单列全宽<br>2. 操作按钮 ≥44px | 删除 `mobile.css` 中 SaveManagerView 相关样式 | Ready |
| TASK-MOB-016 | fe | AC-MOB-022 | 无 | `frontend/src/styles/mobile.css`（添加 ShardCenterView 样式） | `tests/e2e/mobile-shards.spec.ts` | 1. 碎片中心单列全宽<br>2. 购买按钮 ≥44px | 删除 `mobile.css` 中 ShardCenterView 相关样式 | Ready |
| TASK-MOB-017 | fe | AC-MOB-023 | 无 | `frontend/src/styles/mobile.css`（添加 AchievementView 样式） | `tests/e2e/mobile-achievements.spec.ts` | 1. 成就网格转为单列或双列<br>2. 每个成就卡片 ≥44px 可点击 | 删除 `mobile.css` 中 AchievementView 相关样式 | Ready |
| TASK-MOB-018 | fe | AC-MOB-024 | 无 | `frontend/src/styles/mobile.css`（添加 SubscriptionView 样式） | `tests/e2e/mobile-subscription.spec.ts` | 1. 套餐卡片单列全宽<br>2. 订阅按钮 ≥44px | 删除 `mobile.css` 中 SubscriptionView 相关样式 | Ready |
| TASK-MOB-019 | fe | AC-MOB-025 | 无 | `frontend/src/styles/mobile.css`（添加 GalleryView 样式） | `tests/e2e/mobile-gallery.spec.ts` | 1. 图片网格转为单列或双列<br>2. 图片自适应宽度<br>3. 点击图片可正常预览 | 删除 `mobile.css` 中 GalleryView 相关样式 | Ready |
| TASK-MOB-020 | fe | AC-MOB-026 | 无 | `frontend/src/styles/mobile.css`（添加 GiftView 样式） | `tests/e2e/mobile-gift.spec.ts` | 1. 礼物列表单列全宽<br>2. 送礼按钮 ≥44px | 删除 `mobile.css` 中 GiftView 相关样式 | Ready |
| TASK-MOB-021 | fe | AC-MOB-027 | 无 | `frontend/src/styles/mobile.css`（添加 ScriptDetailView 样式） | `tests/e2e/mobile-script-detail.spec.ts` | 1. 剧本内容全宽可读<br>2. 开始游戏按钮 ≥44px | 删除 `mobile.css` 中 ScriptDetailView 相关样式 | Ready |
| TASK-MOB-022 | fe | AC-MOB-028 | 无 | `frontend/src/styles/mobile.css`（添加 EndingView 样式） | `tests/e2e/mobile-ending.spec.ts` | 1. 结局内容单列全宽<br>2. 操作按钮 ≥44px | 删除 `mobile.css` 中 EndingView 相关样式 | Ready |
| TASK-MOB-023 | fe | AC-MOB-029 | 无 | `frontend/src/styles/mobile.css`（添加 RecapView 样式） | `tests/e2e/mobile-recap.spec.ts` | 1. 剧情回顾内容单列全宽<br>2. 文字可读，图片自适应 | 删除 `mobile.css` 中 RecapView 相关样式 | Ready |
| TASK-MOB-024 | fe | AC-MOB-030 | 无 | `frontend/src/styles/mobile.css`（添加 RouteMap 样式） | `tests/e2e/mobile-routemap.spec.ts` | 1. 节点图自适应宽度，无横向滚动<br>2. 节点可点击 ≥44px | 删除 `mobile.css` 中 RouteMap 相关样式 | Ready |
| TASK-MOB-025 | fe | AC-MOB-031 | 无 | `frontend/src/styles/mobile.css`（添加 FreeChatView 样式） | `tests/e2e/mobile-freechat.spec.ts` | 1. 聊天消息全宽显示<br>2. 输入框固定底部 ≥44px<br>3. 发送按钮 ≥44px | 删除 `mobile.css` 中 FreeChatView 相关样式 | Ready |
| TASK-MOB-026 | fe | AC-MOB-032 | 无 | `frontend/src/styles/mobile.css`（添加 ForgotPasswordView 样式） | `tests/e2e/mobile-forgot-password.spec.ts` | 1. 表单全宽，padding 16px<br>2. 输入框和提交按钮 ≥44px | 删除 `mobile.css` 中 ForgotPasswordView 相关样式 | Ready |
| TASK-MOB-027 | fe | AC-MOB-033 | 无 | `frontend/src/styles/mobile.css`（添加 ResetPasswordView 样式） | `tests/e2e/mobile-reset-password.spec.ts` | 1. 表单全宽，padding 16px<br>2. 输入框和提交按钮 ≥44px | 删除 `mobile.css` 中 ResetPasswordView 相关样式 | Ready |
| TASK-MOB-028 | fe | AC-MOB-036, AC-MOB-037, AC-MOB-038 | 无 | `frontend/src/styles/mobile.css`（添加 P2 页面样式） | `tests/e2e/mobile-p2-pages.spec.ts` | 1. ShareView 分享内容单列全宽，CTA 按钮 ≥44px<br>2. OAuthCallbackView 加载中居中，无横向滚动<br>3. NotFoundView 提示居中，返回按钮 ≥44px | 删除 `mobile.css` 中 P2 页面相关样式 | Ready |
| TASK-MOB-029 | fe | AC-MOB-034, AC-MOB-035 | 无 | `frontend/src/styles/mobile.css`（添加公共组件样式） | `tests/e2e/mobile-components.spec.ts` | 1. PaymentModal 转底部抽屉或全屏，支付按钮 ≥44px<br>2. DialogueBox、ChoicePanel、AudioPlayer 等组件布局正常，无溢出/错位/重叠 | 删除 `mobile.css` 中公共组件相关样式 | Ready |
| TASK-MOB-030 | fe | AC-MOB-012 | 无 | 无（仅测试） | `tests/e2e/mobile-pc-regression.spec.ts` | 1. ≥1024px 视口下所有页面视觉与适配前完全一致<br>2. `global.css` git diff 为空<br>3. 所有交互元素 ≥44×44px<br>4. 所有页面无横向滚动 | N/A（测试任务） | Ready |
