# Test Plan — CR-004 移动端适配

| 项 | 内容 |
| --- | --- |
| 变更 ID | CR-004 |
| 变更名称 | mobile-responsive |
| 测试状态 | Ready |
| 测试负责人 | qa |
| 创建时间 | 2026-07-19 |
| 前置条件 | DESIGN passed |

---

## 1. 测试先行范围

### 1.1 测试范围概述

| 类别 | 范围 | 说明 |
|------|------|------|
| P0 页面 | 7 个核心页面 | LandingView, HomeView, GameView, DiscoverView, CharacterListView, CharacterDetailView, CommunityView |
| P1 页面 | 18 个功能页面 | Login, Register, Onboarding, Profile, Settings, SaveManager, ShardCenter, Achievement, Subscription, Gallery, Gift, ScriptDetail, Ending, Recap, RouteMap, FreeChat, ForgotPassword, ResetPassword |
| P2 页面 | 3 个辅助页面 | ShareView, OAuthCallbackView, NotFoundView |
| 公共组件 | 11 个组件 | DialogueBox, ChoicePanel, AudioPlayer, PaymentModal, BalanceDisplay, AffectionMeter, AffectionBar, MemoryCard, TaskPanel, ScriptCard, EndingCard |
| 新增组件 | 1 个 | MobileTabBar |
| 新增文件 | 1 个 | `src/styles/mobile.css` |

### 1.2 测试类型

| 测试类型 | 覆盖范围 | 执行时机 |
|----------|----------|----------|
| Browser Interaction E2E | 所有 AC（38 项） | 每个阶段验收 + RELEASE_GATE |
| PC 端回归测试 | 所有页面 ≥1024px | 每个阶段验收 + RELEASE_GATE |
| CSS 隔离检查 | `global.css` 未修改 | 每个阶段验收 |
| 触摸目标检查 | 所有交互元素 ≥44×44px | 每个阶段验收 |
| 横向滚动检查 | 所有页面 ≤767px | 每个阶段验收 |
| iOS 安全区域检查 | TabBar + 底部固定元素 | P0 验收 + RELEASE_GATE |

### 1.3 测试环境

| 环境 | 视口 | 设备模拟 | 用途 |
|------|------|----------|------|
| Mobile Small | 375×667 | iPhone SE | 最小屏幕兼容 |
| Mobile Standard | 390×844 | iPhone 12/13/14 | 主流 iOS 设备 |
| Mobile Large | 414×896 | iPhone 11/XR | 大屏 iOS |
| Mobile Android | 360×800 | Pixel | 主流 Android |
| Tablet (边界) | 768×1024 | iPad Mini | 验证 ≥768px 不触发移动端样式 |
| PC (回归) | 1024×768 | Desktop | PC 端零影响验证 |
| PC Full HD | 1920×1080 | Desktop | PC 端零影响验证 |

---

## 2. 测试用例产物

### 2.1 E2E 测试文件

| 文件 | 路径 | 覆盖 AC |
|------|------|---------|
| `mobile-responsive.spec.ts` | `tests/e2e/mobile-responsive.spec.ts` | AC-MOB-001 ~ AC-MOB-038 |
| `mobile-tabbar.spec.ts` | `tests/e2e/mobile-tabbar.spec.ts` | AC-MOB-009, AC-MOB-010, AC-MOB-011 |
| `mobile-pc-regression.spec.ts` | `tests/e2e/mobile-pc-regression.spec.ts` | AC-MOB-012 |
| `mobile-ios-safe-area.spec.ts` | `tests/e2e/mobile-ios-safe-area.spec.ts` | AC-MOB-011 |

### 2.2 测试用例详细列表

#### P0 页面测试用例

