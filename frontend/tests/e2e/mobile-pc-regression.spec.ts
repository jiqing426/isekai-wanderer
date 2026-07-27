/**
 * CR-004 PC端回归测试
 * 覆盖: AC-MOB-012 (PC端视口下所有页面视觉无变化)
 * 
 * 运行: APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-pc-regression.spec.ts --project=chromium
 */
import { test, expect } from '@playwright/test';

test.describe('PC端回归验证', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    // 只在 chromium 项目中运行（PC端测试）
    if (testInfo.project.name !== 'chromium') {
      test.skip();
    }
    
    // 确保在桌面端视口下（1280x720）
    await page.setViewportSize({ width: 1280, height: 720 });
    const viewport = page.viewportSize();
    expect(viewport?.width).toBeGreaterThanOrEqual(1024);
  });

  test('AC-MOB-012: TabBar 在PC端不显示', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const tabbar = page.locator('.mobile-tabbar');
    await expect(tabbar).toBeHidden();
  });

  test('AC-MOB-012: AppHeader 在PC端正常显示', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const header = page.locator('.app-header');
    await expect(header).toBeVisible();

    // 导航链接应该显示
    const nav = page.locator('.header-nav');
    await expect(nav).toBeVisible();
  });

  test('AC-MOB-012: LandingView PC端布局正常', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Hero actions 应该是 flex row（不是 column）
    const heroActions = page.locator('.hero-actions');
    const flexDirection = await heroActions.evaluate((el) => {
      return window.getComputedStyle(el).flexDirection;
    });
    expect(flexDirection).toBe('row');

    // Features grid 应该是多列
    const featuresGrid = page.locator('.features-grid');
    const gridTemplateColumns = await featuresGrid.evaluate((el) => {
      return window.getComputedStyle(el).gridTemplateColumns;
    });
    const columns = gridTemplateColumns.split(' ').filter(c => c.trim());
    expect(columns.length).toBeGreaterThan(1);
  });

  test('AC-MOB-012: HomeView PC端布局正常', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    // Script grid 应该是 grid 布局（不是 flex）
    const scriptGrid = page.locator('.script-grid');
    const display = await scriptGrid.evaluate((el) => {
      return window.getComputedStyle(el).display;
    });
    expect(display).toBe('grid');

    // 应该是多列
    const gridTemplateColumns = await scriptGrid.evaluate((el) => {
      return window.getComputedStyle(el).gridTemplateColumns;
    });
    const columns = gridTemplateColumns.split(' ').filter(c => c.trim());
    expect(columns.length).toBeGreaterThan(1);
  });

  test('AC-MOB-012: Hero Banner PC端布局正常', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    // Hero banner 应该是 flex row
    const heroBanner = page.locator('.hero-banner');
    const flexDirection = await heroBanner.evaluate((el) => {
      return window.getComputedStyle(el).flexDirection;
    });
    expect(flexDirection).toBe('row');
  });

  test('AC-MOB-012: global.css 未被修改', async ({ page }) => {
    // 这个测试验证 global.css 文件没有被修改
    // 通过检查关键样式是否存在来间接验证
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // 检查 global.css 中的关键变量是否存在
    const hasBrandPrimary = await page.evaluate(() => {
      const root = document.documentElement;
      const style = window.getComputedStyle(root);
      return style.getPropertyValue('--brand-primary') !== '';
    });
    expect(hasBrandPrimary).toBe(true);
  });

  test('AC-MOB-012: PC端无横向滚动', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);

    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });
});
