# Nhật ký điều phối Dream Labs

Phiên điều phối: Giám đốc kinh doanh Dream Labs (session_012QLWn8J7kt2DoH9Kc6EsMF). Chủ studio duyệt cuối.

## Tài sản (lập nền 2026-11-18)

| Tài sản | Vị trí | Ghi chú |
|---|---|---|
| Web chính | https://dreamlabs.vn, repo harryle1001/DreamLabs-Studio (main, GitHub Pages) | build: `node build.js`; kiểm tra: `node tools/check.js` |
| Trang chủ showroom mẫu vuốt kèm giá | DreamLabs-Studio | commit 13b95df đã lên; phiên con vẫn đang làm (gom video sản phẩm) |
| Trang dịch vụ | 7+ trang (website, landing, bao bì, motion/video, edit video, tự động hóa quy trình, bảng giá) | |
| Trang ngành | `giai-phap-theo-nganh/` 60 trang | liên kết từ trang chủ (68b9cf4) |
| Blog | `blog/` 6 bài SEO | |
| Phòng mẫu + 360 | 44+ mẫu, trình xem xoay 360 | |
| Demo | 16 demo website/landing (Ombrève, Lavrène, Halvesse, Ysmarène, Orvanthe, Élorne, Vauquelle, Séraval, Vọng Giang, Đồi Lặng, Ondinea…) | |
| Bản sao mã nguồn + BRIEF.md | repo này `dreamlab/` | nội bộ |
| Lịch nội dung 30 ngày | repo này `dreamlab-social/` (từ 2026-11-20) | CHƯA có trên nhánh, phiên con đang làm |
| Mạng xã hội (qua vidIQ, cập nhật 18/11 tối) | Instagram dreamlabs.vn: đăng được (đổi tên từ har.ryy). TikTok vẫn hiện "KAKASHI". Facebook chỉ có Page "THUỐC THỦY SẢN NOBEN" (KHÔNG dùng cho Dream Labs) | Chưa thấy Page Dream Labs, X. Threads, Zalo OA đăng tay (không có công cụ) |

## Phiên con đang có (Dream Labs)

- session_012QLWn7yfVf3caDP4EXAAfG: trang chủ gọn, showroom mẫu vuốt (đang chạy)
- session_012QLWn8ct7zRsaaYJqde32v: nội dung mạng xã hội 30 ngày (đang chạy)

## Việc tồn đọng

1. Sức khỏe web: chưa chạy được build/check trong phiên điều phối (lệnh npm/node bị chặn quyền). Cần chủ studio cho phép, hoặc giao phiên con kiểm tra.
2. Chờ `dreamlab-social/lich-dang.json` để làm bản nháp bài đăng hằng ngày.
3. Tài khoản TikTok/Instagram đang kết nối mang tên cá nhân, không phải tên Dream Labs. Cần chủ studio xác nhận có đăng nội dung Dream Labs lên đó không.
4. Facebook Page và Zalo OA chưa nối qua công cụ: Zalo đăng tay; Facebook cần kết nối trong vidIQ nếu muốn tạo nháp.
5. Ý tưởng việc sau: bài blog SEO theo từ khóa còn thiếu, tối ưu chuyển đổi (nút Zalo/form) ở trang dịch vụ.

---

## 2026-11-18 (lần đầu, lập nền)

- Git 1 ngày: DreamLabs-Studio có khoảng 30 commit (showroom trang chủ, gỡ kéo ngang trên điện thoại, 63 trang SEO dịch vụ/ngành, 360 độ, 10 demo landing mới, 6 bài blog). CONG-TY-NOBEN: c08044c đồng bộ mã nguồn.
- Sức khỏe web: CHƯA kiểm tra (npm install/node build bị chặn quyền).
- Mạng xã hội: chưa có lịch đăng nên chưa tạo nháp. Không đăng gì.
- Việc giao mới: không (lần đầu chỉ lập nền).
- Chờ chủ studio: mục 1, 3, 4 ở trên.

