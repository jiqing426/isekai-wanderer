import { test, expect, Page } from '@playwright/test';

test('debug: 查看游戏页面 404 请求', async ({ page }) => {
  const failedRequests: string[] = [];
  
  page.on('response', (response) => {
    if (response.status() >= 400) {
      failedRequests.push(`${response.status()} ${response.url()}`);
    }
  });

  // 登录
  await page.goto('http://localhost:8081/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'Test123456!');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/discover**', { timeout: 10000 }).catch(() => {});

  // 选择剧本并开始游戏
  await page.goto('http://localhost:8081/scripts');
  await page.waitForTimeout(2000);
  
  // 点击第一个剧本
  const scriptLink = page.locator('a[href*="/scripts/"]').first();
  if (await scriptLink.isVisible()) {
    await scriptLink.click();
    await page.waitForTimeout(2000);
    
    // 点击开始游戏
    const startBtn = page.locator('text=🎮 开始游戏').first();
    if (await startBtn.isVisible()) {
      await startBtn.click();
      await page.waitForTimeout(3000);
      
      // 如果出现选角弹窗，选择角色
      const candidateCard = page.locator('[data-testid="candidate-card"]').first();
      if (await candidateCard.isVisible()) {
        await candidateCard.click();
        await page.locator('[data-testid="select-candidate-confirm-btn"]').click();
        await page.waitForTimeout(5000);
      }
    }
  }
  
  // 在游戏页面停留一段时间，捕获所有 404
  await page.waitForTimeout(8000);
  
  console.log('Failed requests:');
  failedRequests.forEach(r => console.log(r));
  
  if (failedRequests.length > 0) {
    console.log(`\nTotal failed requests: ${failedRequests.length}`);
  } else {
    console.log('\nNo failed requests!');
  }
});
