import { test } from 'node:test';
import assert from 'node:assert/strict';
import { classifyRules } from '../src/classify.js';
import { fixtures, KENH, toEvents, testConfig } from './helpers.js';

const cfg = testConfig();

for (const kenh of KENH) {
  test(`fixtures ${kenh}: chuẩn hóa đúng kênh và phân loại đúng nhãn`, () => {
    const list = fixtures(kenh);
    assert.ok(list.length >= 6);
    const labels = new Set();
    for (const fx of list) {
      const evs = toEvents(kenh, fx.payload, cfg);
      assert.equal(evs.length, 1, fx.ten);
      assert.equal(evs[0].channel, kenh);
      assert.ok(evs[0].id && evs[0].text);
      const r = classifyRules(evs[0].text);
      if (fx.spam) assert.equal(r.la_spam, true, fx.ten);
      else { assert.equal(r.nhan, fx.nhan_mong_doi, fx.ten); assert.equal(r.la_spam, false, fx.ten); labels.add(r.nhan); }
    }
    assert.deepEqual([...labels].sort(), ['dat_lich_tu_van', 'hoi_demo', 'hoi_gia', 'khac', 'khieu_nai']);
  });
}

test('bỏ qua tin echo, bình luận của chính Page, sự kiện Zalo không phải văn bản', () => {
  const [echo, self, img] = fixtures('bo-qua');
  assert.equal(toEvents('messenger', echo.payload, cfg).length, 0);
  assert.equal(toEvents('facebook_comment', self.payload, cfg).length, 0);
  assert.equal(toEvents('zalo', img.payload, cfg).length, 0);
});

test('khiếu nại và yêu cầu báo giá riêng luôn cần người thật', () => {
  assert.equal(classifyRules('Tôi muốn khiếu nại').can_nguoi_that, true);
  assert.equal(classifyRules('Cho mình xin báo giá riêng cho dự án 20 trang').can_nguoi_that, true);
  assert.equal(classifyRules('Giảm giá thêm được không ad').can_nguoi_that, true);
  assert.equal(classifyRules('Website giá bao nhiêu').can_nguoi_that, false);
});