| 用例 ID | 用例名称 | 关联 AC | 前置条件 | 测试步骤 | 预期结果 |
|---------|----------|---------|----------|----------|----------|
| TC-MOB-001 | LandingView 移动端布局 | AC-MOB-001 | 未登录用户 | 1. 设置视口 375×667<br>2. 访问 `/`<br>3. 检查布局<br>4. 检查 CTA 按钮尺寸<br>5. 检查图片自适应<br>6. 检查横向滚动 | 1. 单列布局<br>2. CTA 按钮 ≥44px<br>3. 图片 max-width: 100%<br>4. 无横向滚动 |
| TC-MOB-002 | HomeView 移动端布局 | AC-MOB-002 | 已登录用户 | 1. 设置视口 390×844<br>2. 访问 `/home`<br>3. 检查卡片布局<br>4. 检查 TabBar 高亮<br>5. 检查卡片间距 | 1. 卡片单列全宽<br>2. TabBar「首页」高亮<br>3. 卡片间距 12-16px |
| TC-MOB-003 | GameView 移动端布局 | AC-MOB-003 | 已登录用户，有游戏会话 | 1. 设置视口 375×667<br>2. 进入游戏<br>3. 检查对话区域<br>4. 检查选择按钮<br>5. 检查 TabBar 隐藏 | 1. 对话区域全宽<br>2. 选择按钮 ≥44px 全宽<br>3. TabBar 隐藏 |
| TC-MOB-004 | GameView 选择交互 | AC-MOB-004 | 已登录用户，游戏中出现选择 | 1. 设置视口 390×844<br>2. 触发选择分支<br>3. 点击选项按钮<br>4. 检查剧情推进 | 1. 选项按钮全宽单列<br>2. 点击后剧情正常推进<br>3. 无 JS 报错 |
| TC-MOB-005 | DiscoverView 移动端布局 | AC-MOB-005 | 已登录用户 | 1. 设置视口 375×667<br>2. 访问 `/discover`<br>3. 检查列表布局<br>4. 检查 TabBar 高亮<br>5. 检查触摸区域 | 1. 列表单列全宽<br>2. TabBar「发现」高亮<br>3. 列表项 ≥44px |
| TC-MOB-006 | CharacterListView 移动端布局 | AC-MOB-006 | 已登录用户 | 1. 设置视口 390×844<br>2. 访问 `/characters`<br>3. 检查网格布局<br>4. 检查角色卡片<br>5. 检查横向滚动 | 1. 网格转单列<br>2. 角色卡片 ≥44px<br>3. 无横向滚动 |
| TC-MOB-007 | CharacterDetailView 移动端布局 | AC-MOB-007 | 已登录用户 | 1. 设置视口 375×667<br>2. 访问 `/characters/:id`<br>3. 检查图文布局<br>4. 检查图片自适应<br>5. 检查交互按钮 | 1. 单列布局<br>2. 图片自适应<br>3. 按钮 ≥44px |
| TC-MOB-008 | CommunityView 移动端布局 | AC-MOB-008 | 已登录用户 | 1. 设置视口 390×844<br>2. 访问 `/community`<br>3. 检查帖子列表<br>4. 检查 TabBar 高亮<br>5. 检查评论/点赞交互 | 1. 帖子列表单列全宽<br>2. TabBar「社区」高亮<br>3. 列表项 ≥44px<br>4. 评论/点赞正常 |

#### TabBar 测试用例

| 用例 ID | 用例名称 | 关联 AC | 前置条件 | 测试步骤 | 预期结果 |
|---------|----------|---------|----------|----------|----------|
| TC-MOB-009 | TabBar 移动端显示 | AC-MOB-009 | 已登录用户 | 1. 设置视口 375×667<br>2. 访问主要页面<br>3. 检查 TabBar 显示<br>4. 检查 5 个入口<br>5. 点击各 Tab 导航 | 1. TabBar 固定底部显示<br>2. 包含 5 个入口<br>3. 点击可导航 |
| TC-MOB-010 | TabBar PC 端隐藏 | AC-MOB-010 | 已登录用户 | 1. 设置视口 1024×768<br>2. 访问任意页面<br>3. 检查 TabBar 不显示<br>4. 检查顶部导航正常 | 1. TabBar 不可见<br>2. 顶部导航正常 |
| TC-MOB-011 | TabBar iOS 安全区域 | AC-MOB-011 | iOS 设备或模拟器 | 1. 使用 iOS 设备访问<br>2. 检查 TabBar 底部<br>3. 检查内容不被遮挡 | 1. safe-area-inset-bottom 生效<br>2. 内容不被 Home Indicator 遮挡 |

