# CR-004 测试报告

> 变更 ID：CR-004
> 变更名称：mobile-responsive
> 测试负责人：qa
> 测试时间：2026-07-21 11:30
> 状态：**🔴 FAILED — 11 项失败**

---

## 0. 执行摘要

| 类别 | 通过 | 失败 | 总计 |
|------|------|------|------|
| Mobile E2E (--project=mobile) | 11 | 9 | 20 |
| PC 回归 (--project=chromium) | 5 | 2 | 7 |
| **合计** | **16** | **11** | **27** |

**结论**：🔴 测试未通过，存在 11 项失败，需 FE 修复后重新验证。

---

## 1. Delivery E2E / Runtime Smoke

| 任务 | 命令 | 前端入口 | 后端地址 | API/Proxy | Mock API | 结果 |
|------|------|----------|----------|-----------|----------|------|
| 首页可达 | `curl -sf http://localhost:8081/` | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | ✅ HTTP 200 |
| 健康检查 | `curl -sf http://localhost:8000/api/v1/health` | N/A | http://localhost:8000 | /api/v1/health | no | ✅ HTTP 200 |

**Delivery E2E 结论**：✅ 服务层面正常，前端入口可达后端。

---

## 2. Browser Interaction E2E — Mobile (--project=mobile, 390×844)

### 2.1 通过项 (11/20)

| 测试文件 | 测试用例 | 覆盖 AC | 结果 |
|----------|----------|---------|------|
| mobile-basic.spec.ts | AC-MOB-013: 页面无横向滚动 | AC-MOB-013 | ✅ |
| mobile-basic.spec.ts | AC-MOB-013: 落地页无横向滚动 | AC-MOB-013 | ✅ |
| mobile-basic.spec.ts | AC-MOB-013: 主页无横向滚动 | AC-MOB-013 | ✅ |
| mobile-landing.spec.ts | AC-MOB-001: LandingView 单列布局 | AC-MOB-001 | ✅ |
| mobile-landing.spec.ts | AC-MOB-001: CTA 按钮 >= 44px | AC-MOB-001 | ✅ |
| mobile-landing.spec.ts | AC-MOB-001: LandingView 无横向滚动 | AC-MOB-001 | ✅ |
| mobile-landing.spec.ts | AC-MOB-001: Hero 内容全宽显示 | AC-MOB-001 | ✅ |
| mobile-landing.spec.ts | AC-MOB-001: Features 网格单列 | AC-MOB-001 | ✅ |
| mobile-tabbar.spec.ts | AC-MOB-009: TabBar 显示且包含5个入口 | AC-MOB-009 | ✅ |
| mobile-tabbar.spec.ts | AC-MOB-011: TabBar 底部有安全区域 padding | AC-MOB-011 | ✅ |
| mobile-tabbar.spec.ts | AC-MOB-009: TabBar 触摸目标 >= 44px | AC-MOB-009 | ✅ |

### 2.2 失败项 (9/20)

#### 失败组 A: HomeView 测试（6 项）— 认证流程阻塞

| 测试用例 | 覆盖 AC | 错误 | 根因 |
|----------|---------|------|------|
| AC-MOB-002: HomeView 卡片单列布局 | AC-MOB-002 | `page.waitForURL('**/home**,**/onboarding**')` 超时 10s | 登录流程未完成，页面停留在 /login |
| AC-MOB-002: TabBar 首页高亮 | AC-MOB-002 | 同上 | 同上 |
| AC-MOB-002: HomeView 无横向滚动 | AC-MOB-002 | 同上 | 同上 |
| AC-MOB-002: Hero Banner 单列紧凑 | AC-MOB-002 | 同上 | 同上 |
| AC-MOB-002: 快捷入口 2x2 网格 | AC-MOB-002 | 同上 | 同上 |
| AC-MOB-002: 轮播图指示器显示 | AC-MOB-002 | 同上 | 同上 |

**根因分析**：mobile-home.spec.ts 的 `beforeEach` 中尝试登录（填写邮箱/密码 → 点击登录），但登录操作未成功完成，页面未跳转到 /home。测试被重定向到 /login 页面。

**责任归属**：FE — 测试用例中的登录流程与当前认证逻辑不匹配，需修复测试中的登录步骤或提供 mock 登录 bypass。

