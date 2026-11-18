// Lớp kiểm tra câu trả lời trước khi lưu/gửi. Vi phạm → không gửi câu của AI, dùng mẫu an toàn + chuyển người thật.
import { extractMoney } from './knowledge.js';

const FORBIDDEN = [/tỷ lệ vàng|tỉ lệ vàng|ty le vang|golden ratio/i, /φ|Φ/, /\b1[.,]618/];
const TIME_PROMISE = [
  /(trong|sau|tối đa|chậm nhất)\s*(vòng\s*)?\d+\s*(phút|giờ|tiếng|h)\b/i,
  /(phản hồi|trả lời|liên hệ|gọi lại)\s*(bạn\s*)?(ngay|liền|lập tức|ngay lập tức)/i,
  /\b24\s*\/\s*7\b.*(nhân viên|người)/i, /\b(24h|24 giờ)\b/i,
];
const EMAIL = /[\w.+-]+@[\w-]+\.[\w.]+/;

export function fixBrand(s) {
  return String(s || '').replace(/\bDream\s*Lab(s)?\b|\bDreamlab(s)?\b|\bDREAMLABS\b/g, 'Dream Labs');
}

export function checkReply(text, { allowed, maxLen = Infinity } = {}) {
  const issues = [];
  const s = String(text || '');
  if (FORBIDDEN.some((r) => r.test(s))) issues.push('noi_dung_cam');
  if (TIME_PROMISE.some((r) => r.test(s))) issues.push('hua_thoi_gian_phan_hoi');
  if (EMAIL.test(s)) issues.push('co_email');
  if (allowed) {
    const bad = extractMoney(s).filter((n) => !allowed.has(n));
    if (bad.length) issues.push('gia_khong_co_trong_tri_thuc:' + bad.join(','));
  }
  if (s.length > maxLen) issues.push('qua_dai');
  return { ok: issues.length === 0, issues };
}
