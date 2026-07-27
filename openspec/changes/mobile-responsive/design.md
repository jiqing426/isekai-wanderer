# Design — CR-004 移动端适配

| 项 | 内容 |
| --- | --- |
| 变更 ID | CR-004 |
| 变更名称 | mobile-responsive |
| 设计状态 | DESIGN in-progress |
| 设计负责人 | sa (Architect) |
| 创建时间 | 2026-07-19 |
| 前置条件 | REQ_GATE passed (38 AC, 0 阻塞 Q) |

---

## 1. 整体技术方案

### 1.1 核心原则

1. **零改动 PC 端**：所有移动端样式通过 `@media (max-width: 767px)` 隔离，≥1024px 视口完全不受影响
2. **纯 CSS 层改动**：不修改任何业务逻辑、API 调用、数据层、路由
3. **新建 mobile.css**：所有移动端样式集中管理，不动 `global.css`
4. **触摸友好**：所有交互元素 ≥44px（Apple HIG 推荐最小触摸目标）
5. **单列布局**：移动端强制单列，无横向滚动

### 1.2 技术栈

- **CSS 媒体查询**：`@media (max-width: 767px)`
- **Vue 3 组件**：新增 `MobileTabBar.vue`（仅移动端显示）
- **Naive UI 覆盖**：使用 `:deep()` 选择器覆盖组件库样式
- **iOS 安全区域**：`env(safe-area-inset-bottom)` + `viewport-fit=cover`

### 1.3 文件结构

```
frontend/src/
├── styles/
│   ├── global.css              # 不修改
│   ├── mobile.css              # 新增：所有移动端样式
│   └── theme.ts                # 不修改
├── components/
│   ├── MobileTabBar.vue        # 新增：底部 TabBar 组件
│   └── ... (其他组件不修改)
└── views/
    └── ... (28 个页面不修改业务逻辑)
```

### 1.4 样式加载策略

在 `frontend/src/main.ts` 中按顺序加载：

```ts
import './styles/global.css';
import './styles/mobile.css';  // 新增
```

`mobile.css` 内所有规则都在 `@media (max-width: 767px)` 内，PC 端自动忽略。

---

## 2. mobile.css 架构设计

### 2.1 文件组织

```css
/* mobile.css 结构 */

/* ========================================
   Section 1: Global Resets & Base Styles
   ======================================== */
@media (max-width: 767px) {
  html, body {
    overflow-x: hidden;
    /* 防止横向滚动 */
  }
  
  /* 全局单列布局 */
  .page-bg {
    padding: 12px;
  }
}

/* ========================================
   Section 2: Layout Utilities
   ======================================== */
@media (max-width: 767px) {
  .mobile-full-width {
    width: 100%;
    max-width: 100%;
  }
  
  .mobile-single-column {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
}

/* ========================================
   Section 3: Naive UI Component Overrides
   ======================================== */
@media (max-width: 767px) {
  /* 按钮最小触摸目标 */
  :deep(.n-button) {
    min-height: 44px;
    min-width: 44px;
  }
  
  /* 输入框高度 */
  :deep(.n-input) {
    min-height: 44px;
  }
  
  /* 弹窗转底部抽屉 */
  :deep(.n-modal) {
    /* 见 Section 3.1 */
  }
}

/* ========================================
   Section 4: TabBar Styles
   ======================================== */
@media (max-width: 767px) {
  .mobile-tabbar {
    /* 见 Section 5 */
  }
}

/* ========================================
   Section 5: Page-Specific Styles
   ======================================== */

/* P0 Pages */
@media (max-width: 767px) {
  .landing-view { /* ... */ }
  .home-view { /* ... */ }
  .game-view { /* ... */ }
  .discover-view { /* ... */ }
  .character-list-view { /* ... */ }
  .character-detail-view { /* ... */ }
  .community-view { /* ... */ }
}

/* P1 Pages */
@media (max-width: 767px) {
  .login-view { /* ... */ }
  .register-view { /* ... */ }
  /* ... 18 pages */
}

/* P2 Pages */
@media (max-width: 767px) {
  .share-view { /* ... */ }
  .oauth-callback-view { /* ... */ }
  .not-found-view { /* ... */ }
}

/* ========================================
   Section 6: iOS Safe Area
   ======================================== */
@media (max-width: 767px) {
  @supports (padding-bottom: env(safe-area-inset-bottom)) {
    .mobile-tabbar,
    .fixed-bottom-element {
      padding-bottom: env(safe-area-inset-bottom);
    }
  }
}
```

