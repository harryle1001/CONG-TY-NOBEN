// Bộ phân loại theo luật: chạy KHÔNG cần mạng. Dùng làm lớp an toàn (luôn chạy)
// và làm bộ não dự phòng khi chưa có ANTHROPIC_API_KEY.
import { norm } from './text.js';

export const LABELS = ['hoi_gia', 'dat_lich_tu_van', 'hoi_demo', 'khieu_nai', 'khac'];

const has = (t, words) => words.some((w) => (w instanceof RegExp ? w.test(t) : t.includes(w)));

const SPAM = [
  /https?:\/\/(?!(www\.)?dreamlabs\.vn)/, /\bbit\.ly\b/, /\bt\.me\//,
  'kiem tien', 'vay tien', 'vay von', 'giai ngan', 'casino', 'ca do', 'nha cai', 'lo de', 'xo so',
  'tang follow', 'tang like', 'ban follow', 'ban like', 'hack ', 'nhan qua mien phi', 'trung thuong',
  'inbox minh de nhan', 'thu nhap 500k', 'viec nhe luong cao', 'crypto x', 'dau tu sinh loi', 'sex', '18+',
];
const KHIEU_NAI = [
  'khieu nai', 'that vong', 'khong hai long', 'lua dao', 'hoan tien', 'tra lai tien', 'boi thuong',
  'qua te', 'te qua', 'lam an', 'phot', 'cham tre', 'tre han', 'khong ai tra loi', 'bao loi ma', 'buc minh',
  'chat luong kem', 'khong giong', 'sai so voi', 'lam sai',
];
const DAT_LICH = ['dat lich', 'hen lich', 'lich tu van', 'tu van', 'goi cho', 'goi lai', 'call', 'gap truc tiep', 'trao doi', 'meeting', 'hen gap', 'sdt cua minh', 'so dien thoai cua minh'];
const DEMO = ['demo', 'dung thu', 'xem thu', 'mau da lam', 'du an da lam', 'portfolio', 'san pham mau', 'vi du', 'cho xem', 'xem mau', 'case study'];
const GIA = [/\bgia\b/, 'bao nhieu', 'bao gia', 'chi phi', /\bphi\b/, /\bbn\b/, 'goi nao', 'bang gia', /\btien\b/, 'ngan sach', /\btrieu\b/];
// Cần người thật dù không phải khiếu nại: báo giá riêng, đàm phán, hợp đồng, câu khó.
const CAN_NGUOI = [
  'bao gia rieng', 'bao gia chi tiet', 'bao gia cu the', 'giam gia', 'chiet khau', 'bot gia', 'giam them',
  'hop dong', 'xuat hoa don', 'hoa don vat', 'tuy chinh rieng', 'yeu cau rieng', 'du an lon', 'dau thau',
  'hop tac', 'tuyen dung', 'xin viec', 'bao mat du lieu cua', 'phap ly', 'tra gop',
];

export function classifyRules(text) {
  const t = norm(text);
  if (!t || /^[\p{P}\p{S}\s]*$/u.test(String(text))) return { nhan: 'khac', la_spam: false, can_nguoi_that: false, rong: true };
  const spam = has(t, SPAM) || /(.)\1{9,}/.test(t);
  let nhan = 'khac';
  if (has(t, KHIEU_NAI)) nhan = 'khieu_nai';
  else if (has(t, DAT_LICH)) nhan = 'dat_lich_tu_van';
  else if (has(t, DEMO)) nhan = 'hoi_demo';
  else if (has(t, GIA)) nhan = 'hoi_gia';
  const canNguoi = nhan === 'khieu_nai' || has(t, CAN_NGUOI);
  return {
    nhan, la_spam: spam && nhan !== 'khieu_nai', can_nguoi_that: canNguoi,
    ly_do_chuyen: nhan === 'khieu_nai' ? 'Khiếu nại' : canNguoi ? 'Yêu cầu riêng / báo giá riêng / câu khó' : '',
  };
}
