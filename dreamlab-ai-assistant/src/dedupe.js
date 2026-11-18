// Chống trả lời trùng: nhớ id sự kiện đã xử lý (Meta/Zalo có thể gửi lại cùng một sự kiện).
import fs from 'node:fs';
import path from 'node:path';

export class Deduper {
  constructor({ ttlMs = 72 * 3600 * 1000, file = null, now = () => Date.now() } = {}) {
    this.ttlMs = ttlMs; this.file = file; this.now = now; this.seen = new Map();
    if (file && fs.existsSync(file)) {
      try { for (const [k, t] of Object.entries(JSON.parse(fs.readFileSync(file, 'utf8')))) this.seen.set(k, t); } catch { /* bỏ qua file hỏng */ }
    }
  }
  // true nếu id mới (và đánh dấu đã thấy); false nếu trùng
  firstTime(id) {
    const t = this.now();
    for (const [k, ts] of this.seen) if (t - ts > this.ttlMs) this.seen.delete(k);
    if (this.seen.has(id)) return false;
    this.seen.set(id, t);
    this.#save();
    return true;
  }
  #save() {
    if (!this.file) return;
    fs.mkdirSync(path.dirname(this.file), { recursive: true });
    fs.writeFileSync(this.file, JSON.stringify(Object.fromEntries(this.seen)));
  }
}
