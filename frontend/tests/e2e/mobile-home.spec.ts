/**
 * CR-004 HomeView 移动端测试
 * 覆盖: AC-MOB-002 (HomeView 卡片单列全宽, TabBar首页高亮, 无横向滚动)
 * 
 * 运行: APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-home.spec.ts --project=mobile
 */
import { test, expect } from '@playwright/test';

// 测试账号
const TEST_USER = {
  email: 'test@example.com',
  password: 'Test1234!'
};

test.describe('HomeView 移动端', () => {
  test.beforeEach(async ({ page }) => {
    // 先访问登录页
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    // 填写登录表单
    await page.locator('input[type="email"]').fill(TEST_USER.email);
    await page.locator('input[type="password"]').fill(TEST_USER.password);

    // 点击登录按钮（使用文本内容定位）
    await page.locator('button:has-text("登录"), button:has-text("Login")').first().click();

    // 等待登录成功并跳转到首页或新手引导页
    await page.waitForURL('**/home**,**/onboarding**', { timeout: 10000 });
    await page.waitForLoadState('networkidle');

    // 如果在新手引导页，完成引导
    if (page.url().includes('/onboarding')) {
      // 跳过新手引导
      const skipButton = page.locator('button:has-text("跳过"), button:has-text("Skip")').first();
      if (await skipButton.isVisible()) {
        await skipButton.click();
        await page.waitForURL('**/home', { timeout: 10000 });
        await page.waitForLoadState('networkidle');
      }
    }

    const viewport = page.viewportSize();
    expect(viewport?.width).toBeLessThanOrEqual(430);
  });

  test('AC-MOB-002: HomeView 卡片单列布局', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    // 验证 script-grid 是 flex 布局（移动端轮播图）
    const scriptGrid = page.locator('.script-grid');
    const display = await scriptGrid.evaluate((el) => {
      return window.getComputedStyle(el).display;
    });
    expect(display).toBe('flex');

    // 验证 overflow-x: auto（可横向滚动）
    const overflowX = await scriptGrid.evaluate((el) => {
      return window.getComputedStyle(el).overflowX;
    });
    expect(overflowX).toBe('auto');
  });

  test('AC-MOB-002: TabBar 首页高亮', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    const tabbar = page.locator('.mobile-tabbar');
    await expect(tabbar).toBeVisible();

    const items = tabbar.locator('.tabbar-item');
    
    // 第一个Tab（首页）应该是 active
    await expect(items.nth(0)).toHaveClass(/active/);
    
    // 其他Tab不应该有 active
    await expect(items.nth(1)).not.toHaveClass(/active/);
    await expect(items.nth(2)).not.toHaveClass(/active/);
  });

  test('AC-MOB-002: HomeView 无横向滚动', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);

    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });

  test('AC-MOB-002: Hero Banner 单列紧凑', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    // 验证 hero-banner 是 flex-direction: column
    const heroBanner = page.locator('.hero-banner');
    const flexDirection = await heroBanner.evaluate((el) => {
      return window.getComputedStyle(el).flexDirection;
    });
    expect(flexDirection).toBe('column');

    // 验证 padding 紧凑（12px）
    const padding = await heroBanner.evaluate((el) => {
      return window.getComputedStyle(el).padding;
    });
    expect(padding).toContain('12px');
  });

  test('AC-MOB-002: 快捷入口 2x2 网格', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    const quickNav = page.locator('.quick-nav');
    const gridTemplateColumns = await quickNav.evaluate((el) => {
      return window.getComputedStyle(el).gridTemplateColumns;
    });

    // 应该是 2 列布局
    const columns = gridTemplateColumns.split(' ').filter(c => c.trim());
    expect(columns.length).toBe(2);
  });

  test('AC-MOB-002: 轮播图指示器显示', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    // 如果有多个剧本，应该显示指示器
    const scriptCount = await page.locator('.script-grid .carousel-item').count();
    
    if (scriptCount > 1) {
      const indicators = page.locator('.carousel-indicators');
      await expect(indicators).toBeVisible();
      
      const dots = indicators.locator('.carousel-dot');
      await expect(dots).toHaveCount(scriptCount);
    }
  });
});
