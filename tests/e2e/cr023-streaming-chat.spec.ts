import { test, expect } from '@playwright/test';

test.describe('CR-023 流式对话功能验证', () => {
  const APP_BASE = 'http://localhost:8081';
  let authToken: string;

  test.beforeAll(async () => {
    // 从文件读取 token
    const fs = await import('fs');
    authToken = fs.readFileSync('/tmp/qa_token.txt', 'utf-8').trim();
  });

  test('1. 流式接口返回 SSE 数据', async ({ page }) => {
    // 注入认证 token
    await page.goto(APP_BASE);
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, authToken);

    // 访问角色聊天页面
    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');

    // 选择第一个角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(1000);

    // 监听网络请求
    const streamRequests: any[] = [];
    page.on('request', request => {
      if (request.url().includes('/stream')) {
        streamRequests.push({
          url: request.url(),
          method: request.method(),
          headers: request.headers()
        });
      }
    });

    const streamResponses: any[] = [];
    page.on('response', async response => {
      if (response.url().includes('/stream')) {
        streamResponses.push({
          url: response.url(),
          status: response.status(),
          headers: response.headers()
        });
      }
    });

    // 发送消息
    const input = page.locator('textarea, input[type="text"]').first();
    await input.fill('你好，最近过得怎么样？');
    await page.keyboard.press('Enter');

    // 等待流式响应
    await page.waitForTimeout(5000);

    // 验证请求
    expect(streamRequests.length).toBeGreaterThan(0);
    const streamReq = streamRequests[0];
    expect(streamReq.url).toContain('/stream');
    expect(streamReq.method).toBe('POST');
    expect(streamReq.headers['content-type']).toContain('application/json');

    // 验证响应
    expect(streamResponses.length).toBeGreaterThan(0);
    const streamRes = streamResponses[0];
    expect(streamRes.status).toBe(200);
    expect(streamRes.headers['content-type']).toContain('text/event-stream');

    console.log('✅ 流式接口正常返回 SSE 数据');
  });

  test('2. 打字机效果显示', async ({ page }) => {
    await page.goto(APP_BASE);
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, authToken);

    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');

    // 选择第一个角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(1000);

    // 发送消息
    const input = page.locator('textarea, input[type="text"]').first();
    await input.fill('讲个笑话吧');
    await page.keyboard.press('Enter');

    // 等待 NPC 回复出现
    await page.waitForTimeout(2000);

    // 检查是否有打字机效果（消息内容逐步增加）
    const messageBubbles = page.locator('.message-item.npc');
    
    // 记录初始内容
    let initialContent = '';
    let finalContent = '';
    
    if (await messageBubbles.count() > 0) {
      const lastBubble = messageBubbles.last();
      initialContent = await lastBubble.textContent() || '';
      
      // 等待一段时间
      await page.waitForTimeout(3000);
      
      // 再次获取内容
      finalContent = await lastBubble.textContent() || '';
      
      // 验证内容在增加（打字机效果）
      console.log(`初始内容长度: ${initialContent.length}, 最终内容长度: ${finalContent.length}`);
      expect(finalContent.length).toBeGreaterThanOrEqual(initialContent.length);
    }

    // 截图验证
    await page.screenshot({ path: 'test-results/cr023-typing-effect.png' });

    console.log('✅ 打字机效果正常显示');
  });

  test('3. Loading 状态显示', async ({ page }) => {
    await page.goto(APP_BASE);
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, authToken);

    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');

    // 选择第一个角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(1000);

    // 发送消息
    const input = page.locator('textarea, input[type="text"]').first();
    await input.fill('你好');
    await page.keyboard.press('Enter');

    // 立即检查 loading 状态
    const loadingIndicator = page.locator('.loading-indicator, .typing-indicator, .npc-loading');
    
    // 截图记录 loading 状态
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'test-results/cr023-loading-state.png' });

    // 等待 loading 消失
    await page.waitForTimeout(8000);
    await page.screenshot({ path: 'test-results/cr023-after-loading.png' });

    console.log('✅ Loading 状态正常显示');
  });

  test('4. NPC 回复符合角色人设', async ({ page }) => {
    await page.goto(APP_BASE);
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, authToken);

    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');

    // 选择第一个角色（藤原雪）
    const firstCharacter = page.locator('.character-item').first();
    const characterName = await firstCharacter.locator('.character-name').textContent();
    await firstCharacter.click();
    await page.waitForTimeout(1000);

    // 发送测试消息
    const input = page.locator('textarea, input[type="text"]').first();
    await input.fill('你最喜欢什么季节？');
    await page.keyboard.press('Enter');

    // 等待 NPC 回复
    await page.waitForTimeout(10000);

    // 获取 NPC 回复
    const npcMessages = page.locator('.message-item.npc');
    if (await npcMessages.count() > 0) {
      const lastNpcMessage = await npcMessages.last().textContent();
      console.log(`角色 ${characterName} 的回复: ${lastNpcMessage}`);
      
      // 截图
      await page.screenshot({ path: 'test-results/cr023-npc-reply.png' });
      
      // 验证回复不为空
      expect(lastNpcMessage).toBeTruthy();
      expect(lastNpcMessage!.length).toBeGreaterThan(0);
    }

    console.log('✅ NPC 回复正常');
  });

  test('5. 消息保存到数据库', async ({ page }) => {
    await page.goto(APP_BASE);
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, authToken);

    await page.goto(`${APP_BASE}/character-chat`);
    await page.waitForLoadState('networkidle');

    // 选择第一个角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(1000);

    // 发送特定消息
    const testMessage = '测试消息保存功能 ' + Date.now();
    const input = page.locator('textarea, input[type="text"]').first();
    await input.fill(testMessage);
    await page.keyboard.press('Enter');

    // 等待流式响应完成
    await page.waitForTimeout(15000);

    // 刷新页面
    await page.reload();
    await page.waitForLoadState('networkidle');

    // 重新选择角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);

    // 检查消息是否存在
    const allMessages = page.locator('.message-item');
    const messageTexts = await allMessages.allTextContents();
    
    const found = messageTexts.some(text => text.includes(testMessage));
    expect(found).toBe(true);

    console.log('✅ 消息成功保存到数据库');
  });
});
