# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: mobile-pc-regression.spec.ts >> PC端回归验证 >> AC-MOB-012: HomeView PC端布局正常
- Location: tests/e2e/mobile-pc-regression.spec.ts:62:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.evaluate: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('.script-grid')

```

# Page snapshot

```yaml
- main [ref=e4]:
  - generic [ref=e7]:
    - generic [ref=e8]:
      - generic [ref=e9]: ✦
      - heading "Isekai Wanderer" [level=1] [ref=e10]
      - paragraph [ref=e11]: 登录继续你的异世界之旅
    - generic [ref=e12]:
      - generic [ref=e13]:
        - generic [ref=e14]:
          - generic [ref=e15]: 邮箱
          - generic [ref=e16]: "*"
        - generic [ref=e19]:
          - img [ref=e21]:
            - img [ref=e22]
          - textbox "your@email.com" [ref=e26]: test@example.com
      - generic [ref=e28]:
        - generic [ref=e29]:
          - generic [ref=e30]: 密码
          - generic [ref=e31]: "*"
        - generic [ref=e34]:
          - generic [ref=e36]: 🔒
          - textbox "密码" [ref=e38]: Test1234!
          - img [ref=e42] [cursor=pointer]
      - generic [ref=e49]:
        - checkbox "记住我" [ref=e50] [cursor=pointer]:
          - img [ref=e54]
          - generic [ref=e57]: 记住我
        - button "忘记密码？" [ref=e58] [cursor=pointer]:
          - generic [ref=e59]: 忘记密码？
    - button "登录" [ref=e60] [cursor=pointer]:
      - generic [ref=e61]: 登录
    - generic [ref=e64]: 或继续使用
    - button "💚 使用 微信 登录" [ref=e66] [cursor=pointer]:
      - generic [ref=e67]:
        - generic [ref=e68]: 💚
        - text: 使用 微信 登录
    - button "🌐 使用 Google 登录" [ref=e69] [cursor=pointer]:
      - generic [ref=e70]:
        - generic [ref=e71]: 🌐
        - text: 使用 Google 登录
    - button "🍎 使用 Apple 登录" [ref=e72] [cursor=pointer]:
      - generic [ref=e73]:
        - generic [ref=e74]: 🍎
        - text: 使用 Apple 登录
    - generic [ref=e75]:
      - text: 还没有账户？
      - link "立即注册" [ref=e76] [cursor=pointer]:
        - /url: /register
