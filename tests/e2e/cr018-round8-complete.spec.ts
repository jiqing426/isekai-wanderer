import { test, expect } from '@playwright/test';

test.describe('CR-018 Round 8 - 浏览器完整验证', () => {
  const timestamp = Date.now();
  const testEmail = `round8test${timestamp}@test.com`;
  const testPassword = '***';

  test.beforeEach(async ({ page }) => {
    // 注册测试账号
    await page.goto('http://localhost:8081/register');
    await page.waitForLoadState('networkidle');
    
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.click('button[type="submit"]');
    
    await page.waitForTimeout(2000);
  });

  test('T-003: 头像上传完整流程', async ({ page }) => {
    console.log('=== T-003: 头像上传测试 ===');
    
    // 1. 进入个人中心
    await page.goto('http://localhost:8081/personal');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/round8-01-personal-center.png', fullPage: true });
    console.log('✓ 截图: 个人中心页面');

    // 2. 点击设置/头像区域
    const avatarButton = await page.locator('text=更换头像').or(page.locator('text=上传头像')).or(page.locator('.avatar-upload')).first();
    if (await avatarButton.isVisible()) {
      await avatarButton.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'test-results/round8-02-avatar-dialog.png', fullPage: true });
      console.log('✓ 截图: 头像上传对话框');
    } else {
      console.log('⚠ 未找到头像上传按钮，尝试查找设置页面');
      await page.goto('http://localhost:8081/settings');
      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: 'test-results/round8-02-settings-page.png', fullPage: true });
    }

    // 3. 尝试上传测试图片
    const fileInput = await page.locator('input[type="file"]').first();
    if (await fileInput.isVisible()) {
      // 创建测试图片
      const testImagePath = 'test-results/test-avatar.png';
      const fs = require('fs');
      if (!fs.existsSync('test-results')) {
        fs.mkdirSync('test-results', { recursive: true });
      }
      
      // 创建一个简单的 PNG 文件（1x1 像素）
      const pngHeader = Buffer.from([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, // PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52, // IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, // 1x1
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53, // 8-bit RGB
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41, // IDAT chunk
        0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
        0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,
        0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, // IEND chunk
        0x44, 0xAE, 0x42, 0x60, 0x82
      ]);
      fs.writeFileSync(testImagePath, pngHeader);
      
      await fileInput.setInputFiles(testImagePath);
      await page.waitForTimeout(3000);
      
      // 4. 检查上传结果
      await page.screenshot({ path: 'test-results/round8-03-after-upload.png', fullPage: true });
      console.log('✓ 截图: 上传后页面');
      
      // 检查是否有成功提示或错误信息
      const successMsg = await page.locator('text=上传成功').or(page.locator('text=成功')).first();
      const errorMsg = await page.locator('text=失败').or(page.locator('text=错误')).or(page.locator('.error')).first();
      
      if (await successMsg.isVisible({ timeout: 2000 }).catch(() => false)) {
        console.log('✓ 头像上传成功');
      } else if (await errorMsg.isVisible({ timeout: 2000 }).catch(() => false)) {
        const errorText = await errorMsg.textContent();
        console.log(`✗ 头像上传失败: ${errorText}`);
      } else {
        console.log('⚠ 未检测到明确的成功/失败提示');
      }
      
      // 5. 刷新页面验证头像是否持久化
      await page.reload();
      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: 'test-results/round8-04-after-reload.png', fullPage: true });
      console.log('✓ 截图: 刷新后页面');
    } else {
      console.log('✗ 未找到文件上传输入框');
      await page.screenshot({ path: 'test-results/round8-03-no-file-input.png', fullPage: true });
    }
  });

  test('角色详情页验证', async ({ page }) => {
    console.log('=== 角色详情页测试 ===');
    
    // 1. 进入剧本列表
    await page.goto('http://localhost:8081/scripts');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/round8-05-scripts-list.png', fullPage: true });
    console.log('✓ 截图: 剧本列表');

    // 2. 点击第一个剧本
    const firstScript = await page.locator('.script-card, .script-item, [class*="script"]').first();
    if (await firstScript.isVisible()) {
      await firstScript.click();
      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: 'test-results/round8-06-script-detail.png', fullPage: true });
      console.log('✓ 截图: 剧本详情页');

      // 3. 查找角色列表
      const characterLink = await page.locator('text=角色').or(page.locator('text=查看角色')).or(page.locator('[href*="character"]')).first();
      if (await characterLink.isVisible()) {
        await characterLink.click();
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/round8-07-character-list.png', fullPage: true });
        console.log('✓ 截图: 角色列表');

        // 4. 点击第一个角色
        const firstChar = await page.locator('.character-card, .character-item, [class*="character"]').first();
        if (await firstChar.isVisible()) {
          await firstChar.click();
          await page.waitForLoadState('networkidle');
          await page.screenshot({ path: 'test-results/round8-08-character-detail.png', fullPage: true });
          console.log('✓ 截图: 角色详情页');

          // 5. 检查性格特点区域
          const personalitySection = await page.locator('text=性格').or(page.locator('text=特点')).or(page.locator('[class*="personality"]')).first();
          if (await personalitySection.isVisible({ timeout: 3000 }).catch(() => false)) {
            const personalityText = await personalitySection.textContent();
            console.log(`✓ 性格特点: ${personalityText}`);
          } else {
            console.log('⚠ 未找到性格特点区域');
          }

          // 6. 检查语音试听区域
          const voiceSection = await page.locator('text=语音').or(page.locator('text=试听')).or(page.locator('[class*="voice"]')).first();
          if (await voiceSection.isVisible({ timeout: 3000 }).catch(() => false)) {
            const voiceText = await voiceSection.textContent();
            console.log(`✓ 语音试听: ${voiceText}`);
          } else {
            console.log('⚠ 未找到语音试听区域');
          }

          await page.screenshot({ path: 'test-results/round8-09-character-full.png', fullPage: true });
        } else {
          console.log('✗ 未找到角色卡片');
        }
      } else {
        console.log('⚠ 未找到角色链接');
      }
    } else {
      console.log('✗ 未找到剧本卡片');
    }
  });

  test('开始游戏流程', async ({ page }) => {
    console.log('=== 开始游戏流程测试 ===');
    
    // 1. 进入剧本列表
    await page.goto('http://localhost:8081/scripts');
    await page.waitForLoadState('networkidle');
    
    // 2. 点击第一个剧本
    const firstScript = await page.locator('.script-card, .script-item, [class*="script"]').first();
    if (await firstScript.isVisible()) {
      await firstScript.click();
      await page.waitForLoadState('networkidle');
      
      // 3. 点击开始游戏按钮
      const startButton = await page.locator('text=开始游戏').or(page.locator('text=开始')).or(page.locator('button:has-text("开始")')).first();
      if (await startButton.isVisible()) {
        await startButton.click();
        await page.waitForTimeout(3000);
        await page.screenshot({ path: 'test-results/round8-10-game-start.png', fullPage: true });
        console.log('✓ 截图: 游戏开始页面');

        // 4. 检查是否进入游戏页面
        const gameContent = await page.locator('.game-container, .game-content, [class*="game"]').first();
        if (await gameContent.isVisible({ timeout: 5000 }).catch(() => false)) {
          console.log('✓ 成功进入游戏页面');
          
          // 5. 检查是否有对话内容
          const dialogue = await page.locator('.dialogue, .message, [class*="dialogue"]').first();
          if (await dialogue.isVisible({ timeout: 3000 }).catch(() => false)) {
            const dialogueText = await dialogue.textContent();
            console.log(`✓ 对话内容: ${dialogueText.substring(0, 100)}`);
          }
          
          // 6. 检查是否有选择项
          const choices = await page.locator('.choice, .option, [class*="choice"]');
          const choiceCount = await choices.count();
          console.log(`✓ 选择项数量: ${choiceCount}`);
          
          if (choiceCount > 0) {
            await page.screenshot({ path: 'test-results/round8-11-game-choices.png', fullPage: true });
            
            // 7. 点击第一个选择
            await choices.first().click();
            await page.waitForTimeout(2000);
            await page.screenshot({ path: 'test-results/round8-12-after-choice.png', fullPage: true });
            console.log('✓ 截图: 选择后页面');
          }
        } else {
          console.log('✗ 未进入游戏页面');
          
          // 检查是否有错误提示
          const errorMsg = await page.locator('.error, .alert, [class*="error"]').first();
          if (await errorMsg.isVisible({ timeout: 2000 }).catch(() => false)) {
            const errorText = await errorMsg.textContent();
            console.log(`✗ 错误信息: ${errorText}`);
          }
        }
      } else {
        console.log('✗ 未找到开始游戏按钮');
      }
    } else {
      console.log('✗ 未找到剧本');
    }
  });

  test('前端 401 问题排查', async ({ page }) => {
    console.log('=== 401 问题排查 ===');
    
    // 监听网络请求
    const failedRequests = [];
    page.on('requestfailed', request => {
      failedRequests.push({
        url: request.url(),
        method: request.method(),
        status: request.failure()?.errorText
      });
    });

    page.on('response', response => {
      if (response.status() === 401) {
        failedRequests.push({
          url: response.url(),
          method: response.request().method(),
          status: 401
        });
      }
    });

    // 1. 访问多个页面
    await page.goto('http://localhost:8081/scripts');
    await page.waitForLoadState('networkidle');
    
    await page.goto('http://localhost:8081/personal');
    await page.waitForLoadState('networkidle');
    
    // 2. 尝试开始游戏
    const firstScript = await page.locator('.script-card, .script-item, [class*="script"]').first();
    if (await firstScript.isVisible()) {
      await firstScript.click();
      await page.waitForLoadState('networkidle');
      
      const startButton = await page.locator('text=开始游戏').first();
      if (await startButton.isVisible()) {
        await startButton.click();
        await page.waitForTimeout(3000);
      }
    }

    // 3. 检查 LocalStorage 中的 token
    const token = await page.evaluate(() => {
      return localStorage.getItem('token') || localStorage.getItem('access_token');
    });
    
    if (token) {
      console.log(`✓ LocalStorage 中存在 token: ${token.substring(0, 20)}...`);
    } else {
      console.log('✗ LocalStorage 中未找到 token');
    }

    // 4. 检查请求头
    const authHeader = await page.evaluate(() => {
      // 尝试拦截一个请求看 headers
      return new Promise(resolve => {
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
          const request = args[0];
          if (typeof request === 'string' && request.includes('/api/')) {
            const headers = args[1]?.headers || {};
            resolve({
              url: request,
              hasAuth: !!headers.Authorization || !!headers.authorization
            });
          }
          return originalFetch.apply(this, args);
        };
        
        // 触发一个 API 请求
        fetch('/api/v1/users/me/stats').catch(() => {});
        setTimeout(() => resolve(null), 1000);
      });
    });

    if (authHeader) {
      console.log(`✓ API 请求 ${authHeader.url} ${authHeader.hasAuth ? '包含' : '缺少'} Authorization header`);
    }

    // 5. 输出失败请求
    if (failedRequests.length > 0) {
      console.log(`\n✗ 发现 ${failedRequests.length} 个失败请求:`);
      failedRequests.forEach(req => {
        console.log(`  - ${req.method} ${req.url} (${req.status})`);
      });
    } else {
      console.log('✓ 未发现 401 错误');
    }

    await page.screenshot({ path: 'test-results/round8-13-401-check.png', fullPage: true });
  });
});
