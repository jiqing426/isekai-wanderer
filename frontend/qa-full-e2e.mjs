import { chromium } from 'playwright';

const APP_BASE = 'http://localhost:8081';

console.log('=' .repeat(60));
console.log('📊 CR-013/014/015 完整 E2E 测试');
console.log('=' .repeat(60));

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

const results = [];

// 任务 1: 验证登录
console.log('\n[0/3] 验证登录功能...');
try {
  await page.goto(APP_BASE);
  await page.click('text=登录');
  await page.waitForSelector('input[type="email"]');
  
  await page.fill('input[type="email"]', 'qa-e2e-final@isekai.dev');
  await page.fill('input[type="password"]', 'QATest123456');
  await page.click('button[type="submit"]');
  
  await page.waitForTimeout(2000);
  
  const url = page.url();
  if (url.includes('/login')) {
    throw new Error('登录失败，仍在登录页');
  }
  
  console.log('✅ 登录成功');
  results.push({ cr: '登录', status: 'PASS', detail: '浏览器登录正常' });
} catch (e) {
  console.log(`❌ 登录失败: ${e.message}`);
  results.push({ cr: '登录', status: 'FAIL', detail: e.message });
}

// 任务 2: CR-013 剧本详情
console.log('\n[1/3] CR-013: 剧本详情页面...');
try {
  // API 测试
  const apiResp = await page.evaluate(async () => {
    const token = localStorage.getItem('isekai_access_token');
    const resp = await fetch('/api/v1/scripts/66666666-6666-6666-6666-666666666666/detail', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return resp.json();
  });
  
  if (!apiResp.scriptId) throw new Error('API 返回数据不完整');
  
  // 检查节点类型
  const nodeTypes = new Set();
  apiResp.chapters?.forEach(ch => {
    ch.nodes?.forEach(n => nodeTypes.add(n.type));
  });
  
  console.log('✅ API 测试通过');
  console.log(`   - 节点类型: ${Array.from(nodeTypes).join(', ')}`);
  results.push({ cr: 'CR-013-API', status: 'PASS', detail: `节点类型: ${Array.from(nodeTypes).join(', ')}` });
  
  // 前端页面测试
  await page.goto(`${APP_BASE}/scripts/66666666-6666-6666-6666-666666666666`);
  await page.waitForTimeout(2000);
  
  const title = await page.title();
  const bodyText = await page.textContent('body');
  
  if (!bodyText.includes('星月奇缘')) throw new Error('页面内容不完整');
  
  console.log('✅ 前端页面渲染成功');
  results.push({ cr: 'CR-013-UI', status: 'PASS', detail: '页面渲染正常' });
} catch (e) {
  console.log(`❌ CR-013 失败: ${e.message}`);
  results.push({ cr: 'CR-013', status: 'FAIL', detail: e.message });
}

// 任务 3: CR-014 成就系统
console.log('\n[2/3] CR-014: 成就系统...');
try {
  // API 测试
  const apiResp = await page.evaluate(async () => {
    const token = localStorage.getItem('isekai_access_token');
    const resp = await fetch('/api/v1/achievements', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return resp.json();
  });
  
  if (!apiResp.achievements || apiResp.achievements.length === 0) {
    throw new Error('API 返回成就列表为空');
  }
  
  console.log('✅ API 测试通过');
  console.log(`   - 成就数量: ${apiResp.achievements.length}`);
  results.push({ cr: 'CR-014-API', status: 'PASS', detail: `成就数量: ${apiResp.achievements.length}` });
  
  // 前端页面测试
  await page.goto(`${APP_BASE}/achievements`);
  await page.waitForTimeout(2000);
  
  const bodyText = await page.textContent('body');
  
  if (!bodyText.includes('成就') && !bodyText.includes('achievement')) {
    throw new Error('页面内容不完整');
  }
  
  console.log('✅ 前端页面渲染成功');
  results.push({ cr: 'CR-014-UI', status: 'PASS', detail: '页面渲染正常' });
} catch (e) {
  console.log(`❌ CR-014 失败: ${e.message}`);
  results.push({ cr: 'CR-014', status: 'FAIL', detail: e.message });
}

// 任务 4: CR-015 角色设定
console.log('\n[3/3] CR-015: 角色设定...');
try {
  // API 测试
  const apiResp = await page.evaluate(async () => {
    const token = localStorage.getItem('isekai_access_token');
    const resp = await fetch('/api/v1/characters/22222222-2222-2222-2222-222222222222', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return resp.json();
  });
  
  if (!apiResp.name) throw new Error('API 返回数据不完整');
  
  console.log('✅ API 测试通过');
  console.log(`   - 角色名称: ${apiResp.name}`);
  results.push({ cr: 'CR-015-API', status: 'PASS', detail: `角色: ${apiResp.name}` });
  
  // 前端页面测试
  await page.goto(`${APP_BASE}/characters/22222222-2222-2222-2222-222222222222`);
  await page.waitForTimeout(2000);
  
  const bodyText = await page.textContent('body');
  
  if (!bodyText.includes('林辰')) throw new Error('页面内容不完整');
  
  console.log('✅ 前端页面渲染成功');
  results.push({ cr: 'CR-015-UI', status: 'PASS', detail: '页面渲染正常' });
} catch (e) {
  console.log(`❌ CR-015 失败: ${e.message}`);
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
  console.log('   - 所有测试通过');
  console.log('   - 登录问题已修复');
  console.log('   - 功能完整可用');
} else {
  console.log('❌ 建议发布: NO');
  console.log(`   - 存在 ${total - pass} 个失败项`);
}
console.log('=' .repeat(60));
