#!/usr/bin/env python3
"""Sinh mau-quang-cao-google.md và kiểm tra giới hạn ký tự Google Ads.
Chạy: python3 dem-ky-tu.py  (sửa nội dung trong ADS rồi chạy lại)
Đếm theo Unicode NFC: mỗi chữ có dấu tiếng Việt = 1 ký tự (như Google Ads)."""
import unicodedata, sys, pathlib
L = lambda s: len(unicodedata.normalize('NFC', s))
LIM = {'h': 30, 'd': 90, 'path': 15, 'sl': 25, 'sld': 35, 'co': 25}

ADS = [
 {'g': '1. Thiết kế website / landing page',
  'url': 'https://dreamlabs.vn/#p-web', 'path': ['thiet-ke', 'website'],
  'h': ['Thiết Kế Website Cao Cấp', 'Dream Labs – Studio TP.HCM', 'Website Từ 8.000.000đ',
        'Landing Page Từ 3.000.000đ', 'Thiết Kế Riêng Cho Thương Hiệu', 'Chuẩn SEO, Tải Nhanh',
        'Đẹp Trên Mọi Điện Thoại', 'Có Form Liên Hệ Và Nút Zalo', 'Landing Page Cho Quảng Cáo',
        'Nhắn Zalo Nhận Báo Giá', 'Xem Bảng Giá Công Khai', 'Tự Sửa Nội Dung Bằng CMS',
        'Bàn Giao Mã Nguồn, File Gốc', 'Landing Page Giao 3–5 Ngày', 'Gắn Sẵn Pixel Và GA4'],
  'd': ['Website thương hiệu cao cấp, tải nhanh, chuẩn SEO, tự quản trị nội dung. Xem giá ngay.',
        'Landing page tối ưu chuyển đổi cho quảng cáo: form thu lead, gắn Facebook Pixel, GA4.',
        'Bảng giá công khai: website từ 8.000.000đ, landing page từ 3.000.000đ. Nhắn Zalo.',
        'Quy trình 5 bước, cập nhật tiến độ mỗi 3 ngày, kiểm thử trên điện thoại thật.']},
 {'g': '2. Tự động hóa quy trình bằng AI',
  'url': 'https://dreamlabs.vn/#p-ai', 'path': ['tu-dong-hoa', 'ai'],
  'h': ['Tự Động Hóa Quy Trình Bằng AI', 'Trợ Lý AI Trả Lời Zalo OA', 'Trợ Lý AI Cho Messenger',
        'Tự Động Hóa Từ 5.000.000đ', 'Kết Nối CRM, Phần Mềm Bán Hàng', 'Đồng Bộ Dữ Liệu Google Sheets',
        'Báo Cáo Tự Động Bằng AI', 'AI Trả Lời Khách 24/7', 'Bớt Việc Lặp Lại Cho Đội Ngũ',
        'Dream Labs – Studio TP.HCM', 'Gói Khởi Động 5–7 Ngày', 'Đào Tạo Đội Ngũ Vận Hành',
        'AI Chuyển Khách Cho Nhân Viên', 'Nhắn Zalo Nhận Báo Giá', 'Thử Demo Trợ Lý AI Trên Web'],
  'd': ['Tự động hóa bán hàng, chăm sóc khách, kế toán, báo cáo bằng AI. Nhanh hơn, ít sai sót.',
        'Trợ lý AI trả lời khách trên Zalo OA, Messenger 24/7; đồng bộ dữ liệu về Google Sheets.',
        'Gói Khởi động từ 5.000.000đ, làm trong 5–7 ngày, hỗ trợ 1 tháng. Nhắn Zalo để tư vấn.',
        'Kết nối CRM, phần mềm bán hàng, kế toán. Đào tạo đội ngũ vận hành khi bàn giao.']},
 {'g': '3. Thiết kế bao bì + video / motion',
  'url': 'https://dreamlabs.vn/#p-product', 'path': ['bao-bi', 'video'],
  'h': ['Thiết Kế Bao Bì Sản Phẩm', 'Thiết Kế Nhãn Mác Chuẩn In', 'Bao Bì Từ 2.000.000đ',
        'Mockup 3D Cho Quảng Cáo', 'File In Ấn Chuẩn CMYK', 'Video Motion Graphic',
        'Motion Graphic Từ 3.000.000đ', 'Edit Video Từ 800.000đ', 'Dựng Video Reels, TikTok',
        'Logo Animation, Intro', 'Hỗ Trợ Làm Việc Với Nhà In', 'Xuất Video 9:16, 1:1, 16:9',
        'Dream Labs – Studio TP.HCM', 'Nhắn Zalo Nhận Báo Giá', 'Xem Mẫu Concept Trên Web'],
  'd': ['Bao bì, nhãn mác, nhận diện và mockup 3D sẵn sàng in ấn. 2–3 phương án ý tưởng.',
        'Motion graphic giải thích sản phẩm, logo animation, intro thương hiệu. Từ 3.000.000đ.',
        'Edit video quảng cáo, TikTok, Reels, YouTube từ footage của bạn. Từ 800.000đ/video.',
        'Bảng giá công khai trên web. Nhắn Zalo để gửi brief và nhận báo giá theo nhu cầu.']},
]
SITELINKS = [  # (chữ ≤25, mô tả 1 ≤35, mô tả 2 ≤35, url)
 ('Bảng giá Website', 'Gói Cơ bản, Chuyên nghiệp, Cao cấp', 'Từ 8.000.000đ, 7–45 ngày', 'https://dreamlabs.vn/#p-web'),
 ('Bảng giá Landing Page', 'Tối ưu cho chiến dịch quảng cáo', 'Từ 3.000.000đ, 3–10 ngày', 'https://dreamlabs.vn/#p-landing'),
 ('Tự động hóa bằng AI', 'Trợ lý AI Zalo OA, Messenger', 'Gói Khởi động từ 5.000.000đ', 'https://dreamlabs.vn/#p-ai'),
 ('Bao bì & Motion', 'Bao bì từ 2.000.000đ', 'Motion graphic từ 3.000.000đ', 'https://dreamlabs.vn/#p-product'),
 ('Dự án mẫu (concept)', 'Xem các mẫu concept của studio', 'Website, landing, video', 'https://dreamlabs.vn/#du-an'),
 ('Quy trình làm việc', '5 bước từ brief đến bàn giao', 'Cập nhật tiến độ mỗi 3 ngày', 'https://dreamlabs.vn/#quy-trinh'),
 ('Liên hệ báo giá', 'Nhắn Zalo hoặc điền form', 'Phản hồi trong giờ làm việc', 'https://dreamlabs.vn/#lien-he'),
]
CALLOUTS = ['Bảng giá công khai', 'Thiết kế riêng', 'Chuẩn SEO, tải nhanh', 'Bàn giao mã nguồn',
            'Kiểm thử trên điện thoại', 'Cập nhật tiến độ 3 ngày', 'Hỗ trợ sau bàn giao', 'Nhắn Zalo tư vấn']