### 2026-11-18 (tối) – giao việc theo duyệt của chủ studio
- session_012QLWn8QkNPqTN1JPvkkk8e: SEO kỹ thuật toàn site + 2 bài blog (chi phí thiết kế website; tự động hóa báo cáo bằng AI) + sự kiện dataLayer zalo_click/call_click/form_submit. Đẩy main DreamLabs-Studio.
- session_012QLWn7TJsTajqumKmWs7Jd: bộ quảng cáo 3 triệu/tháng (Google ~1,85tr, FB/IG ~1,15tr) → `dreamlab-ads/`. Chỉ soạn, không chạy/chi tiền.
- Chủ studio tự làm: Google Search Console, Google Business Profile, tài khoản Google Ads + Meta Ads, thanh toán; nối TikTok/Page Dream Labs/X (chưa xong).
- Đã dùng 2/2 phiên mới hôm nay.
- Mạng xã hội cập nhật: X @dreamlabsvn (2123013416453586944) kết nối, đăng được. Chủ studio quyết dùng TikTok KAKASHI (_000wEA6UHqpUV68h6jKDjjO2YGxcrDnyZvq) làm kênh Dream Labs, sẽ đổi tên. Facebook Page Dream Labs vẫn chưa vào (chỉ có Page Noben, không dùng).
- Chủ studio DUYỆT 4 mục bộ nội dung 30 ngày (18/11): (1) bài 29 ưu đãi cuối năm giữ nguyên; (2) tư vấn 30 phút miễn phí: đúng; (3) nhạc nền chọn khi duyệt từng bài; (4) Zalo OA ưu tiên bài 2, 8, 13, 23, 26, 29, 30 nếu thiếu lượt. Đây là duyệt nội dung, KHÔNG phải duyệt đăng: mỗi bài vẫn cần duyệt riêng trước khi đăng.
- Facebook: vidIQ vẫn chỉ nhận Page Noben; Page Dream Labs đăng tay qua Meta Business Suite nếu vẫn không vào.
- ĐĂNG THỬ (chủ studio duyệt "Đăng ngay" 18/11): clip demo trợ lý AI Zalo (p02) + bài "5 bước chuẩn hóa tiếp nhận khách hỏi giá". vidIQ postId 305809cd-c490-4379-959a-14b35c08a001. X: https://x.com/i/status/2123111727516512450 (5 credit). Instagram, TikTok (công khai, cho bình luận, đồng ý nhạc, gắn nhãn tự quảng bá thương hiệu): đang xử lý.
- Yêu cầu nội dung mới của chủ studio: mỗi bài có clip demo + hướng dẫn từng bước chuẩn hóa doanh nghiệp, viết chi tiết. Đã gửi cho phiên nội dung session_012QLWn8ct7zRsaaYJqde32v sửa 30 bài.
- 30 bài chuỗi "Chuẩn hóa doanh nghiệp" xong (07c0a45). Chủ studio chốt: bài 27 số là ví dụ, không phải báo giá; bài 29 bỏ câu "điều khoản cụ thể…"; bài 30 bỏ cam kết thời gian trả lời (không hứa 24/7); bài 26 dùng tên Cơ bản/Chuyên nghiệp/Cao cấp cho mọi dịch vụ. Đã gửi phiên nội dung sửa.
- ĐĂNG BÀI 1 (chủ studio chọn "Đăng ngay cả 3 kênh", 18/11 tối): vidIQ postId ee9f77b0-82a6-4bf0-8707-f8e46954e5d3. X: https://x.com/i/status/2123119761714233474 (5 credit). IG Reel + TikTok đang xử lý. IG đăng dạng Reel (không phải carousel) vì mạng phiên chặn mcp.vidiq.com nên không tải được ảnh slide. Bài 1 không còn đăng ngày 20/11.
- Bài 1: IG https://www.instagram.com/reel/Df5I8uVPDtx/ , TikTok https://www.tiktok.com/@ka.ka.shiii/video/7709578684256013620 . Facebook Page Dream Labs vẫn chưa nối vidIQ → chuẩn bị bản đăng tay dreamlab-social/dang-tay/bai-01-facebook.txt.
- Chủ studio duyệt 3 việc (19/11 rạng sáng giờ VN): (1) bản đăng hội nhóm FB + (3a) bộ câu trả lời mẫu/từ khóa tự động Meta → giao phiên nội dung session_012QLWn8ct7zRsaaYJqde32v (không tính phiên mới); (2) mỗi sáng phiên điều phối đọc bình luận IG/TikTok (vidIQ, 5 credit/lượt đọc), soạn câu trả lời chờ duyệt; vidIQ không có công cụ gửi trả lời bình luận IG/TikTok → chủ studio trả lời tay; (3b) phiên mới session_012QLWnBAvkXmMom7VgNnnzA dựng trợ lý AI (FB/IG/Zalo OA, DRY_RUN mặc định) trong dreamlab-ai-assistant/. Hạn mức: 1/2 phiên mới ngày 19/11.

