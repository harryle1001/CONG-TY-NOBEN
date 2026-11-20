# Quy tắc công ty: Tỷ lệ vàng φ = 1.61803
Áp dụng φ cho MỌI việc (web, game, thiết kế, nội dung, bố cục, số liệu):
- Typography: cỡ chữ theo thang φ (vd 10 → 16 → 26 → 42 → 68px); line-height ≈ 1.618.
- Spacing: thang khoảng cách φ (vd 6, 10, 16, 26, 42, 68, 110px).
- Layout: chia cột/vùng 61.8% / 38.2%; khung hình tỷ lệ 1.618:1.
- Màu/độ nhấn: phân bổ diện tích chính/phụ 61.8/38.2.
- Animation: thời lượng theo bậc φ (vd 162ms, 262ms, 424ms); easing tự nhiên.
- Game: kích thước UI, tỉ lệ màn chơi, đường cong độ khó/XP nhân φ mỗi cấp.
- Nội dung: cấu trúc ý chính ~61.8%, phần phụ ~38.2%.
Khai báo biến --phi: 1.61803 trong CSS/code để dùng thống nhất.

# Jarvis
Khi người dùng gọi "Jarvis" (hoặc dùng lệnh `/jarvis`), nhận vai JARVIS: trợ lý riêng, xưng "tôi", gọi người dùng là "anh", trả lời tiếng Việt ngắn gọn.
Bản web/điện thoại (nói bằng giọng): `jarvis/index.html`, đã xuất bản dạng Artifact trên claude.ai.

Bản đầy đủ chạy trên máy (đồ thị kiến thức, công cụ, giọng ElevenLabs): `jarvis-pro/`, xem `jarvis-pro/README.md`.

# Quy tắc hồ sơ lô Noben (áp dụng cho mọi lô, về sau)
- 2 đội sản xuất chạy song song: đội thuốc nước (YUCCA, IODINE, BEN COPPER…) và đội thuốc bột (C MAX, BZT, EDTA…). Trong 1 đội không trùng giờ; chừa 10 phút giữa 2 lô.
- Thứ tự: thức ăn bổ sung (MS 01-…) làm trước, xử lý môi trường (MS 02-…) làm sau. Nghỉ trưa 11:30–13:00.
- Tổng thời gian 1 lô (cân → phối trộn → đóng gói cấp 1 → cấp 2, nối tiếp): nước ≤20 chai = 20p, ≤60 = 30p, ≤120 = 45p; bột ≤15 kg = 20p, ≤50 kg = 30p, ≤120 kg = 45p, ≤250 kg = 60p. Mốc chuẩn: BEN COPPER 20p, C MAX 25% 40p.
- Nhãn = số đơn vị bán + số thùng (mẫu lưu không dán nhãn). Thùng: chai sành 1L 15/thùng, chai nhựa 1L 20/thùng, hũ 1kg và hũ 500g 24/thùng, gói 3kg 10/thùng.
- Mã HQ, TCCS, MS lấy ở ho-so-lo/Danh-muc-104-san-pham-Noben.xlsx. Số lô SX = số cuối mã HQ + ddmmyy. Ô "Số đăng ký" trong hồ sơ lô chỉ ghi MSTN, không ghi Mã HQ, TCCS.
- Kích thước bao bì lấy ở ho-so-lo/du-lieu/Kich-thuoc-bao-bi.xls và Kich-thuoc-bao-bi-bo-sung.csv (bao bì chưa có trong file thì hỏi lại, không tự điền).
- Biểu mẫu rác nguy hại: ngày SX trên 100 sản phẩm mới có rác giẻ lau (0,2 kg), từ 100 trở xuống không có; rác bao bì nhựa cứng và "Bao bì cứng NL, bao bì đựng hóa chất thải" (rắn) luôn 1 kg, SX nhiều cũng chỉ 1 kg.
- Đơn vị sau số lượng viết thường: 30 Hũ, 100 Chai, 20 Gói, 32 Cái (không viết HŨ/CHAI/GÓI).
- Bộ biểu mẫu 12 quy định (ho-so-lo/bieu-mau-12-quy-dinh/) ghép cùng hồ sơ lô thành 1 bộ theo ngày sản xuất.
- Xuất bộ hồ sơ theo giao diện mẫu tham khảo, file rời: mỗi lô 1 file hồ sơ lô; 1 file phiếu QD7 (.xls); 1 file lệnh SX (mỗi lệnh 1 trang); 1 file dán mẫu lưu (tem 64,6 × 34,8 mm, 3 tem/hàng); 1 file biểu mẫu 12 quy định (biểu mẫu 2–12, mỗi phiếu sang trang mới và có khung logo + mã tài liệu, không có trang trắng). Mẫu đã duyệt: ho-so-lo/HO-SO-21.09.2026/BO-HO-SO-LO-21.09.2026/; script ho-so-lo/_build/xuat_rieng_2109.sh.
- Định dạng Word: bảng cùng bề rộng vùng chữ, cột chia theo φ, không bảng nổi, không khung chữ nổi; chỉ xuất Word khi được yêu cầu; làm 1 bản xem thử, được duyệt mới xuất hàng loạt.
