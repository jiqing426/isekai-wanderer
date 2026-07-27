/**
 * CR-004 LandingView 移动端测试
 * 覆盖: AC-MOB-001 (LandingView 单列布局, CTA >= 44px, 无横向滚动)
 * 
 * 运行: APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-landing.spec.ts --project=mobile
 */
import { test, expect } from '@playwright/test';

test.describe('LandingView 移动端', () => {
  test.beforeEach(async ({ page }) => {
    const viewport = page.viewportSize();
    expect(viewport?.width).toBeLessThanOrEqual(430);
  });

  test('AC-MOB-001: LandingView 单列布局', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // 验证 hero-actions 是 flex-direction: column（单列）
    const heroActions = page.locator('.hero-actions');
    const flexDirection = await heroActions.evaluate((el) => {
      return window.getComputedStyle(el).flexDirection;
    });
    expect(flexDirection).toBe('column');
  });

  test('AC-MOB-001: CTA 按钮 >= 44px', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // 验证所有按钮高度 >= 44px
    const buttons = page.locator('.hero-actions .n-button');
    const count = await buttons.count();
    expect(count).toBeGreaterThan(0);

    for (let i = 0; i < count; i++) {
      const box = await buttons.nth(i).boundingBox();
      expect(box).not.toBeNull();
      if (box) {
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('AC-MOB-001: LandingView 无横向滚动', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);

    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });

  test('AC-MOB-001: Hero 内容全宽显示', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const heroContent = page.locator('.hero-content');
    const box = await heroContent.boundingBox();
    const viewport = page.viewportSize();

    expect(box).not.toBeNull();
    if (box && viewport) {
      // hero-content 宽度应该接近视口宽度（减去 padding）
      expect(box.width).toBeGreaterThan(viewport.width * 0.8);
    }
  });

  test('AC-MOB-001: Features 网格单列', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const featuresGrid = page.locator('.features-grid');
    const gridTemplateColumns = await featuresGrid.evaluate((el) => {
      return window.getComputedStyle(el).gridTemplateColumns;
    });

    // 单列布局应该只有一个列定义
    const columns = gridTemplateColumns.split(' ').filter(c => c.trim());
    expect(columns.length).toBe(1);
  });
});
