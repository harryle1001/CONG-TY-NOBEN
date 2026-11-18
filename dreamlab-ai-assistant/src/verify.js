// Xác thực chữ ký webhook.
import crypto from 'node:crypto';

function safeEqualHex(a, b) {
  const ba = Buffer.from(String(a), 'utf8');
  const bb = Buffer.from(String(b), 'utf8');
  return ba.length === bb.length && crypto.timingSafeEqual(ba, bb);
}

// Meta (Facebook Page, Messenger, Instagram): header X-Hub-Signature-256 = "sha256=" + HMAC-SHA256(rawBody, APP_SECRET)
export function signMeta(rawBody, appSecret) {
  return 'sha256=' + crypto.createHmac('sha256', appSecret).update(rawBody).digest('hex');
}
export function verifyMeta(rawBody, header, appSecret) {
  if (!appSecret || !header) return false;
  return safeEqualHex(signMeta(rawBody, appSecret), header.trim());
}

// Zalo OA: header X-ZEvent-Signature = "mac=" + SHA256(app_id + rawBody + timestamp + OA_SECRET_KEY)
// (timestamp lấy từ trường "timestamp" trong body). Đối chiếu lại tài liệu Zalo OA mới nhất khi bật thật.
export function signZalo(rawBody, timestamp, appId, oaSecretKey) {
  return 'mac=' + crypto.createHash('sha256').update(`${appId}${rawBody}${timestamp}${oaSecretKey}`).digest('hex');
}
export function verifyZalo(rawBody, header, appId, oaSecretKey) {
  if (!appId || !oaSecretKey || !header) return false;
  let ts = '';
  try { ts = String(JSON.parse(rawBody).timestamp ?? ''); } catch { return false; }
  const expected = signZalo(rawBody, ts, appId, oaSecretKey);
  const got = header.trim().startsWith('mac=') ? header.trim() : 'mac=' + header.trim();
  return safeEqualHex(expected, got);
}