### 2.2 Naive UI 组件覆盖策略

| 组件 | 覆盖目标 | 方法 |
|------|----------|------|
| `n-button` | 最小高度 44px | `:deep(.n-button) { min-height: 44px; }` |
| `n-input` | 最小高度 44px | `:deep(.n-input) { min-height: 44px; }` |
| `n-modal` | 转底部抽屉 | `:deep(.n-modal) { align-items: flex-end; }` + 内容区 `border-radius: 16px 16px 0 0` |
| `n-card` | 全宽单列 | `:deep(.n-card) { width: 100%; }` |
| `n-data-table` | 转卡片列表 | 隐藏表格，显示卡片视图（需组件内条件渲染） |
| `n-tabs` | 全宽标签 | `:deep(.n-tab) { flex: 1; }` |
| `n-select` | 全宽下拉 | `:deep(.n-select) { width: 100%; }` |

**注意**：部分组件（如 `n-data-table`）可能需要组件内部条件渲染配合，但本 CR 不涉及业务逻辑改动，仅 CSS 覆盖。对于无法纯 CSS 解决的组件，标记为"已知限制"并在验收中说明。

---

## 3. 底部 TabBar 组件设计

### 3.1 组件定义

```vue
<!-- src/components/MobileTabBar.vue -->
<template>
  <div class="mobile-tabbar" v-if="isVisible">
    <div 
      v-for="tab in tabs" 
      :key="tab.route"
      class="tabbar-item"
      :class="{ active: currentRoute === tab.route }"
      @click="navigateTo(tab.route)"
    >
      <div class="tab-icon">{{ tab.icon }}</div>
      <div class="tab-label">{{ tab.label }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const tabs = [
  { route: '/home', icon: '🏠', label: '首页' },
  { route: '/discover', icon: '🔍', label: '发现' },
  { route: '/game', icon: '🎮', label: '游戏' },
  { route: '/community', icon: '👥', label: '社区' },
  { route: '/profile', icon: '👤', label: '我的' },
];

const currentRoute = computed(() => route.path);

// GameView 隐藏 TabBar（沉浸模式）
const isVisible = computed(() => {
  return !route.path.startsWith('/game/') && route.path !== '/game';
});

const navigateTo = (route: string) => {
  router.push(route);
};
</script>

<style scoped>
/* 样式写在 mobile.css，这里只写组件内部结构 */
</style>
```

### 3.2 TabBar 样式（在 mobile.css 中）

```css
@media (max-width: 767px) {
  .mobile-tabbar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 56px;
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-around;
    align-items: center;
    z-index: 1000;
    padding-bottom: env(safe-area-inset-bottom);
  }
  
  .tabbar-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 44px;
    min-height: 44px;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .tabbar-item.active {
    color: var(--brand-primary);
  }
  
  .tab-icon {
    font-size: 20px;
    margin-bottom: 2px;
  }
  
  .tab-label {
    font-size: 12px;
  }
}

/* PC 端隐藏 */
@media (min-width: 1024px) {
  .mobile-tabbar {
    display: none;
  }
}
```

### 3.3 集成方式

在 `App.vue` 或主布局组件中引入：

```vue
<template>
  <div id="app">
    <AppHeader />
    <router-view />
    <MobileTabBar />  <!-- 新增 -->
  </div>
</template>

<script setup>
import MobileTabBar from '@/components/MobileTabBar.vue';
</script>
```

---

## 4. 各页面适配方案

### 4.1 P0 页面（7 个核心页面）

