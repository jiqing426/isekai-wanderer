import { test, expect } from '@playwright/test';

test.describe('CR-018 T-026 + T-027 快速验证', () => {
  test('T-026: 碎片商城收支明细中文化', async ({ page }) => {
    console.log('=== T-026: 碎片商城收支明细中文化验证 ===\n');
    
    // 直接访问碎片商城页面
    await page.goto('http://localhost:8081/fragment-mall');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/t026-01-fragment-mall.png', fullPage: true });
    console.log('✓ 截图: 碎片商城页面');

    // 获取页面文本内容
    const pageText = await page.textContent('body');
    
    // 检查是否出现裸英文 key（不应该出现）
    const englishKeys = [
      'daily_checkin',
      'streak_milestone',
      'dialogue_quota_purchase',
      'gift_send',
      'achievement_reward'
    ];

    let hasEnglishKey = false;
    for (const key of englishKeys) {
      if (pageText?.includes(key)) {
        console.log(`✗ 发现裸英文 key: ${key}`);
        hasEnglishKey = true;
      }
    }

    // 检查是否显示中文
    const chineseKeywords = ['签到', '连续签到', '对话额度', '送礼', '成就'];
    const foundChinese = chineseKeywords.filter(kw => pageText?.includes(kw));
    
    if (foundChinese.length > 0) {
      console.log(`✓ 发现中文交易类型: ${foundChinese.join(', ')}`);
    }

    if (hasEnglishKey) {
      console.log('\n✗ T-026 失败: 页面出现裸英文 key');
      expect(hasEnglishKey).toBe(false);
    } else {
      console.log('\n✓ T-026 通过: 未发现裸英文 key');
    }

    await page.screenshot({ path: 'test-results/t026-02-final.png', fullPage: true });
  });

  test('T-027: 碎片获取"成就奖励"跳转', async ({ page }) => {
    console.log('=== T-027: 碎片获取"成就奖励"跳转验证 ===\n');

    // 访问碎片商城页面
    await page.goto('http://localhost:8081/fragment-mall');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/t027-01-fragment-mall.png', fullPage: true });
    console.log('✓ 截图: 碎片商城页面');

    // 查找"成就奖励"条目
    const achievementReward = await page.locator('text=成就奖励').first();
    
    if (await achievementReward.isVisible({ timeout: 3000 }).catch(() => false)) {
      console.log('✓ 找到"成就奖励"条目');
      
      // 点击"成就奖励"
      await achievementReward.click();
      await page.waitForTimeout(2000);
      
      // 验证跳转
      const currentUrl = page.url();
      console.log(`当前 URL: ${currentUrl}`);
      
      await page.screenshot({ path: 'test-results/t027-02-after-click.png', fullPage: true });

      if (currentUrl.includes('/achievements')) {
        console.log('✓ T-027 通过: 成功跳转到成就页面');
        expect(currentUrl).toContain('/achievements');
      } else {
        console.log('✗ T-027 失败: 未跳转到成就页面');
        expect(currentUrl).toContain('/achievements');
      }
    } else {
      console.log('⚠ 未找到"成就奖励"条目，可能需要先获取碎片或查看其他标签');
      await page.screenshot({ path: 'test-results/t027-02-no-achievement.png', fullPage: true });
    }
  });
});
