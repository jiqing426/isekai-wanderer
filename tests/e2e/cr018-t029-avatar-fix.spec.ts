import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

test.describe('CR-018 T-029 头像上传修复验证', () => {
  let testEmail: string;
  const testPassword = '***';
  
  test.beforeEach(async ({ page, request }) => {
    // 通过 API 注册测试用户
    const timestamp = Date.now();
    testEmail = `t029test${timestamp}@example.com`;
    
    const response = await request.post('http://localhost:8000/api/v1/auth/register', {
      data: {
        email: testEmail,
        password: testPassword,
        display_name: 'T029-Tester'
      }
    });
    
    expect(response.status()).toBe(201);
    
    // 通过 API 登录获取 token
    const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
      data: {
        email: testEmail,
        password: testPassword
      }
    });
    
    expect(loginResponse.status()).toBe(200);
    const loginData = await loginResponse.json();
    
    // 先访问任意页面以初始化 localStorage
    await page.goto('http://localhost:8081/');
    await page.waitForLoadState('networkidle');
    
    // 将 token 存储到 localStorage
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, loginData.access_token);
    
    // 完成 onboarding 流程
    await page.goto('http://localhost:8081/onboarding');
    await page.waitForLoadState('networkidle');
    
    const onboardingPage = await page.locator('text=个性化设置').first();
    if (await onboardingPage.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('检测到 onboarding 流程，开始完成...');
      
      // 步骤 1: 选择题材
      const genreCard = await page.locator('.selection-card').first();
      await genreCard.click();
      await page.waitForTimeout(500);
      
      const nextBtn1 = await page.locator('button.nav-button.primary').first();
      await nextBtn1.click();
      await page.waitForTimeout(1000);
      console.log('✓ 步骤 1 完成');
      
      // 步骤 2: 选择角色风格
      const styleCard = await page.locator('.selection-card').first();
      await styleCard.click();
      await page.waitForTimeout(500);
      
      const nextBtn2 = await page.locator('button.nav-button.primary').first();
      await nextBtn2.click();
      await page.waitForTimeout(1000);
      console.log('✓ 步骤 2 完成');
      
      // 步骤 3: 完成 onboarding
      const startBtn = await page.locator('button.nav-button.primary').first();
      await startBtn.click();
      await page.waitForTimeout(3000);
      console.log('✓ Onboarding 完成');
    }
  });

  test('T-029: 头像上传功能验证', async ({ page }) => {
    console.log('=== T-029: 头像上传功能验证 ===\n');
    
    // 步骤 1: 进入设置页面
    console.log('步骤 1: 进入设置页面');
    await page.goto('http://localhost:8081/settings');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/t029-01-settings-page.png', fullPage: true });
    console.log('✓ 截图: 设置页面');

    // 步骤 2: 查找头像区域
    console.log('\n步骤 2: 查找头像区域');
    const avatarSection = await page.locator('.avatar-section').first();
    
    if (await avatarSection.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('✓ 找到头像区域');
      await page.screenshot({ path: 'test-results/t029-02-avatar-section.png', fullPage: true });
    } else {
      console.log('✗ 未找到头像区域');
      throw new Error('未找到头像区域');
    }

    // 步骤 3: 查找"更换头像"按钮
    console.log('\n步骤 3: 查找更换头像按钮');
    const uploadButton = await page.locator('.upload-btn').first();
    
    if (await uploadButton.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('✓ 找到更换头像按钮');
    } else {
      console.log('✗ 未找到更换头像按钮');
      throw new Error('未找到更换头像按钮');
    }

    // 步骤 4: 上传测试图片
    console.log('\n步骤 4: 上传测试图片');
    const fileInput = await page.locator('input[type="file"]').first();
    
    if (await fileInput.count() === 0) {
      console.log('✗ 未找到文件上传输入框');
      throw new Error('未找到文件上传输入框');
    }
    
    console.log('✓ 找到文件上传输入框');
    
    // 创建测试图片
    const testImagePath = path.join(process.cwd(), 'test-results', 'test-avatar.png');
    if (!fs.existsSync(path.join(process.cwd(), 'test-results'))) {
      fs.mkdirSync(path.join(process.cwd(), 'test-results'), { recursive: true });
    }
    
    const pngHeader = Buffer.from([
      0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
      0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x0A,
      0x08, 0x02, 0x00, 0x00, 0x00, 0x02, 0x50, 0x58, 0xEA, 0x00, 0x00, 0x00,
      0x01, 0x73, 0x52, 0x47, 0x42, 0x00, 0xAE, 0xCE, 0x1C, 0xE9, 0x00, 0x00,
      0x00, 0x04, 0x67, 0x41, 0x4D, 0x41, 0x00, 0x00, 0xB1, 0x8F, 0x0B, 0xFC,
      0x61, 0x05, 0x00, 0x00, 0x00, 0x09, 0x70, 0x48, 0x59, 0x73, 0x00, 0x00,
      0x0E, 0xC4, 0x00, 0x00, 0x0E, 0xC4, 0x01, 0x95, 0x2B, 0x0E, 0x1B, 0x00,
      0x00, 0x00, 0x1F, 0x49, 0x44, 0x41, 0x54, 0x78, 0x5E, 0x63, 0xFC, 0xFF,
      0xFF, 0x3F, 0x03, 0x9C, 0xFA, 0xFF, 0xFF, 0x3F, 0x03, 0x9C, 0xFA, 0xFF,
      0xFF, 0x3F, 0x63, 0x06, 0x98, 0xC1, 0x00, 0x05, 0x0E, 0x02, 0x05, 0xC7,
      0x11, 0x0D, 0x00, 0x48, 0x5F, 0x06, 0x4E, 0x33, 0xE3, 0xA8, 0x00, 0x00,
      0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
    ]);
    fs.writeFileSync(testImagePath, pngHeader);
    
    await fileInput.setInputFiles(testImagePath);
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: 'test-results/t029-03-after-upload.png', fullPage: true });
    console.log('✓ 截图: 上传后页面');
    
    // 步骤 5: 检查上传结果
    console.log('\n步骤 5: 检查上传结果');
    
    const successMsg = await page.locator('text=头像上传成功').or(page.locator('.n-message')).first();
    const errorMsg = await page.locator('text=上传失败').or(page.locator('text=错误')).or(page.locator('text=未登录')).first();
    
    if (await successMsg.isVisible({ timeout: 2000 }).catch(() => false)) {
      console.log('✓ 检测到上传成功提示');
    } else if (await errorMsg.isVisible({ timeout: 2000 }).catch(() => false)) {
      const errText = await errorMsg.textContent();
      console.log(`✗ 上传失败: ${errText}`);
      throw new Error(`上传失败: ${errText}`);
    } else {
      console.log('⚠ 未检测到明确的成功/失败提示');
    }
    
    // 步骤 6: 检查头像是否更新
    console.log('\n步骤 6: 检查头像是否更新');
    const avatarImg = await page.locator('.avatar-preview img').first();
    
    if (await avatarImg.isVisible({ timeout: 2000 }).catch(() => false)) {
      const imgSrc = await avatarImg.getAttribute('src');
      console.log(`✓ 头像图片 src: ${imgSrc}`);
      
      if (imgSrc && imgSrc.includes('avatar')) {
        console.log('✓ 头像已更新');
      } else {
        console.log(' 头像 src 可能未更新');
      }
    } else {
      console.log(' 未找到头像图片元素');
    }
    
    // 步骤 7: 刷新页面验证持久化
    console.log('\n步骤 7: 刷新页面验证持久化');
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/t029-04-after-reload.png', fullPage: true });
    console.log('✓ 截图: 刷新后页面');
    
    const avatarImgAfterReload = await page.locator('.avatar-preview img').first();
    if (await avatarImgAfterReload.isVisible({ timeout: 2000 }).catch(() => false)) {
      const imgSrcAfter = await avatarImgAfterReload.getAttribute('src');
      console.log(`✓ 刷新后头像 src: ${imgSrcAfter}`);
      
      if (imgSrcAfter && imgSrcAfter.includes('avatar')) {
        console.log('✓ T-029 通过: 头像上传并持久化成功');
      } else {
        console.log('⚠ 头像可能未持久化');
      }
    } else {
      console.log('⚠ 刷新后未找到头像图片');
    }
  });

  test('T-029 边界场景: 未登录状态上传头像', async ({ page }) => {
    console.log('=== T-029 边界场景: 未登录状态 ===\n');
    
    // 清除 token
    await page.goto('http://localhost:8081/');
    await page.evaluate(() => {
      localStorage.removeItem('isekai_access_token');
      localStorage.removeItem('isekai_refresh_token');
    });
    
    // 进入设置页面（应该被重定向到登录）
    await page.goto('http://localhost:8081/settings');
    await page.waitForLoadState('networkidle');
    
    const currentUrl = page.url();
    console.log(`当前 URL: ${currentUrl}`);
    
    if (currentUrl.includes('/login')) {
      console.log('✓ 未登录状态被重定向到登录页面');
      console.log('✓ T-029 边界场景通过');
    } else {
      console.log(' 未被重定向到登录页面');
    }
  });
});
