// Máy chủ webhook (Node.js thuần, không framework).
//   GET  /webhook/meta  — Meta xác minh webhook (hub.challenge)
//   POST /webhook/meta  — sự kiện Facebook Page / Messenger / Instagram
//   POST /webhook/zalo  — sự kiện Zalo OA
//   GET  /health
import http from 'node:http';
import { pathToFileURL } from 'node:url';
import { getConfig, loadDotEnv } from './config.js';
import { verifyMeta, verifyZalo } from './verify.js';
import { normalizeMeta, normalizeZalo } from './normalize.js';
import { buildApp } from './app.js';

const MAX_BODY = 1024 * 1024;

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = []; let size = 0;
    req.on('data', (c) => { size += c.length; if (size > MAX_BODY) { reject(new Error('too_large')); req.destroy(); } else chunks.push(c); });
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

export function createServer(cfg, app) {
  const { assistant, log } = app;
  const processAll = (events) => {
    // Trả 200 ngay cho nền tảng, xử lý phía sau để tránh bị gửi lại do chậm.
    setImmediate(async () => {
      for (const ev of events) {
        try { const r = await assistant.handle(ev); log(ev.channel, ev.id, '→', r.trang_thai); } catch (e) { log('Lỗi xử lý', ev.id, e.message); }
      }
    });
  };

  return http.createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost');
    const send = (code, body = '', type = 'text/plain; charset=utf-8') => { res.writeHead(code, { 'Content-Type': type }); res.end(body); };
    try {
      if (req.method === 'GET' && url.pathname === '/health') return send(200, JSON.stringify({ ok: true, dryRun: cfg.dryRun }), 'application/json');

      if (req.method === 'GET' && url.pathname === '/webhook/meta') {
        const ok = url.searchParams.get('hub.mode') === 'subscribe' && cfg.meta.verifyToken && url.searchParams.get('hub.verify_token') === cfg.meta.verifyToken;
        return ok ? send(200, url.searchParams.get('hub.challenge') || '') : send(403, 'forbidden');
      }

      if (req.method === 'POST' && url.pathname === '/webhook/meta') {
        const raw = await readBody(req);
        if (!verifyMeta(raw, req.headers['x-hub-signature-256'], cfg.meta.appSecret)) return send(401, 'bad signature');
        const events = normalizeMeta(JSON.parse(raw.toString('utf8')), cfg.meta);
        send(200, 'EVENT_RECEIVED');
        return processAll(events);
      }

      if (req.method === 'POST' && url.pathname === '/webhook/zalo') {
        const raw = await readBody(req);
        if (!verifyZalo(raw.toString('utf8'), req.headers['x-zevent-signature'], cfg.zalo.appId, cfg.zalo.oaSecretKey)) return send(401, 'bad signature');
        const events = normalizeZalo(JSON.parse(raw.toString('utf8')));
        send(200, 'ok');
        return processAll(events);
      }
      return send(404, 'not found');
    } catch (e) {
      if (!res.headersSent) send(e.message === 'too_large' ? 413 : 400, 'bad request');
    }
  });
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  loadDotEnv();
  const cfg = getConfig();
  const app = await buildApp(cfg);
  createServer(cfg, app).listen(cfg.port, () => {
    console.log(`Trợ lý Dream Labs chạy ở cổng ${cfg.port} — DRY_RUN=${cfg.dryRun ? 'true (NHÁP, không gửi gì ra ngoài)' : 'false (GỬI THẬT)'} — bộ não: ${app.client ? cfg.model : 'luật + câu mẫu (chưa có ANTHROPIC_API_KEY)'}`);
  });
}
