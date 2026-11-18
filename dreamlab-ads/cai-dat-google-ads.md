# Cài đặt Google Ads — hướng dẫn chủ studio tự bấm

Ngân sách: 1.850.000đ/tháng → **61.000đ/ngày** (Google có thể tiêu tới 2 lần/ngày nhưng tổng tháng không vượt 30,4 × 61.000đ ≈ 1.854.000đ).
Tài liệu này chỉ để duyệt. Chưa có tài khoản, chưa chạy, chưa chi tiền.

## 0. Chuẩn bị trước khi bấm (phiên web khác làm)
- Web cần có **Google Tag Manager (GTM)** và đẩy 3 sự kiện vào `dataLayer`: `zalo_click` (bấm Mở/Nhắn Zalo), `call_click` (bấm/sao chép số), `form_submit` (bấm gửi form — lưu ý form hiện chỉ soạn nội dung để dán vào Zalo, không gửi đi).
- Hiện `src/head.html` chưa có mã GA4/GTM/Pixel nào → chưa đo được gì cho tới khi phiên web chèn mã.

## 1. Tạo tài khoản ở chế độ chuyên gia
1. Vào ads.google.com → **Bắt đầu ngay** → đăng nhập Gmail của studio.
2. Khi Google hỏi mục tiêu kinh doanh (chiến dịch thông minh) → kéo xuống cuối, bấm **Chuyển sang Chế độ chuyên gia**.
3. Chọn **Tạo tài khoản không có chiến dịch**.
4. Quốc gia thanh toán: Việt Nam · Múi giờ: **(GMT+07:00) Hồ Chí Minh** · Tiền tệ: **VND**. Hai mục này KHÔNG đổi được sau khi tạo.
5. Thanh toán: thêm phương thức nhưng **chưa nạp/chưa bật chiến dịch** cho tới khi duyệt xong.

## 2. Gắn chuyển đổi (làm TRƯỚC khi chạy)
Cách khuyên dùng: GA4 + GTM.
1. Tạo thuộc tính **GA4** (analytics.google.com) cho `dreamlabs.vn` → lấy Mã đo lường `G-…`.
2. Trong GTM: thẻ Google (GA4) chạy trên mọi trang; 3 trình kích hoạt **Sự kiện tùy chỉnh** tên `zalo_click`, `call_click`, `form_submit`; 3 thẻ Sự kiện GA4 cùng tên.
3. GA4 → Quản trị → Sự kiện → đánh dấu 3 sự kiện là **Sự kiện chính**.
4. Google Ads → Mục tiêu → Chuyển đổi → **Nhập** → Thuộc tính GA4 → chọn 3 sự kiện.
5. Cài đặt từng chuyển đổi: Danh mục "Liên hệ"/"Gửi biểu mẫu khách hàng tiềm năng"; Tính: **Một**; Thời lượng: 30 ngày.
   - `zalo_click`, `form_submit`: **Hành động chính** (dùng cho đặt giá thầu).
   - `call_click`: hành động phụ (chỉ theo dõi) — tránh đếm trùng với tiện ích cuộc gọi.
6. Liên kết Google Ads ↔ GA4 (Công cụ → Tài khoản được liên kết).
7. Kiểm tra: GTM **Xem trước** → bấm nút Zalo trên web → thấy sự kiện chạy; GA4 → Báo cáo theo thời gian thực.

## 3. Tạo chiến dịch Tìm kiếm
1. **+ Chiến dịch mới** → Mục tiêu: **Khách hàng tiềm năng** → Loại: **Tìm kiếm** → chọn 2 chuyển đổi chính ở trên.
2. Tên: `DL-Search-HCM-HN`.
3. Mạng: **BỎ** "Mạng Hiển thị" và **BỎ** "Đối tác tìm kiếm của Google".
4. Vị trí: thêm **Thành phố Hồ Chí Minh** và **Hà Nội**.
   → **Tùy chọn vị trí** → Bao gồm: **Sự hiện diện: Những người ở hoặc thường xuyên ở các vị trí mục tiêu**.
5. Ngôn ngữ: Tiếng Việt.
6. Lịch quảng cáo: Thứ Hai → Thứ Bảy, **08:00 – 20:00** (Chủ nhật không chạy).
7. Ngân sách: **61.000đ/ngày**.
8. Giá thầu giai đoạn 1: **Tối đa hóa số lượt nhấp** + bật **Giới hạn giá thầu CPC tối đa**.
   - Mức trần: lấy "Giá thầu đầu trang (phạm vi thấp)" trung bình trong Công cụ lập kế hoạch từ khóa (xem `tu-khoa-google.md`). Chưa có số liệu thật → đề xuất khởi điểm **10.000đ** (giả định, để có ≥ 6 lượt nhấp/ngày), chỉnh sau 3–5 ngày.
