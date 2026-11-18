# Trợ lý AI Dream Labs

Trợ lý trả lời **bình luận và tin nhắn** trên Facebook Page, Instagram (dreamlabs.vn) và Zalo OA, **phân loại khách**, **ghi khách tiềm năng** vào Google Sheets (hoặc file CSV) và **chuyển người thật** khi cần.
Dùng nội bộ cho Dream Labs, đồng thời là bản demo thật của gói *Tự động hóa – Khởi động*.

> **Trạng thái hiện tại:** bản chạy được nhưng **chưa kết nối tài khoản thật**. Mặc định `DRY_RUN=true`, tức là **chế độ nháp**: không gửi gì ra ngoài, chỉ ghi câu trả lời dự kiến để chủ studio duyệt.

---

## 1. Chạy thử trong 2 phút (không cần tài khoản nào)

Cần Node.js 20 trở lên.

```bash
cd dreamlab-ai-assistant
npm install
npm test                        # 27 bài kiểm tra tự động
npm run chay-thu -- --offline   # chạy 30 sự kiện giả (5 kênh × 5 nhãn + spam), in câu trả lời dự kiến
```

Muốn xem câu trả lời do Claude viết: tạo file `.env` từ `.env.example`, điền `ANTHROPIC_API_KEY`, rồi chạy `npm run chay-thu` (không có `--offline`). Lệnh này vẫn luôn ở chế độ nháp.

Kết quả nháp nằm trong `data/chay-thu/`:
- `nhap-tra-loi.jsonl` – từng câu trả lời dự kiến (công khai / nhắn riêng), nhãn, có cần người thật không.
- `khach-tiem-nang.csv` – mở bằng Excel/Google Sheets.

---

## 2. Vì sao chọn Node.js thay vì n8n

| | Node.js (đã chọn) | n8n |
|---|---|---|
| Xác thực chữ ký webhook, chống trùng, giới hạn tần suất | Viết thẳng, có test | Phải chèn node Code, khó kiểm thử |
| Kiểm thử tự động | `npm test`, 27 bài, không cần mạng | Gần như phải bấm tay |
| Chi phí chạy | Một tiến trình nhỏ, chạy được trên gói miễn phí/rẻ | Cần máy chủ n8n riêng (RAM lớn hơn) hoặc n8n Cloud trả phí |
| Phụ thuộc | Chỉ 1 thư viện (`@anthropic-ai/sdk`) | Cả nền tảng n8n |
| Bán cho khách | Bàn giao mã nguồn gọn | Bàn giao file JSON + yêu cầu khách có n8n |

Khi cần nối thêm CRM/phần mềm bán hàng cho khách, có thể để Node.js gọi sang n8n/Make sau.

---

## 3. Cách hoạt động

```
Meta / Zalo ──webhook──▶ server.js ──xác thực chữ ký──▶ normalize.js (chuẩn hóa sự kiện)
     ▼
pipeline.js: chống trùng → giới hạn tần suất → brain.js (luật an toàn + Claude + tri thức)
     ▼                                       ▼
guard.js chặn: giá không có trong tri thức, hứa thời gian phản hồi, nội dung cấm, email
     ▼
DRY_RUN=true  → ghi nháp (data/nhap-tra-loi.jsonl)        DRY_RUN=false → gửi qua Meta/Zalo API
     ▼
Ghi khách tiềm năng: Google Sheets (nếu cấu hình) hoặc data/khach-tiem-nang.csv
```

**Nhãn:** `hoi_gia`, `dat_lich_tu_van`, `hoi_demo`, `khieu_nai`, `khac`.

**Quy tắc trả lời** (trong `src/brain.js`, phần prompt hệ thống):
- Chỉ trả lời theo tri thức đã duyệt trong `knowledge/` (dịch vụ, giá gói Cơ bản/Chuyên nghiệp/Cao cấp chưa VAT, quy trình 5 bước, tư vấn 30 phút miễn phí).
- Không bịa giá, khách hàng, số liệu. Không hứa thời gian phản hồi.
- **Khiếu nại, báo giá riêng, giảm giá, hợp đồng, câu khó, đặt lịch** → gắn `chuyen_nguoi_that` để người thật xử lý.
- **Spam** → bỏ qua, không trả lời, không ghi vào danh sách khách.
- **Bình luận công khai** → trả lời ngắn, không nêu giá, mời xem tin nhắn; chi tiết gửi riêng (private reply).

**Lớp an toàn chạy cả khi có Claude:** luật từ khóa (`src/classify.js`) luôn ép khiếu nại/yêu cầu riêng sang người thật; `src/guard.js` kiểm tra mọi câu trả lời, nếu vi phạm thì thay bằng câu mẫu đã duyệt (`src/templates.js`) và chuyển người thật. Không có `ANTHROPIC_API_KEY` thì trợ lý vẫn chạy bằng luật + câu mẫu.

