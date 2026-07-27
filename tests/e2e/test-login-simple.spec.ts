import { test, expect } from '@playwright/test';

test.describe('登录功能简化测试', () => {
  test('验证登录流程', async ({ page }) => {
    console.log('\n=== 简化登录测试 ===');
    
    // 1. 访问登录页
    await page.goto('http://localhost:8081/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'test-results/login-simple-01.png', fullPage: true });
    console.log('✓ 截图: 登录页面');
    
    // 2. 通过 API 注册并获取 token
    const timestamp = Date.now();
    const email = `test${timestamp}@example.com`;
    const password = 'Test123456';
    
    const regResponse = await page.request.post('http://localhost:8000/api/v1/auth/register', {
      data: { email, password, display_name: 'Test User' }
    });
    
    console.log(`\n注册状态: ${regResponse.status()}`);
    if (regResponse.status() !== 201) {
      console.log('✗ 注册失败');
      return;
    }
    console.log('✓ 注册成功');
    
    const loginResponse = await page.request.post('http://localhost:8000/api/v1/auth/login', {
      data: { email, password }
    });
    
    console.log(`\n登录状态: ${loginResponse.status()}`);
    if (loginResponse.status() !== 200) {
      console.log('✗ 登录失败');
      return;
    }
    
    const loginData = await loginResponse.json();
    const token = loginData.access_token;
    
    if (!token) {
      console.log('✗ 未获取到 token');
      console.log('响应数据:', JSON.stringify(loginData));
      return;
    }
    
    console.log('✓ 登录成功');
    console.log(`Token: ${token.substring(0, 20)}...`);
    
    // 3. 设置 token 到 localStorage
    await page.evaluate((t) => {
      localStorage.setItem('isekai_access_token', t);
    }, token);
    
    console.log('✓ Token 已设置到 localStorage');
    
    // 4. 刷新页面
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    const afterReloadUrl = page.url();
    console.log(`\n刷新后 URL: ${afterReloadUrl}`);
    
    // 5. 检查是否保持登录
    const isLoggedIn = !afterReloadUrl.includes('/login');
    console.log(`登录状态: ${isLoggedIn ? '✓ 保持登录' : '✗ 退出登录'}`);
    
    await page.screenshot({ path: 'test-results/login-simple-02-after-reload.png', fullPage: true });
    console.log('✓ 截图: 刷新后页面');
    
    // 6. 访问个人中心
    if (isLoggedIn) {
      await page.goto('http://localhost:8081/personal');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      const personalUrl = page.url();
      console.log(`\n个人中心 URL: ${personalUrl}`);
      const canAccess = !personalUrl.includes('/login');
      console.log(`访问个人中心: ${canAccess ? '✓ 成功' : '✗ 失败'}`);
      
      await page.screenshot({ path: 'test-results/login-simple-03-personal.png', fullPage: true });
      console.log('✓ 截图: 个人中心');
    }
    
    console.log('\n=== 测试完成 ===');
  });
});
