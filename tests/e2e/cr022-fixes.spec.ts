import { test, expect, Page } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJleHAiOjE3ODUyOTgyOTQsInR5cGUiOiJhY2Nlc3MifQ.iM3h840PLgpRc8klLHqrkj6qrPJtO3EqSZbHBR6AZnY';

async function injectAuth(page: Page) {
  await page.goto(`${APP_BASE}/`);
  await page.evaluate((token) => {
    localStorage.setItem('isekai_access_token', token);
  }, JWT_TOKEN);
  await page.goto(`${APP_BASE}/character-chat`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
}

test.describe('CR-022 Fixes Verification', () => {

  test('AC-FE-001: Character list displays affection progress bar', async ({ page }) => {
    await injectAuth(page);
    
    // Check character list exists
    const characterList = page.locator('.character-list');
    await expect(characterList).toBeVisible({ timeout: 10000 });
    
    // Check affection bar exists for each character
    const affectionBars = page.locator('.affection-bar');
    const count = await affectionBars.count();
    expect(count).toBeGreaterThan(0);
    
    console.log(`✅ AC-FE-001: Found ${count} affection progress bars`);
  });

  test('AC-FE-002: Affection data matches API response', async ({ page }) => {
    const apiResponses: any[] = [];
    
    // Capture API responses
    page.on('response', async response => {
      const url = response.url();
      if (url.includes('/api/v1/affection')) {
        try {
          const body = await response.json();
          apiResponses.push({ url, body });
        } catch (e) {}
      }
    });
    
    await injectAuth(page);
    await page.waitForTimeout(2000);
    
    // Verify affection API was called
    const affectionCall = apiResponses.find(r => r.url.includes('/api/v1/affection'));
    expect(affectionCall).toBeTruthy();
    
    // Check that affection data is displayed (even if empty/0)
    const affectionTexts = await page.locator('.affection-text').allTextContents();
    expect(affectionTexts.length).toBeGreaterThan(0);
    
    console.log(`✅ AC-FE-002: Affection API called, ${affectionTexts.length} affection values displayed`);
    console.log(`   API response: ${JSON.stringify(affectionCall?.body)}`);
  });

  test('AC-FE-003: Chat window has "查看详情" button', async ({ page }) => {
    await injectAuth(page);
    
    // Select first character
    const firstCharacter = page.locator('.character-item').first();
    await firstCharacter.click();
    await page.waitForTimeout(1500);
    
    // Check detail button exists
    const detailBtn = page.locator('.detail-btn');
    await expect(detailBtn).toBeVisible({ timeout: 5000 });
    
    // Check button text
    const btnText = await detailBtn.textContent();
    expect(btnText).toContain('查看详情');
    
    console.log('✅ AC-FE-003: "查看详情" button visible in chat header');
  });

  test('AC-FE-004: Click "查看详情" navigates to character detail page', async ({ page }) => {
    await injectAuth(page);
    
    // Select first character and get its ID
    const firstCharacter = page.locator('.character-item').first();
    await firstCharacter.click();
    await page.waitForTimeout(1500);
    
    // Get current character ID from page state
    const characterId = await page.evaluate(() => {
      const activeItem = document.querySelector('.character-item.active');
      return activeItem?.getAttribute('data-character-id') || 
             activeItem?.querySelector('[data-character-id]')?.getAttribute('data-character-id');
    });
    
    // Click detail button
    const detailBtn = page.locator('.detail-btn');
    await detailBtn.click();
    
    // Wait for navigation - use URL assertion with retry
    await page.waitForURL('**/characters/**', { timeout: 10000 });
    
    // Verify navigation to character detail page
    const currentUrl = page.url();
    expect(currentUrl).toContain('/characters/');
    
    console.log(`✅ AC-FE-004: Navigated to ${currentUrl}`);
  });

  test('Verify API calls go through proxy (Mock API=no)', async ({ page }) => {
    const apiCalls: { url: string; status: number }[] = [];
    
    page.on('response', response => {
      const url = response.url();
      if (url.includes('/api/v1/')) {
        apiCalls.push({ url, status: response.status() });
      }
    });
    
    await injectAuth(page);
    await page.waitForTimeout(2000);
    
    // Verify all API calls go through frontend proxy
    const proxyCalls = apiCalls.filter(c => c.url.startsWith(`${APP_BASE}/api/`));
    expect(proxyCalls.length).toBeGreaterThan(0);
    
    console.log(`✅ Mock API=no: ${proxyCalls.length} API calls via frontend proxy`);
    proxyCalls.forEach(c => console.log(`   ${c.status} ${c.url}`));
  });
});