```

# Test source

```ts
  1   | /**
  2   |  * CR-004 PC端回归测试
  3   |  * 覆盖: AC-MOB-012 (PC端视口下所有页面视觉无变化)
  4   |  * 
  5   |  * 运行: APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-pc-regression.spec.ts --project=chromium
  6   |  */
  7   | import { test, expect } from '@playwright/test';
  8   | 
  9   | test.describe('PC端回归验证', () => {
  10  |   test.beforeEach(async ({ page }, testInfo) => {
  11  |     // 只在 chromium 项目中运行（PC端测试）
  12  |     if (testInfo.project.name !== 'chromium') {
  13  |       test.skip();
  14  |     }
  15  |     
  16  |     // 确保在桌面端视口下（1280x720）
  17  |     await page.setViewportSize({ width: 1280, height: 720 });
  18  |     const viewport = page.viewportSize();
  19  |     expect(viewport?.width).toBeGreaterThanOrEqual(1024);
  20  |   });
  21  | 
  22  |   test('AC-MOB-012: TabBar 在PC端不显示', async ({ page }) => {
  23  |     await page.goto('/');
  24  |     await page.waitForLoadState('networkidle');
  25  | 
  26  |     const tabbar = page.locator('.mobile-tabbar');
  27  |     await expect(tabbar).toBeHidden();
  28  |   });
  29  | 
  30  |   test('AC-MOB-012: AppHeader 在PC端正常显示', async ({ page }) => {
  31  |     await page.goto('/');
  32  |     await page.waitForLoadState('networkidle');
  33  | 
  34  |     const header = page.locator('.app-header');
  35  |     await expect(header).toBeVisible();
  36  | 
  37  |     // 导航链接应该显示
  38  |     const nav = page.locator('.header-nav');
  39  |     await expect(nav).toBeVisible();
  40  |   });
  41  | 
  42  |   test('AC-MOB-012: LandingView PC端布局正常', async ({ page }) => {
  43  |     await page.goto('/');
  44  |     await page.waitForLoadState('networkidle');
  45  | 
  46  |     // Hero actions 应该是 flex row（不是 column）
  47  |     const heroActions = page.locator('.hero-actions');
  48  |     const flexDirection = await heroActions.evaluate((el) => {
  49  |       return window.getComputedStyle(el).flexDirection;
  50  |     });
  51  |     expect(flexDirection).toBe('row');
  52  | 
  53  |     // Features grid 应该是多列
  54  |     const featuresGrid = page.locator('.features-grid');
  55  |     const gridTemplateColumns = await featuresGrid.evaluate((el) => {
  56  |       return window.getComputedStyle(el).gridTemplateColumns;
  57  |     });
  58  |     const columns = gridTemplateColumns.split(' ').filter(c => c.trim());
  59  |     expect(columns.length).toBeGreaterThan(1);
  60  |   });
  61  | 
  62  |   test('AC-MOB-012: HomeView PC端布局正常', async ({ page }) => {
  63  |     await page.goto('/home');
  64  |     await page.waitForLoadState('networkidle');
  65  | 
  66  |     // Script grid 应该是 grid 布局（不是 flex）
  67  |     const scriptGrid = page.locator('.script-grid');
> 68  |     const display = await scriptGrid.evaluate((el) => {
      |                                      ^ Error: locator.evaluate: Test timeout of 30000ms exceeded.
  69  |       return window.getComputedStyle(el).display;
  70  |     });
  71  |     expect(display).toBe('grid');
  72  | 
  73  |     // 应该是多列
  74  |     const gridTemplateColumns = await scriptGrid.evaluate((el) => {
  75  |       return window.getComputedStyle(el).gridTemplateColumns;
  76  |     });
  77  |     const columns = gridTemplateColumns.split(' ').filter(c => c.trim());
  78  |     expect(columns.length).toBeGreaterThan(1);
  79  |   });
  80  | 
  81  |   test('AC-MOB-012: Hero Banner PC端布局正常', async ({ page }) => {
  82  |     await page.goto('/home');
  83  |     await page.waitForLoadState('networkidle');
  84  | 
  85  |     // Hero banner 应该是 flex row
  86  |     const heroBanner = page.locator('.hero-banner');
  87  |     const flexDirection = await heroBanner.evaluate((el) => {
  88  |       return window.getComputedStyle(el).flexDirection;
  89  |     });
  90  |     expect(flexDirection).toBe('row');
  91  |   });
  92  | 
  93  |   test('AC-MOB-012: global.css 未被修改', async ({ page }) => {
  94  |     // 这个测试验证 global.css 文件没有被修改
  95  |     // 通过检查关键样式是否存在来间接验证
  96  |     await page.goto('/');
  97  |     await page.waitForLoadState('networkidle');
  98  | 
  99  |     // 检查 global.css 中的关键变量是否存在
  100 |     const hasBrandPrimary = await page.evaluate(() => {
  101 |       const root = document.documentElement;
  102 |       const style = window.getComputedStyle(root);
  103 |       return style.getPropertyValue('--brand-primary') !== '';
  104 |     });
  105 |     expect(hasBrandPrimary).toBe(true);
  106 |   });
  107 | 
  108 |   test('AC-MOB-012: PC端无横向滚动', async ({ page }) => {
  109 |     await page.goto('/');
  110 |     await page.waitForLoadState('networkidle');
  111 | 
  112 |     const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
  113 |     const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
  114 | 
  115 |     expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  116 |   });
  117 | });
  118 | 
```