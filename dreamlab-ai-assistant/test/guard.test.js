import { test } from 'node:test';
import assert from 'node:assert/strict';
import { checkReply, fixBrand } from '../src/guard.js';
import { loadKnowledge, allowedPrices, extractMoney } from '../src/knowledge.js';
import { PRIVATE, PUBLIC } from '../src/templates.js';

const allowed = allowedPrices(loadKnowledge());

test('tri thức chứa đúng giá trên web (chưa VAT)', () => {
  for (const p of [5e6, 15e6, 40e6, 8e6, 18e6, 35e6, 3e6, 6e6, 12e6, 8e5, 2e6, 7e6]) assert.ok(allowed.has(p), String(p));
  assert.match(loadKnowledge(), /CHƯA GỒM VAT/);
});

test('đọc được nhiều cách viết tiền', () => {
  assert.deepEqual(extractMoney('từ 5.000.000đ, 18 triệu, 800k, 1,5 triệu, 3 vòng sửa, 30 phút'), [5e6, 18e6, 8e5, 15e5]);
});

test('chặn giá bịa, hứa thời gian, nội dung cấm, email', () => {
  assert.equal(checkReply('Website từ 8.000.000đ chưa VAT', { allowed }).ok, true);
  assert.match(checkReply('Website chỉ 6.500.000đ thôi', { allowed }).issues.join(), /gia_khong_co/);
  assert.match(checkReply('Website 9 triệu', { allowed }).issues.join(), /gia_khong_co/);
  assert.match(checkReply('Bên mình sẽ phản hồi trong 30 phút', { allowed }).issues.join(), /hua_thoi_gian/);
  assert.match(checkReply('Nhân viên trả lời ngay lập tức', { allowed }).issues.join(), /hua_thoi_gian/);
  assert.match(checkReply('Thiết kế theo tỷ lệ vàng', { allowed }).issues.join(), /noi_dung_cam/);
  assert.match(checkReply('Bố cục φ đẹp', { allowed }).issues.join(), /noi_dung_cam/);
  assert.match(checkReply('Gửi về abc@example.com', { allowed }).issues.join(), /co_email/);
  assert.equal(checkReply('Buổi tư vấn 30 phút miễn phí, dự án 7–10 ngày', { allowed }).ok, true);
});

test('câu mẫu đã duyệt tự qua được lớp kiểm tra', () => {
  for (const t of Object.values(PRIVATE)) assert.deepEqual(checkReply(t, { allowed, maxLen: 1200 }).issues, [], t);
  for (const t of Object.values(PUBLIC)) assert.deepEqual(checkReply(t, { allowed: new Set(), maxLen: 300 }).issues, [], t);
});

test('sửa tên thương hiệu', () => {
  assert.equal(fixBrand('Cảm ơn DreamLabs và Dreamlab'), 'Cảm ơn Dream Labs và Dream Labs');
});
