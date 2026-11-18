// Ghi khách tiềm năng: Google Sheets (service account) hoặc file CSV khi chưa có Sheets.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

export const COLUMNS = ['thoi_gian', 'ten', 'kenh', 'noi_dung', 'nhan', 'trang_thai', 'can_nguoi_that', 'ly_do_chuyen', 'tra_loi_cong_khai', 'tin_nhan_rieng', 'ma_su_kien', 'nguon'];

const csvCell = (v) => {
  let s = String(v ?? '');
  if (/^[=+\-@]/.test(s)) s = "'" + s; // chống chèn công thức khi mở bằng Excel/Sheets
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
export const toRow = (rec) => COLUMNS.map((c) => rec[c] ?? '');

export function csvSink(file) {
  return {
    name: 'csv',
    async append(rec) {
      fs.mkdirSync(path.dirname(file), { recursive: true });
      if (!fs.existsSync(file)) fs.writeFileSync(file, '﻿' + COLUMNS.join(',') + '\n');
      fs.appendFileSync(file, toRow(rec).map(csvCell).join(',') + '\n');
    },
  };
}

const b64url = (b) => Buffer.from(b).toString('base64').replace(/=+$/, '').replace(/\+/g, '-').replace(/\//g, '_');

export function sheetsSink(cfg, { fetchImpl = globalThis.fetch, now = () => Date.now() } = {}) {
  let token = null; let exp = 0;
  async function getToken() {
    if (token && now() < exp - 60_000) return token;
    const iat = Math.floor(now() / 1000);
    const head = b64url(JSON.stringify({ alg: 'RS256', typ: 'JWT' }));
    const claim = b64url(JSON.stringify({
      iss: cfg.clientEmail, scope: 'https://www.googleapis.com/auth/spreadsheets',
      aud: 'https://oauth2.googleapis.com/token', iat, exp: iat + 3600,
    }));
    const sig = b64url(crypto.sign('RSA-SHA256', Buffer.from(`${head}.${claim}`), cfg.privateKey));
    const res = await fetchImpl('https://oauth2.googleapis.com/token', {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer', assertion: `${head}.${claim}.${sig}` }),
    });
    if (!res.ok) throw new Error(`Google token ${res.status}: ${await res.text()}`);
    const j = await res.json(); token = j.access_token; exp = now() + (j.expires_in || 3600) * 1000;
    return token;
  }
  return {
    name: 'google_sheets',
    async append(rec) {
      const range = encodeURIComponent(`${cfg.sheetName}!A1`);
      const url = `https://sheets.googleapis.com/v4/spreadsheets/${cfg.spreadsheetId}/values/${range}:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS`;
      const res = await fetchImpl(url, {
        method: 'POST', headers: { Authorization: `Bearer ${await getToken()}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ values: [toRow(rec)] }),
      });
      if (!res.ok) throw new Error(`Sheets ${res.status}: ${await res.text()}`);
    },
  };
}

// Chọn nơi ghi: có đủ biến Sheets → Sheets (lỗi thì ghi dự phòng CSV); thiếu → CSV.
export function createLeadSink(cfg, opts = {}) {
  const csv = csvSink(path.join(cfg.dataDir, 'khach-tiem-nang.csv'));
  const s = cfg.sheets;
  if (!(s.spreadsheetId && s.clientEmail && s.privateKey)) return csv;
  const sheets = sheetsSink(s, opts);
  return {
    name: 'google_sheets+csv_du_phong',
    async append(rec) {
      try { await sheets.append(rec); } catch (e) { (opts.log || console.error)('Ghi Sheets lỗi, ghi CSV dự phòng:', e.message); await csv.append(rec); }
    },
  };
}
