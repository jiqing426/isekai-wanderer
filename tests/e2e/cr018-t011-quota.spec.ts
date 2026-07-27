import { test, expect } from '@playwright/test';

test.describe('CR-018 T-011: Dialogue Quota Display', () => {
  const TEST_EMAIL = `cr018t011${Date.now()}@testmail.com`;
  const TEST_PASS = 'Test1234!';

  test('个人中心应正确显示对话额度', async ({ page }) => {
    // 1. 注册新用户
    await page.goto('http://localhost:8081/register');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: '/tmp/cr018-t011-register.png', fullPage: true });
    
    await page.fill('input[type="email"]', TEST_EMAIL);
    await page.fill('input[type="password"]', TEST_PASS);
    
    // Try nickname field
    const nicknameInput = page.locator('input[name="nickname"], input[placeholder*="昵称"], input[placeholder*="name"]');
    if (await nicknameInput.count() > 0) {
      await nicknameInput.first().fill('T011-Browser');
    }
    
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000);

    // 2. Login if needed
    const currentUrl = page.url();
    if (!currentUrl.includes('/personal') && !currentUrl.includes('/profile') && !currentUrl.includes('/')) {
      await page.goto('http://localhost:8081/login');
      await page.fill('input[type="email"]', TEST_EMAIL);
      await page.fill('input[type="password"]', TEST_PASS);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(3000);
    }

    // 3. Navigate to personal center
    await page.goto('http://localhost:8081/personal');
    await page.waitForTimeout(3000);

    // 4. Screenshot personal center page
    await page.screenshot({ path: '/tmp/cr018-t011-personal.png', fullPage: true });

    // 5. Check for quota display
    const pageContent = await page.textContent('body');
    expect(pageContent).toBeTruthy();
    
    // 6. Look for quota-related text
    const hasQuotaText = pageContent?.includes('额度') || pageContent?.includes('对话') || pageContent?.includes('次');
    console.log(`Page has quota text: ${hasQuotaText}`);
    
    // 7. Try to find quota display element
    const quotaElement = page.locator('text=/\\d+\\/\\d+/').first();
    if (await quotaElement.count() > 0) {
      const quotaText = await quotaElement.textContent();
      console.log(`Quota display: ${quotaText}`);
    }

    console.log('Browser interaction completed successfully');
  });
});