#### 通用检查测试用例

| 用例 ID | 用例名称 | 关联 AC | 前置条件 | 测试步骤 | 预期结果 |
|---------|----------|---------|----------|----------|----------|
| TC-MOB-012 | PC 端回归检查 | AC-MOB-012 | 已登录用户 | 1. 设置视口 1024×768<br>2. 访问所有 28 个页面<br>3. 截图对比<br>4. 检查视觉一致性 | 1. 所有页面视觉与适配前一致<br>2. 无样式偏差 |
| TC-MOB-013 | 横向滚动检查 | AC-MOB-013 | 已登录用户 | 1. 设置视口 375×667<br>2. 访问所有页面<br>3. 检查横向滚动条<br>4. 检查 overflow-x | 1. 所有页面无横向滚动条<br>2. overflow-x: hidden 生效 |
| TC-MOB-014 | 触摸目标检查 | AC-MOB-014 | 已登录用户 | 1. 设置视口 375×667<br>2. 检查所有按钮 bounding box<br>3. 检查所有链接 bounding box<br>4. 检查所有输入框 bounding box | 1. 所有交互元素 ≥44×44px |
| TC-MOB-015 | CSS 隔离检查 | AC-MOB-015 | N/A | 1. 运行 `git diff frontend/src/styles/global.css`<br>2. 检查输出 | 1. git diff 为空<br>2. global.css 未被修改 |

#### P1 页面测试用例

| 用例 ID | 用例名称 | 关联 AC | 测试要点 |
|---------|----------|---------|----------|
| TC-MOB-016 | LoginView 移动端 | AC-MOB-016 | 表单全宽，padding 16px，输入框/按钮 ≥44px |
| TC-MOB-017 | RegisterView 移动端 | AC-MOB-017 | 表单全宽，padding 16px，输入框/按钮 ≥44px |
| TC-MOB-018 | OnboardingView 移动端 | AC-MOB-018 | 步骤单列全宽，按钮 ≥44px |
| TC-MOB-019 | ProfileView 移动端 | AC-MOB-019 | 用户信息单列，菜单项 ≥44px |
| TC-MOB-020 | SettingsView 移动端 | AC-MOB-020 | 设置项全宽单列，≥44px，开关可操作 |
| TC-MOB-021 | SaveManagerView 移动端 | AC-MOB-021 | 存档列表单列全宽，操作按钮 ≥44px |
| TC-MOB-022 | ShardCenterView 移动端 | AC-MOB-022 | 碎片中心单列全宽，购买按钮 ≥44px |
| TC-MOB-023 | AchievementView 移动端 | AC-MOB-023 | 成就网格转单列/双列，卡片 ≥44px |
| TC-MOB-024 | SubscriptionView 移动端 | AC-MOB-024 | 套餐卡片单列全宽，订阅按钮 ≥44px |
| TC-MOB-025 | GalleryView 移动端 | AC-MOB-025 | 图片网格转单列/双列，图片自适应，可预览 |
| TC-MOB-026 | GiftView 移动端 | AC-MOB-026 | 礼物列表单列全宽，送礼按钮 ≥44px |
| TC-MOB-027 | ScriptDetailView 移动端 | AC-MOB-027 | 剧本内容全宽可读，开始游戏按钮 ≥44px |
| TC-MOB-028 | EndingView 移动端 | AC-MOB-028 | 结局内容单列全宽，操作按钮 ≥44px |
| TC-MOB-029 | RecapView 移动端 | AC-MOB-029 | 剧情回顾单列全宽，文字可读，图片自适应 |
| TC-MOB-030 | RouteMap 移动端 | AC-MOB-030 | 节点图自适应宽度，无横向滚动，节点 ≥44px |
| TC-MOB-031 | FreeChatView 移动端 | AC-MOB-031 | 聊天消息全宽，输入框固定底部 ≥44px，发送按钮 ≥44px |
| TC-MOB-032 | ForgotPasswordView 移动端 | AC-MOB-032 | 表单全宽，padding 16px，输入框/按钮 ≥44px |
| TC-MOB-033 | ResetPasswordView 移动端 | AC-MOB-033 | 表单全宽，padding 16px，输入框/按钮 ≥44px |

