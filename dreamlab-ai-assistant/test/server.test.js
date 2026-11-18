import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from '../src/server.js';
import { buildApp } from '../src/app.js';
import { signMeta, signZalo } from '../src/verify.js';
import { fixtures, testConfig, spySenders } from './helpers.js';

async function start() {
  const cfg = testConfig({ META_APP_SECRET: 'thu-app-secret', META_VERIFY_TOKEN: 'thu-verify', ZALO_APP_ID: 'ZALO_APP_ID_GIA', ZALO_OA_SECRET_KEY: 'thu-zalo' });
  const handled = [];
  const app = await buildApp(cfg, { client: null, senders: spySenders(), log: () => {} });
  const orig = app.assistant.handle;
  app.assistant.handle = async (e) => { const r = await orig(e); handled.push(r); return r; };
  const server = createServer(cfg, app);
  await new Promise((r) => server.listen(0, r));
  return { cfg, server, handled, base: `http://127.0.0.1:${server.address().port}` };
}

test('webhook Meta: xác minh hub.challenge, từ chối chữ ký sai, nhận chữ ký đúng', async () => {
  const { server, base, handled } = await start();
  try {
    assert.equal(await (await fetch(`${base}/webhook/meta?hub.mode=subscribe&hub.verify_token=thu-verify&hub.challenge=123`)).text(), '123');
    assert.equal((await fetch(`${base}/webhook/meta?hub.mode=subscribe&hub.verify_token=sai&hub.challenge=1`)).status, 403);
    const body = JSON.stringify(fixtures('messenger')[0].payload);
    assert.equal((await fetch(`${base}/webhook/meta`, { method: 'POST', body, headers: { 'X-Hub-Signature-256': 'sha256=00' } })).status, 401);
    const ok = await fetch(`${base}/webhook/meta`, { method: 'POST', body, headers: { 'X-Hub-Signature-256': signMeta(Buffer.from(body), 'thu-app-secret') } });
    assert.equal(ok.status, 200);
    await new Promise((r) => setTimeout(r, 50));
    assert.equal(handled.length, 1);
    assert.match(handled[0].trang_thai, /nhap_cho_duyet/);
  } finally { server.close(); }
});

test('webhook Zalo: chữ ký đúng mới xử lý', async () => {
  const { server, base, handled } = await start();
  try {
    const payload = fixtures('zalo')[0].payload;
    const body = JSON.stringify(payload);
    assert.equal((await fetch(`${base}/webhook/zalo`, { method: 'POST', body, headers: { 'X-ZEvent-Signature': 'mac=00' } })).status, 401);
    const sig = signZalo(body, payload.timestamp, 'ZALO_APP_ID_GIA', 'thu-zalo');
    assert.equal((await fetch(`${base}/webhook/zalo`, { method: 'POST', body, headers: { 'X-ZEvent-Signature': sig } })).status, 200);
    await new Promise((r) => setTimeout(r, 50));
    assert.equal(handled.length, 1);
    assert.equal((await fetch(`${base}/health`)).status, 200);
  } finally { server.close(); }
});
