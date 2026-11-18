# Facebook / Instagram — Dream Labs

Ngân sách: 1.150.000đ/tháng (~38.000đ/ngày).
- Nhóm A — Nhắm lại khách đã vào web: **~60% = 690.000đ/tháng (~23.000đ/ngày)**
- Nhóm B — Video showroom mẫu, mục tiêu Tin nhắn: **~40% = 460.000đ/tháng (~15.000đ/ngày)**

Danh tính: Page **"Dream Labs"** + Instagram **dreamlabs.vn**. KHÔNG chọn Page "THUỐC THỦY SẢN NOBEN" ở bất kỳ bước nào (kiểm tra lại ô "Trang Facebook" trước khi đăng).
Tài liệu chỉ để duyệt — chưa tạo tài khoản, chưa chạy, chưa chi tiền.

## 1. Cài Meta Pixel + tạo đối tượng

### 1.1 Tài khoản
1. business.facebook.com → tạo/chọn Business Portfolio **Dream Labs**; thêm Page "Dream Labs" và Instagram dreamlabs.vn.
2. Tài khoản quảng cáo mới: Tiền tệ **VND**, Múi giờ **Asia/Ho_Chi_Minh** (không đổi được sau).
3. Cài đặt doanh nghiệp → **Tên miền** → thêm `dreamlabs.vn` → xác minh bằng bản ghi **TXT** DNS.

### 1.2 Pixel (Tập dữ liệu)
1. Trình quản lý sự kiện → **Kết nối nguồn dữ liệu** → Web → tên `Dream Labs Web` → lấy **ID tập dữ liệu (Pixel ID)**.
2. Giao ID cho phiên làm web để gắn qua **GTM** (cùng container với Google): thẻ Meta Pixel `PageView` trên mọi trang.
3. Ánh xạ sự kiện dataLayer → sự kiện chuẩn Meta:
   | dataLayer | Sự kiện Meta |
   |---|---|
   | `zalo_click` | `Contact` |
   | `call_click` | `Contact` (tham số `method: call`) |
   | `form_submit` | `Lead` |
4. Kiểm tra: Trình quản lý sự kiện → **Kiểm tra sự kiện** → mở web, bấm Zalo → thấy `Contact`.
5. Lưu ý: web chưa có banner đồng ý cookie; nên có thông báo quyền riêng tư ngắn ở chân trang trước khi chạy (phiên web làm).

### 1.3 Đối tượng
| Tên | Loại | Cài đặt |
|---|---|---|
| `DL-Web-30N` | Đối tượng tùy chỉnh — Website | Tất cả người truy cập web, **30 ngày** |
| `DL-Lienhe-30N` | Đối tượng tùy chỉnh — Website | Người có `Contact` hoặc `Lead`, 30 ngày (để **loại trừ**) |
| `DL-Tuongtac-IG-FB-60N` | Đối tượng tùy chỉnh — Page/IG | Người tương tác Page Dream Labs + IG dreamlabs.vn, 60 ngày (bổ sung cho nhắm lại) |
| `DL-Xem-video-50` | Đối tượng tùy chỉnh — Video | Xem ≥ 50% video quảng cáo nhóm B, 30 ngày |

Đối tượng cần **≥ 100 người** mới chạy được. Web mới → nhóm A có thể chưa đủ người 1–2 tuần đầu: khi đó dồn tạm ngân sách nhóm A sang nhóm B (ghi lại trong báo cáo).

## 2. Nhóm A — Nhắm lại (khách truy cập web 30 ngày)
- Mục tiêu chiến dịch: **Khách hàng tiềm năng** → nơi chuyển đổi: **Trang web** (sự kiện `Contact`) — hoặc **Ứng dụng nhắn tin** nếu muốn khách nhắn Messenger/IG.
- Đối tượng: `DL-Web-30N` + `DL-Tuongtac-IG-FB-60N`; **loại trừ** `DL-Lienhe-30N`. Vị trí: Việt Nam (hoặc TP.HCM + Hà Nội). Tuổi 25–55.
- Vị trí hiển thị: Facebook Bảng feed, Instagram Bảng feed, Stories, Reels.
- Đích đến: `https://dreamlabs.vn/#bao-gia`.
- Tần suất: theo dõi; nếu > 4 lần/7 ngày thì thay mẫu.

| # | Văn bản chính | Tiêu đề | Nút |
|---|---|---|---|
| A1 | Bạn đã xem qua Dream Labs. Bảng giá công khai trên web: website từ 8.000.000đ, landing page từ 3.000.000đ, tự động hóa bằng AI từ 5.000.000đ. Nhắn để nhận báo giá đúng nhu cầu. | Xem lại bảng giá Dream Labs | Tìm hiểu thêm |
| A2 | Còn phân vân? Quy trình 5 bước rõ ràng: trao đổi brief 30 phút, chọn hướng thẩm mỹ, thiết kế, tinh chỉnh, bàn giao mã nguồn và file gốc. Cập nhật tiến độ mỗi 3 ngày. | Làm việc rõ từng bước | Gửi tin nhắn |
| A3 | Trợ lý AI trả lời khách trên Zalo OA, Messenger 24/7 và đồng bộ dữ liệu về Google Sheets. Gói Khởi động 5–7 ngày. Thử bản demo trên web trước khi quyết định. | Thử demo trợ lý AI | Tìm hiểu thêm |

