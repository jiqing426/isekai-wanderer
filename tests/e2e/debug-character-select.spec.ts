import { test, expect } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDEiLCJleHAiOjE3ODUyOTgyOTQsInR5cGUiOiJhY2Nlc3MifQ.iM3h840PLgpRc8klLHqrkj6qrPJtO3EqSZbHBR6AZnY';

test('调试角色选择', async ({ page }) => {
  // 注入认证
  await page.goto(`${APP_BASE}/`);
  await page.evaluate((token) => {
    localStorage.setItem('isekai_access_token', token);
  }, JWT_TOKEN);
  
  await page.goto(`${APP_BASE}/character-chat`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  
  // 截图初始状态
  await page.screenshot({ path: 'test-results/debug-1-initial.png', fullPage: true });
  
  // 检查角色列表
  const characterItems = page.locator('.character-item');
  const count = await characterItems.count();
  console.log(`找到 ${count} 个角色`);
  
  if (count === 0) {
    console.log('没有找到角色，检查页面内容');
    const content = await page.content();
    console.log('页面 HTML:', content.substring(0, 2000));
    return;
  }
  
  // 获取第一个角色的信息
  const firstItem = characterItems.first();
  const firstText = await firstItem.textContent();
  console.log('第一个角色文本:', firstText?.substring(0, 100));
  
  // 检查聊天窗口是否已存在
  let chatWindow = page.locator('.chat-window');
  let chatVisible = await chatWindow.isVisible();
  console.log('初始聊天窗口可见:', chatVisible);
  
  // 尝试点击第一个角色
  console.log('准备点击第一个角色...');
  await firstItem.click({ force: true });
  await page.waitForTimeout(2000);
  
  // 截图点击后
  await page.screenshot({ path: 'test-results/debug-2-after-click.png', fullPage: true });
  
  // 再次检查聊天窗口
  chatVisible = await chatWindow.isVisible();
  console.log('点击后聊天窗口可见:', chatVisible);
  
  // 检查 selectedCharacterId 是否被设置
  const selectedId = await page.evaluate(() => {
    const app = document.querySelector('#app') as any;
    const vue = app?.__vue_app__;
    if (vue) {
      const component = vue._instance?.proxy;
      return component?.selectedCharacterId;
    }
    return null;
  });
  console.log('selectedCharacterId:', selectedId);
  
  // 检查是否有错误
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.waitForTimeout(1000);
  
  if (errors.length > 0) {
    console.log('页面错误:', errors);
  }
  
  // 检查 no-character-selected 提示
  const noCharMsg = page.locator('.no-character-selected');
  const noCharVisible = await noCharMsg.isVisible();
  console.log('"请选择一个角色"提示可见:', noCharVisible);
  
  // 最终截图
  await page.screenshot({ path: 'test-results/debug-3-final.png', fullPage: true });
});
