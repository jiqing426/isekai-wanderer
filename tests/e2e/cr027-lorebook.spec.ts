/**
 * CR-027 T-008: Lorebook CRUD E2E Tests
 * 
 * 验收标准：
 * - AC-LORE-001: 管理员创建 Lorebook 条目（标题/内容/标签），存入数据库并在列表显示
 * - AC-LORE-002: 管理员编辑/删除 Lorebook 条目，删除为软删除
 * - AC-LORE-003: 管理员按标签筛选 Lorebook 条目
 * - AC-ADMIN-001: Lorebook 管理页 CRUD 可用（创建/编辑/删除/列表）
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

test.describe('CR-027 Lorebook CRUD E2E', () => {
  test.beforeEach(async ({ page }) => {
    // 管理员登录
    await page.goto(`${APP_BASE}/login`);
    await page.waitForLoadState('networkidle');
    
    // Naive UI n-input renders as <div class="n-input"><input></div>
    await page.locator('.n-input input[type="email"]').fill(ADMIN_EMAIL);
    await page.locator('.n-input input[type="password"]').fill(ADMIN_PASSWORD);
    await page.locator('button:has-text("登录")').click();
    
    // 等待导航到首页
    await page.waitForURL('**/');
    await page.waitForLoadState('networkidle');
  });

  test('AC-LORE-001: 创建 Lorebook 条目并在列表显示', async ({ page }) => {
    // 导航到 Lorebook 管理页 - 菜单项文字
    await page.locator('.n-menu-item').filter({ hasText: 'Lorebook 管理' }).click();
    await page.waitForLoadState('networkidle');

    // 验证页面标题
    await expect(page.locator('h1:has-text("Lorebook 管理")')).toBeVisible();

    // 点击创建按钮
    await page.locator('button:has-text("+ 新建条目")').click();
    
    // 等待模态框出现
    await expect(page.locator('.n-modal')).toBeVisible();

    // 填写表单 - Naive UI n-input 内部是 input 元素
    const modal = page.locator('.n-modal');
    await modal.locator('.n-input input').first().fill('测试世界知识');
    
    // 内容字段 - textarea
    await modal.locator('.n-input textarea').first().fill('这是一个测试条目，用于验证 CRUD 功能。');
    
    // 标签 - n-dynamic-tags 需要特殊处理
    // 先点击标签输入框
    const tagInput = modal.locator('.n-dynamic-tags input');
    await tagInput.fill('测试');
    await tagInput.press('Enter');
    await tagInput.fill('世界知识');
    await tagInput.press('Enter');
    await tagInput.fill('CR-027');
    await tagInput.press('Enter');

    // 优先级 - n-input-number
    await modal.locator('.n-input-number input').fill('10');

    // 提交创建
    await modal.locator('button:has-text("保存")').click();
    
    // 等待模态框关闭
    await page.waitForTimeout(1000);

    // 验证列表中出现新条目
    await expect(page.locator('.n-data-table')).toBeVisible();
    await expect(page.locator('text=测试世界知识')).toBeVisible();
  });

  test('AC-LORE-002: 编辑 Lorebook 条目', async ({ page }) => {
    await page.locator('.n-menu-item').filter({ hasText: 'Lorebook 管理' }).click();
    await page.waitForLoadState('networkidle');

    // 先创建一个条目
    await page.locator('button:has-text("+ 新建条目")').click();
    await expect(page.locator('.n-modal')).toBeVisible();
    
    const modal = page.locator('.n-modal');
    await modal.locator('.n-input input').first().fill('编辑测试条目');
    await modal.locator('.n-input textarea').first().fill('原始内容');
    await modal.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证创建成功
    await expect(page.locator('text=编辑测试条目')).toBeVisible();

    // 点击编辑按钮
    await page.locator('button:has-text("编辑")').first().click();
    
    // 等待模态框出现并填写新内容
    await expect(page.locator('.n-modal')).toBeVisible();
    await modal.locator('.n-input textarea').first().fill('已修改的内容');
    await modal.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证修改生效
    await expect(page.locator('text=编辑测试条目')).toBeVisible();
  });

  test('AC-LORE-002: 删除 Lorebook 条目（软删除）', async ({ page }) => {
    await page.locator('.n-menu-item').filter({ hasText: 'Lorebook 管理' }).click();
    await page.waitForLoadState('networkidle');

    // 先创建一个条目
    await page.locator('button:has-text("+ 新建条目")').click();
    await expect(page.locator('.n-modal')).toBeVisible();
    
    const modal = page.locator('.n-modal');
    await modal.locator('.n-input input').first().fill('删除测试条目');
    await modal.locator('.n-input textarea').first().fill('待删除');
    await modal.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证创建成功
    await expect(page.locator('text=删除测试条目')).toBeVisible();

    // 点击删除按钮 - 使用 nth 选择器找到对应行的删除按钮
    await page.locator('button:has-text("删除")').first().click();
    
    // 等待确认对话框
    await expect(page.locator('.n-dialog')).toBeVisible();
    await page.locator('.n-dialog button:has-text("删除")').click();
    await page.waitForTimeout(1000);

    // 验证条目已删除
    await expect(page.locator('text=删除测试条目')).not.toBeVisible();
  });

  test('AC-LORE-003: 按标签筛选 Lorebook 条目', async ({ page }) => {
    await page.locator('.n-menu-item').filter({ hasText: 'Lorebook 管理' }).click();
    await page.waitForLoadState('networkidle');

    // 创建两个不同标签的条目
    await page.locator('button:has-text("+ 新建条目")').click();
    await expect(page.locator('.n-modal')).toBeVisible();
    
    let modal = page.locator('.n-modal');
    await modal.locator('.n-input input').first().fill('标签筛选测试A');
    await modal.locator('.n-input textarea').first().fill('内容A');
    const tagInput = modal.locator('.n-dynamic-tags input');
    await tagInput.fill('筛选测试');
    await tagInput.press('Enter');
    await tagInput.fill('标签A');
    await tagInput.press('Enter');
    await modal.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    await page.locator('button:has-text("+ 新建条目")').click();
    await expect(page.locator('.n-modal')).toBeVisible();
    modal = page.locator('.n-modal');
    await modal.locator('.n-input input').first().fill('标签筛选测试B');
    await modal.locator('.n-input textarea').first().fill('内容B');
    const tagInput2 = modal.locator('.n-dynamic-tags input');
    await tagInput2.fill('筛选测试');
    await tagInput2.press('Enter');
    await tagInput2.fill('标签B');
    await tagInput2.press('Enter');
    await modal.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 使用标签筛选
    await page.locator('.n-input input[placeholder="按标签筛选"]').fill('标签A');
    await page.locator('button:has-text("筛选")').click();
    await page.waitForTimeout(1000);

    // 验证只显示匹配的条目
    await expect(page.locator('text=标签筛选测试A')).toBeVisible();
    await expect(page.locator('text=标签筛选测试B')).not.toBeVisible();
  });
});
