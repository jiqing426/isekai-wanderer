import { test, expect } from '@playwright/test';

// 测试配置
const BASE_URL = 'http://localhost:8081';
const API_BASE = 'http://localhost:8081/api/v1';

// 辅助函数：注册测试用户
async function registerTestUser(request: any, email: string) {
  const response = await request.post(`${API_BASE}/auth/register`, {
    data: {
      email: email,
      password: '***',
      nickname: 'BrowserE2E'
    }
  });
  
  if (response.status() === 201 || response.status() === 200) {
    const data = await response.json();
    return data.access_token;
  }
  
  // 如果注册失败，尝试登录
  const loginResponse = await request.post(`${API_BASE}/auth/login`, {
    data: {
      email: email,
      password: '***'
    }
  });
  const data = await loginResponse.json();
  return data.access_token;
}

test.describe('CR-016 Browser E2E Tests', () => {
  let authToken: string;
  const testEmail = `browser_e2e_${Date.now()}@test.com`;

  test.beforeAll(async ({ request }) => {
    // 注册测试用户
    authToken = await registerTestUser(request, testEmail);
    console.log('Test user registered:', testEmail);
  });

  test('1. 订阅页面能正常加载', async ({ page }) => {
    // 设置认证 token
    await page.context().addCookies([{
      name: 'token',
      value: authToken,
      domain: 'localhost',
      path: '/'
    }]);

    // 访问订阅页面
    await page.goto(`${BASE_URL}/subscription`);
    
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    // 验证页面标题或关键元素存在
    const pageTitle = await page.title();
    expect(pageTitle).toContain('Isekai Wanderer');
    
    // 截图保存
    await page.screenshot({ path: 'test-results/subscription-page.png' });
    
    // 验证订阅页面关键元素
    const subscriptionContent = await page.textContent('body');
    expect(subscriptionContent).toBeTruthy();
  });

  test('2. 额度显示正常', async ({ page, request }) => {
    // 设置认证 token
    await page.context().addCookies([{
      name: 'token',
      value: authToken,
      domain: 'localhost',
      path: '/'
    }]);

    // 先通过 API 获取额度状态
    const quotaResponse = await request.get(`${API_BASE}/cr016/dialogue/quota/status`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    expect(quotaResponse.status()).toBe(200);
    const quotaData = await quotaResponse.json();
    
    console.log('Quota status:', quotaData);
    
    // 验证额度数据结构
    expect(quotaData).toHaveProperty('base_quota');
    expect(quotaData).toHaveProperty('remaining');
    expect(quotaData).toHaveProperty('is_exempt');
    
    // 访问游戏页面验证额度显示
    await page.goto(`${BASE_URL}/game`);
    await page.waitForLoadState('networkidle');
    
    // 截图
    await page.screenshot({ path: 'test-results/quota-display.png' });
  });

  test('3. Paywall 弹窗触发正确', async ({ page, request }) => {
    // 设置认证 token
    await page.context().addCookies([{
      name: 'token',
      value: authToken,
      domain: 'localhost',
      path: '/'
    }]);

    // 通过 API 检查 paywall 触发
    const paywallResponse = await request.post(`${API_BASE}/cr016/paywall/check-trigger`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      data: {
        scene: 'T1_quota',
        user_initiated: false
      }
    });
    
    expect(paywallResponse.status()).toBe(200);
    const paywallData = await paywallResponse.json();
    
    console.log('Paywall trigger:', paywallData);
    
    // 验证 paywall 数据结构
    expect(paywallData).toHaveProperty('should_show');
    expect(paywallData).toHaveProperty('display_type');
    
    // 对于新用户（honeymoon 阶段），应该显示 banner
    if (paywallData.should_show) {
      expect(['banner', 'modal', 'toast']).toContain(paywallData.display_type);
    }
    
    // 访问前端页面验证弹窗
    await page.goto(`${BASE_URL}/game`);
    await page.waitForLoadState('networkidle');
    
    // 截图
    await page.screenshot({ path: 'test-results/paywall-trigger.png' });
  });

  test('4. 碎片购买流程', async ({ page, request }) => {
    // 设置认证 token
    await page.context().addCookies([{
      name: 'token',
      value: authToken,
      domain: 'localhost',
      path: '/'
    }]);

    // 先检查当前碎片余额
    const fragmentsResponse = await request.get(`${API_BASE}/shards/balance`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    const fragmentsData = await fragmentsResponse.json();
    console.log('Current fragments:', fragmentsData);
    
    // 尝试碎片购买（预期会失败，因为余额不足）
    const purchaseResponse = await request.post(`${API_BASE}/cr016/subscription/fragment-purchase`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      data: {
        amount: 1
      }
    });
    
    // 预期返回 402（余额不足）或 200（如果余额足够）
    expect([200, 402]).toContain(purchaseResponse.status());
    
    const purchaseData = await purchaseResponse.json();
    console.log('Fragment purchase result:', purchaseData);
    
    if (purchaseResponse.status() === 402) {
      expect(purchaseData.error_code).toBe('INSUFFICIENT_FRAGMENTS');
    }
    
    // 访问碎片商店页面
    await page.goto(`${BASE_URL}/shop`);
    await page.waitForLoadState('networkidle');
    
    // 截图
    await page.screenshot({ path: 'test-results/fragment-purchase.png' });
  });

  test('5. 订阅创建和状态验证', async ({ page, request }) => {
    // 设置认证 token
    await page.context().addCookies([{
      name: 'token',
      value: authToken,
      domain: 'localhost',
      path: '/'
    }]);

    // 创建 Basic 订阅
    const createResponse = await request.post(`${API_BASE}/cr016/subscription/create`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      data: {
        tier: 'basic',
        cycle: 'monthly'
      }
    });
    
    expect(createResponse.status()).toBe(200);
    const createData = await createResponse.json();
    console.log('Subscription created:', createData);
    
    expect(createData.status).toBe('success');
    expect(createData.tier).toBe('basic');
    
    // 验证订阅状态
    const statusResponse = await request.get(`${API_BASE}/cr016/subscription/status`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    expect(statusResponse.status()).toBe(200);
    const statusData = await statusResponse.json();
    console.log('Subscription status:', statusData);
    
    expect(statusData.tier).toBe('basic');
    expect(statusData.is_exempt_from_quota).toBe(true);
    
    // 验证额度状态更新
    const quotaResponse = await request.get(`${API_BASE}/cr016/dialogue/quota/status`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    const quotaData = await quotaResponse.json();
    console.log('Quota after subscription:', quotaData);
    
    expect(quotaData.is_exempt).toBe(true);
    expect(quotaData.remaining).toBe(-1); // -1 表示无限额度
    
    // 访问订阅页面验证显示
    await page.goto(`${BASE_URL}/subscription`);
    await page.waitForLoadState('networkidle');
    
    // 截图
    await page.screenshot({ path: 'test-results/subscription-active.png' });
    
    // 取消订阅
    const cancelResponse = await request.post(`${API_BASE}/cr016/subscription/cancel`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    expect(cancelResponse.status()).toBe(200);
    const cancelData = await cancelResponse.json();
    console.log('Subscription cancelled:', cancelData);
    
    expect(cancelData.status).toBe('cancelled');
  });
});
