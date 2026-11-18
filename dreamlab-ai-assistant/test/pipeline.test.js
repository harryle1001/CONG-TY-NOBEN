import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { buildApp } from '../src/app.js';
import { createSenders, DryRunError } from '../src/senders.js';
import { Deduper } from '../src/dedupe.js';
import { RateLimiter } from '../src/ratelimit.js';
import { getConfig } from '../src/config.js';
import { fixtures, KENH, toEvents, testConfig, fakeClaude, spySenders } from './helpers.js';

const quiet = () => {};
const ev = (kenh, i = 0) => toEvents(kenh, fixtures(kenh)[i].payload, testConfig())[0];

test('DRY_RUN mặc định là true; chỉ "false" mới tắt', () => {
  assert.equal(getConfig({}).dryRun, true);
  assert.equal(getConfig({ DRY_RUN: '' }).dryRun, true);
  assert.equal(getConfig({ DRY_RUN: 'true' }).dryRun, true);
  assert.equal(getConfig({ DRY_RUN: 'false' }).dryRun, false);
});

test('chế độ nháp: không gửi gì ra ngoài, ghi nháp + CSV cho mọi fixture', async () => {
  const cfg = testConfig();
  const senders = spySenders();
  const { assistant } = await buildApp(cfg, { client: null, senders, log: quiet });
  let n = 0;
  for (const kenh of KENH) for (const fx of fixtures(kenh)) {
    const r = await assistant.handle(toEvents(kenh, fx.payload, cfg)[0]);
    if (fx.spam) assert.equal(r.trang_thai, 'bo_qua_spam', fx.ten);
    else { assert.match(r.trang_thai, /^nhap_cho_duyet/, fx.ten); assert.equal(r.quyet_dinh.nhan, fx.nhan_mong_doi, fx.ten); n++; }
  }
  assert.equal(senders.sent.length, 0);
  const csv = fs.readFileSync(path.join(cfg.dataDir, 'khach-tiem-nang.csv'), 'utf8');
  assert.equal((csv.match(/^\d{4}-\d{2}-\d{2}T/gm) || []).length, n); // mỗi khách một dòng
  assert.match(csv, /^\uFEFFthoi_gian,ten,kenh,noi_dung,nhan,trang_thai/);
  assert.ok(fs.readFileSync(path.join(cfg.dataDir, 'nhap-tra-loi.jsonl'), 'utf8').includes('du_kien_gui'));
});

test('bộ gửi thật tự chặn khi DRY_RUN=true', async () => {
  let called = false;
  const s = createSenders(testConfig(), { fetchImpl: async () => { called = true; } });
  await assert.rejects(() => s.sendMessage(ev('messenger'), 'x'), DryRunError);
  await assert.rejects(() => s.replyComment(ev('facebook_comment'), 'x'), DryRunError);
  await assert.rejects(() => s.sendMessage(ev('zalo'), 'x'), DryRunError);
  assert.equal(called, false);
});

test('bình luận công khai: trả lời ngắn + nhắn riêng; tin nhắn: chỉ trả lời riêng (DRY_RUN=false với bộ gửi giả)', async () => {
  const cfg = { ...testConfig(), dryRun: false };
  const senders = spySenders();
  const { assistant } = await buildApp(cfg, { client: null, senders, log: quiet });
  const r1 = await assistant.handle(ev('facebook_comment', 0));
  assert.equal(r1.trang_thai, 'da_tra_loi');
  assert.deepEqual(senders.sent.map((x) => x.loai), ['cong_khai', 'rieng']);
  assert.ok(senders.sent[0].text.length < 220 && !/\d{3}\.\d{3}/.test(senders.sent[0].text), 'công khai không nêu giá');
  await assistant.handle(ev('zalo', 0));
  assert.equal(senders.sent.at(-1).loai, 'tin_nhan');
});

test('chống trùng: cùng một sự kiện chỉ xử lý một lần', async () => {
  const cfg = testConfig();
  const { assistant } = await buildApp(cfg, { client: null, senders: spySenders(), log: quiet });
  const e = ev('messenger');
  assert.match((await assistant.handle(e)).trang_thai, /nhap_cho_duyet/);
  assert.equal((await assistant.handle(e)).trang_thai, 'trung_lap');
});