**Cột ghi vào Sheets/CSV:** thời gian, tên, kênh, nội dung, nhãn, trạng thái, cần người thật, lý do chuyển, câu trả lời công khai, tin nhắn riêng, mã sự kiện, nguồn (claude/luật/mẫu).
Trạng thái: `nhap_cho_duyet`, `da_tra_loi`, `chuyen_nguoi_that`, `loi_gui`.

---

## 4. Cập nhật tri thức

Sửa các file trong `knowledge/` (Markdown thường). Khi giá trên dreamlabs.vn thay đổi, sửa `knowledge/10-dich-vu-bang-gia.md` **và** câu mẫu giá trong `src/templates.js`, rồi chạy `npm test`. Lớp kiểm tra tự lấy danh sách giá hợp lệ từ tri thức: giá nào không có trong file sẽ bị chặn.

---

## 5. Bật thật từng bước

Ký hiệu: 🔐 = chủ studio phải **tự đăng nhập**, 💳 = có thể **phát sinh phí**.

### 5.1 Khóa Claude API 🔐💳
1. Đăng nhập console của Anthropic, tạo API key, nạp tiền (tính theo lượng dùng).
2. Điền `ANTHROPIC_API_KEY` vào `.env` (hoặc biến môi trường nơi triển khai). Model mặc định: `claude-opus-5-5`.

### 5.2 Meta: Facebook Page + Messenger + Instagram 🔐
1. Instagram `dreamlabs.vn` phải là **tài khoản Business/Creator** và **liên kết với Facebook Page** của Dream Labs.
2. Vào **Meta for Developers** → *Create App* → loại *Business*. Thêm sản phẩm **Messenger**, **Instagram** (API setup with Facebook Login) và **Webhooks**.
3. Lấy **App Secret** (Settings → Basic) → `META_APP_SECRET`. Tự đặt một chuỗi ngẫu nhiên cho `META_VERIFY_TOKEN`.
4. Tạo **Page Access Token** dài hạn cho Page (qua Graph API Explorer hoặc trang Messenger settings) → `META_PAGE_ACCESS_TOKEN`; ghi `META_PAGE_ID` và `IG_USER_ID` (ID tài khoản Instagram Business).
5. **Quyền cần xin:**
   - `pages_show_list`, `pages_read_engagement`, `pages_read_user_content` – đọc bình luận trên Page.
   - `pages_manage_engagement` – trả lời bình luận Facebook.
   - `pages_messaging` – trả lời Messenger và nhắn riêng cho người bình luận.
   - `pages_manage_metadata` – đăng ký webhook cho Page.
   - `instagram_basic`, `instagram_manage_comments` – đọc/trả lời bình luận Instagram.
   - `instagram_manage_messages` – trả lời tin nhắn Instagram.
   - (thường cần thêm `business_management` nếu Page nằm trong Business Manager).
6. **Đăng ký webhook** (sau khi đã triển khai, mục 5.5): Callback URL `https://<tên-miền>/webhook/meta`, Verify token = `META_VERIFY_TOKEN`.
   - Đối tượng **Page**: tích `feed` và `messages`.
   - Đối tượng **Instagram**: tích `comments` và `messages`.
   - Nhấn *Subscribe* Page vào app (Messenger settings → Webhooks → chọn Page).
7. **App Review** 🔐: ở chế độ Development, app chỉ hoạt động với người có vai trò trong app (admin/tester) – đủ để thử nội bộ. Để trả lời khách thật cần gửi **App Review** cho các quyền trên, kèm: **xác minh doanh nghiệp** (Business Verification), **URL chính sách quyền riêng tư** trên dreamlabs.vn, video quay màn hình mô tả cách dùng từng quyền. Duyệt xong mới chuyển app sang **Live**.
8. Lưu ý chính sách: Messenger/Instagram chỉ cho trả lời tự do trong **24 giờ** kể từ tin nhắn cuối của khách; nhắn riêng cho người bình luận (private reply) chỉ **1 lần/bình luận** trong 7 ngày.

### 5.3 Zalo OA 🔐💳
1. OA Dream Labs cần **đã xác thực** (tài khoản doanh nghiệp). Kiểm tra gói dịch vụ OA hiện hành của Zalo – một số API/tin nhắn có thể **tính phí**.
2. Vào **Zalo for Developers** → tạo ứng dụng → liên kết với OA → lấy **App ID** (`ZALO_APP_ID`), **OA Secret Key** (`ZALO_OA_SECRET_KEY`), `ZALO_OA_ID`.
3. Cấp quyền cho ứng dụng truy cập OA, lấy **OA Access Token** (`ZALO_OA_ACCESS_TOKEN`). Token Zalo **hết hạn sau khoảng 1 ngày** và cần làm mới bằng refresh token – bản này chưa tự làm mới; trước khi chạy thật lâu dài cần bổ sung bước này (hoặc dùng n8n/Make để làm mới định kỳ).
4. Cấu hình **Webhook** của ứng dụng: URL `https://<tên-miền>/webhook/zalo`, bật sự kiện **người dùng gửi tin nhắn văn bản** (`user_send_text`). Trợ lý kiểm tra chữ ký header `X-ZEvent-Signature` (= `mac=` + SHA-256 của `app_id + body + timestamp + OA Secret Key`); đối chiếu lại tài liệu Zalo mới nhất khi bật.
5. Zalo chỉ cho OA gửi **tin tư vấn** trong khung thời gian giới hạn sau khi người dùng nhắn – xem điều khoản hiện hành.

