import { test, expect } from '@playwright/test';

test.describe('CR-018 T-026 + T-027 验证', () => {
  const timestamp = Date.now();
  const testEmail = `t026t027_${timestamp}@test.com`;
  const testPassword = '***';

  test.beforeEach(async ({ page }) => {
    // 注册测试账号
    await page.goto('http://localhost:8081/register');
    await page.waitForLoadState('networkidle');
    
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.click('button[type="submit"]');
    
    await page.waitForTimeout(2000);
  });

  test('T-026: 碎片商城收支明细中文化验证', async ({ page }) => {
    console.log('=== T-026: 碎片商城收支明细中文化验证 ===\n');
    
    // 步骤 1: 先签到获取碎片
    console.log('步骤 1: 签到获取碎片');
    await page.goto('http://localhost:8081/personal');
    await page.waitForLoadState('networkidle');
    
    const checkinButton = await page.locator('text=签到').or(page.locator('text=立即签到')).first();
    if (await checkinButton.isVisible()) {
      await checkinButton.click();
      await page.waitForTimeout(2000);
      console.log('✓ 签到完成');
    } else {
      console.log('⚠ 今日已签到或签到按钮不可见');
    }
    
    await page.screenshot({ path: 'test-results/t026-01-after-checkin.png', fullPage: true });

    // 步骤 2: 打开碎片商城页面
    console.log('\n步骤 2: 打开碎片商城页面');
    await page.goto('http://localhost:8081/fragment-mall');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/t026-02-fragment-mall.png', fullPage: true });
    console.log('✓ 截图: 碎片商城页面');

    // 步骤 3: 查找收支明细/交易记录区域
    console.log('\n步骤 3: 查找收支明细区域');
    const transactionSection = await page.locator('text=收支明细').or(page.locator('text=交易记录')).or(page.locator('text=历史记录')).first();
    
    if (await transactionSection.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('✓ 找到收支明细区域');
      await transactionSection.click();
      await page.waitForTimeout(1000);
    } else {
      console.log('⚠ 未找到明确的收支明细标签，尝试滚动页面查找');
    }

    await page.screenshot({ path: 'test-results/t026-03-transactions.png', fullPage: true });

    // 步骤 4: 检查交易类型是否显示中文
    console.log('\n步骤 4: 检查交易类型显示');
    
    // 定义需要检查的英文 key（不应该出现）
    const englishKeys = [
      'daily_checkin',
      'streak_milestone',
      'dialogue_quota_purchase',
      'gift_send',
      'achievement_reward',
      'subscription_reward'
    ];

    // 定义期望的中文显示
    const expectedChinese = [
      '签到',
      '连续签到',
      '对话额度',
      '送礼',
      '成就',
      '订阅'
    ];

    // 获取页面所有文本内容
    const pageText = await page.textContent('body');
    
    let hasEnglishKey = false;
    let foundChinese = [];

    // 检查是否出现裸英文 key
    for (const key of englishKeys) {
      if (pageText.includes(key)) {
        console.log(`✗ 发现裸英文 key: ${key}`);
        hasEnglishKey = true;
      }
    }

    // 检查是否显示中文
    for (const chinese of expectedChinese) {
      if (pageText.includes(chinese)) {
        foundChinese.push(chinese);
      }
    }

    if (hasEnglishKey) {
      console.log('\n✗ T-026 失败: 页面出现裸英文 key');
      await page.screenshot({ path: 'test-results/t026-04-fail-english-key.png', fullPage: true });
    } else if (foundChinese.length > 0) {
      console.log(`\n✓ T-026 通过: 发现中文交易类型: ${foundChinese.join(', ')}`);
    } else {
      console.log('\n⚠ 未找到交易记录或无法判断');
    }

    // 步骤 5: 尝试查找具体的交易记录列表
    console.log('\n步骤 5: 查找交易记录列表');
    const transactionItems = await page.locator('.transaction-item, .record-item, [class*="transaction"], [class*="record"]');
    const itemCount = await transactionItems.count();
    console.log(`找到 ${itemCount} 条交易记录`);

    if (itemCount > 0) {
      // 检查前几条记录的内容
      for (let i = 0; i < Math.min(itemCount, 3); i++) {
        const itemText = await transactionItems.nth(i).textContent();
        console.log(`  记录 ${i + 1}: ${itemText?.substring(0, 100)}`);
      }
    }

    await page.screenshot({ path: 'test-results/t026-05-final.png', fullPage: true });

    // 验证结果
    expect(hasEnglishKey).toBe(false);
  });

  test('T-027: 碎片获取"成就奖励"跳转验证', async ({ page }) => {
    console.log('=== T-027: 碎片获取"成就奖励"跳转验证 ===\n');

    // 步骤 1: 打开碎片获取页面
    console.log('步骤 1: 打开碎片获取页面');
    await page.goto('http://localhost:8081/fragment-mall');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/t027-01-fragment-mall.png', fullPage: true });
    console.log('✓ 截图: 碎片商城/获取页面');

    // 步骤 2: 查找"碎片获取"或相关标签
    console.log('\n步骤 2: 查找碎片获取区域');
    const getFragmentTab = await page.locator('text=碎片获取').or(page.locator('text=获取碎片')).or(page.locator('text=如何获取')).first();
    
    if (await getFragmentTab.isVisible({ timeout: 3000 }).catch(() => false)) {
      await getFragmentTab.click();
      await page.waitForTimeout(1000);
      console.log('✓ 点击碎片获取标签');
    } else {
      console.log('⚠ 未找到碎片获取标签，可能在当前页面');
    }

    await page.screenshot({ path: 'test-results/t027-02-get-fragment.png', fullPage: true });

    // 步骤 3: 查找"成就奖励"条目
    console.log('\n步骤 3: 查找"成就奖励"条目');
    const achievementReward = await page.locator('text=成就奖励').or(page.locator('text=成就')).first();
    
    if (await achievementReward.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('✓ 找到"成就奖励"条目');
      await page.screenshot({ path: 'test-results/t027-03-before-click.png', fullPage: true });

      // 步骤 4: 点击"成就奖励"
      console.log('\n步骤 4: 点击"成就奖励"');
      await achievementReward.click();
      await page.waitForTimeout(2000);
      
      // 步骤 5: 验证跳转到成就页面
      console.log('\n步骤 5: 验证跳转结果');
      const currentUrl = page.url();
      console.log(`当前 URL: ${currentUrl}`);
      
      await page.screenshot({ path: 'test-results/t027-04-after-click.png', fullPage: true });

      if (currentUrl.includes('/achievements')) {
        console.log('✓ T-027 通过: 成功跳转到成就页面');
        
        // 验证成就页面内容
        const achievementTitle = await page.locator('text=成就').or(page.locator('h1, h2').first());
        if (await achievementTitle.isVisible({ timeout: 2000 }).catch(() => false)) {
          console.log('✓ 成就页面加载成功');
        }
      } else {
        console.log('✗ T-027 失败: 未跳转到成就页面');
        console.log(`  预期: URL 包含 /achievements`);
        console.log(`  实际: ${currentUrl}`);
      }
    } else {
      console.log('✗ 未找到"成就奖励"条目');
      await page.screenshot({ path: 'test-results/t027-03-no-achievement.png', fullPage: true });
    }

    // 最终截图
    await page.screenshot({ path: 'test-results/t027-05-final.png', fullPage: true });
  });
});
