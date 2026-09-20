/**
 * CR-027 T-008: Scene Config E2E Tests
 * 
 * 验收标准：
 * - AC-SCENE-001: 管理员为剧本 Node 配置场景（名称/标签/描述），存入 scene_configs 表
 * - AC-ADMIN-002: 场景配置页显示剧本层级结构，可为 Node 配置场景
 * 
 * 测试环境：
 * - 前端入口：http://localhost:3100
 * - 后端地址：http://localhost:8000
 * - API 代理：/api → http://localhost:8000
 * - Mock API：no
 */

import { test, expect } from '@playwright/test';

const APP_BASE = process.env.APP_BASE || 'http://localhost:3100';
const ADMIN_EMAIL = 'test@test.com';
const ADMIN_PASSWORD = 'admin123456';

// 使用固定的 UUID 作为测试 Node ID
const TEST_NODE_ID = '00000000-0000-0000-0000-000000000001';

test.describe('CR-027 Scene Config E2E', () => {
  test.beforeEach(async ({ page }) => {
    // 管理员登录
    await page.goto(`${APP_BASE}/login`);
    await page.waitForLoadState('networkidle');
    
    await page.locator('.n-input input[type="email"]').fill(ADMIN_EMAIL);
    await page.locator('.n-input input[type="password"]').fill(ADMIN_PASSWORD);
    await page.locator('button:has-text("登录")').click();
    
    await page.waitForURL('**/');
    await page.waitForLoadState('networkidle');
  });

  test('AC-SCENE-001: 为 Node 配置场景', async ({ page }) => {
    // 导航到场景配置页
    await page.locator('.n-menu-item').filter({ hasText: '场景配置' }).click();
    await page.waitForLoadState('networkidle');

    // 验证页面标题
    await expect(page.locator('h1:has-text("场景配置管理")')).toBeVisible();

    // 点击创建按钮
    await page.locator('button:has-text("+ 新建配置")').click();
    
    // 等待模态框出现
    await expect(page.locator('.n-modal')).toBeVisible();

    // 填写表单
    const modal = page.locator('.n-modal');
    
    // Node ID
    await modal.locator('.n-input input').first().fill(TEST_NODE_ID);
    
    // 场景名称
    await modal.locator('.n-input input').nth(1).fill('测试场景');
    
    // 标签
    const tagInput = modal.locator('.n-dynamic-tags input');
    await tagInput.fill('测试');
    await tagInput.press('Enter');
    await tagInput.fill('场景');
    await tagInput.press('Enter');
    await tagInput.fill('CR-027');
    await tagInput.press('Enter');
    
    // 描述
    await modal.locator('.n-input textarea').first().fill('这是一个测试场景配置，用于验证功能。');

    // 提交保存
    await modal.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证保存成功
    await expect(page.locator('.n-data-table')).toBeVisible();
    await expect(page.locator('text=测试场景')).toBeVisible();
  });

  test('AC-SCENE-001: 更新场景配置', async ({ page }) => {
    await page.locator('.n-menu-item').filter({ hasText: '场景配置' }).click();
    await page.waitForLoadState('networkidle');

    // 先创建一个配置
    await page.locator('button:has-text("+ 新建配置")').click();
    await expect(page.locator('.n-modal')).toBeVisible();
    
    let modal = page.locator('.n-modal');
    await modal.locator('.n-input input').first().fill(TEST_NODE_ID);
    await modal.locator('.n-input input').nth(1).fill('更新测试场景');
    await modal.locator('.n-input textarea').first().fill('原始描述');
    await modal.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证创建成功
    await expect(page.locator('text=更新测试场景')).toBeVisible();

    // 点击编辑按钮
    await page.locator('button:has-text("编辑")').first().click();
    
    // 等待模态框出现并修改描述
    await expect(page.locator('.n-modal')).toBeVisible();
    modal = page.locator('.n-modal');
    await modal.locator('.n-input textarea').first().fill('已更新的描述');
    await modal.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证更新生效
    await expect(page.locator('text=更新测试场景')).toBeVisible();
  });

  test('AC-SCENE-001: 删除场景配置', async ({ page }) => {
    await page.locator('.n-menu-item').filter({ hasText: '场景配置' }).click();
    await page.waitForLoadState('networkidle');

    // 先创建一个配置
    await page.locator('button:has-text("+ 新建配置")').click();
    await expect(page.locator('.n-modal')).toBeVisible();
    
    const modal = page.locator('.n-modal');
    await modal.locator('.n-input input').first().fill(TEST_NODE_ID);
    await modal.locator('.n-input input').nth(1).fill('删除测试场景');
    await modal.locator('.n-input textarea').first().fill('待删除');
    await modal.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证创建成功
    await expect(page.locator('text=删除测试场景')).toBeVisible();

    // 点击删除按钮
    await page.locator('button:has-text("删除")').first().click();
    
    // 等待确认对话框
    await expect(page.locator('.n-dialog')).toBeVisible();
    await page.locator('.n-dialog button:has-text("删除")').click();
    await page.waitForTimeout(1000);

    // 验证删除成功
    await expect(page.locator('text=删除测试场景')).not.toBeVisible();
  });
});
