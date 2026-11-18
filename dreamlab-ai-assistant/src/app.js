// Lắp ráp các thành phần từ cấu hình.
import path from 'node:path';
import { Deduper } from './dedupe.js';
import { RateLimiter } from './ratelimit.js';
import { createLeadSink } from './sinks.js';
import { createSenders } from './senders.js';
import { createAssistant } from './pipeline.js';
import { loadKnowledge, allowedPrices } from './knowledge.js';

export async function createClaudeClient(cfg) {
  if (!cfg.anthropicKeySet) return null;
  const { default: Anthropic } = await import('@anthropic-ai/sdk');
  return new Anthropic(); // đọc ANTHROPIC_API_KEY từ biến môi trường
}

export async function buildApp(cfg, overrides = {}) {
  const log = overrides.log || ((...a) => console.log('[tro-ly]', ...a));
  const knowledge = overrides.knowledge ?? loadKnowledge();
  const client = 'client' in overrides ? overrides.client : await createClaudeClient(cfg);
  const assistant = createAssistant({
    cfg,
    deduper: overrides.deduper || new Deduper({ ttlMs: cfg.dedupeTtlMs, file: path.join(cfg.dataDir, 'da-xu-ly.json') }),
    limiter: overrides.limiter || new RateLimiter(cfg.rate),
    sink: overrides.sink || createLeadSink(cfg, { log }),
    senders: overrides.senders || createSenders(cfg),
    client, knowledge, allowed: allowedPrices(knowledge), log,
  });
  return { assistant, client, log };
}
