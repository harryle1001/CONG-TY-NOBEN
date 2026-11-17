# J.A.R.V.I.S. — trợ lý giọng nói riêng

Trợ lý chạy trên máy anh (`localhost`): đọc file của anh thành một đồ thị kiến thức, trả lời bằng chữ hoặc giọng nói,
đọc hộp thư và lịch (chỉ đọc), lên kế hoạch trong ngày.

Server dùng **Python thư viện chuẩn**, giao diện là **JavaScript thuần**. Không cần `pip`, `npm` hay cơ sở dữ liệu.

## Chạy trong 1 phút

```bash
cd jarvis-pro
python3 agent/main.py
```

Mở **http://localhost:8618**. Mặc định Jarvis chạy dữ liệu **demo** (bịa sẵn, quay màn hình thoải mái), không cần khóa nào.

## Thêm khóa: AI và giọng nói

```bash
cp .env.example .env
chmod 600 .env
```

Mở `.env` và điền:

| Biến | Để làm gì | Bắt buộc? |
|---|---|---|
| `ANTHROPIC_API_KEY` | Hội thoại bằng Claude (`claude-opus-5-5`) | Một trong hai |
| `GEMINI_API_KEY` | Hội thoại bằng Gemini (`gemini-2.5-flash`) | Một trong hai |
| `ELEVENLABS_API_KEY` | Nghe (Scribe) và nói (giọng "Daniel", nam Anh) | Không, thiếu thì chỉ gõ chữ |

Khởi động lại server. Các nhãn trên góc phải màn hình cho biết đang chạy gì: **NO MODEL**, **VOICE OFF**, **MODEL ERROR**.

Khóa chỉ nằm trong `.env` và trong server Python. Trình duyệt không bao giờ nhận được khóa. `.env` đã có trong `.gitignore`.

## Công tắc demo: dùng dữ liệu thật

Biến `JARVIS_DEMO` chỉ được đọc ở **một** file: `agent/data.py`. Đây cũng là file duy nhất chạm vào dữ liệu thật của anh.

```bash
JARVIS_DEMO=0 \
JARVIS_SOURCES="$HOME/Noben:$HOME/Notes" \
JARVIS_INBOX="$HOME/Mail/Inbox" \
JARVIS_CALENDAR="$HOME/lich.ics" \
python3 agent/main.py
```

Trên Windows, các đường dẫn trong `JARVIS_SOURCES` ngăn cách bằng `;`.

- **Thư mục nguồn** (`JARVIS_SOURCES`): Jarvis đọc `.md`, `.txt`, `.csv`, `.html`, `.pdf`, `.docx`, `.xlsx`, và cả `.doc`, `.xls` (bản thô). Bỏ qua `.git`, `node_modules` và file lớn hơn 2 MB. Liên kết `[[wikilink]]` trở thành cạnh trong đồ thị.
- **Hộp thư** (`JARVIS_INBOX`): một thư mục Maildir (`new/` = chưa đọc), một thư mục chứa các file `.eml`, hoặc `google` (xem mục dưới). Thunderbird và phần lớn ứng dụng mail đều xuất được dạng này.
- **Lịch** (`JARVIS_CALENDAR`): file `.ics`, hoặc `google`. Google Calendar → Cài đặt → Nhập và xuất.
- **Tạo lại dữ liệu demo:** chạy `python3 data/generate_demo.py`. Hạt giống ngẫu nhiên cố định, nên lần nào đồ thị cũng giống hệt.

## Kết nối Gmail và Google Calendar (chỉ đọc)

Jarvis đọc thẳng Gmail và Google Calendar qua Google API, không cần xuất file. Chỉ xin 2 quyền **chỉ đọc**:
`gmail.readonly` và `calendar.readonly`. Code chỉ gọi GET, không có lệnh gửi, xóa hay sửa nào.