#### LandingView
- **现状**：多列布局，CTA 按钮较小
- **适配**：
  - 单列全宽布局
  - CTA 按钮 `width: 100%; min-height: 44px`
  - 图片/视频 `max-width: 100%; height: auto`
  - 文字 `font-size: ≥14px`

#### HomeView
- **现状**：多卡片网格布局
- **适配**：
  - 卡片单列全宽 `width: 100%`
  - 卡片间距 `gap: 12-16px`
  - 底部 TabBar「首页」高亮
  - 底部预留 TabBar 高度 `padding-bottom: 72px`

#### GameView
- **现状**：复杂游戏界面（691 行）
- **适配**：
  - 对话区域全宽 `width: 100%`
  - 选择面板按钮单列全宽 `min-height: 44px`
  - 场景图片 `max-width: 100%`
  - **隐藏 TabBar**（沉浸模式）
  - 字号 `≥14px`

#### DiscoverView
- **现状**：内容列表/网格
- **适配**：
  - 单列全宽布局
  - 列表项 `min-height: 44px`
  - 底部 TabBar「发现」高亮

#### CharacterListView
- **现状**：多列网格
- **适配**：
  - 单列全宽 `grid-template-columns: 1fr`
  - 角色卡片 `min-height: 44px`，可点击

#### CharacterDetailView
- **现状**：图文混排
- **适配**：
  - 单列布局
  - 图片 `max-width: 100%`
  - 交互按钮 `min-height: 44px`

#### CommunityView
- **现状**：帖子列表
- **适配**：
  - 单列全宽
  - 列表项 `min-height: 44px`
  - 底部 TabBar「社区」高亮

### 4.2 P1 页面（18 个功能页面）

#### 表单类页面（Login, Register, ForgotPassword, ResetPassword）
- **统一模式**：
  - 表单容器 `width: 100%; padding: 16px`
  - 输入框 `width: 100%; min-height: 44px`
  - 提交按钮 `width: 100%; min-height: 44px`

#### 列表类页面（Profile, Settings, SaveManager, ShardCenter, Achievement, Gallery, Gift）
- **统一模式**：
  - 列表单列全宽
  - 列表项 `min-height: 44px`
  - 操作按钮 `min-height: 44px`

#### 内容类页面（Onboarding, Subscription, ScriptDetail, Ending, Recap, RouteMap, FreeChat）
- **Onboarding**：步骤单列全宽，按钮 `≥44px`
- **Subscription**：套餐卡片单列全宽，订阅按钮 `≥44px`
- **ScriptDetail**：内容全宽可读，开始游戏按钮 `≥44px`
- **Ending**：内容单列全宽，操作按钮 `≥44px`
- **Recap**：内容单列全宽，图片自适应
- **RouteMap**：节点图自适应宽度，无横向滚动，节点 `≥44px`
- **FreeChat**：聊天消息全宽，输入框固定底部 `≥44px`，发送按钮 `≥44px`

### 4.3 P2 页面（3 个辅助页面）

#### ShareView
- 分享内容单列全宽
- 文字可读，图片自适应
- CTA 按钮 `≥44px`

#### OAuthCallbackView
- 加载中状态居中显示
- 无横向滚动

#### NotFoundView
- 提示信息单列居中
- 返回首页按钮 `≥44px`

---

## 5. iOS 安全区域处理

### 5.1 Viewport Meta

确保 `index.html` 中有：

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
```

### 5.2 Safe Area CSS

```css
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .mobile-tabbar {
    padding-bottom: env(safe-area-inset-bottom);
  }
  
  .fixed-bottom-element {
    padding-bottom: env(safe-area-inset-bottom);
  }
  
  /* 页面内容预留 TabBar + 安全区域高度 */
  .page-with-tabbar {
    padding-bottom: calc(56px + env(safe-area-inset-bottom));
  }
}
```

### 5.3 测试覆盖

- iOS Safari（iPhone X 及以上）
- 验证 TabBar 不被 Home Indicator 遮挡
- 验证页面底部内容不被 TabBar 遮挡

---

## 6. Runtime Contract

### 6.1 前端入口

| 环境 | URL | 说明 |
|------|-----|------|
| Dev | `http://localhost:8081` | Vite dev server |
| Prod | `https://isekai-wanderer.example.com` | Nginx 静态资源 |

