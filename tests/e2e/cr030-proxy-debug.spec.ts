/**
 * CR-030 Proxy Debug Test
 * 验证 Vite proxy 是否正确转发 POST 请求
 */

import { test, expect } from '@playwright/test';

test.describe('Proxy Debug', () => {
  test('验证 proxy 转发 POST 请求', async ({ page }) => {
    // 监听网络请求
    const requests: any[] = [];
    page.on('request', request => {
      if (request.url().includes('/api/v1/auth/login')) {
        requests.push({
          url: request.url(),
          method: request.method(),
          headers: request.headers(),
          postData: request.postData()
        });
      }
    });
    
    const responses: any[] = [];
    page.on('response', response => {
      if (response.url().includes('/api/v1/auth/login')) {
        responses.push({
          url: response.url(),
          status: response.status(),
          headers: response.headers()
        });
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
    await page.click('button[type="submit"]');
    
    // 4. 等待响应
    await page.waitForTimeout(3000);
    
    // 5. 输出请求和响应详情
    console.log('\n=== Request Details ===');
    for (const req of requests) {
      console.log('URL:', req.url);
      console.log('Method:', req.method);
      console.log('Content-Type:', req.headers['content-type']);
      console.log('Post Data:', req.postData);
      console.log('Post Data Length:', req.postData?.length);
    }
    
    console.log('\n=== Response Details ===');
    for (const res of responses) {
      console.log('URL:', res.url);
      console.log('Status:', res.status);
    }
    
    // 6. 直接通过 fetch 测试
    console.log('\n=== Direct Fetch Test ===');
    const result = await page.evaluate(async () => {
      try {
        const response = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: 'qa-test@example.com',
            password: 'Test123456'
          })
        });
        const data = await response.json();
        return {
          status: response.status,
          data: data
        };
      } catch (error) {
        return {
          error: error instanceof Error ? error.message : 'Unknown error'
        };
      }
    });
    
    console.log('Direct fetch result:', JSON.stringify(result, null, 2));
    
    // 测试断言
    expect(requests.length).toBeGreaterThan(0);
  });
});
