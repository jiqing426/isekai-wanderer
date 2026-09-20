import { test, expect } from '@playwright/test';

test('debug: 游戏页面所有4xx请求', async ({ page }) => {
  const failedRequests: string[] = [];
  
  page.on('response', (response) => {
    const status = response.status();
    if (status >= 400) {
      const method = response.request().method();
      const url = response.url().replace('http://localhost:8081', '');
      failedRequests.push(`${status} ${method} ${url}`);
    }
  });

  // 登录
  await page.goto('http://localhost:8081/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'Test123456!');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/discover', { timeout: 10000 }).catch(() => {
    console.log('Login redirect failed, staying on page');
  });
  await page.waitForTimeout(2000);

  // 直接到剧本列表
  await page.goto('http://localhost:8081/scripts');
  await page.waitForTimeout(3000);

  // 打印页面内容
  const links = await page.locator('a[href*="/scripts/"]').count();
  console.log(`Found ${links} script links`);

  // 点击第一个剧本详情链接
  const scriptDetailLinks = page.locator('a[href^="/scripts/"]').filter({ hasNot: page.locator('text=剧本') });
  const count = await scriptDetailLinks.count();
  console.log(`Detail links: ${count}`);
  
  if (count > 0) {
    const href = await scriptDetailLinks.first().getAttribute('href');
    console.log(`Clicking: ${href}`);
    // 直接导航
    await page.goto(`http://localhost:8081${href}`);
    await page.waitForTimeout(3000);

    // 点击开始游戏
    const startBtn = page.locator('text=🎮 开始游戏');
    if (await startBtn.isVisible()) {
      console.log('Clicking start game');
      await startBtn.click();
      await page.waitForTimeout(3000);

      // 选角
      const candidateCard = page.locator('[data-testid="candidate-card"]').first();
      if (await candidateCard.isVisible()) {
        console.log('Selecting candidate');
        await candidateCard.click();
        await page.locator('[data-testid="select-candidate-confirm-btn"]').click();
        await page.waitForTimeout(10000);
        console.log('Now in game page, URL:', page.url());
      } else {
        console.log('No candidate card visible');
        // 可能直接进了游戏页面
        await page.waitForTimeout(5000);
      }
    } else {
      console.log('No start button visible');
    }
  }

  await page.waitForTimeout(5000);

  console.log('--- ALL FAILED REQUESTS ---');
  failedRequests.forEach(r => console.log(r));
  console.log(`Total: ${failedRequests.length}`);
});