9. **Tắt** "Áp dụng đề xuất tự động" (Đề xuất → Tự động áp dụng) và **tắt tài sản tự động tạo** (để Google không tự viết lại nội dung).
10. Không bật khớp rộng; không bật "Tối ưu hóa cho trang đích/AI Max".

## 4. Nhóm quảng cáo, từ khóa, quảng cáo
1. Tạo 3 nhóm: `Web-Landing`, `AI-TuDongHoa`, `BaoBi-Video`.
2. Dán từ khóa từng nhóm theo `tu-khoa-google.md` (giữ ký hiệu `"…"` và `[…]`).
3. Từ khóa có ghi URL cấp từ khóa (#p-landing, #p-motion, #p-video): mở từ khóa → URL cuối cùng → dán URL tương ứng.
4. Mỗi nhóm 1 quảng cáo tìm kiếm thích ứng: chép 15 tiêu đề + 4 mô tả + đường dẫn hiển thị theo `mau-quang-cao-google.md`.
5. Tiện ích (cấp chiến dịch): Cuộc gọi 0934 246 420 (lịch T2–T7 8–20h), 7 liên kết trang web, 8 chú thích.
6. Danh sách từ khóa phủ định: Công cụ → Trình quản lý dùng chung → Danh sách từ khóa phủ định → tạo `DL-Phu-dinh` → áp vào chiến dịch.

## 5. Chuyển sang Tối đa hóa chuyển đổi
Chuyển khi **cả 2** điều kiện đúng:
- Chuyển đổi đã ghi nhận đúng (kiểm tra trong 7 ngày đầu, không đếm trùng).
- Có **≥ 15 chuyển đổi chính trong 30 ngày** gần nhất.
Cách: Cài đặt chiến dịch → Giá thầu → **Chuyển đổi** → chưa đặt CPA mục tiêu 2 tuần đầu. Sau đó có thể đặt CPA mục tiêu ≈ chi phí/khách hỏi thực tế (xem `bao-cao-14-ngay.md`).
Không đủ 15 sau 30 ngày → giữ Tối đa hóa lượt nhấp, chỉ tối ưu từ khóa.

## 6. Google Search Console
1. search.google.com/search-console → **Thêm thuộc tính** → loại **Miền** → `dreamlabs.vn`.
2. Thêm bản ghi **TXT** Google đưa vào DNS nơi quản lý tên miền → Xác minh.
3. Sơ đồ trang web → gửi `https://dreamlabs.vn/sitemap.xml`.
4. Liên kết Search Console với Google Ads (Công cụ → Tài khoản được liên kết) để xem từ khóa tự nhiên cạnh từ khóa trả phí.

## 7. Google Business Profile
1. business.google.com → **Thêm doanh nghiệp** → tên: **Dream Labs**.
2. Danh mục chính: chọn gần nhất với dịch vụ (vd "Nhà thiết kế trang web"); danh mục phụ: thiết kế đồ họa, sản xuất video.
3. Địa chỉ: nếu không đón khách tại văn phòng → chọn **doanh nghiệp theo khu vực dịch vụ**, ẩn địa chỉ, khu vực: TP.HCM, Hà Nội.
4. Điện thoại 0934 246 420 · Web `https://dreamlabs.vn/` · Giờ: T2–T7 8:00–20:00.
5. Dịch vụ + giá: chỉ ghi đúng bảng giá trên web (vd Website từ 8.000.000đ, Landing Page từ 3.000.000đ, Tự động hóa từ 5.000.000đ).
6. Xác minh theo cách Google yêu cầu (video/điện thoại). Không mua/nhờ đánh giá; chỉ mời khách thật để lại đánh giá.
7. Liên kết GBP với Google Ads để bật tiện ích vị trí (nếu có địa chỉ hiển thị).

## Kiểm tra trước khi bật
- [ ] 3 nhóm, 28 từ khóa, danh sách phủ định đã áp
- [ ] Quảng cáo "Đủ điều kiện", không bị "Bị hạn chế"
- [ ] Chuyển đổi chính ở trạng thái "Đang ghi nhận" (đã test)
- [ ] Lịch 8–20h T2–T7, vị trí "ở hoặc thường ở", tắt Mạng hiển thị
- [ ] Ngân sách 61.000đ/ngày, trần CPC đã đặt
