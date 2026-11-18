// Tiện ích chữ tiếng Việt.
export const stripVN = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D');
export const norm = (s) => stripVN(s).toLowerCase().replace(/\s+/g, ' ').trim();