test('chống trùng bền qua khởi động lại (lưu file)', () => {
  const cfg = testConfig();
  const f = path.join(cfg.dataDir, 'da-xu-ly.json');
  assert.equal(new Deduper({ file: f }).firstTime('a'), true);
  assert.equal(new Deduper({ file: f }).firstTime('a'), false);
});

test('giới hạn tần suất theo người gửi', async () => {
  const cfg = testConfig();
  const { assistant } = await buildApp(cfg, { client: null, senders: spySenders(), log: quiet, limiter: new RateLimiter({ perSenderPerMinute: 2, globalPerMinute: 100 }) });
  const base = ev('messenger');
  const res = [];
  for (let i = 0; i < 3; i++) res.push((await assistant.handle({ ...base, id: `x${i}` })).trang_thai);
  assert.equal(res[2], 'gioi_han');
});

test('Claude: gọi đúng model, JSON schema, có tri thức; khiếu nại bị ép chuyển người thật', async () => {
  const cfg = testConfig();
  const client = fakeClaude({ nhan: 'khac', la_spam: false, can_nguoi_that: false, ly_do_chuyen: '', ten_khach: '', tra_loi_cong_khai: '', tin_nhan_rieng: 'Dream Labs xin lỗi bạn.' });
  const { assistant } = await buildApp(cfg, { client, senders: spySenders(), log: quiet });
  const r = await assistant.handle(ev('messenger', 3)); // khiếu nại
  const p = client.calls[0];
  assert.equal(p.model, 'claude-opus-5-5');
  assert.equal(p.output_config.format.type, 'json_schema');
  assert.match(p.system[0].text, /8\.000\.000đ/);
  assert.equal(r.quyet_dinh.nhan, 'khieu_nai');
  assert.equal(r.quyet_dinh.can_nguoi_that, true);
  assert.equal(r.quyet_dinh.nguon, 'claude');
});

test('Claude bịa giá / hứa thời gian → dùng câu mẫu và chuyển người thật', async () => {
  const cfg = testConfig();
  const client = fakeClaude({ nhan: 'hoi_gia', la_spam: false, can_nguoi_that: false, ly_do_chuyen: '', ten_khach: '', tra_loi_cong_khai: 'Giá chỉ 4.500.000đ, bên mình phản hồi trong 5 phút!', tin_nhan_rieng: 'Website chỉ 4.500.000đ thôi bạn.' });
  const { assistant } = await buildApp(cfg, { client, senders: spySenders(), log: quiet });
  const r = await assistant.handle(ev('facebook_comment', 0));
  assert.equal(r.quyet_dinh.can_nguoi_that, true);
  assert.ok(!r.quyet_dinh.tin_nhan_rieng.includes('4.500.000'));
  assert.ok(!r.quyet_dinh.tra_loi_cong_khai.includes('5 phút'));
  assert.match(r.quyet_dinh.ly_do_chuyen, /gia_khong_co_trong_tri_thuc/);
});

test('Claude từ chối hoặc lỗi mạng → không sập, dùng câu mẫu', async () => {
  const cfg = testConfig();
  const refused = fakeClaude(null, { stop_reason: 'refusal' });
  const a1 = (await buildApp(cfg, { client: refused, senders: spySenders(), log: quiet })).assistant;
  const r1 = await a1.handle(ev('zalo', 0));
  assert.equal(r1.quyet_dinh.can_nguoi_that, true);
  assert.ok(r1.quyet_dinh.tin_nhan_rieng.length > 0);
  const broken = { beta: { messages: { create: async () => { throw new Error('mất mạng'); } } } };
  const a2 = (await buildApp(testConfig(), { client: broken, senders: spySenders(), log: quiet })).assistant;
  const r2 = await a2.handle(ev('zalo', 1));
  assert.equal(r2.quyet_dinh.nguon, 'mau_do_loi');
});

test('spam: không trả lời, không ghi khách tiềm năng', async () => {
  const cfg = testConfig();
  const { assistant } = await buildApp(cfg, { client: null, senders: spySenders(), log: quiet });
  const list = fixtures('zalo');
  const r = await assistant.handle(toEvents('zalo', list.at(-1).payload, cfg)[0]);
  assert.equal(r.trang_thai, 'bo_qua_spam');
  assert.equal(fs.existsSync(path.join(cfg.dataDir, 'khach-tiem-nang.csv')), false);
});
