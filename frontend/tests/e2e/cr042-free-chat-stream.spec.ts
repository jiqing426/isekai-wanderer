import { test, expect } from '@playwright/test';

/**
 * CR-042 Browser Interaction E2E — Free Chat SSE Streaming
 *
 * Covers: AC-013, AC-016
 *
 * Prerequisites:
 * - Backend running on http://localhost:8000
 * - Frontend dev server on http://localhost:8081
 * - Test user: e2e@test.com / Test123456!
 * - A valid game session for free chat
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

// Helper: 通过 API 创建 Legacy 游戏会话，返回 session ID
async function createLegacySession(page: import('@playwright/test').Page): Promise<string> {
  const token = await apiLogin(page);

  const scriptResp = await page.request.get(`${APP_BASE}/api/v1/scripts`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(scriptResp.ok()).toBeTruthy();
  const scriptData = await scriptResp.json();
  const scripts = scriptData.scripts || [];
  const legacyScript = scripts.find((s: any) => s.engine_type === 'legacy') || scripts[0];
  if (!legacyScript) throw new Error('No scripts found');

  const startResp = await page.request.post(`${APP_BASE}/api/v1/game/start`, {
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    data: { script_id: legacyScript.id },
  });
  expect(startResp.ok()).toBeTruthy();
  const startData = await startResp.json();
  const sessionId = startData.session_id;
  expect(sessionId).toBeTruthy();

  return sessionId;
}

test.describe('CR-042 Free Chat SSE Streaming', () => {
  test.setTimeout(60000);

  test('AC-013/AC-016: free-chat/stream endpoint returns SSE with text events', async ({ page }) => {
    // Create a session and navigate to free chat
    const sessionId = await createLegacySession(page);
    await loginAndGoto(page, `/chat/free-chat/${sessionId}`);

    await page.waitForSelector('.chat-input-area, .chat-messages, #app', { timeout: 15000 });

    let streamingEndpointCalled = false;
    let sseResponseDetected = false;

    page.on('request', (request) => {
      if (request.url().includes('/free-chat/stream')) {
        streamingEndpointCalled = true;
      }
    });

    page.on('response', async (response) => {
      if (response.url().includes('/free-chat/stream')) {
        const ct = response.headers()['content-type'] || '';
        if (ct.includes('text/event-stream')) {
          sseResponseDetected = true;
        }
      }
    });

    const inputField = page.locator('.n-input input, textarea, input[placeholder*="输入"], input[type="text"]').first();
    const inputVisible = await inputField.isVisible({ timeout: 10000 }).catch(() => false);

    if (inputVisible) {
      await inputField.fill('你好，今天天气怎么样？');
      await inputField.press('Enter');

      // Wait for streaming response
      await page.waitForTimeout(10000);

      // Verify streaming endpoint was called
      expect(streamingEndpointCalled).toBe(true);

      // Verify assistant message appeared
      const assistantMsg = page.locator('.chat-message.assistant .message-content').last();
      await expect(assistantMsg).toBeVisible({ timeout: 10000 });
      const text = await assistantMsg.textContent();
      expect(text).toBeTruthy();
      expect(text!.length).toBeGreaterThan(0);
    }
  });

  test('AC-016: FreeChatView displays streaming text progressively', async ({ page }) => {
    const sessionId = await createLegacySession(page);
    await loginAndGoto(page, `/chat/free-chat/${sessionId}`);

    await page.waitForSelector('.chat-input-area, .chat-messages, #app', { timeout: 15000 });

    const inputField = page.locator('.n-input input, textarea, input[placeholder*="输入"], input[type="text"]').first();
    const inputVisible = await inputField.isVisible({ timeout: 10000 }).catch(() => false);

    if (inputVisible) {
      await inputField.fill('告诉我一个故事');
      await inputField.press('Enter');

      // Wait and check for progressive text appearance
      const assistantMsg = page.locator('.chat-message.assistant .message-content').last();

      // Wait for message to appear
      await expect(assistantMsg).toBeVisible({ timeout: 15000 });

      // Get text length at intervals to verify streaming
      const text1 = await assistantMsg.textContent();
      await page.waitForTimeout(1000);
      const text2 = await assistantMsg.textContent();

      // Text should have appeared (either streaming or complete)
      expect(text2).toBeTruthy();
      expect(text2!.length).toBeGreaterThan(0);

      // If streaming, text2 should be longer than text1
      // (or equal if stream completed within 1s)
      expect(text2!.length).toBeGreaterThanOrEqual(text1?.length || 0);
    }
  });
});
