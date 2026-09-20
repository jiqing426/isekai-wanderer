import { test, expect, Page } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJleHAiOjE3ODUyOTE5NjEsInR5cGUiOiJhY2Nlc3MifQ.H4jcUnRm1AjV93mvae13is6zw_39pKi5JN6OB9Mp8wA';

test('Debug CR-022 page state', async ({ page }) => {
  // Inject auth
  await page.goto(`${APP_BASE}/`);
  await page.evaluate((token) => {
    localStorage.setItem('isekai_access_token', token);
  }, JWT_TOKEN);
  await page.goto(`${APP_BASE}/character-chat`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);

  // Check what's on the page
  const bodyText = await page.textContent('body');
  console.log('=== PAGE TEXT (first 1000) ===');
  console.log(bodyText?.substring(0, 1000));

  // Check character items
  const charItems = await page.locator('.character-item').count();
  console.log(`\n=== CHARACTER ITEMS: ${charItems} ===`);

  // Click first character
  if (charItems > 0) {
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);

    // Check for chat-window
    const chatWindow = await page.locator('.chat-window').count();
    console.log(`=== CHAT WINDOW: ${chatWindow} ===`);

    // Check for detail-btn
    const detailBtn = await page.locator('.detail-btn').count();
    console.log(`=== DETAIL BTN: ${detailBtn} ===`);

    // Check for chat-header
    const chatHeader = await page.locator('.chat-header').count();
    console.log(`=== CHAT HEADER: ${chatHeader} ===`);

    // Get chat window HTML
    if (chatWindow > 0) {
      const chatHtml = await page.locator('.chat-window').innerHTML();
      console.log(`\n=== CHAT WINDOW HTML (first 2000) ===`);
      console.log(chatHtml.substring(0, 2000));
    }

    // Check if there's an error or loading state
    const appHtml = await page.locator('#app').innerHTML();
    console.log(`\n=== APP HTML (first 3000) ===`);
    console.log(appHtml.substring(0, 3000));
  }
});
