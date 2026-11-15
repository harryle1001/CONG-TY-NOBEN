// Chạy trên máy ở Việt Nam: node tools/csdl-recon.js
// Mục đích: lưu cấu trúc trang tra cứu CSDL Tổng cục Thủy sản để viết script tải nhãn chính xác.
// Cài: npm i playwright && npx playwright install chromium
const { chromium } = require('playwright');
const fs = require('fs');

const URL = 'http://csdl.tongcucthuysan.gov.vn/cms.nc/tracuu/sanpham';
const OUT = 'csdl-recon';

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  const calls = [];
  page.on('response', async (r) => {
    const t = r.request().resourceType();
    if (['xhr', 'fetch', 'document'].includes(t)) {
      let body = '';
      try { body = (await r.text()).slice(0, 3000); } catch {}
      calls.push({ url: r.url(), method: r.request().method(), post: r.request().postData(), status: r.status(), body });
    }
  });
  await page.goto(URL, { waitUntil: 'networkidle', timeout: 90000 });
  console.log('Trang đã mở. Hãy gõ "Noben" vào ô tìm kiếm, bấm Tìm, bấm sang trang 2, mở 1 sản phẩm xem nhãn.');
  console.log('Xong thì quay lại terminal bấm Enter.');
  await new Promise((res) => process.stdin.once('data', res));
  fs.writeFileSync(`${OUT}/page.html`, await page.content());
  fs.writeFileSync(`${OUT}/calls.json`, JSON.stringify(calls, null, 2));
  await page.screenshot({ path: `${OUT}/screen.png`, fullPage: true });
  await browser.close();
  console.log(`Đã lưu vào thư mục ${OUT}/ — gửi thư mục này cho Claude.`);
})();
