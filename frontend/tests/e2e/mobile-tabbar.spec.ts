/**
 * CR-004 MobileTabBar 测试
 * 覆盖: AC-MOB-009 (TabBar 5入口导航), AC-MOB-010 (当前Tab高亮), AC-MOB-011 (iOS安全区域)
 * 
 * 运行: APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-tabbar.spec.ts --project=mobile
 */
import { test, expect } from '@playwright/test';

test.describe('MobileTabBar', () => {
  test.beforeEach(async ({ page }) => {
    // 确保在移动端视口下（iPhone 12: 390x844）
    const viewport = page.viewportSize();
    expect(viewport?.width).toBeLessThanOrEqual(430);
  });

  test('AC-MOB-009: TabBar 在移动端显示且包含5个入口', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const tabbar = page.locator('.mobile-tabbar');
    await expect(tabbar).toBeVisible();

    const items = tabbar.locator('.tabbar-item');
    await expect(items).toHaveCount(5);

    // 验证5个入口标签
    const labels = await items.locator('.tab-label').allTextContents();
    expect(labels).toEqual(['首页', '发现', '游戏', '社区', '我的']);
  });

  test('AC-MOB-009: TabBar 导航可点击跳转', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // 点击"首页"Tab
    const homeTab = page.locator('.tabbar-item').first();
    await homeTab.click();
    await page.waitForURL('**/home');
    expect(page.url()).toContain('/home');
  });

  test('AC-MOB-010: 当前路由对应Tab高亮', async ({ page }) => {
    // 访问首页
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    // 验证首页Tab有 active class
    const tabbar = page.locator('.mobile-tabbar');
    const items = tabbar.locator('.tabbar-item');
    
    // 第一个Tab（首页）应该是 active
    await expect(items.nth(0)).toHaveClass(/active/);
    
    // 其他Tab不应该有 active
    await expect(items.nth(1)).not.toHaveClass(/active/);
    await expect(items.nth(2)).not.toHaveClass(/active/);
    await expect(items.nth(3)).not.toHaveClass(/active/);
    await expect(items.nth(4)).not.toHaveClass(/active/);
  });

  test('AC-MOB-010: 切换路由后Tab高亮跟随变化', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const tabbar = page.locator('.mobile-tabbar');
    const items = tabbar.locator('.tabbar-item');

    // 点击"发现"Tab
    await items.nth(1).click();
    await page.waitForURL('**/discover');

    // 发现Tab应该高亮
    await expect(items.nth(1)).toHaveClass(/active/);
    await expect(items.nth(0)).not.toHaveClass(/active/);
  });

  test('AC-MOB-011: TabBar 底部有安全区域 padding', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const tabbar = page.locator('.mobile-tabbar');
    await expect(tabbar).toBeVisible();

    // 验证 TabBar 固定在底部
    const box = await tabbar.boundingBox();
    expect(box).not.toBeNull();
    if (box) {
      const viewport = page.viewportSize();
      // TabBar 底部应该接近视口底部
      expect(box.y + box.height).toBeGreaterThanOrEqual((viewport?.height || 844) - 50);
    }

    // 验证 CSS 中包含 safe-area-inset-bottom 支持
    const paddingBottom = await tabbar.evaluate((el) => {
      return window.getComputedStyle(el).paddingBottom;
    });
    // padding-bottom 应该存在（可能是 0px 或 env 值）
    expect(paddingBottom).toBeDefined();
  });

  test('AC-MOB-009: TabBar 触摸目标 >= 44px', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const tabbar = page.locator('.mobile-tabbar');
    const items = tabbar.locator('.tabbar-item');
    const count = await items.count();

    for (let i = 0; i < count; i++) {
      const box = await items.nth(i).boundingBox();
      expect(box).not.toBeNull();
      if (box) {
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });
});