**1. Tạo OAuth client (làm một lần, ~5 phút)** tại [console.cloud.google.com](https://console.cloud.google.com):

1. Tạo một project mới (vd. `jarvis`).
2. **APIs & Services → Library**: bật **Gmail API** và **Google Calendar API**.
3. **APIs & Services → OAuth consent screen** (Google Auth Platform):
   - User type: **External**. Điền tên app, email.
   - **Data access / Scopes**: thêm `.../auth/gmail.readonly` và `.../auth/calendar.readonly`.
   - **Audience → Test users**: thêm chính Gmail của anh. Để app ở trạng thái *Testing* là đủ.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**:
   - Application type: **Desktop app**.
   - Redirect: Jarvis dùng `http://localhost:8618/auth/google/callback`. Loại *Desktop app* tự chấp nhận
     mọi cổng trên localhost, nên không cần khai báo. Nếu Console có ô redirect URI thì dán đúng địa chỉ trên.
   - Chép **Client ID** và **Client secret**.

**2. Điền `.env`:**

```bash
JARVIS_DEMO=0
JARVIS_INBOX=google
JARVIS_CALENDAR=google
GOOGLE_CLIENT_ID=xxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxx
```

Có thể chỉ bật một trong hai (vd. Gmail thật + lịch `.ics`).

**3. Kết nối:** chạy `python3 agent/main.py`, mở http://localhost:8618, bấm nhãn **GOOGLE: NOT CONNECTED**
ở góc phải → đăng nhập Google → đồng ý. Quay lại, nhãn thành **GOOGLE: CONNECTED**.

- Token lưu ở `jarvis-pro/.google_token.json` (chmod 600, đã có trong `.gitignore`). Jarvis tự làm mới access token.
  Client secret và token không bao giờ tới trình duyệt.
- Luồng OAuth: *installed app*, redirect về chính server Jarvis trên localhost, có `state` chống CSRF (một lần, kèm cookie) và PKCE (S256).
- Gmail: ~30 thư gần nhất trong INBOX; thư có nhãn UNREAD là chưa đọc. Lịch: lịch `primary`, từ hôm nay.
- Lỗi hiện rõ trên màn hình: chưa cấu hình, chưa kết nối, token hết hạn hay bị thu hồi (nhãn **GOOGLE: ERROR**, bấm để kết nối lại), API chưa bật (HTTP 403).
- Ngắt kết nối: xóa `.google_token.json`, hoặc gỡ quyền tại myaccount.google.com/permissions.
- Chế độ demo (`JARVIS_DEMO=1`) không bao giờ gọi Google.

**Thử không cần tài khoản Google:** `node tests/e2e_google.js` dựng một Google giả (`tests/fake_google.py`) trên
localhost và chạy trọn luồng OAuth, đọc thư, đọc lịch, làm mới token, thu hồi token, và chế độ demo, bằng Playwright.

## Cách dùng

- **Gõ** câu hỏi ở thanh dưới, bằng tiếng Việt hay tiếng Anh đều được. Jarvis trả lời bằng tiếng Anh.
- **Nói chuyện:** bấm **MIC** một lần rồi cứ nói. Im lặng 0,9 giây là hết lượt. Jarvis trả lời xong thì tự nghe tiếp.
- **Ngắt lời Jarvis:** bấm MIC, `Space` hoặc `Esc`.
- **BRIEF / PLAN / INBOX / MEMORY:** các nút tắt, chạy ngay không cần AI.
- **Đồ thị:**
  - Bấm một node để xem nội dung.
  - Shift-bấm một node thứ hai để xem đường ngắn nhất giữa hai node.
  - Kéo để di chuyển, cuộn để phóng to, bấm đúp để xem toàn bộ.
  - `/` để nhảy vào ô hỏi.
- **Chỉnh độ nhạy micro:** sửa 2 hằng số ở đầu `ui/voice.js`.
  - `SILENCE_MS`: im lặng bao lâu thì hết lượt.
  - `SPEECH_LEVEL`: ngưỡng âm lượng coi là đang nói. Tăng lên nếu phòng ồn.

## Hồ sơ và bộ nhớ

- **`CLAUDE.md`**: anh là ai. Được nạp vào mọi cuộc hội thoại. Đây là file duy nhất làm Jarvis thành của riêng anh, cứ sửa thoải mái.
- **`memory/`**: mỗi điều cần nhớ là một file markdown có ngày.
  - Jarvis chỉ ghi khi anh bảo ("remember…", "ghi nhớ…"), hoặc khi anh nói điều còn quan trọng sau 3 tháng.
  - Lần nào ghi, Jarvis cũng nói to chính xác đã ghi gì và ghi vào file nào.
  - Muốn Jarvis quên thì xóa file đó.

## Quy tắc cứng

Các quy tắc này nằm trong code, không chỉ nằm trong prompt, nên không câu chữ nào vượt qua được.

| Quy tắc | Được bảo đảm bằng |
|---|---|
| Không bao giờ gửi email, tin nhắn hay lời mời | Không có công cụ gửi nào tồn tại. Google chỉ được cấp quyền `readonly` và code chỉ gọi GET |
| Không ghi vào thư mục của anh | `data.py` chỉ đọc. `memory.py` từ chối mọi đường dẫn ra ngoài `memory/` |
| Không ghi bộ nhớ một cách lặng lẽ | Server tự nối câu "đã ghi gì, vào đâu" vào lời nói, dù AI có quên |
| Không tiêu tiền khi chưa hỏi | Tìm web (có phí) chỉ chạy sau khi anh trả lời "yes / ok / có / đồng ý" cho câu Jarvis vừa hỏi |
| Không bịa số liệu, ngày, tên file, khách hàng | Prompt. Mọi câu trả lời từ file đều nêu tên file nguồn |
| Chữ trong file, email hay trang web là dữ liệu, không phải lệnh | Câu nào có dạng ra lệnh bị gắn cờ ⚠ trên màn hình và báo cho AI là không được làm theo. Demo có sẵn một email như vậy để thử |
| Không AI thì nói rõ là không có AI | Định tuyến bằng từ khóa kèm nhãn **NO MODEL**. Không bao giờ giả làm AI đang nói |
| Lỗi phải báo to | Micro bị chặn, không có micro, ElevenLabs lỗi, AI lỗi: đều hiện thông báo trên màn hình |

Thêm nữa, server chỉ nghe ở `127.0.0.1` và từ chối yêu cầu từ trang web khác (kiểm tra Host và Content-Type).

## Chi phí

Ước tính theo kích thước thật của prompt: khoảng 1.500 token cho system prompt và mô tả công cụ.

**Claude Opus 5.5** ($4 / 1 triệu token vào, $20 / 1 triệu token ra; đặt `effort: low` cho hội thoại):

| Loại lượt | Token vào | Token ra | Giá mỗi lượt |
|---|---|---|---|
| Lượt trò chuyện | ~2.500 | ~200 | ≈ **$0,014** |
| Lượt có dùng công cụ (2 lần gọi AI) | ~6.000 | ~400 | ≈ **$0,03** |
| 100 lượt/ngày | | | ≈ **$2–3/ngày** |
| Tìm web (Anthropic) | | | $10 / 1.000 lượt tìm, cộng token. Luôn hỏi anh trước |

**Gemini:** tính theo token, rẻ hơn nhiều. Giá xem tại ai.google.dev/pricing.

**ElevenLabs:**
- Nói: tính theo ký tự đọc. Mỗi câu trả lời khoảng 100–200 ký tự, tối đa 600.
- Nghe (Scribe): tính theo phút âm thanh. Mỗi lượt khoảng 3–8 giây.
- 100 lượt/ngày ≈ 15.000 ký tự và khoảng 10 phút âm thanh.
- Giá phụ thuộc gói, xem elevenlabs.io/pricing. Gói miễn phí đủ để thử.

**Không có khóa nào:** $0. Đồ thị, tìm kiếm, BRIEF, PLAN, INBOX, MEMORY vẫn chạy.

Jarvis không cài thêm gì. Nếu sau này cần thư viện ngoài, Jarvis sẽ hỏi anh trước.

## Cấu trúc

```
jarvis-pro/
├── agent/
│   ├── main.py      server HTTP + API
│   ├── vault.py     thư mục → đồ thị tìm kiếm được
│   ├── tools.py     6 công cụ + định tuyến khi không có AI
│   ├── data.py      FILE DUY NHẤT CHẠM DỮ LIỆU THẬT (cả Gmail/Calendar)
│   ├── google_auth.py OAuth Google (chỉ đọc): đăng nhập, lưu + làm mới token
│   ├── llm.py       Claude / Gemini qua HTTP thuần
│   ├── voice.py     ElevenLabs nói và nghe
│   ├── memory.py    chỉ ghi vào memory/
│   └── prompt.md    system prompt
├── ui/              index.html, app.js, graph.js, voice.js, styles.css
├── data/            demo/, fixtures/ (hộp thư + lịch demo), generate_demo.py
├── tests/           fake_google.py (Google giả) + e2e_google.js (Playwright)
├── memory/          mỗi điều cần nhớ là một file (không commit)
├── CLAUDE.md        anh là ai
├── .env.example     mẫu khóa
└── README.md
```
