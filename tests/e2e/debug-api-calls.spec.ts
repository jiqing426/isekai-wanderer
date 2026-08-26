import { test, expect } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJleHAiOjE3ODUyOTgyOTQsInR5cGUiOiJhY2Nlc3MifQ.iM3h840PLgpRc8klLHqrkj6qrPJtO3EqSZbHBR6AZnY';

test('调试 API 调用', async ({ page }) => {
  const apiCalls: { url: string; status: number; body?: any }[] = [];
  
  page.on('response', async response => {
    const url = response.url();
    if (url.includes('/api/v1/')) {
      const status = response.status();
      let body = null;
      try {
        body = await response.json();
      } catch (e) {}
      apiCalls.push({ url, status, body });
    }
  });
  
  // 注入认证
  await page.goto(`${APP_BASE}/`);
  await page.evaluate((token) => {
    localStorage.setItem('isekai_access_token', token);
  }, JWT_TOKEN);
  
  await page.goto(`${APP_BASE}/character-chat`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(5000);
  
  console.log('API 调用列表:');
  apiCalls.forEach(call => {
    console.log(`  ${call.status} ${call.url}`);
    if (call.body) {
      console.log(`    Body: ${JSON.stringify(call.body).substring(0, 200)}`);
    }
  });
  
  // 检查 localStorage
  const token = await page.evaluate(() => localStorage.getItem('isekai_access_token'));
  console.log('Token:', token?.substring(0, 50) + '...');
  
  // 检查页面内容
  const bodyText = await page.textContent('body');
  console.log('页面文本:', bodyText?.substring(0, 500));
});
