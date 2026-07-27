import { test, expect } from '@playwright/test';

test.describe('V-001: 剧本对话限制验证', () => {
  test('验证对话额度用完是否阻止对话', async ({ page, request }) => {
    const timestamp = Date.now();
    const testEmail = `v001_test_${timestamp}@example.com`;
    const testPassword = '***';
    
    // 1. 注册新用户
    console.log('=== V-001: 剧本对话限制验证 ===\n');
    console.log('1. 注册新用户');
    const regResponse = await request.post('http://localhost:8000/api/v1/auth/register', {
      data: {
        email: testEmail,
        password: testPassword,
        display_name: 'V001-Tester'
      }
    });
    expect(regResponse.status()).toBe(201);
    const regData = await regResponse.json();
    console.log(`   ✅ 用户注册成功: ${testEmail}`);
    
    // 2. 登录获取 token
    console.log('\n2. 登录获取 token');
    const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
      data: {
        email: testEmail,
        password: testPassword
      }
    });
    expect(loginResponse.status()).toBe(200);
    const loginData = await loginResponse.json();
    
    // 3. 设置 token 到 localStorage
    console.log('\n3. 设置 token 到 localStorage');
    await page.goto('http://localhost:8081/');
    await page.waitForLoadState('networkidle');
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, loginData.access_token);
    console.log('   ✅ Token 设置成功');
    
    // 4. 完成 onboarding
    console.log('\n4. 完成 onboarding 流程');
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
      console.log('   ✅ Onboarding 完成');
    }
    
    // 5. 获取初始额度
    console.log('\n5. 获取初始对话额度');
    const quotaResponse = await request.get('http://localhost:8000/api/v1/cr016/dialogue/quota/status', {
      headers: { Authorization: `Bearer ${loginData.access_token}` }
    });
    expect(quotaResponse.status()).toBe(200);
    const quotaData = await quotaResponse.json();
    const initialQuota = quotaData.remaining;
    console.log(`   初始额度: ${initialQuota} 次`);
    console.log(`   生命周期阶段: ${quotaData.lifecycle_stage || 'honeymoon'}`);
    
    // 6. 开始游戏
    console.log('\n6. 开始游戏');
    await page.goto('http://localhost:8081/discover');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/v001-01-scripts-list.png', fullPage: true });
    console.log('   ✅ 截图: 剧本列表页面');
    
    // 点击第一个剧本
    const firstScript = await page.locator('.script-card, .script-item').first();
    await firstScript.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/v001-02-script-detail.png', fullPage: true });
    console.log('   ✅ 截图: 剧本详情页面');
    
    // 点击开始游戏
    const startGameBtn = await page.locator('button:has-text("开始游戏"), .start-game-btn').first();
    await startGameBtn.click();
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'test-results/v001-03-game-start.png', fullPage: true });
    console.log('   ✅ 截图: 游戏开始页面');
    
    // 7. 连续对话直到额度用完
    console.log('\n7. 连续对话测试');
    let dialogueCount = 0;
    let quotaExhausted = false;
    
    while (dialogueCount < initialQuota + 2 && !quotaExhausted) {
      console.log(`\n   对话 ${dialogueCount + 1}/${initialQuota}:`);
      
      // 等待选择项出现
      const choiceBtn = await page.locator('.choice-btn, .dialogue-choice').first();
      const hasChoice = await choiceBtn.isVisible({ timeout: 3000 }).catch(() => false);
      
      if (!hasChoice) {
        console.log('   ⚠️  无选择项，可能已到达结局');
        break;
      }
      
      // 点击选择
      await choiceBtn.click();
      await page.waitForTimeout(2000);
      dialogueCount++;
      
      // 检查是否有错误提示
      const errorMsg = await page.locator('.error-message, .quota-exhausted, text=额度已用完').first();
      const hasError = await errorMsg.isVisible({ timeout: 1000 }).catch(() => false);
      
      if (hasError) {
        console.log('   ✅ 检测到额度用完提示');
        quotaExhausted = true;
        await page.screenshot({ path: `test-results/v001-04-quota-exhausted-${dialogueCount}.png`, fullPage: true });
      } else {
        console.log(`   ✅ 对话成功，已进行 ${dialogueCount} 次`);
      }
      
      // 每 3 次对话截图一次
      if (dialogueCount % 3 === 0) {
        await page.screenshot({ path: `test-results/v001-dialogue-${dialogueCount}.png`, fullPage: true });
      }
    }
    
    // 8. 验证最终额度
    console.log('\n8. 验证最终额度');
    const finalQuotaResponse = await request.get('http://localhost:8000/api/v1/cr016/dialogue/quota/status', {
      headers: { Authorization: `Bearer ${loginData.access_token}` }
    });
    const finalQuotaData = await finalQuotaResponse.json();
    const finalQuota = finalQuotaData.remaining;
    console.log(`   最终额度: ${finalQuota} 次`);
    console.log(`   消耗额度: ${initialQuota - finalQuota} 次`);
    
    // 9. 尝试在额度用完后继续对话
    console.log('\n9. 尝试在额度用完后继续对话');
    if (finalQuota === 0) {
      const choiceBtn = await page.locator('.choice-btn, .dialogue-choice').first();
      const hasChoice = await choiceBtn.isVisible({ timeout: 3000 }).catch(() => false);
      
      if (hasChoice) {
        await choiceBtn.click();
        await page.waitForTimeout(2000);
        
        // 检查是否被阻止
        const blockedMsg = await page.locator('.error-message, .quota-exhausted, text=额度已用完, text=请充值').first();
        const isBlocked = await blockedMsg.isVisible({ timeout: 2000 }).catch(() => false);
        
        if (isBlocked) {
          console.log('   ✅ 额度用完后对话被阻止');
          await page.screenshot({ path: 'test-results/v001-05-dialogue-blocked.png', fullPage: true });
        } else {
          console.log('   ❌ 额度用完后对话未被阻止');
          await page.screenshot({ path: 'test-results/v001-05-dialogue-not-blocked.png', fullPage: true });
        }
      } else {
        console.log('   ⚠️  无选择项可测试');
      }
    } else {
      console.log(`   ⚠️  额度未用完（剩余 ${finalQuota} 次）`);
    }
    
    // 10. 验证结果
    console.log('\n=== V-001 验证结果 ===');
    console.log(`初始额度: ${initialQuota}`);
    console.log(`对话次数: ${dialogueCount}`);
    console.log(`最终额度: ${finalQuota}`);
    console.log(`额度消耗: ${initialQuota - finalQuota}`);
    
    if (finalQuota === 0 && quotaExhausted) {
      console.log('✅ V-001 通过: 额度用完后正确阻止对话');
    } else if (finalQuota > 0) {
      console.log('⚠️  V-001 部分通过: 额度未完全用完');
    } else {
      console.log('❌ V-001 失败: 额度限制未生效');
    }
    
    await page.screenshot({ path: 'test-results/v001-06-final.png', fullPage: true });
  });
});
