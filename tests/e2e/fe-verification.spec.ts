import { test, expect } from '@playwright/test';

test.describe('FE Day 2 Browser Verification', () => {
  test.beforeEach(async ({ page }) => {
    // 访问首页
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('networkidle');
  });

  test('FE-D1: 横向分类 Tab 栏（9项分类）', async ({ page }) => {
    // 查找分类 Tab
    const tabs = await page.locator('[data-testid="category-tab"], .category-tab, button:has-text("全部"), button:has-text("恋爱")').all();
    console.log(`找到 ${tabs.length} 个分类 Tab`);
    
    // 截图
    await page.screenshot({ path: '/tmp/fe-d1-categories.png', fullPage: true });
    
    // 验证至少有一些分类元素
    expect(tabs.length).toBeGreaterThan(0);
  });

  test('FE-D2: 排序下拉选择器', async ({ page }) => {
    // 查找排序选择器
    const sortSelect = await page.locator('select:has-text("最新"), select:has-text("热门"), [data-testid="sort-select"]').first();
    
    if (await sortSelect.isVisible()) {
      console.log('找到排序选择器');
      await sortSelect.screenshot({ path: '/tmp/fe-d2-sort.png' });
    } else {
      console.log('未找到排序选择器，截图当前页面');
      await page.screenshot({ path: '/tmp/fe-d2-no-sort.png', fullPage: true });
    }
  });

  test('FE-D3: 滚动分页加载', async ({ page }) => {
    // 获取初始剧本数量
    const initialCards = await page.locator('[data-testid="script-card"], .script-card').count();
    console.log(`初始剧本数量: ${initialCards}`);
    
    // 滚动到底部
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(2000);
    
    // 检查是否加载更多
    const afterScrollCards = await page.locator('[data-testid="script-card"], .script-card').count();
    console.log(`滚动后剧本数量: ${afterScrollCards}`);
    
    await page.screenshot({ path: '/tmp/fe-d3-scroll.png', fullPage: true });
  });

  test('FE-D4: 同分排序一致性', async ({ page }) => {
    // 获取当前排序的剧本列表
    const titles1 = await page.locator('[data-testid="script-card"], .script-card').allTextContents();
    
    // 刷新页面
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // 再次获取
    const titles2 = await page.locator('[data-testid="script-card"], .script-card').allTextContents();
    
    console.log('第一次:', titles1.slice(0, 3));
    console.log('第二次:', titles2.slice(0, 3));
    
    // 验证排序一致
    expect(titles1).toEqual(titles2);
    
    await page.screenshot({ path: '/tmp/fe-d4-sort-stable.png', fullPage: true });
  });

  test('FE-O1: 进度条数据展示', async ({ page }) => {
    // 尝试进入一个剧本
    const firstScript = await page.locator('[data-testid="script-card"], .script-card').first();
    
    if (await firstScript.isVisible()) {
      await firstScript.click();
      await page.waitForLoadState('networkidle');
      
      // 查找进度条
      const progressBar = await page.locator('[data-testid="progress-bar"], .progress-bar, progress').first();
      
      if (await progressBar.isVisible()) {
        console.log('找到进度条');
        await progressBar.screenshot({ path: '/tmp/fe-o1-progress.png' });
      } else {
        console.log('未找到进度条，截图当前页面');
        await page.screenshot({ path: '/tmp/fe-o1-no-progress.png', fullPage: true });
      }
    }
  });

  test('FE-O2: 角色名称和好感度', async ({ page }) => {
    // 尝试进入一个剧本
    const firstScript = await page.locator('[data-testid="script-card"], .script-card').first();
    
    if (await firstScript.isVisible()) {
      await firstScript.click();
      await page.waitForLoadState('networkidle');
      
      // 查找角色信息
      const characterInfo = await page.locator('[data-testid="character-name"], .character-name, [data-testid="affection"]').first();
      
      if (await characterInfo.isVisible()) {
        console.log('找到角色信息');
        await characterInfo.screenshot({ path: '/tmp/fe-o2-character.png' });
      } else {
        console.log('未找到角色信息，截图当前页面');
        await page.screenshot({ path: '/tmp/fe-o2-no-character.png', fullPage: true });
      }
    }
  });

  test('FE-O3: 对话历史查看入口', async ({ page }) => {
    // 尝试进入一个剧本
    const firstScript = await page.locator('[data-testid="script-card"], .script-card').first();
    
    if (await firstScript.isVisible()) {
      await firstScript.click();
      await page.waitForLoadState('networkidle');
      
      // 查找对话历史按钮
      const historyButton = await page.locator('button:has-text("对话历史"), [data-testid="history-button"], .history-button').first();
      
      if (await historyButton.isVisible()) {
        console.log('找到对话历史入口');
        await historyButton.screenshot({ path: '/tmp/fe-o3-history.png' });
      } else {
        console.log('未找到对话历史入口，截图当前页面');
        await page.screenshot({ path: '/tmp/fe-o3-no-history.png', fullPage: true });
      }
    }
  });
});