### 5.4 Google Sheets 🔐
1. Vào **Google Cloud Console** → tạo project → bật **Google Sheets API**.
2. *IAM & Admin → Service Accounts* → tạo service account → *Keys → Add key → JSON*. Tải file về máy (**không** đưa vào repo).
3. Từ file JSON: `client_email` → `GOOGLE_SA_CLIENT_EMAIL`, `private_key` → `GOOGLE_SA_PRIVATE_KEY` (giữ nguyên `\n`, đặt trong dấu ngoặc kép).
4. Tạo Google Sheet mới, đặt tên tab `KhachTiemNang`, dòng 1 ghi tiêu đề:
   `thoi_gian | ten | kenh | noi_dung | nhan | trang_thai | can_nguoi_that | ly_do_chuyen | tra_loi_cong_khai | tin_nhan_rieng | ma_su_kien | nguon`
5. Bấm **Share** sheet cho địa chỉ `client_email` của service account với quyền **Editor**. ID sheet (đoạn giữa `/d/` và `/edit` trong URL) → `GOOGLE_SHEETS_ID`.
6. Chưa cấu hình Sheets thì trợ lý tự ghi `data/khach-tiem-nang.csv`; Sheets lỗi thì ghi CSV dự phòng.

### 5.5 Triển khai (chi phí thấp) 🔐💳
Cần một địa chỉ **HTTPS công khai** để Meta/Zalo gọi vào. Gợi ý:
- **Render / Railway / Fly.io**: kết nối repo, lệnh chạy `npm start`, thư mục gốc `dreamlab-ai-assistant`, điền biến môi trường trong bảng điều khiển. Gói miễn phí có thể "ngủ" khi không có truy cập (Meta có thể gửi lại sự kiện – trợ lý đã chống trùng); gói trả phí rẻ nhất đủ dùng.
- **VPS nhỏ** (1 vCPU, 1 GB RAM) + Caddy/Nginx làm HTTPS: ổn định nhất, giữ được file `data/`.
- Chạy **1 tiến trình** (bộ chống trùng và giới hạn tần suất nằm trong bộ nhớ + file `data/da-xu-ly.json`).
- Trên nền tảng có ổ đĩa tạm (Render/Railway), file `data/` có thể mất khi khởi động lại → dùng Google Sheets làm nơi lưu chính.

Kiểm tra sau triển khai: mở `https://<tên-miền>/health` → thấy `{"ok":true,"dryRun":true}`.

### 5.6 Bật / tắt chế độ nháp
- **Mặc định `DRY_RUN=true`**: nhận sự kiện thật, soạn câu trả lời, ghi vào `data/nhap-tra-loi.jsonl` và Sheets (trạng thái `nhap_cho_duyet`), **không gửi gì**. Nên chạy vài ngày ở chế độ này để duyệt chất lượng.
- **Gửi thật**: chủ studio tự đổi biến môi trường thành `DRY_RUN=false` rồi khởi động lại. Chỉ đúng chuỗi `false` (hoặc `0`/`no`/`off`) mới tắt nháp; để trống hay ghi sai đều vẫn là nháp.
- **Tắt khẩn cấp**: đặt lại `DRY_RUN=true` và khởi động lại, hoặc tắt webhook trong Meta/Zalo.
- Hàng chờ người thật: lọc cột `can_nguoi_that = co` trong Sheets.

---

## 6. Cấu trúc thư mục

```
knowledge/          tri thức đã duyệt (lấy từ dreamlabs.vn)
src/server.js       máy chủ webhook (Node.js thuần)
src/verify.js       xác thực chữ ký Meta / Zalo
src/normalize.js    chuẩn hóa sự kiện 5 kênh
src/dedupe.js       chống trả lời trùng
src/ratelimit.js    giới hạn tần suất
src/classify.js     luật phân loại + phát hiện spam/khiếu nại
src/brain.js        gọi Claude + quy tắc trả lời
src/guard.js        kiểm tra câu trả lời trước khi lưu/gửi
src/templates.js    câu mẫu đã duyệt
src/senders.js      gửi qua Meta / Zalo (bị chặn khi DRY_RUN=true)
src/sinks.js        ghi Google Sheets / CSV
fixtures/           sự kiện giả cho từng kênh và từng nhãn
scripts/chay-thu.js chạy thử và in câu trả lời
test/               kiểm thử tự động (node --test)
```

## 7. Bảo mật
- Không có khóa, mật khẩu hay email nào trong mã nguồn. Mọi bí mật đọc từ biến môi trường; `.env` và file khóa service account đã nằm trong `.gitignore`.
- Mọi webhook đều phải có chữ ký hợp lệ; thiếu cấu hình bí mật thì từ chối hết.
- Nội dung khách gửi được coi là dữ liệu, không phải chỉ thị cho AI.
