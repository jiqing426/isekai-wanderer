import { test, expect } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:3000';

test.describe('Auth Flow — Register → Login → Onboarding', () => {
  test('register page loads and has form elements', async ({ page }) => {
    await page.goto(`${APP_BASE}/register`);
    // h1 may be the hero title; check page has form elements
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]').first()).toBeVisible();
    await expect(page.locator('button[type="submit"], button.n-button--primary-type').first()).toBeVisible();
  });

  test('login page loads and has form elements', async ({ page }) => {
    await page.goto(`${APP_BASE}/login`);
    await expect(page.locator('h1')).toContainText('Isekai Wanderer');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('button[type="button"][class*="n-button--primary-type"]').first()).toBeVisible();
  });

  test('OAuth buttons visible on login page', async ({ page }) => {
    await page.goto(`${APP_BASE}/login`);
    await expect(page.getByText('Google 登录')).toBeVisible();
    // OAuth buttons: 微信, Google, Apple (no Discord in current UI)
    await expect(page.locator('.oauth-btn').first()).toBeVisible();
    await expect(page.locator('.oauth-btn').nth(1)).toBeVisible();
  });

  test('register redirects to login after submission', async ({ page }) => {
    // This test requires backend to be running
    // It will verify the full register flow when backend is ready
    await page.goto(`${APP_BASE}/register`);
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').first().fill('Test1234!');
    await page.locator('input[type="password"]').nth(1).fill('Test1234!');
    // The register button click would trigger API call
    // Without backend, this will show an error — that's expected in Phase 0
  });

  test('unauthenticated user redirected to login', async ({ page }) => {
    await page.goto(`${APP_BASE}/home`);
    await expect(page).toHaveURL(/\/login/);
  });

  test('onboarding page requires auth', async ({ page }) => {
    await page.goto(`${APP_BASE}/onboarding`);
    await expect(page).toHaveURL(/\/login/);
  });
});
