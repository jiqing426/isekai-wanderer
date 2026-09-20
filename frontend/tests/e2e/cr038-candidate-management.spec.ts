import { test, expect } from '@playwright/test';

/**
 * CR-038 Corvus Frontend Entry — Browser Interaction E2E (preset character selection)
 *
 * 改造 (2026-09-07): 移除创建表单测试，改为预设角色选择测试
 * 覆盖 3 条 Browser E2E 验收项：
 * - AC-038-010: 选角列表展示（预设角色卡片）
 * - AC-038-012: 查看预设角色列表
 * - AC-038-016: 选择预设角色进入游戏
 */

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const TEST_EMAIL = 'e2e@test.com';
const TEST_PASSWORD = 'Test123456!';

async function apiLogin(page: import('@playwright/test').Page): Promise<string> {
  const resp = await page.request.post(`${APP_BASE}/api/v1/auth/login`, {
    data: { email: TEST_EMAIL, password: TEST_PASSWORD },
  });
  expect(resp.ok()).toBeTruthy();
  const body = await resp.json();
  return body.access_token;
}

async function loginAndGoto(page: import('@playwright/test').Page, path: string) {
  const resp = await page.request.post(`${APP_BASE}/api/v1/auth/login`, {
    data: { email: TEST_EMAIL, password: TEST_PASSWORD },
  });
  const body = await resp.json();
  await page.context().addCookies([
    { name: 'isekai_access_token', value: encodeURIComponent(body.access_token), domain: 'localhost', path: '/', expires: Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60 },
    { name: 'isekai_refresh_token', value: encodeURIComponent(body.refresh_token), domain: 'localhost', path: '/', expires: Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60 },
  ]);
  await page.goto(`${APP_BASE}${path}`);
  await page.waitForLoadState('networkidle');
}

async function getScriptId(page: import('@playwright/test').Page): Promise<string> {
  const token = await apiLogin(page);
  const resp = await page.request.get(`${APP_BASE}/api/v1/scripts`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await resp.json();
  const scripts = data.scripts || [];
  if (scripts.length > 0) {
    expect(scripts[0].engine_type).toBe('corvus');
    return scripts[0].id;
  }
  throw new Error('No scripts found');
}

test.describe('CR-038 Corvus preset character selection Browser E2E', () => {

  // AC-038-010: 选角列表展示
  test('AC-038-010: 选角页面加载 → 可见预设角色卡片列表', async ({ page }) => {
    const scriptId = await getScriptId(page);
    await loginAndGoto(page, `/scripts/${scriptId}`);

    await page.locator('.cta-primary').click({ timeout: 10000 });
    await expect(page.locator('[data-testid="player-candidate-modal"]')).toBeVisible({ timeout: 10000 });

    const cards = await page.locator('[data-testid="script-character-card"]').count();
    expect(cards).toBeGreaterThan(0);
  });

  // AC-038-012: 查看预设角色列表
  test('AC-038-012: 打开选角界面 → 可见预设角色卡片列表', async ({ page }) => {
    const scriptId = await getScriptId(page);
    await loginAndGoto(page, `/scripts/${scriptId}`);

    await page.locator('.cta-primary').click({ timeout: 10000 });
    await expect(page.locator('[data-testid="player-candidate-modal"]')).toBeVisible({ timeout: 10000 });

    const cards = await page.locator('[data-testid="script-character-card"]').count();
    expect(cards).toBeGreaterThan(0);

    // 验证角色卡片有名字
    const firstName = await page.locator('[data-testid="script-character-card"] .candidate-name').first().textContent();
    expect(firstName).toBeTruthy();
  });

  // AC-038-016: 选择预设角色进入游戏
  test('AC-038-016: 点击角色 → 确认 → 进入游戏界面', async ({ page }) => {
    const scriptId = await getScriptId(page);
    await loginAndGoto(page, `/scripts/${scriptId}`);

    await page.locator('.cta-primary').click({ timeout: 10000 });
    await expect(page.locator('[data-testid="player-candidate-modal"]')).toBeVisible({ timeout: 10000 });

    await page.locator('[data-testid="script-character-card"]').first().click({ timeout: 10000 });
    await page.locator('[data-testid="select-candidate-confirm-btn"]').click({ timeout: 10000 });

    await expect(page, { timeout: 15000 }).toHaveURL(/\/game/);
    await expect(page.locator('#app')).toBeVisible();
  });

});
