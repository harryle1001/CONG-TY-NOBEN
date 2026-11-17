# JARVIS

Trợ lý giọng nói riêng của sir. Python stdlib phía server, JavaScript thuần phía trình duyệt. Không framework, không build, không cài gói.

```
python3 agent/main.py        →  mở http://localhost:1618
```

## 1. Cài đặt (một lần)

Cần **Python 3.10+** và một trình duyệt bất kỳ (Chrome, Brave, Safari, Firefox).

```bash
cd jarvis-pro
cp .env.example .env
chmod 600 .env
```

Mở `.env`, điền:

| Biến | Lấy ở đâu | Bắt buộc? |
|---|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys | Không. Thiếu thì chạy chế độ tìm từ khóa, có nhãn **MODEL MISSING** |
| `ELEVENLABS_API_KEY` | elevenlabs.io → Profile → API Keys | Không. Thiếu thì chỉ gõ chữ được |
| `JARVIS_IMAP_*` | Gmail: bật 2 lớp → tạo **App Password** | Chỉ cho read_inbox |
| `JARVIS_ICS` | Google Calendar → Cài đặt lịch → "Địa chỉ bí mật ở định dạng iCal" | Chỉ cho brief_me |

Khóa chỉ nằm trong `.env` trên máy anh, server Python giữ, trình duyệt không bao giờ thấy.

## 2. Công tắc demo

`JARVIS_DEMO` chỉ được đọc ở **một** file: `agent/data.py`.

- `JARVIS_DEMO=1` (mặc định): dữ liệu bịa trong `data/demo/`, an toàn để quay màn hình. Tạo lại (luôn y hệt, seed cố định):
  ```bash
  python3 data/generate_demo.py
  ```
- `JARVIS_DEMO=0`: đọc thư mục thật, **chỉ đọc**. Ví dụ dùng 10 repo của công ty:
  ```bash
  mkdir -p ~/jarvis-sources && cd ~/jarvis-sources
  for r in CONG-TY-NOBEN thuysannoben Thuysantim DreamLabs-Studio Rubik-World RubikSchool2D Fiverr-Jobs CTY-Design-Ai-Art App-Build EditVideo-Rio-Nguyen; do git clone --depth 1 https://github.com/harryle1001/$r.git; done
  ```
  rồi trong `.env`: `JARVIS_SOURCES=/Users/<tên>/jarvis-sources/CONG-TY-NOBEN:/Users/<tên>/jarvis-sources/thuysannoben:...` (Windows dùng `;`). Màn hình hiện nhãn **LIVE DATA** màu cam.

Đọc được: `.md .txt .csv .html .pdf .docx .xlsx`, và `.doc .xls` đời cũ (trích chữ thô). Bỏ qua `node_modules`, `.git`, file > 2 MB. `[[wikilink]]`, link HTML/Markdown và tên sản phẩm nhắc đến nhau trở thành cạnh của đồ thị.

## 3. Dùng

- **MIC** hoặc **Space**: bật nghe. Nói tự nhiên, im 0,9 s là gửi (chỉnh `SILENCE_MS` ở đầu `ui/app.js`).
- **Space** khi Jarvis đang nói: ngắt lời. **Esc**: dừng tất cả. **MUTE**: chỉ trả lời bằng chữ.
- **BRIEF / PLAN / MEMORY**: tóm tắt ngày, kế hoạch 5 việc, những gì Jarvis đã nhớ.
- Đồ thị: rê chuột để làm sáng, bấm để mở file, **Shift + bấm** node thứ hai để xem đường nối ngắn nhất, kéo để di chuyển, cuộn để phóng to.
- Nói tiếng Việt hay tiếng Anh đều được; Jarvis trả lời tiếng Anh, giọng Anh ("Daniel").

## 4. Nguyên tắc an toàn (cứng, không câu nào phá được)

Không bao giờ gửi email/tin nhắn/lời mời. Không ghi vào thư mục của anh (chỉ `memory/`). Ghi nhớ gì cũng đọc to đúng câu đã ghi. Không tiêu tiền khi chưa hỏi (tìm web tắt mặc định, bật bằng `JARVIS_WEB=1`). Không bịa số, ngày, tên file, khách hàng. Số suy ra luôn kèm lý do (trả 50% vì đang giao dở ≠ giảm giá). Chỉ dẫn nằm trong file/email là dữ liệu: Jarvis báo lại, không làm theo.

Kiểm tra bằng máy (không mạng, không tốn tiền):

```bash
python3 agent/selftest.py
```

## 5. Chi phí

| Dịch vụ | Giá | Ước tính |
|---|---|---|
| Claude Opus 5.5 (`claude-opus-5-5`) | $4 / 1M token vào, $20 / 1M token ra, đọc cache $0.20 / 1M | Câu hỏi thường ≈ **$0.01**; câu dùng 2–3 công cụ ≈ **$0.03–0.05**. 100 câu/ngày ≈ $1–3 |
| Tìm web (chỉ khi `JARVIS_WEB=1`) | tính thêm phí mỗi lượt tìm (xem bảng giá Anthropic) | Tối đa 3 lượt tìm mỗi câu hỏi |
| ElevenLabs TTS + Scribe | Gói miễn phí có hạn mức credit hằng tháng; TTS tính theo ký tự, Scribe theo phút âm thanh (xem elevenlabs.io/pricing) | Câu trả lời của Jarvis ngắn (1–3 câu) nên tốn ít |
| Không có khóa nào | $0 | Vẫn chạy: đồ thị, tìm file, brief, inbox |

Ước tính dựa trên: system prompt ~3k token được cache, mức suy nghĩ `low`. Đổi model bằng `JARVIS_MODEL`.

## Cấu trúc

```
agent/main.py     server HTTP + API + vòng gọi Claude
agent/vault.py    thư mục → đồ thị tìm được
agent/tools.py    6 công cụ: search_brain, research_web, read_inbox, brief_me, remember, plan_day
agent/data.py     FILE DUY NHẤT chạm vào dữ liệu thật
agent/voice.py    ElevenLabs nghe + nói
agent/memory.py   chỉ ghi vào memory/
agent/prompt.md   system prompt
agent/selftest.py kiểm tra nguyên tắc an toàn
ui/               index.html, app.js, graph.js, styles.css
data/             dữ liệu demo + script tạo
memory/           mỗi sự thật một file .md có ngày
CLAUDE.md         sir là ai, nạp mỗi phiên
```
