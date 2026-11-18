// Đọc cấu hình từ biến môi trường. KHÔNG ghi khóa/mật khẩu vào code.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// Nạp .env (nếu có) — trình đọc tối giản, không cần thư viện.
export function loadDotEnv(file = path.join(ROOT, '.env')) {
  if (!fs.existsSync(file)) return;
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (!m || line.trim().startsWith('#')) continue;
    let v = m[2];
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
    if (process.env[m[1]] === undefined) process.env[m[1]] = v;
  }
}

const bool = (v, def) => (v === undefined || v === '' ? def : !/^(0|false|no|off)$/i.test(String(v).trim()));
const int = (v, def) => (Number.isFinite(parseInt(v, 10)) ? parseInt(v, 10) : def);

export function getConfig(env = process.env) {
  return {
    port: int(env.PORT, 8787),
    // MẶC ĐỊNH NHÁP: chỉ khi chủ studio tự đặt DRY_RUN=false mới gửi thật.
    dryRun: bool(env.DRY_RUN, true),
    model: env.CLAUDE_MODEL || 'claude-opus-5-5',
    anthropicKeySet: Boolean(env.ANTHROPIC_API_KEY),
    meta: {
      appSecret: env.META_APP_SECRET || '',
      verifyToken: env.META_VERIFY_TOKEN || '',
      pageId: env.META_PAGE_ID || '',
      pageAccessToken: env.META_PAGE_ACCESS_TOKEN || '',
      igUserId: env.IG_USER_ID || '',
      graphVersion: env.META_GRAPH_VERSION || 'v21.0',
    },
    zalo: {
      appId: env.ZALO_APP_ID || '',
      oaSecretKey: env.ZALO_OA_SECRET_KEY || '',
      oaAccessToken: env.ZALO_OA_ACCESS_TOKEN || '',
      oaId: env.ZALO_OA_ID || '',
    },
    sheets: {
      spreadsheetId: env.GOOGLE_SHEETS_ID || '',
      sheetName: env.GOOGLE_SHEETS_TAB || 'KhachTiemNang',
      clientEmail: env.GOOGLE_SA_CLIENT_EMAIL || '',
      privateKey: (env.GOOGLE_SA_PRIVATE_KEY || '').replace(/\\n/g, '\n'),
    },
    dataDir: env.DATA_DIR || path.join(ROOT, 'data'),
    rate: {
      perSenderPerMinute: int(env.RATE_PER_SENDER_PER_MIN, 4),
      globalPerMinute: int(env.RATE_GLOBAL_PER_MIN, 60),
    },
    dedupeTtlMs: int(env.DEDUPE_TTL_HOURS, 72) * 3600 * 1000,
  };
}
