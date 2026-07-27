const { chromium } = require('playwright');
const path = require('path');

const SCREENSHOT_DIR = path.join(__dirname, '..', 'e2e-screens');
const BASE_URL = 'http://localhost:3000';

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  // Capture console errors
  page.on('console', msg => {
    if (msg.type() === 'error') console.log(`  [browser:error] ${msg.text()}`);
  });
  page.on('pageerror', err => console.log(`  [page:error] ${err.message}`));

  async function shot(name) {
    const fp = path.join(SCREENSHOT_DIR, `${name}.png`);
    await page.screenshot({ path: fp, fullPage: false });
    console.log(`  📸 ${name} → ${fp}`);
  }

  try {
    // 0. Landing page
    console.log('0. Landing page');
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(800);
    await shot('00-landing');

    // 1. Login page
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(800);
    await shot('01-login');

    // 2. Register page
    console.log('2. Register page');
    await page.goto(`${BASE_URL}/register`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(800);
    await shot('02-register');

    // 3. Register a new user → auto-login → onboarding
    console.log('3. Register new user');
    const email = `e2e-${Date.now()}@wanderer.com`;
    
    // Wait for all inputs to be visible
    await page.waitForSelector('input[type="email"]', { timeout: 5000 });
    await page.fill('input[type="email"]', email);
    
    // Fill both password fields
    const pwdInputs = await page.locator('input[type="password"]').all();
    console.log(`  found ${pwdInputs.length} password inputs`);
    if (pwdInputs.length >= 2) {
      await pwdInputs[0].fill('Test1234!');
      await pwdInputs[1].fill('Test1234!');
    }
    await page.waitForTimeout(500);
    await shot('02b-register-filled');

    // Click register button and wait for navigation
    console.log('  clicking register button...');
    await Promise.all([
      page.click('button:has-text("注册")'),
      page.waitForURL('**/onboarding', { timeout: 10000 }).catch(e => console.log(`  nav timeout: ${e.message}`))
    ]);
    await page.waitForTimeout(1500);
    console.log(`  after register, URL: ${page.url()}`);

    // 4. Should redirect to onboarding
    console.log('4. Onboarding page');
    const url4 = page.url();
    console.log(`  current URL: ${url4}`);
    await page.waitForTimeout(800);
    await shot('03-onboarding-step1');

    // Click genre cards
    const genreCards = await page.locator('.genre-card').all();
    if (genreCards.length > 0) {
      await genreCards[0].click(); // romance
      await genreCards[1].click(); // fantasy
      await page.waitForTimeout(400);
      await shot('03b-onboarding-genre-selected');
    }

    // Click next
    await page.click('button:has-text("下一步")');
    await page.waitForTimeout(600);
    await shot('03c-onboarding-step2');

    // Click a style card
    const styleCards = await page.locator('.style-card').all();
    if (styleCards.length > 0) {
      await styleCards[0].click();
      await page.waitForTimeout(400);
    }

    // Click next again
    await page.click('button:has-text("下一步")');
    await page.waitForTimeout(600);
    await shot('03d-onboarding-step3-ready');

    // Click complete (text is i18n: 完成设置 ✦)
    await page.click('button:has-text("完成设置")');
    await page.waitForTimeout(3000);

    // 5. Home page
    console.log('5. Home page');
    const url5 = page.url();
    console.log(`  current URL: ${url5}`);
    await page.waitForTimeout(1000);
    await shot('04-home');

    // Check scripts loaded
    const scriptCards = await page.locator('.script-card').count();
    console.log(`  scripts visible: ${scriptCards}`);

    // 6. Click first script → game
    console.log('6. Start game');
    const firstScript = await page.locator('.script-card').first();
    if (firstScript) {
      await firstScript.click();
      await page.waitForTimeout(3000);
      await shot('05-game-dialogue');
    }

    // 7. Check dialogue + choices visible
    const hasDialogue = await page.locator('.dialogue-box').count() > 0;
    const hasChoices = await page.locator('.choice-card').count() > 0;
    console.log(`  dialogue visible: ${hasDialogue}, choices visible: ${hasChoices}`);

    // Click first choice
    if (hasChoices) {
      const firstChoice = await page.locator('.choice-card').first();
      await firstChoice.click();
      await page.waitForTimeout(3000);
      await shot('06-game-after-choice');
      console.log('  choice submitted');
    }

    // 8. Open affection sidebar
    const topbarBtn = await page.locator('.topbar-btn').first();
    if (topbarBtn) {
      await topbarBtn.click();
      await page.waitForTimeout(800);
      await shot('07-game-affection-sidebar');
    }

    // 9. Click check-in from home
    console.log('7. Check-in');
    await page.goto(`${BASE_URL}/home`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(1500);
    
    // Use the class selector for the checkin button (Naive UI renders with emoji + text)
    const checkinOpenBtn = page.locator('.checkin-btn');
    if (await checkinOpenBtn.count() > 0) {
      await checkinOpenBtn.click();
      await page.waitForTimeout(1000);
      await shot('08-checkin-modal');

      // Click checkin button in modal - use the button with "签到领取奖励" text
      const doCheckin = page.locator('.n-modal button').first();
      if (await doCheckin.count() > 0) {
        await doCheckin.click();
        await page.waitForTimeout(1500);
        await shot('09-checkin-result');
        console.log('  check-in submitted');
      }
    } else {
      console.log('  checkin button not found, taking screenshot of home');
      await shot('08-home-no-checkin-btn');
    }

    // === Phase 3 pages ===

    // 10. Subscription page
    console.log('8. Subscription page');
    await page.goto(`${BASE_URL}/subscription`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(1500);
    await shot('10-subscription');

    // Scroll down to see comparison table
    await page.evaluate(() => window.scrollBy(0, 600));
    await page.waitForTimeout(500);
    await shot('10b-subscription-comparison');

    // 11. Community page
    console.log('9. Community page');
    await page.goto(`${BASE_URL}/community`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(1500);
    await shot('11-community');

    // Click first post to see detail
    const firstPost = page.locator('.post-card').first();
    if (await firstPost.count() > 0) {
      await firstPost.click();
      await page.waitForTimeout(1000);
      await shot('11b-community-detail');
    }

    // 12. Gallery page
    console.log('10. Gallery page');
    await page.goto(`${BASE_URL}/gallery`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(1500);
    await shot('12-gallery-cgs');

    // Click characters tab
    const charTab = page.locator('.n-tabs-tab').filter({ hasText: '角色图鉴' });
    if (await charTab.count() > 0) {
      await charTab.click();
      await page.waitForTimeout(800);
      await shot('12b-gallery-characters');
    }

    // Click achievements tab
    const achTab = page.locator('.n-tabs-tab').filter({ hasText: '成就墙' });
    if (await achTab.count() > 0) {
      await achTab.click();
      await page.waitForTimeout(800);
      await shot('12c-gallery-achievements');
    }

    // 13. Share page (public)
    console.log('11. Share page');
    await page.goto(`${BASE_URL}/share/share_abc123`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(1500);
    await shot('13-share-card');

    // 14. Login page with social buttons
    console.log('12. Login page (social buttons)');
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(1000);
    await shot('14-login-social');

    console.log('\n✅ All screenshots captured!');
  } catch (err) {
    console.error(`❌ Error: ${err.message}`);
    await shot('99-error-state');
  } finally {
    await browser.close();
  }
})();
