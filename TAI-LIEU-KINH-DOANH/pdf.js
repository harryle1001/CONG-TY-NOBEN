// node pdf.js a.html b.html …  → a.pdf b.pdf (A4, in nền)
const { chromium } = require('playwright');
(async () => {
  const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
  const br = await chromium.launch(proxy ? { proxy: { server: proxy } } : {});
  const ctx = await br.newContext({ ignoreHTTPSErrors: true });
  for (const f of process.argv.slice(2)) {
    const pg = await ctx.newPage();
    await pg.goto('file://' + require('path').resolve(f), { waitUntil: 'networkidle', timeout: 120000 });
    await pg.evaluate(() => document.fonts.ready);
    const fonts = await pg.evaluate(() => [...new Set([...document.fonts].filter(x => x.status === 'loaded').map(x => x.family))]);
    await pg.emulateMedia({ media: 'print' });
    await pg.pdf({ path: f.replace(/\.html$/, '.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true });
    console.log(f, 'fonts:', fonts.join(', '));
    await pg.close();
  }
  await br.close();
})();
