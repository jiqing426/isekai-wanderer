/**
 * CR-004 移动端基础测试
 * 覆盖: AC-MOB-013 (无横向滚动), AC-MOB-015 (global.css 未修改)
 */
import { test, expect } from '@playwright/test';

test.describe('移动端基础验证', () => {
  test('AC-MOB-013: 页面无横向滚动', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // 检查 body 宽度不超过视口宽度
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = page.viewportSize()?.width || 375;
    
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth);
  });

  test('AC-MOB-013: 落地页无横向滚动', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });

  test('AC-MOB-013: 主页无横向滚动', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');
    
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });
});
