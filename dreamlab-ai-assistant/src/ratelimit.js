// Giới hạn tần suất: cửa sổ trượt 60 giây, theo từng người gửi và toàn hệ thống.
export class RateLimiter {
  constructor({ perSenderPerMinute = 4, globalPerMinute = 60, now = () => Date.now() } = {}) {
    this.perSender = perSenderPerMinute; this.global = globalPerMinute; this.now = now;
    this.bySender = new Map(); this.all = [];
  }
  allow(senderId) {
    const t = this.now(), win = 60_000;
    this.all = this.all.filter((x) => t - x < win);
    const list = (this.bySender.get(senderId) || []).filter((x) => t - x < win);
    if (this.all.length >= this.global) return { ok: false, reason: 'gioi_han_toan_he_thong' };
    if (list.length >= this.perSender) return { ok: false, reason: 'gioi_han_nguoi_gui' };
    list.push(t); this.all.push(t); this.bySender.set(senderId, list);
    return { ok: true };
  }
}
