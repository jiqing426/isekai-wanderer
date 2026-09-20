import { test } from '@playwright/test';

const APP_BASE = 'http://localhost:8081';
const JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJleHAiOjE3ODUyOTM5MDcsInR5cGUiOiJhY2Nlc3MifQ.aycF1wGnreec-4oAzYJSW6lnNPRKgxyDXR7YAM4A4N4';

test('debug: inspect chat window structure', async ({ page }) => {
  await page.goto(APP_BASE);
  await page.evaluate((token) => {
    localStorage.setItem('isekai_access_token', token);
  }, JWT_TOKEN);
  await page.goto(`${APP_BASE}/character-chat`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);

  // Select first character
  await page.locator('.character-item').first().click();
  await page.waitForTimeout(2000);

  // Dump chat window HTML
  const chatHtml = await page.locator('.chat-window').innerHTML();
  console.log('=== CHAT WINDOW HTML ===');
  console.log(chatHtml.substring(0, 5000));

  // Check input elements
  const inputs = await page.locator('input').count();
  console.log(`\n=== ALL INPUTS: ${inputs} ===`);
  
  const inputInfo = await page.locator('input').evaluateAll(els => 
    els.map(el => ({ type: el.type, placeholder: el.placeholder, class: el.className }))
  );
  console.log('Input details:', JSON.stringify(inputInfo, null, 2));

  // Check plus menu structure
  await page.locator('.plus-btn').click();
  await page.waitForTimeout(500);
  const menuHtml = await page.locator('.plus-menu').innerHTML();
  console.log('\n=== PLUS MENU HTML ===');
  console.log(menuHtml);
  
  // Check detail page
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
  await page.locator('.detail-btn').click();
  await page.waitForTimeout(3000);
  
  const detailHtml = await page.locator('#app').innerHTML();
  console.log('\n=== DETAIL PAGE HTML (first 2000) ===');
  console.log(detailHtml.substring(0, 2000));
});
