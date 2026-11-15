# Hồ sơ nhãn & thông tin sản phẩm Noben

Nguồn: CSDL Cục Thủy sản và Kiểm ngư (csdl.tongcucthuysan.gov.vn), trích xuất 16/11/2026.
Gồm 113 sản phẩm đang kinh doanh đã công bố (không lấy sản phẩm ngừng kinh doanh).

- `index.html`: trang xem, tìm kiếm và in (Ctrl+P, khổ A4, mỗi sản phẩm một trang).
- `data.json`: dữ liệu gốc (tên, mã số, thành phần, chỉ tiêu, hướng dẫn sử dụng…).
- `nhan/`: ảnh nhãn, đặt tên theo `<mã số tiếp nhận>_<số thứ tự>.jpg`.
- `build.py`: tạo lại `index.html` từ `data.json`.

## Chỉnh sửa online
Mở `data.json` trên GitHub, bấm biểu tượng bút chì, sửa rồi Commit.
Sau đó chạy `python3 build.py` để tạo lại `index.html` (hoặc nhờ Claude chạy).
