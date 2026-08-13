// Generic HTML slide-deck -> PDF exporter for emg-o-portal.
//
// Usage:
//   node generate-pdf.js <path-to-deck.html> [output.pdf]
//
// Renders every .slide in the deck (the same @media print rule the deck
// already ships for browser "print to PDF") via headless Chromium and
// writes one PDF page per slide at the deck's native 1280x720 stage size.
// Default output: <deck-dir>/assets/<deck-basename>.pdf
//
// Requires the deck to expose the standard #stage / #stage-wrap structure
// used by every EMG-O presentation deck (product-concepts.html, e2e-mode*.html, etc).

const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('/opt/docker/mission-control/node_modules/playwright');

const CHROMIUM_PATH = '/root/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome';

async function generatePdf(htmlPath, outPath) {
  const resolvedHtml = path.resolve(htmlPath);
  const resolvedOut = outPath
    ? path.resolve(outPath)
    : path.join(path.dirname(resolvedHtml), 'assets', path.basename(resolvedHtml, '.html') + '.pdf');

  const browser = await chromium.launch({ executablePath: CHROMIUM_PATH });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
    await page.goto(pathToFileURL(resolvedHtml).href);
    await page.waitForTimeout(300);

    // Neutralize the on-screen "fit stage to window" scale/centering so every
    // slide lays out at its true 1280x720 size regardless of viewport.
    await page.evaluate(() => {
      const stage = document.getElementById('stage');
      if (stage) stage.style.transform = 'none';
      const wrap = document.getElementById('stage-wrap');
      if (wrap) {
        wrap.style.width = 'auto';
        wrap.style.height = 'auto';
        wrap.style.overflow = 'visible';
      }
    });

    await page.emulateMedia({ media: 'print' });
    await page.pdf({
      path: resolvedOut,
      width: '1280px',
      height: '720px',
      printBackground: true,
      margin: { top: '0', bottom: '0', left: '0', right: '0' },
    });
    console.log('PDF written:', resolvedOut);
  } finally {
    await browser.close();
  }
}

if (require.main === module) {
  const [, , htmlArg, outArg] = process.argv;
  if (!htmlArg) {
    console.error('Usage: node generate-pdf.js <path-to-deck.html> [output.pdf]');
    process.exit(1);
  }
  generatePdf(htmlArg, outArg).catch((err) => {
    console.error(err);
    process.exit(1);
  });
}

module.exports = { generatePdf };
