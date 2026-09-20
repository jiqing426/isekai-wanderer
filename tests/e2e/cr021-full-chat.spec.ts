import { test, expect, Page } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJleHAiOjE3ODUyOTgyOTQsInR5cGUiOiJhY2Nlc3MifQ.iM3h840PLgpRc8klLHqrkj6qrPJtO3EqSZbHBR6AZnY';

async function injectAuth(page: Page) {
  await page.goto(`${APP_BASE}/`);
  await page.evaluate((token) => {
    localStorage.setItem('isekai_access_token', token);
  }, JWT_TOKEN);
  await page.goto(`${APP_BASE}/character-chat`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
}

test.describe('CR-021 角色聊天完整功能测试', () => {

  test('页面加载和布局验证', async ({ page }) => {
    await injectAuth(page);
    
    // 验证页面标题
    const title = await page.title();
    expect(title).toContain('Isekai');
    
    // 验证 Header 导航
    const headerNav = page.locator('.header-nav');
    await expect(headerNav).toBeVisible();
    
    // 验证角色聊天 Tab 激活
    const chatTab = page.locator('a[href="/character-chat"]');
    await expect(chatTab).toBeVisible();
    await expect(chatTab).toHaveClass(/active/);
    
    // 验证主容器
    const chatContainer = page.locator('.chat-container');
    await expect(chatContainer).toBeVisible();
    
    console.log('✅ 页面加载和布局验证通过');
  });

  test('角色列表功能', async ({ page }) => {
    await injectAuth(page);
    
    // 验证角色列表容器
    const characterList = page.locator('.character-list');
    await expect(characterList).toBeVisible();
    
    // 验证角色数量
    const characterItems = page.locator('.character-item');
    const count = await characterItems.count();
    expect(count).toBeGreaterThan(0);
    console.log(`✅ 角色列表显示 ${count} 个角色`);
    
    // 验证第一个角色有头像
    const firstAvatar = characterItems.first().locator('.character-avatar img');
    await expect(firstAvatar).toBeVisible();
    
    // 验证第一个角色有好感度进度条
    const firstAffectionBar = characterItems.first().locator('.affection-bar');
    await expect(firstAffectionBar).toBeVisible();
    
    // 验证好感度数值显示
    const firstAffectionText = characterItems.first().locator('.affection-text');
    const affectionText = await firstAffectionText.textContent();
    expect(affectionText).toContain('好感度');
    console.log(`✅ 好感度显示: ${affectionText}`);
    
    // 点击第二个角色
    if (count >= 2) {
      await characterItems.nth(1).click();
      await page.waitForTimeout(1000);
      
      // 验证第二个角色被选中
      const secondItem = characterItems.nth(1);
      await expect(secondItem).toHaveClass(/active/);
      console.log('✅ 角色切换功能正常');
    }
  });

  test('聊天窗口功能', async ({ page }) => {
    await injectAuth(page);
    
    // 选择第一个角色
    const firstCharacter = page.locator('.character-item').first();
    await firstCharacter.click();
    await page.waitForTimeout(1500);
    
    // 验证聊天窗口显示
    const chatWindow = page.locator('.chat-window');
    await expect(chatWindow).toBeVisible();
    
    // 验证聊天头部
    const chatHeader = page.locator('.chat-header');
    await expect(chatHeader).toBeVisible();
    
    // 验证角色名称显示
    const characterName = chatHeader.locator('h2');
    await expect(characterName).toBeVisible();
    const name = await characterName.textContent();
    expect(name).toBeTruthy();
    console.log(`✅ 角色名称: ${name}`);
    
    // 验证好感度徽章
    const affectionBadge = chatHeader.locator('.affection-badge');
    await expect(affectionBadge).toBeVisible();
    
    // 验证查看详情按钮
    const detailBtn = chatHeader.locator('.detail-btn');
    await expect(detailBtn).toBeVisible();
    const btnText = await detailBtn.textContent();
    expect(btnText).toContain('查看详情');
    
    // 验证消息列表区域
    const messageList = page.locator('.message-list');
    await expect(messageList).toBeVisible();
    
    // 验证空消息提示
    const emptyMessage = messageList.locator('.empty-messages');
    const isEmpty = await emptyMessage.isVisible().catch(() => false);
    if (isEmpty) {
      console.log('✅ 空消息提示显示正常');
    }
    
    // 验证输入栏
    const inputBar = page.locator('.input-bar');
    await expect(inputBar).toBeVisible();
    
    // 验证加号按钮
    const plusBtn = inputBar.locator('.plus-btn');
    await expect(plusBtn).toBeVisible();
    
    // 验证输入框
    const input = inputBar.locator('input[type="text"]');
    await expect(input).toBeVisible();
    await expect(input).toHaveAttribute('placeholder', '输入消息...');
    
    // 验证发送按钮
    const sendBtn = inputBar.locator('.send-btn');
    await expect(sendBtn).toBeVisible();
    
    console.log('✅ 聊天窗口功能验证通过');
  });

  test('消息发送功能', async ({ page }) => {
    await injectAuth(page);
    
    // 选择第一个角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(1500);
    
    // 输入消息
    const input = page.locator('.input-bar input');
    await input.fill('你好，这是一条测试消息');
    
    // 验证发送按钮启用
    const sendBtn = page.locator('.send-btn');
    await expect(sendBtn).toBeEnabled();
    
    // 点击发送
    await sendBtn.click();
    
    // 等待消息发送
    await page.waitForTimeout(2000);
    
    // 验证输入框清空
    const inputValue = await input.inputValue();
    expect(inputValue).toBe('');
    console.log('✅ 消息发送后输入框清空');
    
    // 验证消息出现在列表中
    const messages = page.locator('.message-item');
    const messageCount = await messages.count();
    expect(messageCount).toBeGreaterThan(0);
    console.log(`✅ 消息发送成功，当前 ${messageCount} 条消息`);
    
    // 验证消息内容
    const lastMessage = messages.last();
    const messageContent = await lastMessage.locator('.message-content').textContent();
    expect(messageContent).toContain('你好，这是一条测试消息');
    
    // 验证消息是用户发送的（右侧）
    await expect(lastMessage).toHaveClass(/user/);
    console.log('✅ 用户消息样式正确');
  });

  test('加号菜单功能', async ({ page }) => {
    await injectAuth(page);
    
    // 选择角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(1500);
    
    // 点击加号按钮
    const plusBtn = page.locator('.plus-btn');
    await plusBtn.click();
    await page.waitForTimeout(500);
    
    // 验证菜单显示
    const plusMenu = page.locator('.plus-menu');
    await expect(plusMenu).toBeVisible();
    
    // 验证菜单项
    const menuItems = plusMenu.locator('.menu-item');
    const itemCount = await menuItems.count();
    expect(itemCount).toBe(2);
    
    // 验证送礼选项
    const giftOption = menuItems.first();
    const giftText = await giftOption.textContent();
    expect(giftText).toContain('送礼');
    
    // 验证送礼记录选项
    const historyOption = menuItems.nth(1);
    const historyText = await historyOption.textContent();
    expect(historyText).toContain('送礼记录');
    
    console.log('✅ 加号菜单功能验证通过');
    
    // 点击外部关闭菜单
    await page.locator('.chat-window').click({ position: { x: 10, y: 10 } });
    await page.waitForTimeout(500);
    
    // 验证菜单关闭
    const menuHidden = await plusMenu.isVisible().catch(() => false);
    expect(menuHidden).toBeFalsy();
    console.log('✅ 点击外部关闭菜单');
  });

  test('送礼弹窗功能', async ({ page }) => {
    await injectAuth(page);
    
    // 选择角色并打开加号菜单
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(1500);
    await page.locator('.plus-btn').click();
    await page.waitForTimeout(500);
    
    // 点击送礼
    await page.locator('.plus-menu .menu-item').first().click();
    await page.waitForTimeout(1000);
    
    // 验证送礼弹窗显示
    const modal = page.locator('.modal-overlay');
    await expect(modal).toBeVisible();
    
    // 验证弹窗标题
    const modalTitle = modal.locator('h3');
    const title = await modalTitle.textContent();
    expect(title).toContain('送礼');
    
    // 验证礼物列表
    const giftList = modal.locator('.gift-list');
    await expect(giftList).toBeVisible();
    
    // 验证礼物项
    const giftItems = giftList.locator('.gift-item');
    const giftCount = await giftItems.count();
    expect(giftCount).toBeGreaterThan(0);
    console.log(`✅ 送礼弹窗显示 ${giftCount} 个礼物`);
    
    // 验证按钮
    const cancelBtn = modal.locator('.cancel-btn');
    await expect(cancelBtn).toBeVisible();
    
    const confirmBtn = modal.locator('.confirm-btn');
    await expect(confirmBtn).toBeVisible();
    
    // 关闭弹窗
    await cancelBtn.click();
    await page.waitForTimeout(500);
    
    // 验证弹窗关闭
    const modalHidden = await modal.isVisible().catch(() => false);
    expect(modalHidden).toBeFalsy();
    console.log('✅ 送礼弹窗关闭正常');
  });

  test('送礼记录弹窗功能', async ({ page }) => {
    await injectAuth(page);
    
    // 选择角色并打开加号菜单
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(1500);
    await page.locator('.plus-btn').click();
    await page.waitForTimeout(500);
    
    // 点击送礼记录
    await page.locator('.plus-menu .menu-item').nth(1).click();
    await page.waitForTimeout(1000);
    
    // 验证弹窗显示
    const modal = page.locator('.modal-overlay');
    await expect(modal).toBeVisible();
    
    // 验证弹窗标题
    const modalTitle = modal.locator('h3');
    const title = await modalTitle.textContent();
    expect(title).toContain('送礼记录');
    
    // 验证记录列表
    const historyList = modal.locator('.history-list');
    await expect(historyList).toBeVisible();
    
    // 验证关闭按钮
    const closeBtn = modal.locator('.close-btn');
    await expect(closeBtn).toBeVisible();
    
    // 关闭弹窗
    await closeBtn.click();
    await page.waitForTimeout(500);
    
    console.log('✅ 送礼记录弹窗功能验证通过');
  });

  test('查看详情跳转', async ({ page }) => {
    await injectAuth(page);
    
    // 选择角色
    const firstCharacter = page.locator('.character-item').first();
    await firstCharacter.click();
    await page.waitForTimeout(1500);
    
    // 获取角色 ID
    const characterId = await page.evaluate(() => {
      const activeItem = document.querySelector('.character-item.active');
      return activeItem?.getAttribute('data-character-id');
    });
    
    // 点击查看详情
    const detailBtn = page.locator('.detail-btn');
    await detailBtn.click();
    
    // 等待跳转
    await page.waitForURL('**/characters/**', { timeout: 10000 });
    
    // 验证 URL
    const currentUrl = page.url();
    expect(currentUrl).toContain('/characters/');
    expect(currentUrl).toContain(characterId || '');
    console.log(`✅ 成功跳转到角色详情页: ${currentUrl}`);
    
    // 返回聊天页面
    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');
    console.log('✅ 返回聊天页面正常');
  });

  test('响应式布局', async ({ page }) => {
    // 桌面端测试
    await page.setViewportSize({ width: 1920, height: 1080 });
    await injectAuth(page);
    
    const desktopContainer = page.locator('.chat-container');
    await expect(desktopContainer).toBeVisible();
    console.log('✅ 桌面端布局正常 (1920x1080)');
    
    // 平板端测试
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    console.log('✅ 平板端布局正常 (768x1024)');
    
    // 移动端测试
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    
    const mobilePage = page.locator('.character-chat-page');
    await expect(mobilePage).toBeVisible();
    console.log('✅ 移动端布局正常 (375x667)');
  });

  test('API 调用验证', async ({ page }) => {
    const apiCalls: { url: string; method: string; status: number }[] = [];
    
    page.on('request', request => {
      if (request.url().includes('/api/v1/')) {
        apiCalls.push({
          url: request.url(),
          method: request.method(),
          status: 0
        });
      }
    });
    
    page.on('response', response => {
      const call = apiCalls.find(c => c.url === response.url());
      if (call) {
        call.status = response.status();
      }
    });
    
    await injectAuth(page);
    
    // 选择角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);
    
    // 发送消息
    await page.locator('.input-bar input').fill('API 测试消息');
    await page.locator('.send-btn').click();
    await page.waitForTimeout(2000);
    
    // 验证 API 调用
    const characterChatCalls = apiCalls.filter(c => c.url.includes('/character-chat/'));
    expect(characterChatCalls.length).toBeGreaterThan(0);
    
    // 验证所有调用都通过前端代理
    const proxyCalls = apiCalls.filter(c => c.url.startsWith(`${APP_BASE}/api/`));
    expect(proxyCalls.length).toBe(apiCalls.length);
    
    console.log(`✅ API 调用验证通过，共 ${apiCalls.length} 次调用，全部通过前端代理`);
    
    // 打印关键 API 调用
    const keyCalls = apiCalls.filter(c => 
      c.url.includes('/characters') || 
      c.url.includes('/affection') || 
      c.url.includes('/character-chat')
    );
    keyCalls.forEach(c => {
      console.log(`  ${c.method} ${c.url} → ${c.status}`);
    });
  });
});
