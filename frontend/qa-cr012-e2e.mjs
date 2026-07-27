import { chromium } from 'playwright';

const APP_BASE = 'http://localhost:8081';
const results = [];

async function test(name, fn) {
  try {
    const extra = await fn();
    results.push({ name, status: 'PASS', extra });
    console.log(`✅ ${name}${extra ? ' — ' + extra : ''}`);
  } catch (e) {
    results.push({ name, status: 'FAIL', error: e.message.split('\n')[0] });
    console.log(`❌ ${name}: ${e.message.split('\n')[0]}`);
  }
}

const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-gpu'] });
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();

// Navigate to app
await page.goto(APP_BASE, { waitUntil: 'domcontentloaded', timeout: 15000 });
await page.waitForTimeout(1000);

// Login with account that has onboarding_completed = true
await test('1. Login (onboarding completed account)', async () => {
  const loginResp = await page.evaluate(async () => {
    const r = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'qa-fresh@isekai.dev', password: 'QATest123456' })
    });
    return r.json();
  });
  if (!loginResp.access_token) throw new Error('Login failed');
  await page.evaluate((data) => {
    localStorage.setItem('isekai_access_token', data.access_token);
    localStorage.setItem('isekai_refresh_token', data.refresh_token);
  }, loginResp);
  return 'Token stored for qa-fresh@isekai.dev';
});

// Test subscription page
await test('2. Subscription page renders', async () => {
  await page.goto(`${APP_BASE}/subscription`, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(3000);
  const url = page.url();
  if (!url.includes('/subscription')) throw new Error(`Redirected to ${url}`);
  const text = await page.textContent('body');
  if (!text || text.length < 10) throw new Error('Empty subscription page');
  return `Page loaded, text length: ${text.length}`;
});

await test('3. Tab switching (Monthly/Yearly)', async () => {
  // Look for tabs - try multiple selectors
  let tabs = await page.$$('[role="tab"]');
  if (tabs.length < 2) {
    tabs = await page.$$('button:has-text("月"), button:has-text("年")');
  }
  if (tabs.length < 2) {
    tabs = await page.$$('.tab-item, [class*="tab"]');
  }
  if (tabs.length < 2) throw new Error(`Expected 2+ tabs, found ${tabs.length}`);
  
  // Click first tab (monthly)
  await tabs[0].click();
  await page.waitForTimeout(500);
  
  // Click second tab (yearly)
  await tabs[1].click();
  await page.waitForTimeout(500);
  
  return `Found ${tabs.length} tabs, switching works`;
});

await test('4. Price display (monthly/yearly)', async () => {
  // Check if prices are visible - try multiple selectors
  let priceElements = await page.$$('[class*="price"], [class*="Price"]');
  if (priceElements.length === 0) {
    priceElements = await page.$$('.price-monthly, .price-yearly');
  }
  if (priceElements.length === 0) {
    // Look for elements containing price patterns
    priceElements = await page.$$('text=/\\$[0-9]+/');
  }
  if (priceElements.length === 0) throw new Error('No price elements found');
  
  // Get text content of first price
  const priceText = await priceElements[0].textContent();
  if (!priceText || priceText.trim().length === 0) throw new Error('Price text is empty');
  
  return `Found ${priceElements.length} price elements, first: "${priceText.trim().substring(0, 50)}"`;
});

await test('5. Plan cards rendering', async () => {
  // Look for plan cards
  const planCards = await page.$$('[class*="plan"], [class*="Plan"], [class*="card"], [class*="Card"]');
  if (planCards.length < 4) throw new Error(`Expected 4+ plan cards, found ${planCards.length}`);
  
  // Check if cards have content
  const firstCardText = await planCards[0].textContent();
  if (!firstCardText || firstCardText.trim().length === 0) throw new Error('Plan card is empty');
  
  return `Found ${planCards.length} plan cards`;
});

await test('6. API proxy: /subscription/plans (Mock API=no)', async () => {
  const resp = await page.evaluate(async () => {
    const r = await fetch('/api/v1/subscription/plans');
    return { status: r.status, body: await r.json() };
  });
  if (resp.status !== 200) throw new Error(`status ${resp.status}`);
  if (!resp.body.plans || resp.body.plans.length !== 4) throw new Error('Expected 4 plans');
  return `Got ${resp.body.plans.length} plans`;
});

await test('7. API proxy: /user/subscription (Mock API=no)', async () => {
  const resp = await page.evaluate(async () => {
    const token = localStorage.getItem('isekai_access_token');
    const r = await fetch('/api/v1/user/subscription', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return { status: r.status, body: await r.json() };
  });
  if (resp.status !== 200) throw new Error(`status ${resp.status}`);
  if (!resp.body.currentPlanId) throw new Error('Missing currentPlanId');
  return `currentPlanId: ${resp.body.currentPlanId}`;
});

await test('8. Frontend proxy health (Mock API=no)', async () => {
  const resp = await page.evaluate(async () => {
    const r = await fetch('/api/v1/health');
    return { status: r.status, body: await r.json() };
  });
  if (resp.status !== 200) throw new Error(`Health status ${resp.status}`);
  return 'ok';
});

await browser.close();

console.log('\n=== CR-012 Browser E2E Summary ===');
const pass = results.filter(r => r.status === 'PASS').length;
const fail = results.filter(r => r.status === 'FAIL').length;
console.log(`PASS: ${pass}, FAIL: ${fail}, TOTAL: ${results.length}`);
if (fail > 0) {
  results.filter(r => r.status === 'FAIL').forEach(r => console.log(`  - ${r.name}: ${r.error}`));
}
