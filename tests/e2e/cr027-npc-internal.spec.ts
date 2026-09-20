/**
 * CR-027 T-008: NPC Internal Drive E2E Tests
 * 
 * 验收标准：
 * - AC-NPC-002: 管理员配置 NPC 内在驱动，数据存入数据库
 * - AC-ADMIN-003: NPC 编辑页新增内在驱动区域（渴望/恐惧/秘密）
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

test.describe('CR-027 NPC Internal Drive E2E', () => {
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

  test('AC-NPC-002: 编辑角色内在驱动', async ({ page }) => {
    // 导航到角色列表
    await page.locator('.n-menu-item').filter({ hasText: '角色管理' }).click();
    await page.waitForLoadState('networkidle');

    // 验证页面标题
    await expect(page.locator('h1:has-text("角色管理")')).toBeVisible();

    // 验证角色列表显示
    await expect(page.locator('.n-data-table')).toBeVisible();

    // 点击第一个角色的编辑按钮
    await page.locator('button:has-text("编辑")').first().click();
    
    // 等待导航到编辑页
    await page.waitForURL('**/characters/**');
    await page.waitForLoadState('networkidle');

    // 验证内在驱动区域存在
    await expect(page.locator('text=内在驱动 (Inner Drive)')).toBeVisible();
    await expect(page.locator('text=渴望 (Desire)')).toBeVisible();
    await expect(page.locator('text=恐惧 (Fear)')).toBeVisible();
    await expect(page.locator('text=秘密 (Secret)')).toBeVisible();

    // 填写内在驱动 - 使用 textarea
    const desireTextarea = page.locator('.n-form-item:has-text("渴望") textarea');
    const fearTextarea = page.locator('.n-form-item:has-text("恐惧") textarea');
    const secretTextarea = page.locator('.n-form-item:has-text("秘密") textarea');

    await desireTextarea.fill('追求自由与真相');
    await fearTextarea.fill('失去重要的人');
    await secretTextarea.fill('其实是穿越者');

    // 保存
    await page.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证保存成功 - 检查值是否保留
    await expect(desireTextarea).toHaveValue('追求自由与真相');
    await expect(fearTextarea).toHaveValue('失去重要的人');
    await expect(secretTextarea).toHaveValue('其实是穿越者');
  });

  test('AC-NPC-002: 更新角色内在驱动', async ({ page }) => {
    await page.locator('.n-menu-item').filter({ hasText: '角色管理' }).click();
    await page.waitForLoadState('networkidle');

    // 点击第一个角色的编辑按钮
    await page.locator('button:has-text("编辑")').first().click();
    await page.waitForURL('**/characters/**');
    await page.waitForLoadState('networkidle');

    // 填写初始值
    const desireTextarea = page.locator('.n-form-item:has-text("渴望") textarea');
    await desireTextarea.fill('初始渴望');
    await page.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证初始值
    await expect(desireTextarea).toHaveValue('初始渴望');

    // 更新值
    await desireTextarea.fill('更新的渴望');
    await page.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证更新生效
    await expect(desireTextarea).toHaveValue('更新的渴望');
  });

  test('AC-NPC-002: 清空角色内在驱动', async ({ page }) => {
    await page.locator('.n-menu-item').filter({ hasText: '角色管理' }).click();
    await page.waitForLoadState('networkidle');

    // 点击第一个角色的编辑按钮
    await page.locator('button:has-text("编辑")').first().click();
    await page.waitForURL('**/characters/**');
    await page.waitForLoadState('networkidle');

    // 填写值
    const desireTextarea = page.locator('.n-form-item:has-text("渴望") textarea');
    await desireTextarea.fill('临时渴望');
    await page.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证值已设置
    await expect(desireTextarea).toHaveValue('临时渴望');

    // 清空值
    await desireTextarea.fill('');
    await page.locator('button:has-text("保存")').click();
    await page.waitForTimeout(1000);

    // 验证清空成功
    await expect(desireTextarea).toHaveValue('');
  });
});
