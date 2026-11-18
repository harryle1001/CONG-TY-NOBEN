// Luồng xử lý một sự kiện: chống trùng → giới hạn tần suất → bộ não → (nháp | gửi thật) → ghi khách tiềm năng.
import fs from 'node:fs';
import path from 'node:path';
import { decide } from './brain.js';

export function createAssistant({ cfg, deduper, limiter, sink, senders, client = null, knowledge, allowed, log = () => {}, now = () => new Date() }) {
  const draftFile = path.join(cfg.dataDir, 'nhap-tra-loi.jsonl');
  const writeDraft = (obj) => {
    fs.mkdirSync(cfg.dataDir, { recursive: true });
    fs.appendFileSync(draftFile, JSON.stringify(obj) + '\n');
  };

  async function handle(event) {
    if (!deduper.firstTime(event.id)) return { id: event.id, trang_thai: 'trung_lap' };
    const rl = limiter.allow(`${event.channel}:${event.senderId}`);
    if (!rl.ok) { log('Bỏ qua do giới hạn tần suất', event.id, rl.reason); return { id: event.id, trang_thai: 'gioi_han', ly_do: rl.reason }; }

    const d = await decide(event, { client, model: cfg.model, knowledge, allowed, log });
    const thoi_gian = now().toISOString();

    if (d.la_spam) {
      writeDraft({ thoi_gian, ma_su_kien: event.id, kenh: event.channel, noi_dung: event.text, trang_thai: 'bo_qua_spam' });
      return { id: event.id, trang_thai: 'bo_qua_spam', quyet_dinh: d };
    }

    // Kế hoạch gửi
    const actions = [];
    if (event.kind === 'comment') {
      if (d.tra_loi_cong_khai) actions.push({ loai: 'tra_loi_binh_luan', text: d.tra_loi_cong_khai });
      if (d.tin_nhan_rieng) actions.push({ loai: 'nhan_rieng', text: d.tin_nhan_rieng });
    } else if (d.tin_nhan_rieng) {
      actions.push({ loai: 'tin_nhan', text: d.tin_nhan_rieng });
    }

    let trang_thai;
    if (cfg.dryRun) {
      trang_thai = d.can_nguoi_that ? 'nhap_cho_duyet|chuyen_nguoi_that' : 'nhap_cho_duyet';
      writeDraft({ thoi_gian, ma_su_kien: event.id, kenh: event.channel, nguoi_gui: event.senderName || event.senderId, noi_dung: event.text, nhan: d.nhan, can_nguoi_that: d.can_nguoi_that, ly_do_chuyen: d.ly_do_chuyen, du_kien_gui: actions, nguon: d.nguon });
    } else {
      const loi = [];
      for (const a of actions) {
        try {
          if (a.loai === 'tra_loi_binh_luan') await senders.replyComment(event, a.text);
          else if (a.loai === 'nhan_rieng') await senders.privateReply(event, a.text);
          else await senders.sendMessage(event, a.text);
        } catch (e) { loi.push(`${a.loai}: ${e.message}`); log('Gửi lỗi', event.id, e.message); }
      }
      trang_thai = loi.length ? 'loi_gui|chuyen_nguoi_that' : d.can_nguoi_that ? 'da_tra_loi|chuyen_nguoi_that' : 'da_tra_loi';
      if (loi.length) d.ly_do_chuyen = [d.ly_do_chuyen, ...loi].filter(Boolean).join(' | ');
    }

    const rec = {
      thoi_gian, ten: d.ten_khach || event.senderName || event.senderId, kenh: event.channel, noi_dung: event.text,
      nhan: d.nhan, trang_thai, can_nguoi_that: d.can_nguoi_that ? 'co' : 'khong', ly_do_chuyen: d.ly_do_chuyen || '',
      tra_loi_cong_khai: d.tra_loi_cong_khai || '', tin_nhan_rieng: d.tin_nhan_rieng || '', ma_su_kien: event.id, nguon: d.nguon,
    };
    try { await sink.append(rec); } catch (e) { log('Ghi khách tiềm năng lỗi', e.message); }
    return { id: event.id, trang_thai, quyet_dinh: d, hanh_dong: actions };
  }

  return { handle };
}