#### 失败组 B: TabBar 导航/高亮（3 项）— 认证 + 路由高亮问题

| 测试用例 | 覆盖 AC | 错误 | 根因 |
|----------|---------|------|------|
| AC-MOB-009: TabBar 导航可点击跳转 | AC-MOB-009 | `waitForURL('**/home')` 超时 30s，被重定向到 /login | 点击 Tab 后需要登录才能访问 /home，未登录状态被拦截 |
| AC-MOB-010: 当前路由对应Tab高亮 | AC-MOB-010 | `expect(items.nth(0)).toHaveClass(/active/)` 失败，实际 class 为 `"tabbar-item"` | MobileTabBar 组件未根据当前路由添加 `active` class |
| AC-MOB-010: 切换路由后Tab高亮跟随变化 | AC-MOB-010 | `waitForURL('**/discover')` 超时，被重定向到 /login | 同认证问题 + 高亮未实现 |

**根因分析**：
1. **认证问题**：TabBar 导航目标页（/home, /discover）需要登录，未登录时被路由守卫重定向到 /login
2. **高亮 Bug**：即使在 LandingView（/）可以看到 TabBar，Tab 的 `active` class 也未被正确设置 — 这是 **FE 实现缺陷**

**责任归属**：
- 认证流程：FE 需修复测试中的登录 bypass
- Tab 高亮：FE 需修复 MobileTabBar.vue 的路由匹配逻辑（**真实 Bug**）

---

## 3. Browser Interaction E2E — PC 回归 (--project=chromium, 1280×720)

### 3.1 通过项 (5/7)

| 测试用例 | 覆盖 AC | 结果 |
|----------|---------|------|
| AC-MOB-012: TabBar 在PC端不显示 | AC-MOB-010 | ✅ |
| AC-MOB-012: AppHeader 在PC端正常显示 | AC-MOB-012 | ✅ |
| AC-MOB-012: LandingView PC端布局正常 | AC-MOB-012 | ✅ |
| AC-MOB-012: global.css 未被修改 | AC-MOB-015 | ✅ |
| AC-MOB-012: PC端无横向滚动 | AC-MOB-013 | ✅ |

### 3.2 失败项 (2/7)

| 测试用例 | 覆盖 AC | 错误 | 根因 |
|----------|---------|------|------|
| AC-MOB-012: HomeView PC端布局正常 | AC-MOB-012 | `locator('.script-grid')` 超时 30s，元素不存在 | HomeView 页面需要登录才能看到内容，选择器 `.script-grid` 在未登录状态下不存在 |
| AC-MOB-012: Hero Banner PC端布局正常 | AC-MOB-012 | `locator('.hero-banner')` 超时 30s，元素不存在 | 同上，`.hero-banner` 在未登录的 HomeView 中不存在 |

**根因分析**：PC 回归测试中 HomeView 相关用例也需要登录状态。测试用例缺少认证 bypass。

**责任归属**：FE — 测试用例需增加认证 bypass 或在未登录状态下使用正确的选择器。

---

## 4. AC 覆盖汇总

| AC 编号 | 验收标准 | 测试类型 | 结果 | 说明 |
|---------|----------|----------|------|------|
| AC-MOB-001 | LandingView 移动端适配 | Browser E2E (mobile) | ✅ **PASS** | 5/5 测试通过 |
| AC-MOB-002 | HomeView 移动端适配 | Browser E2E (mobile) | 🔴 **FAIL** | 0/6 测试通过，认证流程阻塞 |
| AC-MOB-009 | TabBar 移动端显示+导航 | Browser E2E (mobile) | 🟡 **PARTIAL** | 2/3 通过（显示✅、触摸✅、导航❌） |
| AC-MOB-010 | TabBar PC端隐藏 + 高亮 | Browser E2E (both) | 🔴 **FAIL** | PC隐藏✅，Tab高亮❌（实现缺陷） |
| AC-MOB-011 | iOS 安全区域 | Browser E2E (mobile) | ✅ **PASS** | 1/1 测试通过 |
| AC-MOB-012 | PC 端回归 | Browser E2E (chromium) | 🟡 **PARTIAL** | 3/5 通过（TabBar隐藏✅、Header✅、Landing✅、HomeView❌、Hero❌） |
| AC-MOB-013 | 无横向滚动 | Browser E2E (both) | ✅ **PASS** | mobile 3/3 + PC 1/1 通过 |
| AC-MOB-015 | global.css 未修改 | Browser E2E (chromium) | ✅ **PASS** | 1/1 测试通过 |

