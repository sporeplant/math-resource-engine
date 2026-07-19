const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const htmlPath = path.resolve('C:/MRE/outputs/reviews/review-01-02_课件.html');
  const assetsDir = path.resolve('C:/MRE/outputs/reviews/assets');
  fs.mkdirSync(assetsDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1960, height: 1120 }, deviceScaleFactor: 2 });

  console.log('[加载]', htmlPath);
  await page.goto('file:///' + htmlPath.replace(/\\/g, '/'), { waitUntil: 'domcontentloaded', timeout: 30000 });

  // 等待 MathJax
  console.log('[等待] MathJax...');
  try {
    await page.waitForFunction('() => window.MathJax && typeof MathJax.typesetPromise === "function"', { timeout: 20000 });
    await page.evaluate('MathJax.typesetPromise()');
    await page.waitForTimeout(1000);
  } catch (e) { console.log('  MathJax 超时:', e.message); }

  // 等待图片
  console.log('[等待] 图片加载...');
  try { await page.waitForLoadState('networkidle', { timeout: 30000 }); } catch (e) {}
  await page.waitForTimeout(500);

  // 重置样式
  await page.evaluate(() => {
    const nav = document.querySelector('.nav-dots');
    if (nav) nav.style.display = 'none';
    document.body.style.padding = '0';
    document.body.style.gap = '0';
    document.body.style.background = '#fff';
    document.querySelectorAll('.slide').forEach(s => {
      s.style.transform = 'none';
      s.style.marginBottom = '0';
      s.style.boxShadow = 'none';
      s.style.display = 'none';
    });
  });

  const slideCount = await page.evaluate('document.querySelectorAll(".slide").length');
  console.log(`[幻灯片] 共 ${slideCount} 张\n`);

  for (let i = 0; i < slideCount; i++) {
    const slideId = `s${i}`;
    await page.evaluate((id) => {
      document.querySelectorAll('.slide').forEach(s => s.style.display = 'none');
      const cur = document.querySelector('#' + id);
      if (cur) cur.style.display = 'block';
    }, slideId);
    await page.waitForTimeout(300);

    const filename = `slide_${String(i + 1).padStart(2, '0')}.png`;
    const filepath = path.join(assetsDir, filename);

    try {
      const el = await page.$('#' + slideId);
      if (el) {
        await el.screenshot({ path: filepath, type: 'png' });
        const stat = fs.statSync(filepath);
        console.log(`  [${String(i + 1).padStart(2)}/${slideCount}] ${filename}  (${Math.round(stat.size / 1024)} KB)`);
      } else {
        console.log(`  [${String(i + 1).padStart(2)}/${slideCount}] 跳过: #${slideId} 未找到`);
      }
    } catch (e) {
      console.log(`  [${String(i + 1).padStart(2)}/${slideCount}] 失败: ${e.message}`);
      await page.screenshot({ path: filepath, type: 'png' });
    }
  }

  await browser.close();
  console.log(`\n[完成] ${slideCount} 张截图 → ${assetsDir}`);
})();
