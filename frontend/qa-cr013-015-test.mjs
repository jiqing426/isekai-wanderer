import { chromium } from 'playwright';
import fs from 'fs';

const APP_BASE = 'http://localhost:8081';
const token = fs.readFileSync('/tmp/qa_token.txt', 'utf-8').trim();

console.log('='.repeat(60));
console.log('📊 CR-013/014/015 E2E 测试（修正 Token Key）');
console.log('='.repeat(60));

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

// 注入 token 使用正确的 key
console.log('\n[0] 注入 Token...');
await page.goto(APP_BASE);
await page.evaluate((t) => {
  localStorage.setItem('isekai_access_token', t);
  console.log('Token 已注入 isekai_access_token');
}, token);

const results = [];

// CR-013: 剧本详情
console.log('\n[1/3] CR-013: 剧本详情...');
try {
  await page.goto(`${APP_BASE}/scripts/66666666-6666-6666-6666-666666666666`);
  await page.waitForTimeout(3000);
  
  const currentUrl = page.url();
  console.log(`  当前 URL: ${currentUrl}`);
  
  if (currentUrl.includes('/login') || currentUrl.includes('/onboarding')) {
    throw new Error(`页面被重定向到 ${currentUrl}`);
  }
  
  const content = await page.textContent('body');
  if (!content.includes('星月奇缘')) {
    throw new Error('页面内容不完整，未找到"星月奇缘"');
  }
  
  console.log('✅ CR-013 测试通过');
  results.push({ cr: 'CR-013', status: 'PASS', detail: '剧本详情页面正常' });
} catch (e) {
  console.log(`❌ CR-013 失败: ${e.message}`);
  results.push({ cr: 'CR-013', status: 'FAIL', detail: e.message });
}

// CR-014: 成就系统
console.log('\n[2/3] CR-014: 成就系统...');
try {
  await page.goto(`${APP_BASE}/achievements`);
  await page.waitForTimeout(3000);
  
  const currentUrl = page.url();
  console.log(`  当前 URL: ${currentUrl}`);
  
  if (currentUrl.includes('/login') || currentUrl.includes('/onboarding')) {
    throw new Error(`页面被重定向到 ${currentUrl}`);
  }
  
  const content = await page.textContent('body');
  if (!content.includes('成就') && !content.includes('achievement')) {
    throw new Error('页面内容不完整，未找到成就相关内容');
  }
  
  console.log('✅ CR-014 测试通过');
  results.push({ cr: 'CR-014', status: 'PASS', detail: '成就系统页面正常' });
} catch (e) {
  console.log(`❌ CR-014 失败: ${e.message}`);
  results.push({ cr: 'CR-014', status: 'FAIL', detail: e.message });
}

// CR-015: 角色设定
console.log('\n[3/3] CR-015: 角色设定...');
try {
  await page.goto(`${APP_BASE}/characters/22222222-2222-2222-2222-222222222222`);
  await page.waitForTimeout(3000);
  
  const currentUrl = page.url();
  console.log(`  当前 URL: ${currentUrl}`);
  
  if (currentUrl.includes('/login') || currentUrl.includes('/onboarding')) {
    throw new Error(`页面被重定向到 ${currentUrl}`);
  }
  
  const content = await page.textContent('body');
  if (!content.includes('林辰')) {
    throw new Error('页面内容不完整，未找到"林辰"');
  }
  
  console.log('✅ CR-015 测试通过');
  results.push({ cr: 'CR-015', status: 'PASS', detail: '角色设定页面正常' });
} catch (e) {
  console.log(`❌ CR-015 失败: ${e.message}`);
  results.push({ cr: 'CR-015', status: 'FAIL', detail: e.message });
}

await browser.close();

// 输出测试报告
console.log('\n' + '='.repeat(60));
console.log('📊 测试报告');
console.log('='.repeat(60));

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

console.log('\n' + '='.repeat(60));
if (rate === '100.0') {
  console.log('✅ 建议发布: YES');
  console.log('   - 所有测试通过');
  console.log('   - 功能完整可用');
} else {
  console.log('❌ 建议发布: NO');
  console.log(`   - 存在 ${total - pass} 个失败项`);
}
console.log('='.repeat(60));
