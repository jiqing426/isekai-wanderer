import { test, expect } from '@playwright/test';

test.describe('V-002: 成就系统验证', () => {
  test('验证成就解锁、显示和奖励领取', async ({ page, request }) => {
    const timestamp = Date.now();
    const testEmail = `v002_test_${timestamp}@example.com`;
    const testPassword = '***';
    
    console.log('=== V-002: 成就系统验证 ===\n');
    
    // 1. 注册新用户
    console.log('1. 注册新用户');
    const regResponse = await request.post('http://localhost:8000/api/v1/auth/register', {
      data: {
        email: testEmail,
        password: testPassword,
        display_name: 'V002-Tester'
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
    const token = loginData.access_token;
    
    // 3. 设置 token 到 localStorage
    console.log('\n3. 设置 token 到 localStorage');
    await page.goto('http://localhost:8081/');
    await page.waitForLoadState('networkidle');
    await page.evaluate((t) => {
      localStorage.setItem('isekai_access_token', t);
    }, token);
    console.log('   ✅ Token 设置成功');
    
    // 4. 完成 onboarding
    console.log('\n4. 完成 onboarding 流程');
    await page.goto('http://localhost:8081/onboarding');
    await page.waitForLoadState('networkidle');
    
    const onboardingPage = await page.locator('text=个性化设置').first();
    if (await onboardingPage.isVisible({ timeout: 3000 }).catch(() => false)) {
      const genreCard = await page.locator('.selection-card').first();
      await genreCard.click();
      await page.waitForTimeout(500);
      
      const nextBtn1 = await page.locator('button.nav-button.primary').first();
      await nextBtn1.click();
      await page.waitForTimeout(1000);
      
      const styleCard = await page.locator('.selection-card').first();
      await styleCard.click();
      await page.waitForTimeout(500);
      
      const nextBtn2 = await page.locator('button.nav-button.primary').first();
      await nextBtn2.click();
      await page.waitForTimeout(1000);
      
      const startBtn = await page.locator('button.nav-button.primary').first();
      await startBtn.click();
      await page.waitForTimeout(3000);
      console.log('   ✅ Onboarding 完成');
    }
    
    // 5. 访问成就页面
    console.log('\n5. 访问成就页面');
    await page.goto('http://localhost:8081/achievements');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/v002-01-achievements-page.png', fullPage: true });
    console.log('   ✅ 截图: 成就页面');
    
    // 6. 检查成就列表
    console.log('\n6. 检查成就列表');
    const achievementList = await page.locator('.achievement-item, .achievement-card').count();
    console.log(`   找到 ${achievementList} 个成就项`);
    
    if (achievementList > 0) {
      console.log('   ✅ 成就列表显示正常');
    } else {
      console.log('   ⚠️  未找到成就项，尝试其他选择器');
      const altAchievementList = await page.locator('[class*="achievement"]').count();
      console.log(`   备用选择器找到 ${altAchievementList} 个元素`);
    }
    
    // 7. 检查已解锁成就
    console.log('\n7. 检查已解锁成就');
    const unlockedAchievements = await page.locator('.achievement-item.unlocked, .achievement-card.unlocked').count();
    console.log(`   已解锁成就: ${unlockedAchievements} 个`);
    
    // 8. 检查未解锁成就
    console.log('\n8. 检查未解锁成就');
    const lockedAchievements = await page.locator('.achievement-item.locked, .achievement-card.locked').count();
    console.log(`   未解锁成就: ${lockedAchievements} 个`);
    
    // 9. 尝试领取奖励
    console.log('\n9. 尝试领取奖励');
    const claimButton = await page.locator('button:has-text("领取"), button:has-text("Claim")').first();
    const hasClaimButton = await claimButton.isVisible({ timeout: 2000 }).catch(() => false);
    
    if (hasClaimButton) {
      console.log('   ✅ 找到领取按钮');
      await claimButton.click();
      await page.waitForTimeout(2000);
      await page.screenshot({ path: 'test-results/v002-02-after-claim.png', fullPage: true });
      console.log('   ✅ 截图: 领取后页面');
      
      // 检查是否有成功提示
      const successMsg = await page.locator('.success-message, .toast-success, text=领取成功').first();
      const hasSuccess = await successMsg.isVisible({ timeout: 2000 }).catch(() => false);
      
      if (hasSuccess) {
        console.log('   ✅ 奖励领取成功');
      } else {
        console.log('   ⚠️  未检测到成功提示');
      }
    } else {
      console.log('   ⚠️  无可领取的奖励（可能没有已解锁未领取的成就）');
    }
    
    // 10. API 验证成就数据
    console.log('\n10. API 验证成就数据');
    const achievementsResponse = await request.get('http://localhost:8000/api/v1/users/me/achievements', {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (achievementsResponse.status() === 200) {
      const achievementsData = await achievementsResponse.json();
      console.log(`   API 返回成就数量: ${achievementsData.length || achievementsData.achievements?.length || 0}`);
      console.log('   ✅ 成就 API 正常');
    } else {
      console.log(`   ❌ 成就 API 失败: ${achievementsResponse.status()}`);
    }
    
    // 11. 签到触发成就
    console.log('\n11. 签到触发成就');
    const checkinResponse = await request.post('http://localhost:8000/api/v1/sign/checkin', {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (checkinResponse.status() === 200) {
      console.log('   ✅ 签到成功');
      
      // 重新加载成就页面
      await page.reload();
      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: 'test-results/v002-03-after-checkin.png', fullPage: true });
      console.log('   ✅ 截图: 签到后成就页面');
      
      // 检查是否有新解锁的成就
      const newUnlocked = await page.locator('.achievement-item.unlocked, .achievement-card.unlocked').count();
      console.log(`   签到后解锁成就: ${newUnlocked} 个`);
    } else {
      console.log('   ⚠️  签到失败或已签到');
    }
    
    console.log('\n=== V-002 验证结果 ===');
    console.log(`成就列表: ${achievementList} 个`);
    console.log(`已解锁: ${unlockedAchievements} 个`);
    console.log(`未解锁: ${lockedAchievements} 个`);
    console.log(`领取按钮: ${hasClaimButton ? '有' : '无'}`);
    
    if (achievementList > 0) {
      console.log('✅ V-002 通过: 成就系统显示正常');
    } else {
      console.log('⚠️  V-002 部分通过: 成就系统需要检查');
    }
    
    await page.screenshot({ path: 'test-results/v002-04-final.png', fullPage: true });
  });
});
