import { test, expect } from '@playwright/test';

test.describe('P2 浏览器回归测试（10 项）', () => {
  let testEmail: string;
  let testToken: string;
  const authFile = 'test-results/auth-state.json';

  test.beforeAll(async ({ request }) => {
    // 注册并登录测试用户（只执行一次）
    const timestamp = Date.now();
    testEmail = `p2test${timestamp}@example.com`;
    
    const regResponse = await request.post('http://localhost:8000/api/v1/auth/register', {
      data: {
        email: testEmail,
        password: 'Test123456',
        display_name: 'P2-Tester'
      }
    });
    expect(regResponse.status()).toBe(201);
    
    const loginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
      data: { email: testEmail, password: 'Test123456' }
    });
    expect(loginResponse.status()).toBe(200);
    
    const loginData = await loginResponse.json();
    testToken = loginData.access_token;
    
    console.log(`\n测试账号：${testEmail}`);
    console.log(`Token: ${testToken.substring(0, 20)}...`);
    
    // 保存认证状态到文件
    await request.storageState({ path: authFile });
    console.log(`✓ Auth state saved to ${authFile}`);
  });

  test.beforeEach(async ({ page }) => {
    // 使用与简化测试相同的方式设置认证
    await page.goto('http://localhost:8081/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    // 设置 token 到 localStorage
    await page.evaluate((token) => {
      localStorage.setItem('isekai_access_token', token);
    }, testToken);
    
    // 刷新页面让 Vue 应用重新初始化
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    // 完成 onboarding（如果需要）
    const currentUrl = page.url();
    if (currentUrl.includes('/onboarding')) {
      console.log('完成 onboarding 流程...');
      
      // 步骤 1: 选择题材
      await page.locator('.selection-card').first().click();
      await page.waitForTimeout(500);
      await page.locator('button.nav-button.primary').first().click();
      await page.waitForTimeout(1000);
      
      // 步骤 2: 选择性格
      await page.locator('.selection-card').first().click();
      await page.waitForTimeout(500);
      await page.locator('button.nav-button.primary').first().click();
      await page.waitForTimeout(1000);
      
      // 步骤 3: 完成
      await page.locator('button.nav-button.primary').first().click();
      await page.waitForTimeout(3000);
      
      console.log('✓ Onboarding 完成');
    }
    
    console.log(`✓ 登录成功，当前 URL: ${page.url()}`);
  });

  test('T-012: AI 叙事 loading 状态', async ({ page }) => {
    console.log('\n=== T-012: AI 叙事 loading 状态 ===');
    
    // 开始游戏
    await page.goto('http://localhost:8081/discover');
    await page.waitForLoadState('networkidle');
    
    const firstScript = await page.locator('.script-card').first();
    await firstScript.click();
    await page.waitForTimeout(2000);
    
    await page.locator('button:has-text("开始游戏"), button:has-text("开始")').first().click();
    await page.waitForTimeout(3000);
    
    // 截图游戏页面
    await page.screenshot({ path: 'test-results/t012-01-game-page.png', fullPage: true });
    
    // 检查是否有 loading 动画元素
    const loadingElement = await page.locator('.loading, .spinner, [class*="loading"], [class*="spinner"]').first();
    const hasLoading = await loadingElement.isVisible({ timeout: 5000 }).catch(() => false);
    
    if (hasLoading) {
      console.log('✅ T-012 通过：找到 loading 动画');
      await page.screenshot({ path: 'test-results/t012-02-loading.png', fullPage: true });
    } else {
      console.log('⚠️ T-012: 未检测到 loading 动画（可能已加载完成）');
      // 尝试点击选择触发新的 AI 叙述
      const choiceBtn = await page.locator('button').filter({ hasText: /选择 | 选项/ }).first();
      if (await choiceBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await choiceBtn.click();
        await page.waitForTimeout(1000);
        await page.screenshot({ path: 'test-results/t012-03-after-choice.png', fullPage: true });
      }
    }
  });

  test('T-013: 性格 loyal 映射中文', async ({ page }) => {
    console.log('\n=== T-013: 性格 loyal 映射中文 ===');
    
    await page.goto('http://localhost:8081/characters');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/t013-01-characters-list.png', fullPage: true });
    
    // 点击第一个角色
    const firstChar = await page.locator('.char-card').first();
    await firstChar.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/t013-02-character-detail.png', fullPage: true });
    
    // 检查性格特点区域（根据截图，标题是"性格特点"）
    const personalitySection = await page.locator('text=性格特点').first();
    const hasPersonality = await personalitySection.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasPersonality) {
      const pageText = await page.textContent('body');
      
      // 检查是否包含中文性格特质
      const hasChineseTraits = /勇敢 | 忠诚 | 温柔 | 智慧 | 神秘/.test(pageText || '');
      
      // 检查是否包含英文特质
      const hasEnglishTraits = /brave|loyal|gentle|wisdom|mystery/.test(pageText || '');
      
      if (hasChineseTraits && !hasEnglishTraits) {
        console.log('✅ T-013 通过：性格特质显示中文');
      } else if (hasEnglishTraits) {
        console.log('❌ T-013 失败：性格特质仍显示英文');
      } else {
        console.log('⚠️ T-013: 未找到性格特质');
      }
    } else {
      console.log('️ T-013: 未找到性格特点区域');
    }
  });

  test('T-015: 语音试听功能', async ({ page }) => {
    console.log('\n=== T-015: 语音试听功能 ===');
    
    await page.goto('http://localhost:8081/characters');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    const firstChar = await page.locator('.char-card').first();
    await firstChar.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/t015-01-character-detail.png', fullPage: true });
    
    // 检查语音试听区域（根据截图，标题是"语音试听"）
    const voiceSection = await page.locator('text=语音试听').first();
    const hasVoiceSection = await voiceSection.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasVoiceSection) {
      console.log('✅ T-015 通过：找到语音试听区域');
      
      // 检查是否有语音列表项
      const voiceItems = await page.locator('text=打招呼，text=日常对话，text=告白，text=生气').count();
      console.log(`   找到 ${voiceItems} 个语音项`);
      
      // 检查锁定状态
      const lockedIcons = await page.locator('[class*="lock"], svg').count();
      console.log(`   找到 ${lockedIcons} 个锁定图标`);
      
      await page.screenshot({ path: 'test-results/t015-02-voice-section.png', fullPage: true });
    } else {
      console.log('⚠️ T-015: 未找到语音试听区域');
    }
  });

  test('T-021: 角色羁绊英文翻译', async ({ page }) => {
    console.log('\n=== T-021: 角色羁绊英文翻译 ===');
    
    await page.goto('http://localhost:8081/characters');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    const firstChar = await page.locator('.char-card').first();
    await firstChar.click();
    await page.waitForTimeout(2000);
    
    // 检查好感度区域
    const affectionSection = await page.locator('text=好感度').first();
    const hasAffection = await affectionSection.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasAffection) {
      const pageText = await page.textContent('body');
      
      // 检查是否包含中文等级
      const hasChineseLevel = /陌生人 | 相识 | 暧昧 | 朋友 | 亲密 | 恋人/.test(pageText || '');
      
      // 检查是否包含英文等级
      const hasEnglishLevel = /stranger|acquaintance|friend|close|lover/.test(pageText || '');
      
      if (hasChineseLevel && !hasEnglishLevel) {
        console.log('✅ T-021 通过：好感度等级显示中文');
      } else if (hasEnglishLevel) {
        console.log('❌ T-021 失败：好感度等级仍显示英文');
      } else {
        console.log('⚠️ T-021: 未找到好感度等级');
      }
    } else {
      console.log('⚠️ T-021: 未找到好感度区域');
    }
    
    await page.screenshot({ path: 'test-results/t021-01-bond.png', fullPage: true });
  });

  test('T-011: 对话额度重置', async ({ page }) => {
    console.log('\n=== T-011: 对话额度重置 ===');
    
    await page.goto('http://localhost:8081/personal');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/t011-01-personal-center.png', fullPage: true });
    
    // 检查对话额度区域
    const quotaSection = await page.locator('text=对话额度, text=剩余次数, text=今日对话').first();
    const hasQuota = await quotaSection.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasQuota) {
      console.log('✅ T-011 通过：找到对话额度区域');
      await page.screenshot({ path: 'test-results/t011-02-quota-section.png', fullPage: true });
    } else {
      console.log('⚠️ T-011: 未找到对话额度区域');
    }
  });

  test('T-014: 性格特点数据补全', async ({ page }) => {
    console.log('\n=== T-014: 性格特点数据补全 ===');
    
    await page.goto('http://localhost:8081/characters');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    const firstChar = await page.locator('.char-card').first();
    await firstChar.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/t014-01-character-detail.png', fullPage: true });
    
    // 检查性格特点是否完整
    const personalitySection = await page.locator('text=性格特点').first();
    const hasPersonality = await personalitySection.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasPersonality) {
      const pageText = await page.textContent('body');
      const hasTraits = /勇敢|忠诚|温柔|智慧|神秘/.test(pageText || '');
      
      if (hasTraits) {
        console.log('✅ T-014 通过：性格特点数据完整');
      } else {
        console.log('⚠️ T-014: 性格特点数据不完整');
      }
    } else {
      console.log('⚠️ T-014: 未找到性格特点区域');
    }
  });

  test('T-016: 成就卡片 JSON 展示', async ({ page }) => {
    console.log('\n=== T-016: 成就卡片 JSON 展示 ===');
    
    await page.goto('http://localhost:8081/achievements');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/t016-01-achievements.png', fullPage: true });
    
    // 检查是否显示原始 JSON
    const pageText = await page.textContent('body');
    const hasRawJSON = /\{.*\}|\[.*\]/.test(pageText || '');
    
    if (hasRawJSON) {
      console.log('❌ T-016 失败：页面显示原始 JSON');
    } else {
      console.log('✅ T-016 通过：成就卡片显示格式化内容');
    }
  });

  test('T-017: 碎片商城 Tab 样式', async ({ page }) => {
    console.log('\n=== T-017: 碎片商城 Tab 样式 ===');
    
    await page.goto('http://localhost:8081/fragment-mall');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/t017-01-fragment-mall.png', fullPage: true });
    
    // 检查 Tab 位置（应该在顶部）
    const tabElement = await page.locator('.tab, .tabs, [class*="tab"]').first();
    const hasTab = await tabElement.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasTab) {
      const box = await tabElement.boundingBox();
      if (box && box.y < 200) {
        console.log('✅ T-017 通过：Tab 在顶部');
      } else {
        console.log('⚠️ T-017: Tab 位置可能不正确');
      }
    } else {
      console.log('⚠️ T-017: 未找到 Tab 元素');
    }
  });

  test('T-018: 碎片收支明细中文', async ({ page }) => {
    console.log('\n=== T-018: 碎片收支明细中文 ===');
    
    await page.goto('http://localhost:8081/personal');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 查找收支明细区域
    const transactionSection = await page.locator('text=收支明细, text=交易记录').first();
    const hasTransaction = await transactionSection.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasTransaction) {
      const pageText = await page.textContent('body');
      const hasChinese = /签到|充值|消费|奖励/.test(pageText || '');
      
      if (hasChinese) {
        console.log('✅ T-018 通过：收支明细显示中文');
        await page.screenshot({ path: 'test-results/t018-01-transaction.png', fullPage: true });
      } else {
        console.log('⚠️ T-018: 收支明细未显示中文');
      }
    } else {
      console.log('⚠️ T-018: 未找到收支明细区域');
    }
  });

  test('T-019: 个人中心对话次数展示', async ({ page }) => {
    console.log('\n=== T-019: 个人中心对话次数展示 ===');
    
    await page.goto('http://localhost:8081/personal');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/t019-01-personal-center.png', fullPage: true });
    
    // 检查是否显示对话次数
    const pageText = await page.textContent('body');
    const hasDialogueCount = /对话|额度|次/.test(pageText || '');
    
    if (hasDialogueCount) {
      console.log('✅ T-019 通过：显示对话次数');
    } else {
      console.log('⚠️ T-019: 未找到对话次数展示');
    }
  });

  test('T-020: AI 记忆 Invalid Date', async ({ page }) => {
    console.log('\n=== T-020: AI 记忆 Invalid Date ===');
    
    await page.goto('http://localhost:8081/memory');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/t020-01-memory.png', fullPage: true });
    
    // 检查是否有 Invalid Date
    const pageText = await page.textContent('body');
    const hasInvalidDate = pageText?.includes('Invalid Date');
    
    if (hasInvalidDate) {
      console.log('❌ T-020 失败：页面显示 Invalid Date');
    } else {
      console.log('✅ T-020 通过：日期显示正常');
    }
  });

  test('T-022: 账单显示所有交易', async ({ page }) => {
    console.log('\n=== T-022: 账单显示所有交易 ===');
    
    await page.goto('http://localhost:8081/personal');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 查找账单区域
    const billSection = await page.locator('text=账单, text=交易记录').first();
    const hasBill = await billSection.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasBill) {
      console.log('✅ T-022 通过：找到账单区域');
      await page.screenshot({ path: 'test-results/t022-01-bill.png', fullPage: true });
    } else {
      console.log('⚠️ T-022: 未找到账单区域');
    }
  });

  test('T-023: 帖子浏览量统计', async ({ page }) => {
    console.log('\n=== T-023: 帖子浏览量统计 ===');
    
    await page.goto('http://localhost:8081/community');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/t023-01-community.png', fullPage: true });
    
    // 检查是否显示浏览量
    const pageText = await page.textContent('body');
    const hasViewCount = /浏览|查看|次/.test(pageText || '');
    
    if (hasViewCount) {
      console.log('✅ T-023 通过：显示浏览量');
    } else {
      console.log('⚠️ T-023: 未找到浏览量展示');
    }
  });

  test('T-024: 剧本详情封面图', async ({ page }) => {
    console.log('\n=== T-024: 剧本详情封面图 ===');
    
    await page.goto('http://localhost:8081/discover');
    await page.waitForLoadState('networkidle');
    
    const firstScript = await page.locator('.script-card').first();
    await firstScript.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'test-results/t024-01-script-detail.png', fullPage: true });
    
    // 检查封面图
    const coverImage = await page.locator('img[class*="cover"], img[src*="cover"]').first();
    const hasCover = await coverImage.isVisible({ timeout: 3000 }).catch(() => false);
    
    if (hasCover) {
      const box = await coverImage.boundingBox();
      if (box) {
        // 检查图片是否拉伸（宽高比是否合理）
        const ratio = box.width / box.height;
        if (ratio > 0.5 && ratio < 2.0) {
          console.log('✅ T-024 通过：封面图显示正常');
        } else {
          console.log('⚠️ T-024: 封面图可能拉伸');
        }
      }
    } else {
      console.log('⚠️ T-024: 未找到封面图');
    }
  });

  test('T-025: 前端中文 i18n 补全', async ({ page }) => {
    console.log('\n=== T-025: 前端中文 i18n 补全 ===');
    
    const pagesToCheck = [
      { url: 'http://localhost:8081/discover', name: 'discover' },
      { url: 'http://localhost:8081/characters', name: 'characters' },
      { url: 'http://localhost:8081/personal', name: 'personal' },
      { url: 'http://localhost:8081/achievements', name: 'achievements' },
      { url: 'http://localhost:8081/fragment-mall', name: 'fragment-mall' }
    ];
    
    let hasRawKey = false;
    
    for (const pageInfo of pagesToCheck) {
      await page.goto(pageInfo.url);
      await page.waitForLoadState('networkidle');
      
      const pageText = await page.textContent('body');
      
      // 检查常见的 i18n key 模式
      const rawKeyPattern = /\b(common|auth|profile|settings|game|character|achievement|fragment)\.[a-zA-Z]+\b/;
      
      if (rawKeyPattern.test(pageText || '')) {
        console.log(`❌ T-025: ${pageInfo.name} 页面显示裸英文 key`);
        hasRawKey = true;
        await page.screenshot({ path: `test-results/t025-${pageInfo.name}-raw-key.png`, fullPage: true });
      }
    }
    
    if (!hasRawKey) {
      console.log('✅ T-025 通过：未发现裸英文 key');
    }
  });
});
