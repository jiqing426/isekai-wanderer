import { test, expect } from '@playwright/test';

test.describe('T-024 & T-012 深度测试', () => {
  let testToken: string;

  test.beforeAll(async ({ request }) => {
    const timestamp = Date.now();
    const email = `deep_test${timestamp}@example.com`;
    
    await request.post('http://localhost:8000/api/v1/auth/register', {
      data: { email, password: 'Test123456', display_name: 'Deep Tester' }
    });
    
    const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
      data: { email, password: 'Test123456' }
    });
    
    const loginData = await loginResponse.json();
    testToken = loginData.access_token;
  });

  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8081/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, testToken);
    
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    const currentUrl = page.url();
    if (currentUrl.includes('/onboarding')) {
      await page.locator('.selection-card').first().click();
      await page.waitForTimeout(500);
      await page.locator('button.nav-button.primary').first().click();
      await page.waitForTimeout(1000);
      
      await page.locator('.selection-card').first().click();
      await page.waitForTimeout(500);
      await page.locator('button.nav-button.primary').first().click();
      await page.waitForTimeout(1000);
      
      await page.locator('button.nav-button.primary').first().click();
      await page.waitForTimeout(3000);
    }
  });

  test('T-024: 剧本详情页验证', async ({ page }) => {
    console.log('\n=== T-024: 剧本详情页验证 ===');
    
    // 访问剧本列表
    await page.goto('http://localhost:8081/discover');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 点击第一个剧本进入详情页
    const firstScript = await page.locator('.script-card').first();
    const scriptTitle = await firstScript.locator('h3, .title').textContent();
    console.log(`选择剧本: ${scriptTitle}`);
    
    await firstScript.click();
    await page.waitForTimeout(3000);
    
    const detailUrl = page.url();
    console.log(`详情页 URL: ${detailUrl}`);
    
    // 截图详情页
    await page.screenshot({ path: 'test-results/t024-01-script-detail.png', fullPage: true });
    console.log('✓ 截图: 剧本详情页');
    
    // 验证封面图
    const coverImage = await page.locator('img[src*="cover"], .cover-image, img').first();
    const hasCover = await coverImage.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasCover) {
      const imgSrc = await coverImage.getAttribute('src');
      console.log(`✓ 封面图存在: ${imgSrc?.substring(0, 50)}...`);
      
      // 检查图片尺寸
      const box = await coverImage.boundingBox();
      if (box) {
        console.log(`   尺寸: ${box.width}x${box.height}`);
        const ratio = box.width / box.height;
        if (ratio > 0.5 && ratio < 2.0) {
          console.log('   ✅ 封面图比例正常');
        } else {
          console.log(`   ⚠️ 封面图比例异常: ${ratio.toFixed(2)}`);
        }
      }
    } else {
      console.log('❌ 未找到封面图');
    }
    
    // 验证剧本信息
    const pageText = await page.textContent('body');
    
    // 检查标题
    const hasTitle = pageText?.includes(scriptTitle || '');
    console.log(`${hasTitle ? '✅' : '❌'} 剧本标题: ${hasTitle ? '显示' : '未显示'}`);
    
    // 检查描述
    const hasDescription = pageText?.length > 500; // 页面有足够内容
    console.log(`${hasDescription ? '✅' : '⚠️'} 剧本描述: ${hasDescription ? '存在' : '可能缺失'}`);
    
    // 检查开始游戏按钮
    const startButton = await page.locator('button:has-text("开始游戏"), button:has-text("开始"), .start-btn').first();
    const hasStartButton = await startButton.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasStartButton) {
      console.log('✅ 开始游戏按钮存在');
      
      // 检查按钮是否可点击
      const isEnabled = await startButton.isEnabled();
      console.log(`   按钮状态: ${isEnabled ? '可点击' : '禁用'}`);
      
      await page.screenshot({ path: 'test-results/t024-02-start-button.png', fullPage: true });
    } else {
      console.log('❌ 未找到开始游戏按钮');
    }
    
    // 检查其他信息
    const hasRouteInfo = /路线|分支|结局/.test(pageText || '');
    console.log(`${hasRouteInfo ? '✅' : '⚠️'} 路线信息: ${hasRouteInfo ? '显示' : '可能缺失'}`);
    
    await page.screenshot({ path: 'test-results/t024-03-full-detail.png', fullPage: true });
  });

  test('T-012: 剧本游戏深度测试', async ({ page }) => {
    console.log('\n=== T-012: 剧本游戏深度测试 ===');
    
    // 访问剧本列表
    await page.goto('http://localhost:8081/discover');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 点击第一个剧本
    const firstScript = await page.locator('.script-card').first();
    await firstScript.click();
    await page.waitForTimeout(3000);
    
    // 点击开始游戏
    const startButton = await page.locator('button:has-text("开始游戏"), button:has-text("开始")').first();
    await startButton.click();
    await page.waitForTimeout(5000);
    
    const gameUrl = page.url();
    console.log(`游戏页面 URL: ${gameUrl}`);
    
    // 截图游戏页面
    await page.screenshot({ path: 'test-results/t012-01-game-start.png', fullPage: true });
    console.log('✓ 截图: 游戏开始页面');
    
    // 检查游戏内容
    const pageText = await page.textContent('body');
    
    // 检查对话内容
    const hasDialogue = pageText?.length > 200;
    console.log(`${hasDialogue ? '✅' : '❌'} 对话内容: ${hasDialogue ? '存在' : '缺失'}`);
    
    // 检查选择项
    const choiceButtons = await page.locator('button').filter({ hasText: /选择|选项|对话/ });
    const choiceCount = await choiceButtons.count();
    console.log(`找到 ${choiceCount} 个选择项`);
    
    if (choiceCount > 0) {
      console.log('✅ 选择项存在');
      
      // 点击第一个选择
      const firstChoice = choiceButtons.first();
      const choiceText = await firstChoice.textContent();
      console.log(`   选择: ${choiceText?.substring(0, 50)}`);
      
      await firstChoice.click();
      await page.waitForTimeout(3000);
      
      // 截图选择后
      await page.screenshot({ path: 'test-results/t012-02-after-choice.png', fullPage: true });
      console.log('✓ 截图: 选择后页面');
      
      // 检查剧情是否推进
      const newPageText = await page.textContent('body');
      const isProgressed = newPageText !== pageText;
      console.log(`${isProgressed ? '✅' : '⚠️'} 剧情推进: ${isProgressed ? '是' : '可能未推进'}`);
      
      // 检查好感度更新
      const affectionElement = await page.locator('[class*="affection"], text=好感度').first();
      const hasAffection = await affectionElement.isVisible({ timeout: 2000 }).catch(() => false);
      
      if (hasAffection) {
        console.log('✅ 好感度显示存在');
      } else {
        console.log('⚠️ 未检测到好感度显示');
      }
    } else {
      console.log('⚠️ 未找到选择项（可能已到达结局）');
      
      // 检查是否是结局页面
      const isEnding = /结局|结束|ending/i.test(pageText || '');
      console.log(`${isEnding ? '✅' : '⚠️'} 结局页面: ${isEnding ? '是' : '否'}`);
    }
    
    // 检查 loading 动画（选择后）
    const loadingElement = await page.locator('.loading, .spinner, [class*="loading"]').first();
    const hasLoading = await loadingElement.isVisible({ timeout: 2000 }).catch(() => false);
    
    if (hasLoading) {
      console.log('✅ 检测到 loading 动画');
      await page.screenshot({ path: 'test-results/t012-03-loading.png', fullPage: true });
    } else {
      console.log('⚠️ 未检测到 loading 动画（可能加载过快）');
    }
    
    await page.screenshot({ path: 'test-results/t012-04-final.png', fullPage: true });
  });
});