---

## 5. 缺陷清单

### DEFECT-001: MobileTabBar Tab 高亮未实现 🔴 P0

- **AC**：AC-MOB-010
- **现象**：访问 `/` 后，TabBar 第一个 Tab（首页）的 class 为 `"tabbar-item"`，不包含 `active`
- **期望**：当前路由对应的 Tab 应有 `active` class
- **复现**：移动端视口访问 `/`，检查 `.mobile-tabbar .tabbar-item:first-child` 的 class
- **责任**：FE
- **优先级**：P0

### DEFECT-002: 测试用例登录流程不匹配 🟡 P1

- **AC**：AC-MOB-002, AC-MOB-009, AC-MOB-010, AC-MOB-012
- **现象**：mobile-home.spec.ts 和部分 tabbar/pc-regression 测试因登录流程未完成而超时
- **根因**：测试中的登录操作（填写邮箱密码 → 点击登录）未能成功通过认证，可能被重定向到 /login
- **责任**：FE（测试用例编写者）
- **修复建议**：
  1. 在 `beforeEach` 中通过 API 直接注入 auth token（绕过 UI 登录）
  2. 或使用 `storageState` 保存已登录状态
  3. 或创建测试专用 bypass 路由

---

## 6. 测试命令与证据

### 6.1 Mobile E2E 命令
```bash
cd /root/isekai-wanderer/frontend
APP_BASE=http://localhost:8081 SKIP_WEB_SERVER=true npx playwright test \
  tests/e2e/mobile-landing.spec.ts tests/e2e/mobile-home.spec.ts \
  tests/e2e/mobile-tabbar.spec.ts tests/e2e/mobile-basic.spec.ts \
  --project=mobile --trace on
```
- Browser / Tool: Playwright (Chromium, iPhone 12 device emulation, 390×844)
- 前端入口: http://localhost:8081
- 后端地址: http://localhost:8000
- API / Proxy Path: /api/v1
- Mock API: no
- 结果: 11 passed, 9 failed (1.5m)

### 6.2 PC 回归命令
```bash
cd /root/isekai-wanderer/frontend
APP_BASE=http://localhost:8081 SKIP_WEB_SERVER=true npx playwright test \
  tests/e2e/mobile-pc-regression.spec.ts --project=chromium --trace on
```
- Browser / Tool: Playwright (Chromium, Desktop Chrome, 1280×720)
- 前端入口: http://localhost:8081
- 后端地址: http://localhost:8000
- API / Proxy Path: /api/v1
- Mock API: no
- 结果: 5 passed, 2 failed (37.8s)

### 6.3 证据文件
- Trace 文件: `frontend/test-results/*/trace.zip`
- 截图: `frontend/test-results/*/test-failed-*.png`
- 错误上下文: `frontend/test-results/*/error-context.md`

---

## 7. 退回决定

| 退回项 | 退回对象 | 原因 |
|--------|----------|------|
| DEFECT-001: Tab 高亮未实现 | FE | MobileTabBar.vue 路由匹配逻辑缺陷，active class 未设置 |
| DEFECT-002: 测试登录流程 | FE | 测试用例登录步骤与当前认证逻辑不匹配，需修复 bypass |

**整体结论**：🔴 **FAILED** — 需 FE 修复后重新提交测试。

---

## 8. 通信记录

| 时间 | from | to | 内容 | 状态 |
|------|------|-----|------|------|
| 2026-07-21T10:29 | qa | pl | 测试文件缺失，退回 FE | sent_msg |
| 2026-07-21T10:30 | pl | qa | 确认收到，通知 FE | acked_msg |
| 2026-07-21T11:26 | pl | qa | 测试文件已就绪，请重新测试 | received |
| 2026-07-21T11:30 | qa | — | 执行测试，11 passed / 11 failed | — |
| 2026-07-21T11:35 | qa | pl | 测试报告完成，11 项失败需修复 | sent_msg |
