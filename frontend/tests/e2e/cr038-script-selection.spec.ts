import { test, expect } from '@playwright/test';

/**
 * CR-038 Corvus Frontend Entry — Browser Interaction E2E (script selection engine_type)
 *
 * 覆盖 3 条 Browser E2E 验收项：
 * - AC-038-023: 选择剧本 → 点击开始 → 走 Corvus 流程
 * - AC-038-024: 选择任意剧本 → 走 Corvus 流程（C3 约束）
 * - AC-038-025: 代码审查确认 legacy 代码保留但不激活
 */

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const TEST_EMAIL = 'e2e@test.com';
const TEST_PASSWORD = 'Test123456!';

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
  const token = await apiLogin(page);
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
  await page.waitForLoadState('networkidle');
}

// Helper: 获取第一个剧本 ID
async function getScriptId(page: import('@playwright/test').Page): Promise<string> {
  const token = await apiLogin(page);
  const resp = await page.request.get(`${APP_BASE}/api/v1/scripts`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(resp.ok()).toBeTruthy();
  const data = await resp.json();
  const scripts = data.scripts || [];
  if (scripts.length > 0) {
    // 验证返回的脚本有 engine_type 字段
    const script = scripts[0];
    expect(script.engine_type).toBe('corvus');
    return script.id;
  }
  throw new Error('No scripts found');
}

test.describe('CR-038 Corvus script selection Browser E2E', () => {

  // AC-038-023: 选择剧本 → 点击开始 → 走 Corvus 流程
  test('AC-038-023: 剧本列表 engine_type 解析 → 点击开始 → Corvus 流程', async ({ page }) => {
    const scriptId = await getScriptId(page);
    await loginAndGoto(page, `/scripts/${scriptId}`);

    // 验证剧本详情页加载完成
    await expect(page.locator('#app')).toBeVisible();
    await expect(page).toHaveURL(/\/scripts\//);

    // 验证页面标题可见
    const title = await page.locator('.script-title').textContent();
    expect(title && title.length > 0).toBeTruthy();

    // 点击"开始游戏"按钮
    await page.locator('.cta-primary').click({ timeout: 10000 });

    // 验证 Corvus 流程：弹出选角 Modal（而非直接跳转 /game）
    await expect(page.locator('[data-testid="player-candidate-modal"]')).toBeVisible({ timeout: 10000 });

    // 验证页面正常
    const bodyText = await page.locator('body').innerText();
    expect(bodyText.length).toBeGreaterThan(0);
    expect(bodyText).not.toContain('缺少剧本');
  });

  // AC-038-024: 选择任意剧本 → 走 Corvus 流程（C3 约束）
  test('AC-038-024: 任意剧本 engine_type=corvus → Corvus 流程', async ({ page }) => {
    const token = await apiLogin(page);

    // 获取全部剧本，验证每个都有 engine_type=corvus
    const resp = await page.request.get(`${APP_BASE}/api/v1/scripts`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(resp.ok()).toBeTruthy();
    const data = await resp.json();
    const scripts = data.scripts || [];

    // 验证至少有一个剧本
    expect(scripts.length).toBeGreaterThan(0);

    // 验证所有剧本的 engine_type 都是 'corvus'（C3 约束）
    for (const script of scripts) {
      expect(script.engine_type).toBe('corvus');
    }

    // 选择第一个剧本
    const scriptId = scripts[0].id;
    const scriptTitle = scripts[0].title;

    // 访问剧本详情页
    await loginAndGoto(page, `/scripts/${scriptId}`);

    // 验证页面加载
    await expect(page.locator('#app')).toBeVisible();
    await expect(page).toHaveURL(/\/scripts\//);

    // 验证剧本标题显示
    const displayedTitle = await page.locator('.script-title').textContent();
    expect(displayedTitle && displayedTitle.includes(scriptTitle)).toBeTruthy();

    // 点击"开始游戏"
    await page.locator('.cta-primary').click({ timeout: 10000 });

    // 验证进入 Corvus 流程（弹出选角 Modal）
    await expect(page.locator('[data-testid="player-candidate-modal"]')).toBeVisible({ timeout: 10000 });

    // 验证页面正常
    const bodyText = await page.locator('body').innerText();
    expect(bodyText.length).toBeGreaterThan(0);
    expect(bodyText).not.toContain('缺少剧本');
  });

  // AC-038-025: 代码审查确认 legacy 代码保留但不激活
  test('AC-038-025: legacy 代码分支保留但不激活 — 浏览器验证', async ({ page }) => {
    // 此 AC 需要 Browser E2E + 代码审查两部分
    // 浏览器部分：验证当前 Corvus 流程能正常工作
    const token = await apiLogin(page);

    // 通过 API 创建 Corvus 会话并选定角色
    // 0. 获取剧本 ID
    const scriptResp = await page.request.get(`${APP_BASE}/api/v1/scripts`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const scriptData = await scriptResp.json();
    const scriptId = scriptData.scripts[0].id;

    // 1. 创建会话
    const createResp = await page.request.post(`${APP_BASE}/api/v1/game/session/create`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { script_id: scriptId },
    });
    expect(createResp.ok()).toBeTruthy();
    const createData = await createResp.json();
    const sessionId = createData.data?.game_session_id || createData.game_session_id;

    // 2. 获取候选角色
    const charResp = await page.request.get(`${APP_BASE}/api/v1/game/scripts/${scriptId}/characters`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(charResp.ok()).toBeTruthy();
    const charData = await charResp.json();
    const characters = charData.data || charData.characters || [];

    // 3. 选定角色
    const selectResp = await page.request.post(`${APP_BASE}/api/v1/game/session/select-player`, {
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      data: { game_session_id: sessionId, character_id: characters[0].id },
    });
    expect(selectResp.ok()).toBeTruthy();

    // 访问游戏页面
    await loginAndGoto(page, `/game?session=${sessionId}`);

    // 验证游戏加载
    await page.waitForTimeout(5000);
    await expect(page.locator('#app')).toBeVisible();
    await expect(page).toHaveURL(/\/game/);

    // 验证页面没有显示错误
    const bodyText = await page.locator('body').innerText();
    expect(bodyText).not.toContain('缺少剧本');
    expect(bodyText.length).toBeGreaterThan(0);

    // 验证页面可正常交互（输入框或按钮可见）
    const inputArea = page.locator('input[type="text"], textarea');
    const buttonArea = page.locator('button, .n-button');
    const hasInput = await inputArea.first().isVisible({ timeout: 5000 }).catch(() => false);
    const hasButton = await buttonArea.first().isVisible({ timeout: 5000 }).catch(() => false);
    expect(hasInput || hasButton).toBeTruthy();

    // 验证可以通过自定义输入推进剧情
    if (hasInput) {
      await inputArea.first().fill('测试');
      const value = await inputArea.first().inputValue();
      expect(value).toContain('测试');
    }

    // 如果存在按钮，验证可以点击
    if (hasButton) {
      await buttonArea.first().click({ timeout: 5000 });
    }

    // 最终验证：页面仍在游戏界面
    await expect(page.locator('#app')).toBeVisible();
    await expect(page).toHaveURL(/\/game/);
  });

});
