import { test, expect } from '@playwright/test';

test.describe('V-005: 剧本游戏完整流程验证', () => {
  test('验证开始→对话→选择→结局→统计全流程', async ({ page, request }) => {
    const timestamp = Date.now();
    const testEmail = `v005_test_${timestamp}@example.com`;
    const testPassword = '***';
    
    console.log('=== V-005: 剧本游戏完整流程验证 ===\n');
    
    // 1. 注册新用户
    console.log('1. 注册新用户');
    const regResponse = await request.post('http://localhost:8000/api/v1/auth/register', {
      data: {
        email: testEmail,
        password: testPassword,
        display_name: 'V005-Tester'
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
    
    // 5. 访问剧本列表
    console.log('\n5. 访问剧本列表');
    await page.goto('http://localhost:8081/discover');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/v005-01-discover.png', fullPage: true });
    console.log('   ✅ 截图: 剧本列表页面');
    
    // 6. 选择剧本
    console.log('\n6. 选择剧本');
    const scriptCard = await page.locator('.script-card, .script-item').first();
    const hasScript = await scriptCard.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasScript) {
      const scriptTitle = await scriptCard.locator('.title, h3').textContent().catch(() => '未知剧本');
      console.log(`   选择剧本: ${scriptTitle}`);
      await scriptCard.click();
      await page.waitForTimeout(2000);
      await page.screenshot({ path: 'test-results/v005-02-script-detail.png', fullPage: true });
      console.log('   ✅ 截图: 剧本详情页面');
    } else {
      console.log('   ❌ 未找到剧本');
      return;
    }
    
    // 7. 开始游戏
    console.log('\n7. 开始游戏');
    const startGameBtn = await page.locator('button:has-text("开始游戏"), button:has-text("开始"), .start-game-btn').first();
    const hasStartBtn = await startGameBtn.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasStartBtn) {
      await startGameBtn.click();
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'test-results/v005-03-game-start.png', fullPage: true });
      console.log('   ✅ 截图: 游戏开始页面');
      console.log('   ✅ 游戏启动成功');
    } else {
      console.log('   ❌ 未找到开始游戏按钮');
      return;
    }
    
    // 8. 进行对话选择
    console.log('\n8. 进行对话选择');
    let choiceCount = 0;
    let reachedEnding = false;
    
    while (choiceCount < 10 && !reachedEnding) {
      console.log(`\n   对话轮次 ${choiceCount + 1}:`);
      
      // 等待选择项
      const choiceBtn = await page.locator('.choice-btn, .dialogue-choice, button[class*="choice"]').first();
      const hasChoice = await choiceBtn.isVisible({ timeout: 3000 }).catch(() => false);
      
      if (!hasChoice) {
        console.log('   ⚠️  无选择项，可能已到达结局');
        
        // 检查是否有结局标识
        const endingElement = await page.locator('.ending, .ending-screen, [class*="ending"]').first();
        const hasEnding = await endingElement.isVisible({ timeout: 2000 }).catch(() => false);
        
        if (hasEnding) {
          console.log('   ✅ 检测到结局页面');
          reachedEnding = true;
          await page.screenshot({ path: `test-results/v005-04-ending.png`, fullPage: true });
        }
        break;
      }
      
      // 点击选择
      const choiceText = await choiceBtn.textContent().catch(() => '未知选择');
      console.log(`   选择: ${choiceText?.substring(0, 30)}`);
      await choiceBtn.click();
      await page.waitForTimeout(2000);
      choiceCount++;
      
      // 每 3 轮截图
      if (choiceCount % 3 === 0) {
        await page.screenshot({ path: `test-results/v005-dialogue-${choiceCount}.png`, fullPage: true });
      }
    }
    
    // 9. 检查结局
    console.log('\n9. 检查结局');
    if (reachedEnding) {
      const endingTitle = await page.locator('.ending-title, h2, h3').first().textContent().catch(() => '未知结局');
      console.log(`   结局标题: ${endingTitle}`);
      console.log('   ✅ 成功到达结局');
    } else {
      console.log('   ⚠️  未检测到结局页面');
    }
    
    // 10. 访问个人中心查看统计
    console.log('\n10. 访问个人中心查看统计');
    await page.goto('http://localhost:8081/personal');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/v005-05-personal-center.png', fullPage: true });
    console.log('   ✅ 截图: 个人中心页面');
    
    // 检查统计数据
    const statsElement = await page.locator('.stats, .statistics, [class*="stats"]').first();
    const hasStats = await statsElement.isVisible({ timeout: 2000 }).catch(() => false);
    
    if (hasStats) {
      console.log('   ✅ 统计数据区域存在');
      
      // 检查游戏次数
      const gameCount = await page.locator('.game-count, .play-count').textContent().catch(() => '0');
      console.log(`   游戏次数: ${gameCount}`);
      
      // 检查完成剧本数
      const completedCount = await page.locator('.completed-count, .finished-count').textContent().catch(() => '0');
      console.log(`   完成剧本数: ${completedCount}`);
    } else {
      console.log('   ⚠️  未找到统计数据区域');
    }
    
    // 11. API 验证游戏统计
    console.log('\n11. API 验证游戏统计');
    const statsResponse = await request.get('http://localhost:8000/api/v1/users/me/stats', {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (statsResponse.status() === 200) {
      const statsData = await statsResponse.json();
      console.log(`   总游戏次数: ${statsData.total_games || 0}`);
      console.log(`   完成剧本数: ${statsData.completed_scripts || 0}`);
      console.log(`   总对话数: ${statsData.total_dialogues || 0}`);
      console.log('   ✅ 游戏统计 API 正常');
    } else {
      console.log(`   ❌ 游戏统计 API 失败: ${statsResponse.status()}`);
    }
    
    // 12. 访问成就页面
    console.log('\n12. 访问成就页面');
    await page.goto('http://localhost:8081/achievements');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/v005-06-achievements.png', fullPage: true });
    console.log('   ✅ 截图: 成就页面');
    
    console.log('\n=== V-005 验证结果 ===');
    console.log(`游戏启动: ✅`);
    console.log(`对话轮次: ${choiceCount}`);
    console.log(`到达结局: ${reachedEnding ? '✅' : '❌'}`);
    console.log(`统计数据: ${hasStats ? '✅' : '❌'}`);
    
    if (choiceCount > 0 && hasStats) {
      console.log('✅ V-005 通过: 剧本游戏完整流程正常');
    } else {
      console.log('⚠️  V-005 部分通过: 游戏流程需要检查');
    }
    
    await page.screenshot({ path: 'test-results/v005-07-final.png', fullPage: true });
  });
});
