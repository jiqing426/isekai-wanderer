/**
 * CR-029 Branch E2E Test
 * 验证不同角色看到不同分支内容，最终汇合到相同节点
 */
import { test, expect } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:8081';
const API_BASE = process.env.API_BASE || 'http://localhost:8000/api/v1';

test.describe('CR-029: Character Branch Narrative', () => {
  
  test('AC-BRANCH-003: 不同角色看到不同分支内容', async ({ page }) => {
    // 1. 打开前端首页
    await page.goto(APP_BASE);
    await expect(page).toHaveTitle(/.*星月奇缘.*/i);
    
    // 2. 登录（使用测试账号）
    await page.goto(`${APP_BASE}/login`);
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'Test123456');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/discover');
    
    // 3. 进入星月奇缘剧本
    await page.click('.script-card:has-text("星月奇缘")');
    await page.waitForURL('**/script/**');
    
    // 4. 选择角色A（沈星澜）开始游戏
    await page.click('.character-card:has-text("沈星澜")');
    await page.click('button:has-text("开始游戏")');
    await page.waitForURL('**/game/**');
    
    // 5. 记录角色A看到的分支节点
    const sessionA = await page.evaluate(async () => {
      const response = await fetch('/api/v1/game/current', {
        credentials: 'include'
      });
      return response.json();
    });
    
    const charANodeId = sessionA.current_node?.id;
    console.log(`角色A（沈星澜）当前节点: ${charANodeId}`);
    
    // 6. 返回剧本选择页，选择角色B（白夜）
    await page.goto(APP_BASE + '/discover');
    await page.click('.script-card:has-text("星月奇缘")');
    await page.click('.character-card:has-text("白夜")');
    await page.click('button:has-text("开始游戏")');
    await page.waitForURL('**/game/**');
    
    // 7. 记录角色B看到的分支节点
    const sessionB = await page.evaluate(async () => {
      const response = await fetch('/api/v1/game/current', {
        credentials: 'include'
      });
      return response.json();
    });
    
    const charBNodeId = sessionB.current_node?.id;
    console.log(`角色B（白夜）当前节点: ${charBNodeId}`);
    
    // 8. 验证两个角色看到的节点不同
    expect(charANodeId).not.toEqual(charBNodeId);
    
    // 9. 继续游戏直到汇合点（模拟用户选择）
    // 这里简化处理：直接验证 API 返回的节点 character_id
    const nodeA = await page.evaluate(async (nodeId) => {
      const response = await fetch(`/api/v1/nodes/${nodeId}`, {
        credentials: 'include'
      });
      return response.json();
    }, charANodeId);
    
    const nodeB = await page.evaluate(async (nodeId) => {
      const response = await fetch(`/api/v1/nodes/${nodeId}`, {
        credentials: 'include'
      });
      return response.json();
    }, charBNodeId);
    
    // 验证节点确实属于不同角色
    expect(nodeA.character_id).toBeTruthy();
    expect(nodeB.character_id).toBeTruthy();
    expect(nodeA.character_id).not.toEqual(nodeB.character_id);
    
    // 10. 截图证据
    await page.screenshot({ path: 'logs/e2e/cr029-branch-different-nodes.png' });
  });
  
  test('AC-BRANCH-003: 分支结束后汇合到相同节点', async ({ page }) => {
    // 这个测试需要完整的游戏流程，简化验证逻辑：
    // 验证分支节点的 choice 指向的下一个节点是公共节点（character_id=NULL）
    
    await page.goto(APP_BASE + '/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'Test123456');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/discover');
    
    // 通过 API 验证汇合逻辑
    const convergeTest = await page.evaluate(async () => {
      // 获取所有分支节点的选择项
      const branchNodesResponse = await fetch('/api/v1/nodes?character_id_not_null=true', {
        credentials: 'include'
      });
      const branchNodes = await branchNodesResponse.json();
      
      // 验证每个分支节点的选择项指向的下一个节点是公共节点
      for (const node of branchNodes) {
        if (node.choices && node.choices.length > 0) {
          for (const choice of node.choices) {
            if (choice.next_node_id) {
              const nextNodeResponse = await fetch(`/api/v1/nodes/${choice.next_node_id}`, {
                credentials: 'include'
              });
              const nextNode = await nextNodeResponse.json();
              
              // 汇合节点应该是公共节点
              if (nextNode.character_id !== null) {
                return { success: false, error: `Converge node ${nextNode.id} has character_id` };
              }
            }
          }
        }
      }
      
      return { success: true };
    });
    
    expect(convergeTest.success).toBe(true);
    
    await page.screenshot({ path: 'logs/e2e/cr029-branch-converge.png' });
  });
});
