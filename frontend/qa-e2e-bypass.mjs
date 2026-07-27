import { chromium } from 'playwright';
import fs from 'fs';

const APP_BASE = 'http://localhost:8081';
const token = fs.readFileSync('/tmp/qa_token.txt', 'utf-8').trim();

console.log('=' .repeat(60));
console.log('📊 CR-013/014/015 前端 E2E 测试（绕过登录）');
console.log('=' .repeat(60));

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

// 访问首页，注入token
await page.goto(APP_BASE);
await page.evaluate((t) => {
  localStorage.setItem('isekai_access_token', t);
}, token);

const results = [];

// CR-013: 剧本详情页面
console.log('\n[1/3] CR-013: 剧本详情页面渲染...');
try {
  await page.goto(`${APP_BASE}/scripts/66666666-6666-6666-6666-666666666666`);
  await page.waitForTimeout(2000);
  
  const url = page.url();
  if (url.includes('/login') || url.includes('/onboarding')) {
    throw new Error(`重定向到 ${url}`);
  }
  
  const title = await page.title();
  const bodyText = await page.textContent('body');
  
  if (bodyText.includes('星月奇缘')) {
    console.log('✅ 页面渲染成功');
    console.log(`   - 标题: ${title}`);
    console.log(`   - 内容包含: 星月奇缘`);
    results.push({ cr: 'CR-013', status: 'PASS', detail: '页面渲染正常' });
  } else {
    throw new Error('页面内容不完整');
  }
} catch (e) {
  console.log(`❌ 失败: ${e.message}`);
  results.push({ cr: 'CR-013', status: 'FAIL', detail: e.message });
}

// CR-014: 成就系统页面
console.log('\n[2/3] CR-014: 成就系统页面渲染...');
try {
  await page.goto(`${APP_BASE}/achievements`);
  await page.waitForTimeout(2000);
  
  const url = page.url();
  if (url.includes('/login') || url.includes('/onboarding')) {
    throw new Error(`重定向到 ${url}`);
  }
  
  const title = await page.title();
  const bodyText = await page.textContent('body');
  
  if (bodyText.includes('成就') || bodyText.includes('achievement')) {
    console.log('✅ 页面渲染成功');
    console.log(`   - 标题: ${title}`);
    console.log(`   - 内容包含: 成就相关文本`);
    results.push({ cr: 'CR-014', status: 'PASS', detail: '页面渲染正常' });
  } else {
    throw new Error('页面内容不完整');
  }
} catch (e) {
  console.log(`❌ 失败: ${e.message}`);
  results.push({ cr: 'CR-014', status: 'FAIL', detail: e.message });
}

// CR-015: 角色设定页面
console.log('\n[3/3] CR-015: 角色设定页面渲染...');
try {
  await page.goto(`${APP_BASE}/characters/22222222-2222-2222-2222-222222222222`);
  await page.waitForTimeout(2000);
  
  const url = page.url();
  if (url.includes('/login') || url.includes('/onboarding')) {
    throw new Error(`重定向到 ${url}`);
  }
  
  const title = await page.title();
  const bodyText = await page.textContent('body');
  
  if (bodyText.includes('林辰') || bodyText.includes('角色')) {
    console.log('✅ 页面渲染成功');
    console.log(`   - 标题: ${title}`);
    console.log(`   - 内容包含: 林辰`);
    results.push({ cr: 'CR-015', status: 'PASS', detail: '页面渲染正常' });
  } else {
    throw new Error('页面内容不完整');
  }
} catch (e) {
  console.log(`❌ 失败: ${e.message}`);
  results.push({ cr: 'CR-015', status: 'FAIL', detail: e.message });
}

await browser.close();

// 输出测试报告
console.log('\n' + '=' .repeat(60));
console.log('📊 测试报告');
console.log('=' .repeat(60));

const pass = results.filter(r => r.status === 'PASS').length;
const total = results.length;
const rate = ((pass / total) * 100).toFixed(1);

console.log(`\n✅ 通过: ${pass}/${total}`);
console.log(`📈 通过率: ${rate}%`);

console.log('\n详细结果:');
results.forEach(r => {
  const icon = r.status === 'PASS' ? '✅' : '❌';
  console.log(`  ${icon} ${r.cr}: ${r.detail}`);
});

console.log('\n' + '=' .repeat(60));
if (rate === '100.0') {
  console.log('✅ 建议发布: YES');
} else {
  console.log('❌ 建议发布: NO');
}
console.log('=' .repeat(60));