### 6.2 后端地址

| 环境 | URL | 说明 |
|------|-----|------|
| Dev | `http://localhost:8000` | Uvicorn |
| Prod | `https://isekai-wanderer.example.com:8000` | Docker 内部 |

### 6.3 API Base Path

```
/api/v1
```

### 6.4 Vite Proxy Target

```ts
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### 6.5 Health Endpoint

```bash
curl -f http://localhost:8000/api/v1/health
# Response: {"status": "ok", "version": "1.0.0"}
```

### 6.6 Delivery E2E Command

```bash
docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health
```

### 6.7 Browser E2E Command

```bash
APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-responsive.spec.ts --headed --trace on
```

### 6.8 Browser E2E User Actions

| 动作 | AC | 描述 |
|------|-----|------|
| 移动端落地页访问 | AC-MOB-001 | ≤767px 视口访问 `/`，验证单列布局、CTA 按钮 ≥44px、无横向滚动 |
| 移动端主页访问 | AC-MOB-002 | ≤767px 视口访问 `/home`，验证卡片单列全宽、TabBar「首页」高亮 |
| 移动端游戏进入 | AC-MOB-003, AC-MOB-004 | ≤767px 视口进入游戏，验证对话全宽、选择按钮 ≥44px、TabBar 隐藏、点击选项触发剧情 |
| 移动端发现页 | AC-MOB-005 | ≤767px 视口访问 `/discover`，验证列表单列全宽、TabBar「发现」高亮 |
| 移动端角色列表 | AC-MOB-006 | ≤767px 视口访问 `/characters`，验证网格转单列、角色卡片可点击 |
| 移动端角色详情 | AC-MOB-007 | ≤767px 视口访问 `/characters/:id`，验证图文单列、按钮 ≥44px |
| 移动端社区 | AC-MOB-008 | ≤767px 视口访问 `/community`，验证帖子列表单列、TabBar「社区」高亮 |
| TabBar 导航 | AC-MOB-009, AC-MOB-010 | ≤767px 验证 TabBar 显示、5 入口导航、当前 Tab 高亮；≥1024px 验证 TabBar 不显示 |
| iOS 安全区域 | AC-MOB-011 | iOS 设备验证 TabBar 底部 safe-area-inset-bottom |
| PC 端回归 | AC-MOB-012 | ≥1024px 视口验证所有页面视觉与适配前一致 |
| 横向滚动检查 | AC-MOB-013 | ≤767px 视口验证所有页面无横向滚动条 |
| 触摸目标检查 | AC-MOB-014 | ≤767px 视口验证所有按钮、链接、输入框 ≥44×44px |
| CSS 隔离检查 | AC-MOB-015 | 验证 `global.css` 未被修改（git diff 为空） |

### 6.9 API Contract Doc

```
docs/api/api.md
```

### 6.10 Database Contract Doc

```
docs/database/database.md
```

### 6.11 Persistence Contract

```
PostgreSQL (主数据) + pgvector (向量) + Redis (缓存/限流/会话)
```

### 6.12 Mock Policy

```
no mock API for Delivery E2E / Release evidence;
mock only for IPaymentProvider/ISubscriptionProvider/IOAuthProvider/MockEmailService/MockDiscordService implementations
```

---

## 7. Document Sync

| 目标文档 | 同步状态 | 说明 |
|----------|----------|------|
| `docs/architecture/architecture.md` | Not Required | 本 CR 为纯 CSS 层改动，不涉及架构变化 |
| `docs/api/api.md` | Not Required | 本 CR 不涉及 API 变化 |
| `docs/database/database.md` | Not Required | 本 CR 不涉及数据模型变化 |
| `docs/security/security.md` | Not Required | 本 CR 不涉及安全边界变化 |
| `docs/decisions/decisions.md` | Not Required | 本 CR 无不可逆技术决策 |
| `docs/runtime/runtime-contract.md` | Synced | 已更新 Browser E2E Command 和 User Actions |

---

## 8. 风险与缓解

| # | 风险 | 影响 | 缓解 |
|---|------|------|------|
| R1 | Naive UI 组件自带响应式逻辑可能冲突 | 样式覆盖不生效 | 使用 `:deep()` 覆盖，逐个组件验证；无法纯 CSS 解决的标记为"已知限制" |
| R2 | GameView 复杂度高（691 行） | 适配难度大 | 单独分配任务，充分测试；优先保证核心交互（对话、选择） |
| R3 | iOS 安全区域适配 | 底部内容被遮挡 | `env(safe-area-inset-bottom)` + `viewport-fit=cover` |
| R4 | 移动端触摸事件与 PC 端鼠标事件差异 | 交互异常 | 仅改 CSS，不改 JS 逻辑；依赖浏览器原生触摸支持 |
| R5 | 部分 Naive UI 组件无法纯 CSS 适配 | 体验降级 | 标记为"已知限制"，后续 CR 处理；本 CR 优先保证 P0 页面核心功能 |

---

## 9. 设计落点追踪

| AC 编号 | 设计落点 |
|---------|----------|
| AC-MOB-001 ~ AC-MOB-015 | `mobile.css` + `MobileTabBar.vue` + 各页面 CSS 覆盖 |
| AC-MOB-016 ~ AC-MOB-033 | 各 P1 页面 CSS 覆盖 |
| AC-MOB-034 ~ AC-MOB-035 | 公共组件 CSS 覆盖 |
| AC-MOB-036 ~ AC-MOB-038 | P2 页面 CSS 覆盖 |

---

## 10. 待确认事项

无。所有技术选型均为 CSS 层实现，不涉及新依赖、不改变架构、不影响 API/数据/安全。

---

## Overview

- 为 28 个前端页面 + 22 个公共组件增加移动端（≤767px）CSS 适配
- 零改动 PC 端（≥1024px），纯 CSS 层改动，不动业务逻辑
- 新建 mobile.css 集中管理所有移动端样式
- 新增底部 TabBar 组件（5 入口：首页/发现/游戏/社区/我的）
- Demo 先行：LandingView + HomeView → 用户确认 → P0 → P1 → P2

## Technical Approach

- 使用 `@media (max-width: 767px)` 隔离移动端样式
- 新建 `src/styles/mobile.css`，在 `main.ts` 中 import
- 新增 `MobileTabBar.vue` 组件，仅移动端显示
- Naive UI 组件使用 `:deep()` 覆盖样式
- iOS 安全区域使用 `env(safe-area-inset-bottom)` + `viewport-fit=cover`
- 布局转换：多列网格→单列全宽，弹窗→底部抽屉
- 触摸目标：所有交互元素 ≥44px

## Technology Decisions

| 选型项 | 选择 | 状态 | 确认依据 |
|--------|------|------|----------|
| CSS 方案 | `@media (max-width: 767px)` | Accepted | 人工确认：用户已确认 5 项全部通过 |
| 组件库覆盖 | `:deep()` 选择器 | Accepted | 人工确认：CEO 已 INIT 通过 |
| TabBar 实现 | Vue 3 组件 + CSS | Accepted | 人工确认：PL 已确认 |
| iOS 安全区域 | `env(safe-area-inset-bottom)` | Accepted | 人工确认：PL 已确认 |
| 新增依赖 | Not Required | Not Required | 纯 CSS 改动，不引入新包 |

## Document Sync

| 目标文档 | 状态 | 说明 |
|----------|------|------|
| `docs/architecture/architecture.md` | Not Required | 纯 CSS 改动，不涉及架构变化 |
| `docs/api/api.md` | Not Required | 不涉及 API 变化 |
| `docs/database/database.md` | Not Required | 不涉及数据模型变化 |
| `docs/runtime/runtime-contract.md` | Synced | design.md 已包含 Runtime Contract |
| `docs/security/security.md` | Not Required | 纯 CSS 改动，不涉及安全边界变化 |
| `docs/decisions/decisions.md` | Not Required | 无不可逆技术决策 |
