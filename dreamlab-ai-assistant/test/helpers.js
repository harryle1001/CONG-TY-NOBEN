import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { ROOT, getConfig } from '../src/config.js';
import { normalizeMeta, normalizeZalo } from '../src/normalize.js';

export const tmpDir = () => fs.mkdtempSync(path.join(os.tmpdir(), 'dl-tro-ly-'));
export const fixtures = (kenh) => JSON.parse(fs.readFileSync(path.join(ROOT, 'fixtures', `${kenh}.json`), 'utf8'));
export const KENH = ['facebook_comment', 'messenger', 'instagram_comment', 'instagram_dm', 'zalo'];
export const toEvents = (kenh, payload, cfg = getConfig({})) => (kenh === 'zalo' ? normalizeZalo(payload) : normalizeMeta(payload, cfg.meta));
export const testConfig = (extra = {}) => ({ ...getConfig({ META_PAGE_ID: '100000000000001', IG_USER_ID: '178400000000001', ...extra }), dataDir: tmpDir() });

// Client Claude giả: trả JSON cố định, ghi lại tham số gọi.
export function fakeClaude(reply, { stop_reason = 'end_turn' } = {}) {
  const calls = [];
  return {
    calls,
    beta: { messages: { create: async (params) => { calls.push(params); return { stop_reason, content: stop_reason === 'refusal' ? [] : [{ type: 'text', text: JSON.stringify(typeof reply === 'function' ? reply(params) : reply) }] }; } } },
  };
}

// Bộ gửi giả: ghi lại mọi lần gửi.
export function spySenders() {
  const sent = [];
  const rec = (loai) => async (event, text) => { sent.push({ loai, id: event.id, text }); return { ok: true }; };
  return { sent, replyComment: rec('cong_khai'), privateReply: rec('rieng'), sendMessage: rec('tin_nhan') };
}
