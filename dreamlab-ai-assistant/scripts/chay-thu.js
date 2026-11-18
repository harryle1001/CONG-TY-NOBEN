// Chạy thử toàn bộ fixtures qua trợ lý ở CHẾ ĐỘ NHÁP và in câu trả lời dự kiến.
//   npm run chay-thu                 → dùng Claude nếu có ANTHROPIC_API_KEY, không thì dùng luật + câu mẫu
//   npm run chay-thu -- --offline    → luôn dùng luật + câu mẫu (không gọi mạng)
//   npm run chay-thu -- zalo         → chỉ chạy một kênh
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, getConfig, loadDotEnv } from '../src/config.js';
import { normalizeMeta, normalizeZalo } from '../src/normalize.js';
import { buildApp } from '../src/app.js';
import { Deduper } from '../src/dedupe.js';
import { RateLimiter } from '../src/ratelimit.js';
import { csvSink } from '../src/sinks.js';

loadDotEnv();
const args = process.argv.slice(2);
const offline = args.includes('--offline');
const only = args.find((a) => !a.startsWith('--'));

const cfg = { ...getConfig(), dryRun: true, dataDir: path.join(ROOT, 'data', 'chay-thu') }; // luôn nháp
fs.rmSync(cfg.dataDir, { recursive: true, force: true });
const app = await buildApp(cfg, {
  ...(offline ? { client: null } : {}),
  deduper: new Deduper(), limiter: new RateLimiter({ perSenderPerMinute: 1e6, globalPerMinute: 1e6 }),
  sink: csvSink(path.join(cfg.dataDir, 'khach-tiem-nang.csv')), log: () => {},
});
console.log(`Bộ não: ${app.client ? cfg.model : 'luật + câu mẫu (offline)'} · DRY_RUN=true\n`);

const files = fs.readdirSync(path.join(ROOT, 'fixtures')).filter((f) => f.endsWith('.json') && f !== 'bo-qua.json' && (!only || f.startsWith(only)));
let dung = 0, tong = 0;
for (const f of files) {
  const kenh = f.replace('.json', '');
  for (const fx of JSON.parse(fs.readFileSync(path.join(ROOT, 'fixtures', f), 'utf8'))) {
    const events = kenh === 'zalo' ? normalizeZalo(fx.payload) : normalizeMeta(fx.payload, cfg.meta);
    for (const ev of events) {
      const r = await app.assistant.handle(ev);
      const d = r.quyet_dinh || {};
      const ok = fx.spam ? r.trang_thai === 'bo_qua_spam' : d.nhan === fx.nhan_mong_doi;
      tong++; if (ok) dung++;
      console.log(`━━ ${fx.ten} ${ok ? '✓' : '✗ (mong đợi ' + (fx.spam ? 'spam' : fx.nhan_mong_doi) + ')'}`);
      console.log(`   Khách: ${ev.text}`);
      console.log(`   Nhãn: ${d.nhan} · Trạng thái: ${r.trang_thai}${d.can_nguoi_that ? ' · CHUYỂN NGƯỜI THẬT: ' + d.ly_do_chuyen : ''}`);
      if (d.tra_loi_cong_khai) console.log(`   ↳ Trả lời công khai: ${d.tra_loi_cong_khai}`);
      if (d.tin_nhan_rieng) console.log(`   ↳ Tin nhắn: ${d.tin_nhan_rieng.replace(/\n/g, '\n               ')}`);
      console.log();
    }
  }
}
console.log(`Khớp nhãn mong đợi: ${dung}/${tong}. Bản nháp: ${path.relative(ROOT, cfg.dataDir)}/nhap-tra-loi.jsonl và khach-tiem-nang.csv`);
