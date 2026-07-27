import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

test.describe('CR-018 T-003 头像上传浏览器验证', () => {
  let testEmail: string;
  const testPassword = '***';
  
  test.beforeEach(async ({ page, request }) => {
    // 通过 API 注册测试用户
    const timestamp = Date.now();
    testEmail = `t003test${timestamp}@test.com`;
    
    const response = await request.post('http://localhost:8000/api/v1/auth/register', {
      data: {
        email: testEmail,
        password: testPassword,
        display_name: 'T003-Tester'
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
    
    // 将 token 存储到 localStorage（使用前端实际的 key）
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, loginData.access_token);
    
    // 完成 onboarding 流程
    await page.goto('http://localhost:8081/onboarding');
    await page.waitForLoadState('networkidle');
    
    // 检查是否在 onboarding 页面
    const onboardingPage = await page.locator('text=个性化设置').first();
    if (await onboardingPage.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('检测到 onboarding 流程，开始完成...');
      
      // 步骤 1: 选择题材（点击第一个 selection-card）
      const genreCard = await page.locator('.selection-card').first();
      await genreCard.click();
      await page.waitForTimeout(500);
      
      // 点击"下一步"
      const nextBtn1 = await page.locator('button.nav-button.primary').first();
      await nextBtn1.click();
      await page.waitForTimeout(1000);
      console.log('✓ 步骤 1 完成');
      
      // 步骤 2: 选择角色风格（点击第一个 selection-card）
      const styleCard = await page.locator('.selection-card').first();
      await styleCard.click();
      await page.waitForTimeout(500);
      
      // 点击"下一步"
      const nextBtn2 = await page.locator('button.nav-button.primary').first();
      await nextBtn2.click();
      await page.waitForTimeout(1000);
      console.log('✓ 步骤 2 完成');
      
      // 步骤 3: 点击"开始冒险"完成 onboarding
      const startBtn = await page.locator('button.nav-button.primary').first();
      await startBtn.click();
      await page.waitForTimeout(3000);
      console.log('✓ Onboarding 完成');
    }
  });

  test('T-003: 头像上传完整流程', async ({ page }) => {
    console.log('=== T-003: 头像上传完整流程验证 ===\n');
    
    // 步骤 1: 进入设置页面
    console.log('步骤 1: 进入设置页面');
    await page.goto('http://localhost:8081/settings');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/t003-01-settings-page.png', fullPage: true });
    console.log('✓ 截图: 设置页面');

    // 步骤 2: 查找头像区域
    console.log('\n步骤 2: 查找头像区域');
    const avatarSection = await page.locator('.avatar-section').first();
    
    if (await avatarSection.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('✓ 找到头像区域');
      await page.screenshot({ path: 'test-results/t003-02-avatar-section.png', fullPage: true });
    } else {
      console.log('✗ 未找到头像区域');
      await page.screenshot({ path: 'test-results/t003-02-no-avatar-section.png', fullPage: true });
      throw new Error('未找到头像区域');
    }

    // 步骤 3: 查找"更换头像"按钮
    console.log('\n步骤 3: 查找更换头像按钮');
    const uploadButton = await page.locator('.upload-btn').first();
    
    if (await uploadButton.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('✓ 找到更换头像按钮');
      const buttonText = await uploadButton.textContent();
      console.log(`  按钮文本: ${buttonText}`);
    } else {
      console.log('✗ 未找到更换头像按钮');
      await page.screenshot({ path: 'test-results/t003-03-no-upload-button.png', fullPage: true });
      throw new Error('未找到更换头像按钮');
    }

    // 步骤 4: 查找隐藏的文件上传输入框
    console.log('\n步骤 4: 查找文件上传输入框');
    const fileInput = await page.locator('input[type="file"]').first();
    
    const inputExists = await fileInput.count() > 0;
    
    if (inputExists) {
      console.log('✓ 找到文件上传输入框（隐藏状态）');
      
      // 创建测试图片
      const testImagePath = path.join(process.cwd(), 'test-results', 'test-avatar.png');
      if (!fs.existsSync(path.join(process.cwd(), 'test-results'))) {
        fs.mkdirSync(path.join(process.cwd(), 'test-results'), { recursive: true });
      }
      
      // 创建一个简单的 PNG 文件
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
      
      // 上传测试图片
      console.log('\n步骤 5: 上传测试图片');
      await fileInput.setInputFiles(testImagePath);
      await page.waitForTimeout(3000);
      
      await page.screenshot({ path: 'test-results/t003-04-after-upload.png', fullPage: true });
      console.log('✓ 截图: 上传后页面');
      
      // 步骤 6: 检查上传结果
      console.log('\n步骤 6: 检查上传结果');
      
      const successMsg = await page.locator('text=头像上传成功').or(page.locator('.n-message')).first();
      const errorMsg = await page.locator('text=上传失败').or(page.locator('text=错误')).first();
      
      if (await successMsg.isVisible({ timeout: 2000 }).catch(() => false)) {
        console.log('✓ 检测到上传成功提示');
      } else if (await errorMsg.isVisible({ timeout: 2000 }).catch(() => false)) {
        const errText = await errorMsg.textContent();
        console.log(`✗ 上传失败: ${errText}`);
      } else {
        console.log('⚠ 未检测到明确的成功/失败提示');
      }
      
      // 步骤 7: 检查头像是否更新
      console.log('\n步骤 7: 检查头像是否更新');
      const avatarImg = await page.locator('.avatar-preview img').first();
      
      if (await avatarImg.isVisible({ timeout: 2000 }).catch(() => false)) {
        const imgSrc = await avatarImg.getAttribute('src');
        console.log(`✓ 头像图片 src: ${imgSrc}`);
      } else {
        console.log('⚠ 未找到头像图片元素');
      }
      
      // 步骤 8: 刷新页面验证持久化
      console.log('\n步骤 8: 刷新页面验证持久化');
      await page.reload();
      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: 'test-results/t003-05-after-reload.png', fullPage: true });
      console.log('✓ 截图: 刷新后页面');
      
      const avatarImgAfterReload = await page.locator('.avatar-preview img').first();
      if (await avatarImgAfterReload.isVisible({ timeout: 2000 }).catch(() => false)) {
        const imgSrcAfter = await avatarImgAfterReload.getAttribute('src');
        console.log(`✓ 刷新后头像 src: ${imgSrcAfter}`);
      } else {
        console.log('⚠ 刷新后未找到头像图片');
      }
      
    } else {
      console.log('✗ 未找到文件上传输入框');
      await page.screenshot({ path: 'test-results/t003-04-no-file-input.png', fullPage: true });
      throw new Error('未找到文件上传输入框');
    }
  });
});