err = []
def chk(kind, s):
    n = L(s)
    if n > LIM[kind]: err.append(f'QUÁ GIỚI HẠN {kind} ({n}>{LIM[kind]}): {s}')
    return n
out = ['# Mẫu quảng cáo Google Search (RSA) — Dream Labs', '',
       '> File này do `dem-ky-tu.py` sinh ra. Sửa nội dung trong script rồi chạy `python3 dem-ky-tu.py` để đếm lại ký tự.',
       '> Giới hạn: tiêu đề ≤30, mô tả ≤90, đường dẫn hiển thị ≤15/ô, liên kết trang web ≤25 (mô tả ≤35), chú thích ≤25.',
       '> Không ghi số điện thoại trong tiêu đề/mô tả (Google cấm) — số chỉ nằm ở tiện ích cuộc gọi.', '']
for a in ADS:
    assert len(a['h']) == 15 and len(a['d']) == 4 and len(set(a['h'])) == 15
    out += [f"## Nhóm {a['g']}", '',
            f"- **URL cuối cùng:** `{a['url']}`",
            f"- **Đường dẫn hiển thị:** dreamlabs.vn/{a['path'][0]}/{a['path'][1]} "
            f"({chk('path', a['path'][0])} + {chk('path', a['path'][1])} ký tự)", '',
            '| # | Tiêu đề | Ký tự |', '|---|---|---|']
    out += [f'| {i} | {h} | {chk("h", h)} |' for i, h in enumerate(a['h'], 1)]
    out += ['', '| # | Mô tả | Ký tự |', '|---|---|---|']
    out += [f'| {i} | {d} | {chk("d", d)} |' for i, d in enumerate(a['d'], 1)]
    out += ['', 'Ghim (tùy chọn): tiêu đề 1 ở vị trí 1. Không ghim thêm để Google tự thử tổ hợp.', '']
out += ['## Tiện ích (dùng chung cấp chiến dịch)', '',
        '### Cuộc gọi', '- Số: **0934 246 420** (Việt Nam). Lịch hiển thị: T2–T7, 08:00–20:00. Bật "Báo cáo cuộc gọi" nếu có.', '',
        '### Liên kết trang web', '', '| Chữ liên kết | Ký tự | Mô tả 1 | Ký tự | Mô tả 2 | Ký tự | URL |', '|---|---|---|---|---|---|---|']
for t, d1, d2, u in SITELINKS:
    out.append(f'| {t} | {chk("sl", t)} | {d1} | {chk("sld", d1)} | {d2} | {chk("sld", d2)} | `{u}` |')
out += ['', '### Chú thích', '', '| Chú thích | Ký tự |', '|---|---|']
out += [f'| {c} | {chk("co", c)} |' for c in CALLOUTS]
out += ['', '## Ghi chú URL (đã kiểm tra trong mã nguồn web, bản sao `dreamlab/`)', '',
        '- Web là **một trang** (`sitemap.xml` chỉ có `https://dreamlabs.vn/`). Các "trang dịch vụ" là neo trong trang:',
        '  `#p-web, #p-landing, #p-ai, #p-product, #p-motion, #p-video` (sinh bởi `js/core.js` dòng 79), `#du-an, #quy-trinh, #lien-he, #dich-vu, #tu-dong-hoa` (partials).',
        '- Từ khóa video/motion trong nhóm 3: đặt **URL cuối cùng cấp từ khóa** = `https://dreamlabs.vn/#p-motion` hoặc `#p-video` (xem `tu-khoa-google.md`).',
        '- Nếu Google báo trùng URL liên kết trang web (chỉ khác phần `#`) hoặc không chấp nhận: đổi URL liên kết về `https://dreamlabs.vn/` hoặc làm trang con riêng (việc cần chủ studio quyết).', '']
if err:
    print('\n'.join(err)); sys.exit(1)
p = pathlib.Path(__file__).with_name('mau-quang-cao-google.md')
p.write_text('\n'.join(out), encoding='utf-8')
print('OK, đã ghi', p.name, '— mọi dòng trong giới hạn ký tự')
