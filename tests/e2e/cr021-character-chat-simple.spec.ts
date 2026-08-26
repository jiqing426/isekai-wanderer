import { test, expect, Page } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJleHAiOjE3ODUyODkyMzQsInR5cGUiOiJhY2Nlc3MifQ.8k1uCpM8K1aBv-_XyTZqMph8f6oRQLsMpieBSQ5pHgA';

async function injectAuth(page: Page) {
  await page.goto(`${APP_BASE}/`);
  await page.evaluate((token) => {
    localStorage.setItem('isekai_access_token', token);
  }, JWT_TOKEN);
  await page.goto(`${APP_BASE}/character-chat`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
}

test.describe('CR-021 Character Chat - Core Verification', () => {

  test('AC-FE-001: Page loads', async ({ page }) => {
    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');
    const text = await page.textContent('body');
    expect(text).toContain('角色');
    console.log('✅ AC-FE-001 PASS');
  });

  test('AC-FE-002: Character list renders', async ({ page }) => {
    await injectAuth(page);
    const count = await page.locator('.character-item').count();
    expect(count).toBeGreaterThan(0);
    console.log(`✅ AC-FE-002 PASS: ${count} characters`);
  });

  test('AC-FE-003: Chat window renders', async ({ page }) => {
    await injectAuth(page);
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(1500);
    expect(await page.locator('.chat-window').isVisible()).toBeTruthy();
    console.log('✅ AC-FE-003 PASS');
  });

  test('AC-FE-004: Message list renders', async ({ page }) => {
    await injectAuth(page);
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(1500);
    expect(await page.locator('.message-list').isVisible()).toBeTruthy();
    console.log('✅ AC-FE-004 PASS');
  });

  test('AC-FE-005: Topics section exists', async ({ page }) => {
    await injectAuth(page);
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);
    const html = await page.locator('.chat-window').innerHTML();
    expect(html).toContain('topics-section');
    console.log('✅ AC-FE-005 PASS');
  });

  test('AC-FE-006: Input bar renders', async ({ page }) => {
    await injectAuth(page);
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(1500);
    expect(await page.locator('.input-bar').isVisible()).toBeTruthy();
    expect(await page.locator('.input-bar input').isVisible()).toBeTruthy();
    expect(await page.locator('.plus-btn').isVisible()).toBeTruthy();
    expect(await page.locator('.send-btn').isVisible()).toBeTruthy();
    console.log('✅ AC-FE-006 PASS');
  });

  test('AC-FE-010: API via proxy', async ({ page }) => {
    const calls: string[] = [];
    page.on('response', r => {
      if (r.url().includes('/api/v1/character-chat') || r.url().includes('/api/v1/characters')) {
        calls.push(r.url());
      }
    });
    await injectAuth(page);
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(3000);
    expect(calls.length).toBeGreaterThan(0);
    expect(calls.every(u => u.startsWith(`${APP_BASE}/api/`))).toBeTruthy();
    console.log(`✅ AC-FE-010 PASS: ${calls.length} calls via proxy`);
  });

  test('AC-FE-012: Route works', async ({ page }) => {
    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');
    expect(page.url()).toContain('/character-chat');
    console.log('✅ AC-FE-012 PASS');
  });

  test('AC-FE-013: Header tab', async ({ page }) => {
    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');
    const link = page.locator('a.nav-link[href="/character-chat"]');
    expect(await link.isVisible()).toBeTruthy();
    expect(await link.evaluate(el => el.classList.contains('active'))).toBeTruthy();
    console.log('✅ AC-FE-013 PASS');
  });

  test('AC-FE-014: Responsive', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await injectAuth(page);
    expect(await page.locator('.chat-container').isVisible()).toBeTruthy();
    
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    expect(await page.locator('.character-chat-page').isVisible()).toBeTruthy();
    console.log('✅ AC-FE-014 PASS');
  });
});
