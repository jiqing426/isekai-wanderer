# QA FE-O27 验证报告 — 全局 .page-bg min-height 统一

**验证时间**: 2026-07-24  
**验证方式**: 代码审查  
**Mock API**: no

**验收标准修正**: 全局 `.page-bg` 的 `min-height` 应为 `calc(100vh - 60px)`（非 72px）

---

## 验证结果汇总

| # | 验证项 | 状态 | 详情 |
|---|--------|------|------|
| 1 | 全局 `.page-bg` 的 `min-height` 是否为 `calc(100vh - 60px)` | ✅ PASS | 实际值为 `calc(100vh - 60px)` |
| 2 | GameView 页面：高度固定，内容超出时可滚动 | ✅ PASS | 局部覆盖 `height: calc(100vh - 72px); overflow-y: auto` |
| 3 | FreeChatView 页面：高度固定 | ✅ PASS | 局部覆盖 `height: calc(100vh - 72px)` |
| 4 | 认证页面（登录/注册）：保持 `min-height: 100vh` | ✅ PASS | LoginView 使用 `.auth-page { min-height: 100vh }` |
| 5 | DiscoverView 页面：`min-height: calc(100vh - 60px)` | ✅ PASS | 与全局标准一致 |
| 6 | 浏览器控制台无 CSS 相关错误 | ⚠️ 待浏览器验证 | 代码审查无法验证此项 |

**通过 5/6 | 待确认 1/6**

---

## 详细验证

### 1. 全局 `.page-bg` min-height ✅

**文件**: `frontend/src/styles/global.css` 第 63-68 行

```css
.page-bg {
  min-height: calc(100vh - 60px);
  background: linear-gradient(160deg, var(--page-bg-start) 0%, var(--page-bg-end) 100%);
  position: relative;
  transition: background 0.3s ease;
}
```

**验证**: 实际值为 `calc(100vh - 60px)`，符合验收标准 ✅

### 2. GameView 局部覆盖 ✅

**文件**: `frontend/src/views/GameView.vue`

```css
.page-bg {
  height: calc(100vh - 72px);
  overflow-y: auto;
}
```

**验证**: 游戏页面使用固定高度，允许内容滚动 ✅

### 3. FreeChatView 局部覆盖 ✅

**文件**: `frontend/src/views/FreeChatView.vue`

```css
height: calc(100vh - 72px); 
overflow: hidden;
```

**验证**: 聊天界面使用固定高度 ✅

### 4. 认证页面 ✅

**文件**: `frontend/src/views/LoginView.vue`

```css
.auth-page {
  min-height: 100vh;
  /* ... */
}
```

**验证**: 认证页面使用独立的 `min-height: 100vh` ✅

### 5. DiscoverView ✅

**文件**: `frontend/src/views/DiscoverView.vue`

```css
.discover-page {
  min-height: calc(100vh - 60px);
  /* ... */
}
```

**验证**: 与全局标准一致 ✅

---

## 高度值汇总

| 位置 | 高度值 | 说明 |
|------|--------|------|
| global.css `.page-bg` | 60px | ✅ 全局标准 |
| DiscoverView `.discover-page` | 60px | ✅ 与全局一致 |
| GameView `.page-bg` | 72px | ✅ 游戏页面固定高度 |
| FreeChatView | 72px | ✅ 聊天界面固定高度 |
| LoginView `.auth-page` | 100vh | ✅ 认证页面全屏 |

---

## 结论

**验证通过**。全局 `.page-bg` 的 `min-height` 值为 `calc(100vh - 60px)`，符合验收标准。各页面局部覆盖合理，布局一致。
