/**
 * CR-029 Choices E2E Test
 * 验证选择节点显示 3 个选项
 */
import { test, expect } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const API_BASE = process.env.API_BASE || 'http://localhost:8000/api/v1';

test.describe('CR-029: Choice Count = 3', () => {
  
  test('AC-BRANCH-006: 选择节点显示 3 个选项', async ({ page }) => {
    // 1. 打开前端并登录
    await page.goto(APP_BASE);
    await page.click('text=登录');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'Test123456');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/scripts');
    
    // 2. 进入一个有选择项的剧本
    await page.click('text=星月奇缘');
    await page.waitForURL('**/scripts/**');
    
    // 3. 开始游戏
    await page.click('text=开始游戏');
    await page.waitForURL('**/game/**');
    
    // 4. 等待选择面板出现
    await page.waitForSelector('[data-testid="choice-panel"], .choice-panel, .choices', { timeout: 10000 });
    
    // 5. 验证选择项数量
    const choiceCount = await page.evaluate(() => {
      // 尝试多种选择器
      const choicePanel = document.querySelector('[data-testid="choice-panel"]') 
        || document.querySelector('.choice-panel')
        || document.querySelector('.choices');
      
      if (!choicePanel) return 0;
      
      const choices = choicePanel.querySelectorAll('[data-testid="choice-item"], .choice-item, button');
      return choices.length;
    });
    
    console.log(`选择项数量: ${choiceCount}`);
    
    // 6. 验证选择项数量为 3
    expect(choiceCount).toBe(3);
    
    // 7. 截图证据
    await page.screenshot({ path: 'logs/e2e/cr029-choices-3-options.png' });
    
    // 8. 通过 API 验证
    const apiChoiceCount = await page.evaluate(async () => {
      const sessionResponse = await fetch('/api/v1/game/current', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const session = await sessionResponse.json();
      
      if (session.current_node && session.current_node.choices) {
        return session.current_node.choices.length;
      }
      return 0;
    });
    
    console.log(`API 返回的选择项数量: ${apiChoiceCount}`);
    expect(apiChoiceCount).toBe(3);
  });
  
  test('AC-BRANCH-006: 数据库验证选择项数量', async ({ page }) => {
    // 直接通过 API 验证特定节点的选择项数量
    await page.goto(APP_BASE);
    await page.click('text=登录');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'Test123456');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/scripts');
    
    // 验证 b1000001, b1000002, b1000003 节点各有 3 个选择项
    const nodeIds = [
      'b1000001-0000-0000-0000-0000b1000001',
      'b1000002-0000-0000-0000-0000b1000002',
      'b1000003-0000-0000-0000-0000b1000003'
    ];
    
    for (const nodeId of nodeIds) {
      const choiceCount = await page.evaluate(async (nid) => {
        const response = await fetch(`/api/v1/nodes/${nid}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const node = await response.json();
        return node.choices ? node.choices.length : 0;
      }, nodeId);
      
      console.log(`节点 ${nodeId} 的选择项数量: ${choiceCount}`);
      expect(choiceCount).toBe(3);
    }
    
    await page.screenshot({ path: 'logs/e2e/cr029-choices-db-verification.png' });
  });
});
