// INTEGRATION E2E — 10 路径完整验证（含 onboarding 跳过）
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE = 'http://localhost:3000';
const DIR = path.join(__dirname, '..', 'e2e-screens', 'integration');
fs.mkdirSync(DIR, { recursive: true });

const email = `e2e_int_${Date.now()}@test.com`;
const password = 'Test1234!';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

  // 收集 API 调用
  const apiCalls = [];
  page.on('response', async (resp) => {
    if (resp.url().includes('/api/v1/')) {
      apiCalls.push({ status: resp.status(), url: resp.url().split('/api/v1/')[1] });
    }
  });

  async function shot(name) {
    const p = path.join(DIR, `${name}.png`);
    await page.screenshot({ path: p, fullPage: false });
    console.log(`  📸 ${name}`);
  }

  try {
    // ═══ PATH-1: 注册 ═══
    console.log('═══ PATH-1: 注册 ═══');
    await page.goto(`${BASE}/register`);
    await page.waitForTimeout(800);
    await page.fill('input[type="email"]', email);
    const pws = await page.locator('input[type="password"]').all();
    if (pws.length >= 2) { await pws[0].fill(password); await pws[1].fill(password); }
    await shot('01-register');
    await page.locator('button.n-button--primary-type').first().click();
    await page.waitForTimeout(3000);
    console.log(`  after register: ${page.url()}`);

    // ═══ 完成 Onboarding（跳过） ═══
    console.log('═══ 完成 Onboarding ═══');
    if (page.url().includes('/onboarding')) {
      // Step 1: 选一个题材
      const genreCard = await page.locator('.genre-card').first();
      if (await genreCard.count() > 0) await genreCard.click();
      await page.waitForTimeout(300);

      // 点下一步
      const nextBtn1 = await page.locator('button:has-text("下一步")').first();
      if (await nextBtn1.count() > 0) await nextBtn1.click();
      await page.waitForTimeout(500);

      // Step 2: 选一个风格
      const styleCard = await page.locator('.style-card').first();
      if (await styleCard.count() > 0) await styleCard.click();
      await page.waitForTimeout(300);

      const nextBtn2 = await page.locator('button:has-text("下一步")').first();
      if (await nextBtn2.count() > 0) await nextBtn2.click();
      await page.waitForTimeout(500);

      // Step 3: 点"跳过"或"完成设置"
      const skipBtn = await page.locator('button:has-text("跳过")').first();
      const completeBtn = await page.locator('button:has-text("完成设置")').first();
      if (await skipBtn.count() > 0) {
        await skipBtn.click();
      } else if (await completeBtn.count() > 0) {
        await completeBtn.click();
      }
      await page.waitForTimeout(3000);
      console.log(`  after onboarding: ${page.url()}`);
    }

    // ═══ PATH-2: 登录页 ═══
    console.log('═══ PATH-2: 登录 ═══');
    await page.evaluate(() => { localStorage.clear(); });
    await page.goto(`${BASE}/login`);
    await page.waitForTimeout(800);
    await shot('02-login');
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.locator('button.n-button--primary-type').first().click();
    await page.waitForTimeout(3000);
    console.log(`  after login: ${page.url()}`);

    // 如果又进 onboarding，再跳一次
    if (page.url().includes('/onboarding')) {
      await page.locator('button:has-text("跳过")').first().click().catch(() => {});
      await page.waitForTimeout(2000);
      if (page.url().includes('/onboarding')) {
        await page.locator('button:has-text("完成设置")').first().click().catch(() => {});
        await page.waitForTimeout(2000);
      }
    }

    // ═══ PATH-3: 首页（登录后） ═══
    console.log('═══ PATH-3: 首页 ═══');
    await page.goto(`${BASE}/home`);
    await page.waitForTimeout(2000);
    await shot('03-home');

    // ═══ PATH-4: 剧本列表 ═══
    console.log('═══ PATH-4: 剧本列表 ═══');
    const scriptCount = await page.locator('.script-card').count();
    console.log(`  scripts: ${scriptCount}`);
    await shot('04-scripts');

    // ═══ PATH-5: 游戏对话 ═══
    console.log('═══ PATH-5: 游戏 ═══');
    if (scriptCount > 0) {
      await page.locator('.script-card').first().click();
      await page.waitForTimeout(3000);
      await shot('05-game-dialogue');
    } else {
      // 直接导航到游戏
      await page.goto(`${BASE}/game`);
      await page.waitForTimeout(3000);
      await shot('05-game-dialogue');
    }

    // ═══ PATH-6: 选择后好感变化 ═══
    console.log('═══ PATH-6: 好感度 ═══');
    const choiceCard = await page.locator('.choice-card').first();
    if (await choiceCard.count() > 0) {
      await shot('06-before-choice');
      await choiceCard.click();
      await page.waitForTimeout(3000);
      await shot('06-affection-change');
    } else {
      console.log('  no choice cards, taking screenshot of current state');
      await shot('06-affection-change');
    }

    // ═══ PATH-7: 签到 ═══
    console.log('═══ PATH-7: 签到 ═══');
    await page.goto(`${BASE}/home`);
    await page.waitForTimeout(1500);
    const checkinBtn = await page.locator('.checkin-btn').first();
    if (await checkinBtn.count() > 0) {
      await checkinBtn.click();
      await page.waitForTimeout(1000);
      await shot('07-daily-checkin');
      const confirmBtn = await page.locator('.n-modal .n-button--primary-type').first();
      if (await confirmBtn.count() > 0) {
        await confirmBtn.click();
        await page.waitForTimeout(1000);
        await shot('07b-checkin-result');
      }
    } else {
      await shot('07-daily-checkin');
    }

    // ═══ PATH-8: 订阅 ═══
    console.log('═══ PATH-8: 订阅 ═══');
    await page.goto(`${BASE}/subscription`);
    await page.waitForTimeout(1500);
    const planCount = await page.locator('.plan-card').count();
    console.log(`  plans: ${planCount}`);
    await shot('08-subscription');

    // ═══ PATH-9: 画廊 ═══
    console.log('═══ PATH-9: 画廊 ═══');
    await page.goto(`${BASE}/gallery`);
    await page.waitForTimeout(1500);
    await shot('09-gallery');

    // ═══ PATH-10: 社区 ═══
    console.log('═══ PATH-10: 社区 ═══');
    await page.goto(`${BASE}/community`);
    await page.waitForTimeout(1500);
    const postCount = await page.locator('.post-card').count();
    console.log(`  posts: ${postCount}`);
    await shot('10-community');

  } catch (err) {
    console.log(`❌ Error: ${err.message}`);
    await shot('99-error');
  }

  console.log('\n═══ API 调用汇总 ═══');
  for (const c of apiCalls) {
    console.log(`  ${c.status} ${c.url}`);
  }

  // 截图清单
  console.log('\n═══ 截图清单 ═══');
  const files = fs.readdirSync(DIR).filter(f => f.endsWith('.png')).sort();
  for (const f of files) {
    console.log(`  ${f}`);
  }

  await browser.close();
  console.log('\n✅ Done');
})();
