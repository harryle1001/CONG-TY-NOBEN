// Câu trả lời mẫu đã duyệt — dùng khi chạy không có Claude, hoặc khi câu của AI bị lớp kiểm tra chặn.
const ZALO = '0934 246 420';

export const PRIVATE = {
  hoi_gia:
    'Chào bạn, cảm ơn bạn đã quan tâm Dream Labs! Giá khởi điểm (chưa gồm VAT):\n' +
    '• Tự động hóa quy trình bằng AI: từ 5.000.000đ\n• Website: từ 8.000.000đ\n• Landing page: từ 3.000.000đ\n' +
    '• Edit video: từ 800.000đ/video\n• Thiết kế bao bì, sản phẩm: từ 2.000.000đ\n• Motion graphic: từ 3.000.000đ/video\n' +
    'Chọn từ 3 hạng mục trở lên được giảm 10%. Bạn đang quan tâm hạng mục nào để mình gửi chi tiết từng gói? ' +
    'Bảng giá đầy đủ ở dreamlabs.vn, và Dream Labs có buổi tư vấn 30 phút miễn phí nếu bạn muốn trao đổi kỹ hơn.',
  dat_lich_tu_van:
    'Chào bạn, Dream Labs có buổi tư vấn 30 phút miễn phí, không ràng buộc. Bạn để lại giúp mình tên, số điện thoại/Zalo, ' +
    'nhu cầu chính và khung giờ thuận tiện (T2–T7, 8:30–18:00). Người phụ trách của Dream Labs sẽ liên hệ để xác nhận lịch.',
  hoi_demo:
    'Chào bạn, bạn có thể bấm thử các demo (website, video, quy trình AI) ngay trên dreamlabs.vn. Các dự án gắn nhãn Concept ' +
    'là dự án Dream Labs tự dựng để bạn thấy đúng tay nghề. Trợ lý đang trả lời bạn cũng chính là một bản demo của gói ' +
    'Tự động hóa Khởi động. Bạn muốn xem demo cho lĩnh vực nào để mình gợi ý đúng phần?',
  khieu_nai:
    'Dream Labs rất tiếc về trải nghiệm chưa tốt của bạn. Mình đã chuyển nội dung này tới người phụ trách để xem xét trực tiếp. ' +
    `Bạn có thể nhắn thêm chi tiết qua Zalo ${ZALO} để Dream Labs nắm rõ hơn.`,
  khac:
    'Chào bạn, Dream Labs là studio tại TP.HCM chuyên tự động hóa quy trình doanh nghiệp bằng AI, kèm thiết kế website, ' +
    'landing page, bao bì, motion graphic và edit video. Bạn đang cần hỗ trợ việc gì để mình tư vấn đúng nhé?',
};

export const PUBLIC = {
  hoi_gia: 'Cảm ơn bạn đã quan tâm! Dream Labs đã gửi bảng giá vào tin nhắn, bạn kiểm tra hộp thư giúp mình nhé.',
  dat_lich_tu_van: 'Cảm ơn bạn! Dream Labs đã nhắn tin để hẹn buổi tư vấn 30 phút miễn phí, bạn xem hộp thư giúp mình nhé.',
  hoi_demo: 'Bạn bấm thử demo ngay trên dreamlabs.vn nhé! Dream Labs cũng đã gửi gợi ý chi tiết vào tin nhắn.',
  khieu_nai: 'Dream Labs rất tiếc về trải nghiệm của bạn. Mình đã nhắn tin riêng để người phụ trách hỗ trợ trực tiếp.',
  khac: 'Cảm ơn bạn đã ghé Dream Labs! Bạn nhắn tin cho Page để mình hỗ trợ chi tiết hơn nhé.',
};

export function templateReply(nhan, kind) {
  const key = PRIVATE[nhan] ? nhan : 'khac';
  return { tra_loi_cong_khai: kind === 'comment' ? PUBLIC[key] : '', tin_nhan_rieng: PRIVATE[key] };
}