#### 公共组件测试用例

| 用例 ID | 用例名称 | 关联 AC | 测试要点 |
|---------|----------|---------|----------|
| TC-MOB-034 | PaymentModal 移动端 | AC-MOB-034 | 转底部抽屉或全屏，支付按钮 ≥44px，可关闭 |
| TC-MOB-035 | 公共组件布局检查 | AC-MOB-035 | DialogueBox, ChoicePanel, AudioPlayer 等无溢出/错位/重叠 |

#### P2 页面测试用例

| 用例 ID | 用例名称 | 关联 AC | 测试要点 |
|---------|----------|---------|----------|
| TC-MOB-036 | ShareView 移动端 | AC-MOB-036 | 分享内容单列全宽，文字可读，图片自适应，CTA ≥44px |
| TC-MOB-037 | OAuthCallbackView 移动端 | AC-MOB-037 | 加载中居中，无横向滚动，文字可读 |
| TC-MOB-038 | NotFoundView 移动端 | AC-MOB-038 | 提示单列居中，返回按钮 ≥44px |

---

## 3. Browser Interaction E2E 计划

### 3.1 测试框架

| 项 | 选择 |
| --- | --- |
| 框架 | Playwright |
| 浏览器 | Chromium (Desktop + Mobile emulation) |
| 移动端模拟 | `viewport: { width: 375, height: 667 }` + `isMobile: true` + `hasTouch: true` |
| iOS 测试 | WebKit (可选，如有 iOS 设备) |
| 截图对比 | Playwright `toHaveScreenshot()` |

### 3.2 测试配置

```typescript
// playwright.config.ts 新增 mobile 项目
{
  name: 'mobile',
  use: {
    viewport: { width: 375, height: 667 },
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)',
  },
  testMatch: /mobile-.*\.spec\.ts/,
}
```

### 3.3 E2E 执行命令

```bash
# Mobile E2E 全量
APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-*.spec.ts --project=mobile --headed --trace on

# Mobile E2E 单个文件
APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-responsive.spec.ts --project=mobile --headed

# PC 回归
APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-pc-regression.spec.ts --project=chromium --headed

# iOS 安全区域（需要 iOS 设备或 WebKit）
APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-ios-safe-area.spec.ts --project=webkit --headed
```

### 3.4 Browser E2E User Actions（按阶段）

#### Demo 阶段

| 动作 | AC | 描述 |
|------|-----|------|
| 移动端落地页访问 | AC-MOB-001 | ≤767px 视口访问 `/`，验证单列布局、CTA 按钮 ≥44px、无横向滚动 |
| 移动端主页访问 | AC-MOB-002 | ≤767px 视口访问 `/home`，验证卡片单列全宽、TabBar「首页」高亮 |
| TabBar 导航 | AC-MOB-009, AC-MOB-010 | ≤767px 验证 TabBar 显示、5 入口导航；≥1024px 验证 TabBar 不显示 |
| PC 端回归 | AC-MOB-012 | ≥1024px 视口验证 LandingView + HomeView 视觉无变化 |

#### GameView 单独阶段

