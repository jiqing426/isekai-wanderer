# 🚨 导航栏重复渲染 Bug 报告

**Bug ID**: BUG-NAV-001  
**优先级**: P0 - 高  
**报告时间**: 2026-07-24T11:30:00Z  
**报告人**: CEO（通过 PL 转达）  
**负责人**: FE (Cat01-fe)

## 问题描述

老大反馈：异世界漫游项目导航栏出现异常——**左边也出现了导航栏**，不应该出现的地方出现了。

## 排查结果（PL 已完成代码审查）

### 发现的 3 个核心问题

#### 问题 1：BottomTabBar 缺少桌面端隐藏响应式断点

**位置**: `frontend/src/components/BottomTabBar.vue`

**现状**:
```css
@media (min-width: 769px) {
  .bottom-tabbar { display: none; }
}
```

**问题**: 断点设置为 `769px`，但 AppHeader 的断点是 `768px`，存在边界冲突。

**修复要求**: 统一断点为 `768px`，确保桌面端 BottomTabBar 完全隐藏。

```css
@media (min-width: 768px) {
  .bottom-tabbar { display: none !important; }
}
```

---

#### 问题 2：BottomTabBar Tab 项与设计稿不符

**位置**: `frontend/src/components/BottomTabBar.vue`

**现状**:
```typescript
const tabs = [
  { route: '/home', icon: '🏠', label: '首页' },
  { route: '/discover', icon: '🧭', label: '发现' },
  { route: '/game', icon: '🎮', label: '游戏' },      // ❌ 不应存在
  { route: '/saves', icon: '💾', label: '存档' },     // ❌ 不应存在
  { route: '/profile', icon: '👤', label: '我的' },
];
```

**设计稿要求** (CR-003 D-007):
> 底部 Tab Bar 从 [首页/社区/画廊/我的] 调整为 **[首页/发现/角色/我的]**

**修复要求**: 更新 tabs 数组为设计稿要求：
```typescript
const tabs = [
  { route: '/home', icon: '🏠', label: '首页' },
  { route: '/discover', icon: '🧭', label: '发现' },
  { route: '/characters', icon: '👥', label: '角色' },
  { route: '/profile', icon: '👤', label: '我的' },
];
```

---

#### 问题 3：AppHeader 移动端 Drawer 放置位置错误

**位置**: `frontend/src/components/AppHeader.vue`

**现状**:
```vue
<n-drawer v-model:show="showMobileMenu" placement="right" :width="280">
```

**问题**: 
- Drawer 放在 `right`（右侧），但用户反馈"左边也出现了导航栏"
- 可能是因为 Drawer 在移动端显示时，从右侧滑入造成视觉混乱
- 或者在某些断点下，Drawer 被错误地渲染为左侧固定导航

**修复要求**: 
1. 确认 Drawer 只在移动端（`max-width: 768px`）显示
2. 确保 Drawer 从右侧滑入，不影响左侧布局
3. 添加 CSS 确保桌面端不渲染 Drawer：
```css
@media (min-width: 768px) {
  .mobile-menu-btn { display: none !important; }
  /* Drawer 自动不显示，因为 v-if 控制 */
}
```

---

## 修复验证要求

### 1. 桌面端（≥768px）
- [ ] 只显示顶部 AppHeader
- [ ] 不显示底部 TabBar
- [ ] 不显示左侧/右侧 Drawer
- [ ] 导航栏只在顶部

### 2. 移动端（<768px）
- [ ] 显示顶部 AppHeader（简化版，带汉堡菜单）
- [ ] 显示底部 TabBar（4 个 Tab：首页/发现/角色/我的）
- [ ] 点击汉堡菜单从右侧滑出 Drawer
- [ ] 不显示左侧导航

### 3. 响应式断点一致性
- [ ] 所有断点统一为 `768px`
- [ ] 无边界冲突（`768px` vs `769px`）

---

## 影响范围

- **页面**: 所有页面（App.vue 根组件）
- **组件**: AppHeader, BottomTabBar
- **用户体验**: 导航混乱，影响所有用户
- **阻塞**: 否（功能可用，但体验差）

---

## 修复时间要求

- **优先级**: P0 - 立即修复
- **预计工时**: 1-2 小时
- **Deadline**: 2026-07-24 EOD

---

## 验收标准

1. 桌面端只有顶部导航
2. 移动端有顶部 + 底部导航
3. 无左/右侧固定导航栏
4. Tab 项与设计稿一致
5. 响应式断点无冲突
6. Playwright 导航测试通过
