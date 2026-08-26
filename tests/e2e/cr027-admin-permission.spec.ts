/**
 * CR-027 T-008: Admin Permission E2E Tests
 * 
 * 验收标准：
 * - AC-ADMIN-004: 非管理员无法访问管理页（403）
 * 
 * 测试环境：
 * - 前端入口：http://localhost:3100
 * - 后端地址：http://localhost:8000
 * - API 代理：/api → http://localhost:8000
 * - Mock API：no
 */

import { test, expect } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:3100';
const NON_ADMIN_EMAIL = 'user@test.com';
const NON_ADMIN_PASSWORD = 'user123456';

test.describe('CR-027 Admin Permission E2E', () => {
  test('AC-ADMIN-004: 非管理员无法访问 Lorebook 管理页', async ({ page }) => {
    // 使用非管理员账户登录
    await page.goto(`${APP_BASE}/login`);
    await page.waitForLoadState('networkidle');
    
    await page.locator('.n-input input[type="email"]').fill(NON_ADMIN_EMAIL);
    await page.locator('.n-input input[type="password"]').fill(NON_ADMIN_PASSWORD);
    await page.locator('button:has-text("登录")').click();
    
    // 非管理员应该被拒绝或重定向
    await page.waitForTimeout(2000);

    // 尝试直接导航到 Lorebook 管理页
    await page.goto(`${APP_BASE}/lorebook`);
    await page.waitForLoadState('networkidle');

    // 验证被重定向到登录页或首页，或显示权限错误
    const url = page.url();
    const isRedirected = url.includes('/login') || url === `${APP_BASE}/`;
    
    // 或者检查是否有权限错误提示
    const hasPermissionError = await page.locator('text=没有权限, text=权限不足, text=403, text=该账号没有管理员权限').count() > 0;
    
    expect(isRedirected || hasPermissionError).toBeTruthy();
  });

  test('AC-ADMIN-004: 非管理员无法访问场景配置页', async ({ page }) => {
    await page.goto(`${APP_BASE}/login`);
    await page.waitForLoadState('networkidle');
    
    await page.locator('.n-input input[type="email"]').fill(NON_ADMIN_EMAIL);
    await page.locator('.n-input input[type="password"]').fill(NON_ADMIN_PASSWORD);
    await page.locator('button:has-text("登录")').click();
    await page.waitForTimeout(2000);

    // 尝试导航到场景配置页
    await page.goto(`${APP_BASE}/scene-config`);
    await page.waitForLoadState('networkidle');

    // 验证被重定向或显示权限错误
    const url = page.url();
    const isRedirected = url.includes('/login') || url === `${APP_BASE}/`;
    const hasPermissionError = await page.locator('text=没有权限, text=权限不足, text=403, text=该账号没有管理员权限').count() > 0;
    
    expect(isRedirected || hasPermissionError).toBeTruthy();
  });

  test('AC-ADMIN-004: 非管理员无法访问角色编辑页', async ({ page }) => {
    await page.goto(`${APP_BASE}/login`);
    await page.waitForLoadState('networkidle');
    
    await page.locator('.n-input input[type="email"]').fill(NON_ADMIN_EMAIL);
    await page.locator('.n-input input[type="password"]').fill(NON_ADMIN_PASSWORD);
    await page.locator('button:has-text("登录")').click();
    await page.waitForTimeout(2000);

    // 尝试导航到角色编辑页
    await page.goto(`${APP_BASE}/characters/some-character-id`);
    await page.waitForLoadState('networkidle');

    // 验证被重定向或显示权限错误
    const url = page.url();
    const isRedirected = url.includes('/login') || url === `${APP_BASE}/`;
    const hasPermissionError = await page.locator('text=没有权限, text=权限不足, text=403, text=该账号没有管理员权限').count() > 0;
    
    expect(isRedirected || hasPermissionError).toBeTruthy();
  });

  test('AC-ADMIN-004: 非管理员访问管理页时 API 返回 403', async ({ request }) => {
    // 使用非管理员账户登录获取 token
    const loginResponse = await request.post(`${APP_BASE}/api/v1/auth/login`, {
      data: {
        email: NON_ADMIN_EMAIL,
        password: NON_ADMIN_PASSWORD,
      },
    });
    
    expect(loginResponse.ok()).toBeTruthy();
    const loginData = await loginResponse.json();
    const accessToken = loginData.access_token;
    expect(accessToken).toBeTruthy();

    // 尝试访问 Lorebook API
    const lorebookResponse = await request.get(`${APP_BASE}/api/v1/lorebook`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    // 验证返回 403
    expect(lorebookResponse.status()).toBe(403);

    // 尝试访问 Scene Config API
    const sceneConfigResponse = await request.get(`${APP_BASE}/api/v1/scene-configs`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    // 验证返回 403
    expect(sceneConfigResponse.status()).toBe(403);
  });
});
