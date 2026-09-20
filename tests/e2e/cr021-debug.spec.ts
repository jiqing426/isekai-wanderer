import { test, Page } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const JWT_TOKEN = '***';

test('debug: dump page state', async ({ page }) => {
  await page.goto(`${APP_BASE}/`);
  await page.evaluate((token) => {
    localStorage.setItem('isekai_access_token', token);
  }, JWT_TOKEN);
  await page.goto(`${APP_BASE}/character-chat`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);

  const bodyText = await page.textContent('body');
  console.log('=== BODY TEXT (first 500) ===');
  console.log(bodyText?.substring(0, 500));

  const appHtml = await page.locator('#app').innerHTML();
  console.log('\n=== APP HTML (first 3000) ===');
  console.log(appHtml.substring(0, 3000));

  // Check for any error messages
  const errors = await page.locator('.error, .err, [class*="error"]').count();
  console.log(`\n=== ERROR ELEMENTS: ${errors} ===`);

  // Check character list
  const charList = await page.locator('.character-list').count();
  console.log(`=== .character-list: ${charList} ===`);

  const charItems = await page.locator('.character-item').count();
  console.log(`=== .character-item: ${charItems} ===`);

  const chatWindow = await page.locator('.chat-window').count();
  console.log(`=== .chat-window: ${chatWindow} ===`);

  const chatPage = await page.locator('.character-chat-page').count();
  console.log(`=== .character-chat-page: ${chatPage} ===`);
});
