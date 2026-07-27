import { chromium } from 'playwright';

const APP_BASE = 'http://localhost:8081';

const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-gpu'] });
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await ctx.newPage();

// Navigate to app
await page.goto(APP_BASE, { waitUntil: 'domcontentloaded', timeout: 15000 });
await page.waitForTimeout(1000);

// Login
const loginResp = await page.evaluate(async () => {
  const r = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'qa-fresh@isekai.dev', password: 'QATest123456' })
  });
  return r.json();
});
await page.evaluate((data) => {
  localStorage.setItem('isekai_access_token', data.access_token);
  localStorage.setItem('isekai_refresh_token', data.refresh_token);
}, loginResp);

// Go to subscription page
await page.goto(`${APP_BASE}/subscription`, { waitUntil: 'domcontentloaded', timeout: 15000 });
await page.waitForTimeout(3000);

// Take screenshot
await page.screenshot({ path: '/tmp/cr012-subscription.png', fullPage: true });
console.log('Screenshot saved to /tmp/cr012-subscription.png');

// Get page content
const text = await page.textContent('body');
console.log(`\nPage text length: ${text.length}`);
console.log(`\nPage text preview:\n${text.substring(0, 500)}`);

// Check URL
console.log(`\nCurrent URL: ${page.url()}`);

// Check for tabs
const tabs = await page.$$('[role="tab"]');
console.log(`\nTabs found: ${tabs.length}`);

// Check for buttons
const buttons = await page.$$('button');
console.log(`Buttons found: ${buttons.length}`);

// Check for cards
const cards = await page.$$('[class*="card"], [class*="Card"]');
console.log(`Cards found: ${cards.length}`);

// Check for price elements
const prices = await page.$$('[class*="price"], [class*="Price"]');
console.log(`Price elements found: ${prices.length}`);

// Get all class names to understand structure
const allClasses = await page.evaluate(() => {
  const elements = document.querySelectorAll('*');
  const classes = new Set();
  elements.forEach(el => {
    el.classList.forEach(cls => classes.add(cls));
  });
  return Array.from(classes).slice(0, 100);
});
console.log(`\nSample of class names on page:\n${allClasses.slice(0, 50).join(', ')}`);

await browser.close();
