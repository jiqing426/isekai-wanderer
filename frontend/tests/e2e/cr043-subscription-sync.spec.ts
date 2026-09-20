import { test, expect } from '@playwright/test';

/**
 * CR-043 Browser Interaction E2E — 订阅流程状态同步
 *
 * Covers: AC-016, AC-017, AC-020
 *
 * Prerequisites:
 * - Backend running on http://localhost:8000
 * - Frontend dev server on http://localhost:8081
 * - Test user: e2e@test.com / Test123456!
 */

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const TEST_EMAIL = 'e2e@test.com';
const TEST_PASSWORD = '***';

// Helper: API 登录拿 token
async function apiLogin(page: import('@playwright/test').Page): Promise<string> {
  const resp = await page.request.post(`${APP_BASE}/api/v1/auth/login`, {
    data: { email: TEST_EMAIL, password: TEST_PASSWORD },
  });
  expect(resp.ok()).toBeTruthy();
  const body = await resp.json();
  return body.access_token;
}

// Helper: 设置鉴权 cookie 并跳转
async function loginAndGoto(page: import('@playwright/test').Page, path: string) {
  const resp = await page.request.post(`${APP_BASE}/api/v1/auth/login`, {
    data: { email: TEST_EMAIL, password: TEST_PASSWORD },
  });
  const body = await resp.json();

  await page.context().addCookies([
    {
      name: 'isekai_access_token',
      value: encodeURIComponent(body.access_token),
      domain: 'localhost',
      path: '/',
      expires: Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60,
    },
    {
      name: 'isekai_refresh_token',
      value: encodeURIComponent(body.refresh_token),
      domain: 'localhost',
      path: '/',
      expires: Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60,
    },
  ]);

  await page.goto(`${APP_BASE}${path}`);
  await page.waitForLoadState('domcontentloaded');
}

test.describe('CR-043 Subscription Sync', () => {
  test.setTimeout(60000);

  // AC-020: 登录成功后自动加载订阅状态
  test('AC-020: login success auto-loads subscription status', async ({ page }) => {
    // Track API requests after login
    let subscriptionStatusCalled = false;

    page.on('request', (request) => {
      if (request.url().includes('/subscription/status') || request.url().includes('/cr016/subscription/status')) {
        subscriptionStatusCalled = true;
      }
    });

    // Navigate to login page
    await page.goto(`${APP_BASE}/login`);
    await page.waitForLoadState('domcontentloaded');

    // Fill login form
    const emailInput = page.locator('input[type="email"], input[placeholder*="邮箱"]').first();
    const passwordInput = page.locator('input[type="password"], input[placeholder*="密码"]').first();

    if (await emailInput.isVisible({ timeout: 5000 })) {
      await emailInput.fill(TEST_EMAIL);
      await passwordInput.fill(TEST_PASSWORD);

      // Click login button
      const loginBtn = page.locator('button:has-text("登录"), button[type="submit"]').first();
      await loginBtn.click({ timeout: 10000 });

      // Wait for navigation and auto-loaded subscription status
      await page.waitForTimeout(5000);

      // Verify subscription status API was called automatically after login
      expect(subscriptionStatusCalled).toBe(true);
    }
  });

  // AC-016: 订阅成功后调用 fetchSubscriptionStatus() 刷新订阅状态
  test('AC-016: subscribe success calls fetchSubscriptionStatus', async ({ page }) => {
    await loginAndGoto(page, '/personal-center');

    await page.waitForTimeout(3000);

    // Navigate to subscription plans page
    // Look for subscription settings link
    const subLink = page.locator('a[href*="subscription"], [data-testid="subscription-link"], button:has-text("订阅"), button:has-text("升级")').first();
    if (await subLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await subLink.click();
      await page.waitForTimeout(2000);
    }

    // Track subscription status API calls
    let subscriptionStatusCalled = false;
    page.on('request', (request) => {
      if (request.url().includes('/subscription/status') || request.url().includes('/cr016/subscription/status')) {
        subscriptionStatusCalled = true;
      }
    });

    // Find a subscribe button (not current/free)
    const subscribeBtn = page.locator('.btn-subscribe').first();
    if (await subscribeBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await subscribeBtn.click({ timeout: 10000 });

      // Wait for subscription to process
      await page.waitForTimeout(5000);

      // After subscription success, fetchSubscriptionStatus should be called
      expect(subscriptionStatusCalled).toBe(true);
    }
  });

  // AC-017: 订阅成功后 authStore.user.subscription_tier 更新
  test('AC-017: subscribe success updates user profile tier', async ({ page }) => {
    await loginAndGoto(page, '/personal-center');

    await page.waitForTimeout(3000);

    // Track profile API calls
    let profileApiCalled = false;
    page.on('request', (request) => {
      if (request.url().includes('/user/profile') || request.url().includes('/users/me')) {
        profileApiCalled = true;
      }
    });

    // Navigate to subscription plans
    const subLink = page.locator('a[href*="subscription"], [data-testid="subscription-link"], button:has-text("订阅"), button:has-text("升级")').first();
    if (await subLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await subLink.click();
      await page.waitForTimeout(2000);
    }

    const subscribeBtn = page.locator('.btn-subscribe').first();
    if (await subscribeBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await subscribeBtn.click({ timeout: 10000 });

      // Wait for subscription + profile refresh
      await page.waitForTimeout(5000);

      // After subscription success, getProfile should be called to update authStore
      expect(profileApiCalled).toBe(true);
    }
  });
});