## 2026-11-19 (sáng, 07:40 VN)
- Hôm qua xong: SEO + dataLayer + 2 blog (70bd3cb, web main); bộ quảng cáo dreamlab-ads/ (a479172); 30 bài "Chuẩn hóa doanh nghiệp" + bản hội nhóm + mẫu trả lời (fa85b74, c8e9636, 6f8d1e5); trợ lý AI nháp dreamlab-ai-assistant/ (bcb50a3, DRY_RUN). Web còn có thiết kế lại trang chủ, /en/ /ja/, logo mới, 13 trang mới (phiên khác).
- Đăng: bài thử + bài 1 đã lên IG/X/TikTok; 0 bình luận (IG, TikTok bài 1; 10 credit vidIQ).
- Sức khỏe web: không build được trong phiên này (npm/node bị chặn; mạng chặn dreamlabs.vn). Firecrawl: trang chủ 200 OK. Rà tĩnh: không dấu xung đột gộp; chú thích CSS/JS công khai có nhắc φ; commit 29dbdcf (repo công khai) nhắc φ trong message.
- Giao: session_012QLWn87G9fWbexz44T7dEf kiểm tra sức khỏe web + sửa lỗi nghiêm trọng (gồm gỡ chú thích φ khỏi file công khai). Hạn mức 19/11: 2/2.
- Nháp chờ duyệt: bài 3 (SOP 1 trang) postId 0b1d656a-9fd0-4021-beec-fb08488283dc, IG 12:00 + X 12:30 ngày 20/11, clip quảng cáo 9:16 (kho/7-video-quang-cao). TikTok chờ chủ studio chọn quyền xem/bình luận/nhạc. IG dùng video thay carousel vì mạng chặn mcp.vidiq.com (tải ảnh).
- Chờ chủ studio: duyệt bài 3; Page FB Dream Labs (vidIQ vẫn chỉ nhận Page Noben); Search Console/GA4/Ads; bật trợ lý AI theo README; cho phép mạng mcp.vidiq.com nếu muốn carousel.
- Chủ studio duyệt "làm hết" (19/11): bài 3 đã HẸN GIỜ trên vidIQ: IG 20/11 12:00, X 12:30 (5 credit), TikTok 21:00 (công khai, cho bình luận, đồng ý nhạc). Mạng môi trường NOBEN đã thêm mcp.vidiq.com + dreamlabs.vn (chủ studio duyệt) → từ nay tải được carousel và tự kiểm tra web. Web live: 7 trang chính trả 200.

## 2026-11-20 (sáng, 07:40 VN)
- Hôm qua xong: phiên kiểm tra web (session_012QLWn87G9fWbexz44T7dEf) sửa bản đóng gói thiếu /en/, /ja/, track.js; còn chờ mã GA4/GTM. Phiên khác (không do điều phối giao) thêm ~32 bài blog hỏi-đáp, 15 demo concept mới (trang sức, xe sang, nước hoa), trang /thiet-ke-website/xe-sang/, nhạc nền video, hero mới.
- Web live: 9 trang chính 200, sitemap 139 URL, không lộ φ/tỷ lệ vàng ở trang chủ, blog, xe-sang; không dấu xung đột.
- Mạng xã hội: bài 3 hẹn hôm nay IG 12:00, X 12:30, TikTok 21:00. 0 bình luận ở IG bài thử + bài 1 (10 credit đọc).
- Nháp chờ duyệt: bài 4 "Trang chủ 7 khối" postId f457e83a-bafa-4cfb-911c-8ff93c219043: IG carousel 11 ảnh 21/11 10:30; X 10:00 (5 credit); TikTok 19:30 chờ chọn quyền xem/bình luận/nhạc.
- Giao việc: không giao phiên mới (web đang có nhiều phiên khác làm; tránh trùng, tiết kiệm hạn mức).
- Chờ chủ studio: duyệt bài 4 + lựa chọn TikTok; mã Search Console/GA4/Ads; Page FB Dream Labs.