Hình/video cho nhóm A: ảnh dịch vụ có sẵn trên web (`img/svc-web.webp`, `svc-landing.webp`, `svc-ai.webp`) — chỉ dùng hình do studio làm.

## 3. Nhóm B — Video showroom mẫu, mục tiêu Tin nhắn
- Mục tiêu chiến dịch: **Tương tác** → nơi chuyển đổi: **Ứng dụng nhắn tin** → Messenger + Instagram Direct. (Meta không hỗ trợ Zalo làm đích tin nhắn — trong mẫu chào tin nhắn tự động, gửi kèm số Zalo 0934 246 420.)
- Đối tượng mới: TP.HCM + Hà Nội, 25–55 tuổi, sở thích gợi ý: Chủ doanh nghiệp nhỏ, Thương mại điện tử, Tiếp thị kỹ thuật số, Quảng cáo trên Facebook. Bật Advantage+ đối tượng nếu Meta gợi ý.
- Vị trí hiển thị: Reels FB/IG, Stories, Bảng feed (video dọc 9:16).
- Mẫu chào tin nhắn: "Chào bạn, Dream Labs đây. Bạn cần làm: Website · Landing page · Tự động hóa AI · Bao bì · Video/Motion?" (4–5 nút trả lời nhanh).

| # | Văn bản chính | Tiêu đề | Nút |
|---|---|---|---|
| B1 | Một vòng showroom mẫu của Dream Labs: website, landing page và motion graphic chạy mượt trên điện thoại. Các mẫu là concept do studio tự làm. Nhắn để nhận gợi ý cho thương hiệu của bạn. | Xem showroom mẫu concept | Gửi tin nhắn |
| B2 | Khách hỏi lúc 23h ai trả lời? Xem trợ lý AI concept của Dream Labs trả lời câu hỏi giá, giao hàng, đặt hàng. Gói tự động hóa từ 5.000.000đ. | Trợ lý AI trả lời khách 24/7 | Gửi tin nhắn |
| B3 | Bao bì, nhãn mác, mockup 3D và video motion cho sản phẩm. Bảng giá công khai: bao bì từ 2.000.000đ, motion graphic từ 3.000.000đ. Nhắn để gửi brief. | Bao bì và video cho sản phẩm | Gửi tin nhắn |

## 4. Kịch bản 2 video ngắn (9:16, 1080×1920, 15–20 giây)
Quay màn hình điện thoại thật đang mở dreamlabs.vn + cảnh tay cầm máy. Chữ đặt trong vùng an toàn (cách mép trên/dưới ~14%). Có phụ đề (nhiều người xem tắt tiếng). Nhạc nền có bản quyền. Góc dưới: nhãn nhỏ **"Mẫu concept"** suốt video.

### Video 1 — "Showroom mẫu" (18 giây) — dùng cho B1
| Giây | Cảnh | Chữ trên màn hình | Lời đọc |
|---|---|---|---|
| 0–2 | Cận tay mở điện thoại, trang chủ dreamlabs.vn hiện lên | Website bạn muốn trông thế nào? | Website của bạn trông thế nào trên điện thoại? |
| 2–7 | Cuộn nhanh phần Dự án: lướt 3 mẫu concept website | Website thương hiệu — mẫu concept | Đây là vài mẫu concept của Dream Labs. |
| 7–11 | Mở một landing page mẫu, cuộn qua form và nút | Landing page cho quảng cáo | Landing page gọn, có form và nút Zalo. |
| 11–15 | Tab Motion graphic trong Lab, hiệu ứng chạy | Motion mượt trên điện thoại | Chuyển động mượt, tải nhanh. |
| 15–18 | Màn hình kết: logo chữ Dream Labs + nút "Gửi tin nhắn" | Nhắn để nhận báo giá · dreamlabs.vn | Nhắn Dream Labs để nhận báo giá. |

### Video 2 — "Trợ lý AI 24/7" (17 giây) — dùng cho B2
| Giây | Cảnh | Chữ trên màn hình | Lời đọc |
|---|---|---|---|
| 0–3 | Điện thoại trên bàn tối, đồng hồ 23:00, tin nhắn khách đến | 23h. Khách hỏi giá. | Mười một giờ đêm, khách nhắn hỏi giá. |
| 3–9 | Quay màn hình tab "Trợ lý AI bán hàng" trong Lab: gõ "giá", AI trả lời | Trợ lý AI trả lời ngay — bản demo | Trợ lý AI trả lời ngay, kể cả lúc bạn ngủ. |
| 9–13 | Tab "Luồng tự động hóa": khách → AI → Google Sheets | Lead tự về Google Sheets | Thông tin khách tự về Google Sheets. |
| 13–17 | Màn hình kết: Dream Labs + "Tự động hóa từ 5.000.000đ" + nút | Nhắn để xem demo cho shop bạn | Nhắn Dream Labs để xem bản demo cho shop bạn. |

## 5. Quy tắc nội dung (đã áp ở trên)
- Không hứa kết quả ("tăng doanh thu x%", "chắc chắn ra đơn"), không "top 1", không lời khen/khách hàng bịa.
- Giá chỉ theo bảng giá web. Mẫu concept ghi rõ là concept.
- Không dùng tên/logo hãng khác trong hình, video, chữ (che logo ứng dụng trên màn hình nếu lộ).
- Không nhắm theo đặc điểm nhạy cảm; không nói "Bạn là chủ shop…" kiểu ám chỉ đặc điểm cá nhân — Meta có thể từ chối.
