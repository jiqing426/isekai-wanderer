import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

test.describe('CR-018 T-026/T-018/T-030 前端验证', () => {
  let testEmail: string;
  const testPassword = '***';
  
  test.beforeEach(async ({ page, request }) => {
    // 注册测试用户
    const timestamp = Date.now();
    testEmail = `t026t018t030_${timestamp}@example.com`;
    
    const response = await request.post('http://localhost:8000/api/v1/auth/register', {
      data: {
        email: testEmail,
        password: testPassword,
        display_name: 'T026T018T030-Test'
      }
    });
    
    expect(response.status()).toBe(201);
    
    // 登录获取 token
    const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
      data: {
        email: testEmail,
        password: testPassword
      }
    });
    
    expect(loginResponse.status()).toBe(200);
    const loginData = await loginResponse.json();
    
    // 设置 token
    await page.goto('http://localhost:8081/');
    await page.waitForLoadState('networkidle');
    
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, loginData.access_token);
    
    // 完成 onboarding
    await page.goto('http://localhost:8081/onboarding');
    await page.waitForLoadState('networkidle');
    
    const onboardingPage = await page.locator('text=个性化设置').first();
    if (await onboardingPage.isVisible({ timeout: 3000 }).catch(() => false)) {
      // 步骤 1: 选择题材
      const genreCard = await page.locator('.selection-card').first();
      await genreCard.click();
      await page.waitForTimeout(500);
      
      const nextBtn1 = await page.locator('button.nav-button.primary').first();
      await nextBtn1.click();
      await page.waitForTimeout(1000);
      
      // 步骤 2: 选择角色风格
      const styleCard = await page.locator('.selection-card').first();
      await styleCard.click();
      await page.waitForTimeout(500);
      
      const nextBtn2 = await page.locator('button.nav-button.primary').first();
      await nextBtn2.click();
      await page.waitForTimeout(1000);
      
      // 步骤 3: 完成
      const startBtn = await page.locator('button.nav-button.primary').first();
      await startBtn.click();
      await page.waitForTimeout(3000);
    }
    
    // 签到获取碎片交易记录
    await request.post('http://localhost:8000/api/v1/sign/checkin', {
      headers: { Authorization: `Bearer ${loginData.access_token}` }
    });
  });

  test('T-026: 碎片收支明细中文化', async ({ page }) => {
    console.log('=== T-026: 碎片收支明细中文化验证 ===\n');
    
    // 进入碎片商城页面
    await page.goto('http://localhost:8081/fragment-mall');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/t026-01-fragment-mall.png', fullPage: true });
    console.log('✓ 截图: 碎片商城页面');
    
    // 检查是否有收支明细区域
    const transactionSection = await page.locator('text=收支明细').or(page.locator('text=交易记录')).first();
    
    if (await transactionSection.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('✓ 找到收支明细区域');
      
      // 获取页面文本内容
      const pageText = await page.textContent('body');
      
      // 检查是否显示中文
      const chineseKeywords = ['签到', '连续签到', '对话额度', '送礼', '成就'];
      const foundChinese = chineseKeywords.filter(kw => pageText?.includes(kw));
      
      if (foundChinese.length > 0) {
        console.log(`✓ 发现中文交易类型: ${foundChinese.join(', ')}`);
      }
      
      // 检查是否显示英文 key
      const englishKeys = ['daily_checkin', 'streak_milestone', 'dialogue_quota_purchase', 'gift_send'];
      let hasEnglishKey = false;
      
      for (const key of englishKeys) {
        if (pageText?.includes(key)) {
          console.log(`✗ 发现英文 key: ${key}`);
          hasEnglishKey = true;
        }
      }
      
      if (hasEnglishKey) {
        console.log('✗ T-026 失败: 页面显示英文 key');
        await page.screenshot({ path: 'test-results/t026-02-fail-english-key.png', fullPage: true });
        throw new Error('T-026 失败: 页面显示英文 key');
      } else {
        console.log('✓ T-026 通过: 未发现英文 key');
      }
    } else {
      console.log('⚠️  未找到收支明细区域');
      await page.screenshot({ path: 'test-results/t026-02-no-transaction-section.png', fullPage: true });
    }
    
    await page.screenshot({ path: 'test-results/t026-03-final.png', fullPage: true });
  });

  test('T-018: API 层碎片收支明细', async ({ page, request }) => {
    console.log('=== T-018: API 层碎片收支明细验证 ===\n');
    
    // 获取 token
    const token = await page.evaluate(() => localStorage.getItem('isekai_access_token'));
    
    // 调用 API
    const response = await request.get('http://localhost:8000/api/v1/shards/transactions', {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    const transactions = data.transactions || [];
    
    if (transactions.length > 0) {
      console.log(`找到 ${transactions.length} 条交易记录`);
      
      for (const t of transactions.slice(0, 3)) {
        const reason = t.reason || '';
        const reasonLabel = t.reason_label || '';
        
        console.log(`- reason: ${reason}`);
        console.log(`  reason_label: ${reasonLabel}`);
        
        if (reasonLabel) {
          console.log('  ✅ 有 reason_label 字段');
        } else {
          console.log('  ❌ 无 reason_label 字段');
        }
      }
      
      // 检查是否有 reason_label
      const hasReasonLabel = transactions.some(t => t.reason_label);
      
      if (hasReasonLabel) {
        console.log('\n✓ T-018 通过: API 返回 reason_label 字段');
      } else {
        console.log('\n✗ T-018 失败: API 未返回 reason_label 字段');
        throw new Error('T-018 失败: API 未返回 reason_label 字段');
      }
    } else {
      console.log('⚠️  无交易记录');
    }
  });

  test('T-030: 会员账单 API', async ({ page, request }) => {
    console.log('=== T-030: 会员账单 API 验证 ===\n');
    
    // 获取 token
    const token = await page.evaluate(() => localStorage.getItem('isekai_access_token'));
    
    // 调用 API
    const response = await request.get('http://localhost:8000/api/v1/users/me/transactions', {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    const transactions = data.transactions || [];
    
    if (transactions.length > 0) {
      console.log(`找到 ${transactions.length} 条交易记录`);
      
      for (const t of transactions.slice(0, 3)) {
        const reason = t.reason || '';
        const reasonLabel = t.reason_label || '';
        const description = t.description || '';
        
        console.log(`- reason: ${reason}`);
        console.log(`  reason_label: ${reasonLabel}`);
        console.log(`  description: ${description}`);
        
        if (reasonLabel || description) {
          console.log('  ✅ 有中文映射字段');
        } else {
          console.log('  ❌ 无中文映射字段');
        }
      }
      
      // 检查是否有中文映射
      const hasChineseMapping = transactions.some(t => t.reason_label || t.description);
      
      if (hasChineseMapping) {
        console.log('\n✓ T-030 通过: API 返回中文映射字段');
      } else {
        console.log('\n✗ T-030 失败: API 未返回中文映射字段');
        throw new Error('T-030 失败: API 未返回中文映射字段');
      }
    } else {
      console.log('⚠️  无交易记录');
    }
  });
});
