import { test } from 'node:test';
import assert from 'node:assert/strict';
import { signMeta, verifyMeta, signZalo, verifyZalo } from '../src/verify.js';

test('Meta: chữ ký đúng được chấp nhận, sai/thiếu bị từ chối', () => {
  const body = Buffer.from('{"object":"page"}');
  const sig = signMeta(body, 'bi-mat-thu');
  assert.equal(verifyMeta(body, sig, 'bi-mat-thu'), true);
  assert.equal(verifyMeta(body, sig, 'bi-mat-khac'), false);
  assert.equal(verifyMeta(Buffer.from('{"object":"page","x":1}'), sig, 'bi-mat-thu'), false);
  assert.equal(verifyMeta(body, undefined, 'bi-mat-thu'), false);
  assert.equal(verifyMeta(body, sig, ''), false);
});

test('Zalo: chữ ký mac=sha256(appId+body+timestamp+secret)', () => {
  const body = JSON.stringify({ event_name: 'user_send_text', timestamp: '1763452800000' });
  const sig = signZalo(body, '1763452800000', 'app1', 'secret1');
  assert.equal(verifyZalo(body, sig, 'app1', 'secret1'), true);
  assert.equal(verifyZalo(body, sig.replace('mac=', ''), 'app1', 'secret1'), true);
  assert.equal(verifyZalo(body, sig, 'app1', 'secret2'), false);
  assert.equal(verifyZalo(body, sig, '', ''), false);
});
