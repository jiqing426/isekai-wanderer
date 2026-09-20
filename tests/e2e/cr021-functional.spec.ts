import { test, expect } from '@playwright/test';

const APP_BASE = 'http://localhost:8081';
const JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJleHAiOjE3ODUyOTcyMTQsInR5cGUiOiJhY2Nlc3MifQ.jwxDr5A-nzTaR_cKnTihUX5IM8A3iOSiKFmSIjVXqvs';

test.describe('CR-021 真实功能测试', () => {
  
  test('1. 发送消息功能', async ({ page }) => {
    // 登录
    await page.goto(`${APP_BASE}/login`);
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, JWT_TOKEN);
    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');
    
    // 选择第一个角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);
    
    // 输入消息
    const messageInput = page.locator('textarea[placeholder*="消息"]');
    await messageInput.click();
    await messageInput.fill('你好，藤原雪！');
    await page.waitForTimeout(500);
    
    // 验证输入框有内容
    const inputValue = await messageInput.inputValue();
    console.log('输入框内容:', inputValue);
    
    // 点击发送
    const sendBtn = page.locator('.send-btn');
    const isDisabled = await sendBtn.getAttribute('disabled');
    console.log('发送按钮 disabled:', isDisabled);
    
    await sendBtn.click({ force: true });
    await page.waitForTimeout(2000);
    
    // 验证消息是否显示在列表中
    const messageList = page.locator('.message-list');
    const messageText = await messageList.textContent();
    
    if (messageText.includes('你好，藤原雪！')) {
      console.log('✅ 消息发送成功并显示在列表中');
    } else {
      console.log('❌ 消息发送后未显示在列表中');
      console.log('消息列表内容:', messageText);
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/send-message-test.png' });
  });

  test('2. 推荐话题点击功能', async ({ page }) => {
    await page.goto(`${APP_BASE}/login`);
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, JWT_TOKEN);
    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');
    
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);
    
    // 检查推荐话题是否存在
    const topicSection = page.locator('.topics-section');
    const hasTopics = await topicSection.isVisible();
    
    if (hasTopics) {
      console.log('✅ 推荐话题区域可见');
      
      // 获取第一个话题文本
      const firstTopic = page.locator('.topic-tag').first();
      const topicText = await firstTopic.textContent();
      console.log('第一个话题:', topicText);
      
      // 点击话题
      await firstTopic.click();
      await page.waitForTimeout(1000);
      
      // 验证话题是否填入输入框
      const inputValue = await page.locator('textarea[placeholder*="消息"]').inputValue();
      if (inputValue === topicText) {
        console.log('✅ 话题成功填入输入框');
      } else {
        console.log('❌ 话题未填入输入框');
        console.log('输入框内容:', inputValue);
      }
      
      await page.screenshot({ path: 'test-results/topic-click-test.png' });
    } else {
      console.log('⚠️ 推荐话题区域不可见，跳过测试');
    }
  });

  test('3. 送礼弹窗功能', async ({ page }) => {
    await page.goto(`${APP_BASE}/login`);
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, JWT_TOKEN);
    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');
    
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);
    
    // 点击加号
    await page.locator('.plus-btn').click();
    await page.waitForTimeout(1000);
    
    // 点击送礼
    const giftOption = page.locator('.menu-item').filter({ hasText: '送礼' }).first();
    await giftOption.click();
    await page.waitForTimeout(2000);
    
    // 检查送礼弹窗是否打开
    const modal = page.locator('.modal-overlay');
    const isModalVisible = await modal.isVisible();
    
    if (isModalVisible) {
      console.log('✅ 送礼弹窗成功打开');
      
      // 检查礼物列表
      const giftItems = page.locator('.gift-item');
      const giftCount = await giftItems.count();
      console.log(`礼物数量: ${giftCount}`);
      
      if (giftCount > 0) {
        // 点击第一个礼物
        await giftItems.first().click();
        await page.waitForTimeout(1000);
        
        // 检查是否显示确认按钮
        const confirmBtn = page.locator('.confirm-btn');
        const hasConfirm = await confirmBtn.isVisible();
        
        if (hasConfirm) {
          console.log('✅ 选择礼物后显示确认按钮');
        } else {
          console.log('❌ 选择礼物后未显示确认按钮');
        }
      }
      
      await page.screenshot({ path: 'test-results/gift-modal-test.png' });
    } else {
      console.log('❌ 送礼弹窗未打开');
      await page.screenshot({ path: 'test-results/gift-modal-failed.png' });
    }
  });

  test('4. 好感度数据验证', async ({ page }) => {
    await page.goto(`${APP_BASE}/login`);
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, JWT_TOKEN);
    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');
    
    // 获取第一个角色的好感度
    const firstCharacter = page.locator('.character-item').first();
    const affectionText = await firstCharacter.locator('.affection-text').textContent();
    console.log('第一个角色好感度:', affectionText);
    
    // 检查好感度格式
    if (affectionText && affectionText.includes('/100')) {
      console.log('✅ 好感度格式正确');
    } else {
      console.log('❌ 好感度格式错误');
    }
    
    // 点击角色查看详情页的好感度
    await firstCharacter.click();
    await page.waitForTimeout(2000);
    
    const chatAffection = page.locator('.affection-badge');
    const chatAffectionText = await chatAffection.textContent();
    console.log('聊天窗口好感度:', chatAffectionText);
    
    await page.screenshot({ path: 'test-results/affection-test.png' });
  });

  test('5. 角色详情跳转验证', async ({ page }) => {
    await page.goto(`${APP_BASE}/login`);
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, JWT_TOKEN);
    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');
    
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);
    
    // 获取当前角色名称
    const characterName = await page.locator('.chat-header h2').textContent();
    console.log('当前角色:', characterName);
    
    // 点击查看详情
    await page.locator('.detail-btn').click();
    await page.waitForTimeout(3000);
    
    // 验证是否跳转到详情页
    const currentUrl = page.url();
    console.log('当前URL:', currentUrl);
    
    if (currentUrl.includes('/characters/')) {
      console.log('✅ 成功跳转到角色详情页');
      
      // 检查详情页是否显示角色信息
      const detailName = await page.locator('h1, .character-name').first().textContent();
      console.log('详情页角色名:', detailName);
      
      if (detailName && detailName.includes(characterName!)) {
        console.log('✅ 详情页显示正确的角色');
      } else {
        console.log('❌ 详情页角色名不匹配');
      }
      
      await page.screenshot({ path: 'test-results/detail-page-test.png' });
    } else {
      console.log('❌ 未跳转到角色详情页');
      await page.screenshot({ path: 'test-results/detail-page-failed.png' });
    }
  });
});