| 动作 | AC | 描述 |
|------|-----|------|
| 移动端游戏进入 | AC-MOB-003 | ≤767px 视口进入游戏，验证对话全宽、选择按钮 ≥44px、TabBar 隐藏 |
| 移动端游戏选择 | AC-MOB-004 | ≤767px 视口点击选项按钮，验证剧情正常推进、无 JS 报错 |
| PC 端游戏回归 | AC-MOB-012 | ≥1024px 视口验证 GameView 视觉与交互无变化 |

#### P0 其余阶段

| 动作 | AC | 描述 |
|------|-----|------|
| 移动端发现页 | AC-MOB-005 | ≤767px 视口访问 `/discover`，验证列表单列全宽、TabBar「发现」高亮 |
| 移动端角色列表 | AC-MOB-006 | ≤767px 视口访问 `/characters`，验证网格转单列、角色卡片可点击 |
| 移动端角色详情 | AC-MOB-007 | ≤767px 视口访问 `/characters/:id`，验证图文单列、按钮 ≥44px |
| 移动端社区 | AC-MOB-008 | ≤767px 视口访问 `/community`，验证帖子列表单列、TabBar「社区」高亮 |
| 触摸目标检查 | AC-MOB-014 | ≤767px 视口验证所有按钮、链接、输入框 ≥44×44px |

#### P1 阶段

| 动作 | AC | 描述 |
|------|-----|------|
| 表单页面遍历 | AC-MOB-016~017, 032~033 | ≤767px 视口访问 4 个表单页面，验证表单全宽、输入框/按钮 ≥44px |
| 功能页面遍历 | AC-MOB-018~031 | ≤767px 视口访问 14 个功能页面，验证布局正常、交互元素 ≥44px |

#### P2 阶段 + 最终验收

| 动作 | AC | 描述 |
|------|-----|------|
| P2 页面遍历 | AC-MOB-036~038 | ≤767px 视口访问 3 个 P2 页面 |
| 公共组件检查 | AC-MOB-034~035 | ≤767px 视口触发各公共组件，验证无溢出/错位 |
| iOS 安全区域 | AC-MOB-011 | iOS 设备/模拟器验证 TabBar safe-area |
| PC 全量回归 | AC-MOB-012 | ≥1024px 视口验证所有 28 个页面 |
| CSS 隔离检查 | AC-MOB-015 | `git diff global.css` 为空 |
| 横向滚动检查 | AC-MOB-013 | ≤767px 视口所有页面无横向滚动 |

---

## 4. CI/CD 证据计划

### 4.1 CI Pipeline 集成

```yaml
# .github/workflows/e2e.yml 新增 mobile 步骤
mobile-e2e:
  runs-on: ubuntu-latest
  steps:
    - name: Start services
      run: docker compose up -d && sleep 5
    
    - name: Health check
      run: curl -f http://localhost/api/v1/health
    
    - name: Mobile E2E (Demo)
      run: APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-responsive.spec.ts --project=mobile --trace on
      if: github.event_name == 'pull_request' && contains(github.head_ref, 'mobile')
    
    - name: Mobile E2E (Full)
      run: APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-*.spec.ts --project=mobile --trace on
      if: github.ref == 'refs/heads/main'
    
    - name: PC Regression
      run: APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-pc-regression.spec.ts --project=chromium --trace on
    
    - name: Upload traces
      uses: actions/upload-artifact@v4
      if: failure()
      with:
        name: playwright-traces
        path: test-results/
```

### 4.2 证据等级要求

| 证据类型 | 等级 | 说明 |
|----------|------|------|
| Mobile Browser E2E | L2 (联调通过) | 真实前端 + 真实后端 + 真实 proxy |
| PC Regression | L2 (联调通过) | 真实前端 + 真实后端 |
| CSS 隔离检查 | L1 (本地通过) | git diff 命令输出 |
| iOS Safe Area | L2/L3 | 需要 iOS 设备或模拟器 |

