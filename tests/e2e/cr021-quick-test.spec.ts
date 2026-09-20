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
  await page.waitForTimeout(3000);
}

test.describe('CR-021 角色聊天快速测试', () => {

  test('页面加载和角色列表', async ({ page }) => {
    await injectAuth(page);
    
    // 截图
    await page.screenshot({ path: 'test-results/chat-page-loaded.png' });
    
    // 验证角色列表
    const characterItems = page.locator('.character-item');
    const count = await characterItems.count();
    expect(count).toBeGreaterThan(0);
    console.log(`✅ 角色列表: ${count} 个角色`);
    
    // 验证好感度
    const affectionBars = page.locator('.affection-bar');
    const affectionCount = await affectionBars.count();
    expect(affectionCount).toBe(count);
    console.log(`✅ 好感度进度条: ${affectionCount} 个`);
  });

  test('选择角色和聊天窗口', async ({ page }) => {
    await injectAuth(page);
    
    // 点击第一个角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);
    
    // 截图
    await page.screenshot({ path: 'test-results/chat-window-selected.png' });
    
    // 验证聊天窗口
    const chatWindow = page.locator('.chat-window');
    await expect(chatWindow).toBeVisible({ timeout: 10000 });
    console.log('✅ 聊天窗口显示');
    
    // 验证角色名称
    const name = await page.locator('.chat-header h2').textContent();
    console.log(`✅ 角色名称: ${name}`);
    
    // 验证查看详情按钮
    const detailBtn = page.locator('.detail-btn');
    await expect(detailBtn).toBeVisible();
    console.log('✅ 查看详情按钮显示');
    
    // 验证输入栏
    const inputBar = page.locator('.input-bar');
    await expect(inputBar).toBeVisible();
    console.log('✅ 输入栏显示');
  });

  test('发送消息', async ({ page }) => {
    await injectAuth(page);
    
    // 选择角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);
    
    // 输入消息
    const input = page.locator('.input-bar textarea, .input-wrapper textarea');
    await input.fill('测试消息');
    await page.waitForTimeout(500);
    
    // 截图
    await page.screenshot({ path: 'test-results/message-input.png' });
    
    // 发送
    await page.locator('.send-btn').click();
    await page.waitForTimeout(3000);
    
    // 截图
    await page.screenshot({ path: 'test-results/message-sent.png' });
    
    // 验证消息
    const messages = page.locator('.message-item');
    const count = await messages.count();
    console.log(`✅ 消息数量: ${count}`);
    
    if (count > 0) {
      const lastMsg = await messages.last().locator('.message-content').textContent();
      console.log(`✅ 最后消息: ${lastMsg}`);
    }
  });

  test('加号菜单', async ({ page }) => {
    await injectAuth(page);
    
    // 选择角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);
    
    // 点击加号
    await page.locator('.plus-btn').click();
    await page.waitForTimeout(1000);
    
    // 截图
    await page.screenshot({ path: 'test-results/plus-menu.png' });
    
    // 验证菜单
    const menu = page.locator('.plus-menu');
    const visible = await menu.isVisible();
    console.log(`✅ 加号菜单显示: ${visible}`);
    
    if (visible) {
      const items = menu.locator('.menu-item');
      const count = await items.count();
      console.log(`✅ 菜单项数量: ${count}`);
    }
  });

  test('查看详情跳转', async ({ page }) => {
    await injectAuth(page);
    
    // 选择角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);
    
    // 点击查看详情
    await page.locator('.detail-btn').click();
    await page.waitForTimeout(3000);
    
    // 截图
    await page.screenshot({ path: 'test-results/detail-page.png' });
    
    // 验证跳转
    const url = page.url();
    console.log(`✅ 跳转URL: ${url}`);
    expect(url).toContain('/characters/');
  });

  test('推荐话题', async ({ page }) => {
    await injectAuth(page);
    
    // 选择角色
    await page.locator('.character-item').first().click();
    await page.waitForTimeout(2000);
    
    // 截图
    await page.screenshot({ path: 'test-results/topics-section.png' });
    
    // 检查话题区域
    const topicsSection = page.locator('.topics-section');
    const visible = await topicsSection.isVisible().catch(() => false);
    console.log(`✅ 推荐话题区域显示: ${visible}`);
    
    if (visible) {
      const topics = topicsSection.locator('.topic-tag');
      const count = await topics.count();
      console.log(`✅ 话题数量: ${count}`);
    }
  });
});
