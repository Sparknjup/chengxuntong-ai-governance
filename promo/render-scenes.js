const { chromium } = require('C:/Users/31066/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const root = path.resolve(__dirname);
  const out = path.join(root, 'frames');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    args: ['--disable-gpu', '--font-render-hinting=none']
  });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const base = 'file:///' + path.join(root, 'scene-board.html').replace(/\\/g, '/');
  for (let scene = 1; scene <= 13; scene += 1) {
    await page.goto(`${base}?scene=${scene}`, { waitUntil: 'load' });
    await page.screenshot({ path: path.join(out, `scene-${String(scene).padStart(2, '0')}.png`) });
  }
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
