# Tài liệu kinh doanh 2026 – Noben & Thủy Sản Tím

| File | Nội dung |
|---|---|
| `BANG-GIA-NOBEN-2026.pdf / .xlsx / .html` | 3 bảng giá Noben hiệu lực 01/05/2026: Bảng giá Noben 2026 (A), Bảng giá Tôm 02-03 (T), Báo giá Noben (B). Excel có thêm sheet "Tong hop" lọc được. |
| `CATALOGUE-NOBEN-2026.pdf / .html` | 74 sản phẩm = mọi tên có trong 3 bảng giá; giá đúng từng bảng (nhãn BG 2026 / BG Tôm / BG (B)); ảnh tách nền từ thuysannoben/public/images/products-cutout. |
| `CATALOGUE-THUY-SAN-TIM-2026.pdf / .html` | 15 sản phẩm Tím; SP trùng tên lấy giá theo bảng giá Noben (7 SP), còn lại "Liên hệ báo giá". |
| `DANH-MUC-SAN-PHAM-NOBEN-TIM-2026.xlsx` | Danh mục 2 thương hiệu dạng bảng. |

**Sửa giá:** sửa `data/bang-gia-noben-2026.json` rồi chạy `python3 build.py` (cần Node + Playwright để xuất PDF; `--no-pdf` để bỏ qua).

- 11 SP trong bảng giá chưa có ảnh/dữ liệu web (BENMER, BENXID 300, NB-MIX 500 NEW, BLUE MAX, BZT – CẮT TẢO, PRAWZYME, NH3 – ROVAZYME, NB CLEAR FOR FISH, HEPALIV – FS, BIOBETS TÔM, TĂNG KIỀM): thẻ chỉ có chữ.
- Ảnh Tím tách nền bằng `tach-nen-tim.py` (rembg) -> `assets/tim-cutout/`.
- Dấu `*` = ô ảnh gốc mờ/gộp, cần đối chiếu: PREMIX KHOÁNG NEW, MRIRAL N.08 (bảng A), NB CLEAR FOR FISH, SUPER VIDAL gói 1kg (bảng T).
- Web: Bảng giá https://claude.ai/artifact/Fad2YjuHP6a2KBKETQCkns · Catalogue Noben https://claude.ai/artifact/9cPgdTUif95GEMCA3xqoQe · Catalogue Tím https://claude.ai/artifact/Tx7dE5pqoDBfTnFBeFQN9q
