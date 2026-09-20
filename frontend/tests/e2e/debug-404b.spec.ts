import { test, expect, Page } from '@playwright/test';

test('debug: 游戏页面所有4xx请求', async ({ page }) => {
  const failedRequests: string[] = [];
  
  page.on('response', (response) => {
    const status = response.status();
    if (status >= 400) {
      const method = response.request().method();
      failedRequests.push(`${status} ${method} ${response.url().replace('http://localhost:8081', '')}`);
    }
  });

  // 先注册/登录
  await page.goto('http://localhost:8081/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'Test123456!');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000);

  // 导航到剧本详情并开始 Corvus 游戏
  await page.goto('http://localhost:8081/scripts');
  await page.waitForTimeout(2000);
  
  // 获取第一个剧本链接
  const scriptLink = page.locator('a[href*="/scripts/"]').first();
  await scriptLink.click();
  await page.waitForTimeout(2000);
  
  // 点击开始游戏
  const startBtn = page.locator('text=🎮 开始游戏').first();
  await startBtn.click();
  await page.waitForTimeout(2000);
  
  // 选角
  const candidateCard = page.locator('[data-testid="candidate-card"]').first();
  if (await candidateCard.isVisible()) {
    await candidateCard.click();
    await page.locator('[data-testid="select-candidate-confirm-btn"]').click();
    await page.waitForTimeout(8000);
  }
  
  // 在游戏页面停留，捕获所有请求
  await page.waitForTimeout(10000);
  
  console.log('--- ALL FAILED REQUESTS ---');
  failedRequests.forEach(r => console.log(r));
  console.log(`\nTotal: ${failedRequests.length}`);
});
