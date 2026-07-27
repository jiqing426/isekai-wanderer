import { chromium } from 'playwright';
import fs from 'fs';

const APP_BASE = 'http://localhost:8081';
const token = fs.readFileSync('/tmp/qa_token.txt', 'utf-8').trim();

console.log('='.repeat(60));
console.log('🔍 调试页面内容');
console.log('='.repeat(60));

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

// 注入 token
console.log('\n[1] 注入 Token...');
await page.goto(APP_BASE);
await page.evaluate((t) => {
  localStorage.setItem('access_token', t);
  console.log('Token 已注入 localStorage');
}, token);

// 验证 token
const storedToken = await page.evaluate(() => localStorage.getItem('access_token'));
console.log(`Token 验证: ${storedToken ? '✅ 存在' : '❌ 不存在'}`);

// 测试 CR-013
console.log('\n[2] 测试 CR-013 剧本详情...');
await page.goto(`${APP_BASE}/scripts/66666666-6666-6666-6666-666666666666`);
await page.waitForTimeout(3000);

const currentUrl = page.url();
console.log(`当前 URL: ${currentUrl}`);

const title = await page.title();
console.log(`页面标题: ${title}`);

const content = await page.textContent('body');
console.log(`\n页面内容 (前 500 字符):\n${content.substring(0, 500)}`);

// 截图
await page.screenshot({ path: '/tmp/cr013-debug.png', fullPage: true });
console.log('\n截图已保存: /tmp/cr013-debug.png');

// 检查是否被重定向
if (currentUrl.includes('/login') || currentUrl.includes('/onboarding')) {
  console.log('\n⚠️  页面被重定向到登录/引导页');
}

await browser.close();
