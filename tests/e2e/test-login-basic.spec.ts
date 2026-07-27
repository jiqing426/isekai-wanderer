import { test, expect } from '@playwright/test';

test.describe('登录功能基础测试', () => {
  test('浏览器登录流程', async ({ page }) => {
    console.log('\n=== 浏览器登录测试 ===');
    
    // 1. 访问登录页
    await page.goto('http://localhost:8081/login');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/login-01-page.png', fullPage: true });
    console.log('✓ 截图: 登录页面');
    
    // 2. 注册新账号
    const timestamp = Date.now();
    const email = `test${timestamp}@example.com`;
    const password = 'Test123456';
    
    console.log(`\n测试账号: ${email}`);
    
    // 点击注册链接
    await page.click('text=立即注册');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/login-02-register.png', fullPage: true });
    console.log('✓ 截图: 注册页面');
    
    // 填写注册表单
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.fill('input[placeholder*="确认"]', password);
    
    // 点击注册按钮
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // 3. 登录
    await page.goto('http://localhost:8081/login');
    await page.waitForLoadState('networkidle');
    
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    const afterLoginUrl = page.url();
    console.log(`\n登录后 URL: ${afterLoginUrl}`);
    await page.screenshot({ path: 'test-results/login-03-after-login.png', fullPage: true });
    console.log('✓ 截图: 登录后页面');
    
    // 4. 检查是否登录成功
    const isLoggedIn = !afterLoginUrl.includes('/login');
    console.log(`\n登录状态: ${isLoggedIn ? '✓ 成功' : '✗ 失败'}`);
    
    // 5. 检查 localStorage
    const token = await page.evaluate(() => localStorage.getItem('isekai_access_token'));
    console.log(`Token 存在: ${token ? '✓ 是' : '✗ 否'}`);
    if (token) {
      console.log(`Token: ${token.substring(0, 20)}...`);
    }
    
    // 6. 刷新页面测试持久化
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    const afterReloadUrl = page.url();
    console.log(`\n刷新后 URL: ${afterReloadUrl}`);
    const stillLoggedIn = !afterReloadUrl.includes('/login');
    console.log(`刷新后登录状态: ${stillLoggedIn ? '✓ 保持登录' : '✗ 退出登录'}`);
    
    await page.screenshot({ path: 'test-results/login-04-after-reload.png', fullPage: true });
    console.log('✓ 截图: 刷新后页面');
    
    // 7. 访问个人中心
    if (stillLoggedIn) {
      await page.goto('http://localhost:8081/personal');
      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: 'test-results/login-05-personal.png', fullPage: true });
      console.log('✓ 截图: 个人中心');
      
      const personalUrl = page.url();
      console.log(`个人中心 URL: ${personalUrl}`);
      const canAccessPersonal = !personalUrl.includes('/login');
      console.log(`访问个人中心: ${canAccessPersonal ? '✓ 成功' : '✗ 失败'}`);
    }
    
    console.log('\n=== 测试完成 ===');
  });
});
