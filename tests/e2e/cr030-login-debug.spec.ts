/**
 * CR-030 Browser E2E Test - Login Debug
 * 调试登录失败问题
 */

import { test, expect } from '@playwright/test';

test.describe('CR-030 Login Debug', () => {
  test('调试登录流程', async ({ page }) => {
    // 监听控制台消息
    page.on('console', msg => {
      console.log('Browser console:', msg.text());
    });
    
    page.on('pageerror', error => {
      console.log('Page error:', error.message);
    });
    
    // 监听网络请求
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        console.log('Request:', request.method(), request.url());
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('/api/')) {
        console.log('Response:', response.status(), response.url());
      }
    });
    
    // 1. 打开登录页
    await page.goto('http://localhost:8081/login');
    await page.waitForLoadState('networkidle');
    
    // 2. 填写表单
    await page.waitForSelector('input[type="email"]', { timeout: 10000 });
    await page.fill('input[type="email"]', 'qa-test@example.com');
    await page.fill('input[type="password"]', 'Test123456');
    
    // 3. 点击登录按钮
    console.log('Clicking login button...');
    await page.click('button[type="submit"]');
    
    // 4. 等待并检查错误信息
    await page.waitForTimeout(3000);
    
    // 5. 检查是否有错误信息
    const errorElement = await page.locator('.auth-error').first();
    if (await errorElement.isVisible()) {
      const errorText = await errorElement.textContent();
      console.log('Login error:', errorText);
      
      // 检查网络请求日志
      console.log('--- Network requests ---');
    }
    
    // 6. 检查是否成功跳转
    const currentUrl = page.url();
    console.log('Current URL:', currentUrl);
    
    // 7. 截图
    await page.screenshot({ 
      path: 'logs/e2e/cr030-login-debug.png',
      fullPage: true 
    });
    
    // 8. 检查 localStorage
    const token = await page.evaluate(() => localStorage.getItem('token'));
    console.log('Token in localStorage:', token ? 'exists' : 'null');
    
    // 测试断言 - 这里故意失败以便查看日志
    expect(currentUrl).toContain('/login'); // 预期仍在登录页
  });
});