### 4.3 Mock Policy

| 项 | 策略 |
| --- | --- |
| Delivery E2E | **禁止 mock API**；必须使用真实后端 |
| Browser Interaction E2E | **禁止 mock API**；必须使用真实前端 + 真实后端 |
| 组件测试 | 可使用 mock 数据 |
| 视觉回归 | 使用截图对比，不使用 mock |

### 4.4 证据收集清单

| 阶段 | 证据 | 格式 |
|------|------|------|
| Demo | Playwright trace + 截图 | `test-results/demo/` |
| GameView | Playwright trace + 截图 + 无 JS 报错日志 | `test-results/gameview/` |
| P0 全面 | Playwright trace + 截图 | `test-results/p0/` |
| P1 | Playwright trace + 截图 | `test-results/p1/` |
| P2 + 最终 | Playwright trace + 截图 + PC 回归截图 + git diff 输出 | `test-results/final/` |
| RELEASE_GATE | 所有阶段证据汇总 + CI/CD 运行链接 | `test-results/release/` |

---

## 5. 测试通过标准

### 5.1 阶段通过标准

| 阶段 | 通过条件 |
|------|----------|
| Demo | AC-MOB-001, 002, 009, 010, 012, 013, 015 全部 covered |
| GameView | AC-MOB-003, 004, 012 全部 covered |
| P0 全面 | AC-MOB-005~008, 014 全部 covered |
| P1 | AC-MOB-016~033 全部 covered |
| P2 + 最终 | AC-MOB-034~038, 011, 012 全部 covered |
| RELEASE_GATE | 38 项 AC 全部 covered + CI/CD 通过 + Mock API=no |

### 5.2 阻塞条件

| 条件 | 处理 |
|------|------|
| 任一 P0 AC 未通过 | 阻塞 RELEASE_GATE |
| PC 端回归失败 | 阻塞当前阶段，必须回滚修复 |
| `global.css` 被修改 | 阻塞当前阶段，必须回滚 |
| Naive UI 覆盖冲突无法解决 | 上报 PL，标记 Blocked |
| iOS 安全区域无法验证 | 标记为已知限制，不阻塞 RELEASE_GATE |

---

## 6. 测试时间表

| 阶段 | 测试时间 | 与开发并行 |
|------|----------|------------|
| Demo | 0.5 天 | 开发 1 天 + 测试 0.5 天 |
| GameView | 0.5 天 | 开发 1 天 + 测试 0.5 天 |
| P0 其余 | 0.5 天 | 开发 1-2 天 + 测试 0.5 天 |
| P1 | 1-2 天 | 开发 3-4 天 + 测试 1-2 天 |
| P2 + 最终 | 1 天 | 开发 1-2 天 + 测试 1 天 |
| **合计** | **3.5-4.5 天** | **总计 10-14 天** |

---

## 7. 测试风险

| # | 风险 | 影响 | 缓解 |
|---|------|------|------|
| T1 | iOS 设备/模拟器不可用 | AC-MOB-011 无法验证 | 使用 WebKit 浏览器模拟；标记为已知限制 |
| T2 | 截图对比基线缺失 | PC 回归无法自动对比 | 首次适配前截图作为基线 |
| T3 | Naive UI 组件内部结构变化 | `:deep()` 覆盖失效 | 逐个组件验证；失效时上报 PL |
| T4 | 移动端触摸事件与鼠标事件差异 | E2E 测试通过但实际交互异常 | 使用 `hasTouch: true` 模拟真实触摸 |

---

## 8. 测试工具

| 工具 | 用途 |
|------|------|
| Playwright | Browser Interaction E2E |
| Playwright Inspector | 调试测试用例 |
| Playwright Trace Viewer | 分析测试失败原因 |
| Chrome DevTools | 移动端视口模拟 + 触摸目标测量 |
| git diff | CSS 隔离检查 |
| Lighthouse | 移动端性能/可访问性检查（可选） |
