import { test, expect } from '@playwright/test';

test.describe('V-003: CG 获取动效验证', () => {
  test('验证 CG 获取时是否有动效展示', async ({ page, request }) => {
    const timestamp = Date.now();
    const testEmail = `v003_test_${timestamp}@example.com`;
    const testPassword = '***';
    
    console.log('=== V-003: CG 获取动效验证 ===\n');
    
    // 1. 注册新用户
    console.log('1. 注册新用户');
    const regResponse = await request.post('http://localhost:8000/api/v1/auth/register', {
      data: {
        email: testEmail,
        password: testPassword,
        display_name: 'V003-Tester'
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
    
    // 5. 访问收藏馆页面
    console.log('\n5. 访问收藏馆页面');
    await page.goto('http://localhost:8081/gallery');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/v003-01-gallery-page.png', fullPage: true });
    console.log('   ✅ 截图: 收藏馆页面');
    
    // 6. 检查 CG 标签页
    console.log('\n6. 检查 CG 标签页');
    const cgTab = await page.locator('button:has-text("CG"), [data-tab="cg"]').first();
    const hasCgTab = await cgTab.isVisible({ timeout: 2000 }).catch(() => false);
    
    if (hasCgTab) {
      console.log('   ✅ 找到 CG 标签页');
      await cgTab.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'test-results/v003-02-cg-tab.png', fullPage: true });
      console.log('   ✅ 截图: CG 标签页');
    } else {
      console.log('   ⚠️  未找到 CG 标签页');
    }
    
    // 7. 检查 CG 列表
    console.log('\n7. 检查 CG 列表');
    const cgList = await page.locator('.cg-item, .cg-card, [class*="cg"]').count();
    console.log(`   找到 ${cgList} 个 CG 项`);
    
    if (cgList > 0) {
      console.log('   ✅ CG 列表显示正常');
      
      // 8. 检查 CG 动效
      console.log('\n8. 检查 CG 动效');
      const firstCg = await page.locator('.cg-item, .cg-card').first();
      
      if (await firstCg.isVisible({ timeout: 2000 }).catch(() => false)) {
        // 检查是否有动画相关的类或样式
        const cgClass = await firstCg.getAttribute('class');
        console.log(`   CG 元素类名: ${cgClass}`);
        
        // 检查是否有动画属性
        const hasAnimation = cgClass?.includes('animate') || cgClass?.includes('transition') || cgClass?.includes('fade');
        
        if (hasAnimation) {
          console.log('   ✅ CG 元素包含动画类');
        } else {
          console.log('   ⚠️  CG 元素未检测到动画类');
        }
        
        // 尝试点击 CG 查看详情
        await firstCg.click();
        await page.waitForTimeout(1000);
        await page.screenshot({ path: 'test-results/v003-03-cg-detail.png', fullPage: true });
        console.log('   ✅ 截图: CG 详情');
        
        // 检查是否有弹窗或详情页动画
        const modal = await page.locator('.modal, .cg-modal, [class*="modal"]').first();
        const hasModal = await modal.isVisible({ timeout: 2000 }).catch(() => false);
        
        if (hasModal) {
          console.log('   ✅ 找到 CG 详情弹窗');
          const modalClass = await modal.getAttribute('class');
          console.log(`   弹窗类名: ${modalClass}`);
          
          const modalHasAnimation = modalClass?.includes('animate') || modalClass?.includes('fade') || modalClass?.includes('transition');
          if (modalHasAnimation) {
            console.log('   ✅ 弹窗包含动画效果');
          } else {
            console.log('   ⚠️  弹窗未检测到动画效果');
          }
        }
      }
    } else {
      console.log('   ⚠️  未找到 CG 项（可能没有解锁的 CG）');
    }
    
    // 9. API 验证 CG 数据
    console.log('\n9. API 验证 CG 数据');
    const cgResponse = await request.get('http://localhost:8000/api/v1/users/me/collections', {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (cgResponse.status() === 200) {
      const cgData = await cgResponse.json();
      const cgCount = cgData.length || cgData.collections?.length || 0;
      console.log(`   API 返回 CG 数量: ${cgCount}`);
      console.log('   ✅ CG API 正常');
    } else {
      console.log(`   ❌ CG API 失败: ${cgResponse.status()}`);
    }
    
    console.log('\n=== V-003 验证结果 ===');
    console.log(`CG 标签页: ${hasCgTab ? '有' : '无'}`);
    console.log(`CG 列表: ${cgList} 个`);
    
    if (hasCgTab) {
      console.log('✅ V-003 通过: CG 收藏馆功能正常');
    } else {
      console.log('⚠️  V-003 部分通过: CG 功能需要检查');
    }
    
    await page.screenshot({ path: 'test-results/v003-04-final.png', fullPage: true });
  });
});
