// 标准 E2E 样例模板
// 目的：证明真实前端入口可打开、真实后端可达、至少一个 AC 绑定用户动作有效。
// 端口、路径、选择器全部通过环境变量配置，禁止把本地端口或业务路径硬编码为发布证据。

const APP_BASE = process.env.APP_BASE || 'http://localhost:3000';
const API_BASE = process.env.API_BASE || 'http://localhost:8080/api/v1';
const PROXY_HEALTH_PATH = process.env.E2E_PROXY_HEALTH_PATH || '/api/v1/health';
const BACKEND_HEALTH_PATH = process.env.E2E_BACKEND_HEALTH_PATH || '/health';
const HOME_READY_SELECTOR = process.env.E2E_HOME_READY_SELECTOR || '#root, [data-testid="app-root"], main';
const EXPECT_TITLE = process.env.E2E_EXPECT_TITLE || '';
const ACTION_SELECTOR = process.env.E2E_ACTION_SELECTOR || '';
const EXPECT_TEXT = process.env.E2E_EXPECT_TEXT || '';
const CHROME_PATH = process.env.CHROME_PATH || '/usr/bin/google-chrome';
const E2E_EVIDENCE_DIR = process.env.E2E_EVIDENCE_DIR || 'logs/e2e';

// eslint-disable-next-line @typescript-eslint/no-var-requires
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

let browser: any;
let page: any;

async function fetchStatus(url: string): Promise<number> {
  const response = await fetch(url);
  return response.status;
}

async function keepScreenshot(name: string): Promise<void> {
  fs.mkdirSync(E2E_EVIDENCE_DIR, { recursive: true });
  await page.screenshot({
    path: path.join(E2E_EVIDENCE_DIR, name),
    fullPage: true,
  });
}

describe('standard delivery e2e smoke', () => {
  beforeAll(async () => {
    browser = await puppeteer.launch({
      executablePath: CHROME_PATH,
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    });
    page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
  }, 60000);

  afterAll(async () => {
    if (browser) await browser.close();
  });

  test('homepage loads from real frontend origin', async () => {
    await page.goto(APP_BASE, { waitUntil: 'networkidle0', timeout: 30000 });
    await page.waitForSelector(HOME_READY_SELECTOR, { timeout: 10000 });

    const title = await page.title();
    expect(title).toBeTruthy();
    if (EXPECT_TITLE) {
      expect(title).toContain(EXPECT_TITLE);
    }
    await keepScreenshot('home-ready.png');
  });

  test('frontend proxy reaches real backend health endpoint', async () => {
    await page.goto(APP_BASE, { waitUntil: 'domcontentloaded', timeout: 30000 });
    const status = await page.evaluate(async (path: string) => {
      const response = await fetch(path, { headers: { 'X-E2E-Mock-Policy': 'Mock API=no' } });
      return response.status;
    }, PROXY_HEALTH_PATH);

    expect([200, 204]).toContain(status);
  });

  test('direct backend health endpoint is reachable', async () => {
    const status = await fetchStatus(`${API_BASE}${BACKEND_HEALTH_PATH}`);
    expect([200, 204]).toContain(status);
  });

  test('ac-bound browser action works when configured', async () => {
    if (!ACTION_SELECTOR || !EXPECT_TEXT) {
      console.warn('SKIPPED AC action: set E2E_ACTION_SELECTOR and E2E_EXPECT_TEXT to bind this case to an AC.');
      return;
    }

    await page.goto(APP_BASE, { waitUntil: 'networkidle0', timeout: 30000 });
    await page.waitForSelector(ACTION_SELECTOR, { timeout: 10000 });
    await page.click(ACTION_SELECTOR);
    await page.waitForFunction(
      (text: string) => document.body.innerText.includes(text),
      { timeout: 10000 },
      EXPECT_TEXT,
    );
    await keepScreenshot('ac-action-result.png');
  });
});
