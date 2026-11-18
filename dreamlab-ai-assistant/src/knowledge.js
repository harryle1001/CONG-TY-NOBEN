// Nạp cơ sở tri thức đã duyệt trong knowledge/*.md
import fs from 'node:fs';
import path from 'node:path';
import { ROOT } from './config.js';

export function loadKnowledge(dir = path.join(ROOT, 'knowledge')) {
  return fs.readdirSync(dir).filter((f) => f.endsWith('.md')).sort()
    .map((f) => fs.readFileSync(path.join(dir, f), 'utf8').trim()).join('\n\n---\n\n');
}

// Đổi các cách viết tiền (5.000.000đ, 5 triệu, 5tr, 800k, 1,5 triệu) sang số đồng.
export function extractMoney(text) {
  const out = [];
  const s = String(text);
  const re = /(\d{1,3}(?:[.,\s]\d{3})+|\d+(?:[.,]\d+)?)\s*(đ|₫|vnd|vnđ|đồng|triệu|tr\b|củ|k\b|nghìn|ngàn|tỷ)?/gi;
  for (const m of s.matchAll(re)) {
    const raw = m[1]; const unit = (m[2] || '').toLowerCase();
    const grouped = /[.,\s]\d{3}$/.test(raw) && /^\d{1,3}([.,\s]\d{3})+$/.test(raw);
    let n = grouped ? Number(raw.replace(/[.,\s]/g, '')) : Number(raw.replace(',', '.'));
    if (['triệu', 'tr', 'củ'].includes(unit)) n *= 1e6;
    else if (['k', 'nghìn', 'ngàn'].includes(unit)) n *= 1e3;
    else if (unit === 'tỷ') n *= 1e9;
    else if (!unit && !grouped) continue; // số trơn (vd "3 vòng", "30 phút") không phải tiền
    if (n >= 100000) out.push(Math.round(n));
  }
  return out;
}

export function allowedPrices(knowledgeText) {
  return new Set(extractMoney(knowledgeText));
}
