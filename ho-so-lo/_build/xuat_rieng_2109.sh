#!/bin/bash
# Bộ hồ sơ 21.09.2026 dạng file rời, giao diện như mẫu tham khảo:
# 6 hồ sơ lô + 1 phiếu QD7 (.xls) + 1 lệnh SX + 1 dán mẫu lưu + 1 biểu mẫu 12 quy định (2–12, mỗi biểu mẫu 1 trang mới).
# Dùng: xuat_rieng_2109.sh <thư mục mẫu 04.09> <thư mục tạm>
set -e
REF="$1"; TMP="$2/rieng"; R="$(cd "$(dirname "$0")/../.." && pwd)"; B="$R/ho-so-lo/_build"
O="$R/ho-so-lo/HO-SO-21.09.2026/BO-HO-SO-LO-21.09.2026"
rm -rf "$TMP" "$O" && mkdir -p "$TMP" "$O"
MAU_GOC=1 python3 -I "$B/build_2109.py" "$REF" "$TMP" >/dev/null
# hồ sơ lô (bản đã duyệt)
for f in "$R"/ho-so-lo/word/*.docx; do cp "$f" "$O/"; done
python3 -I "$B/compact.py" "$O"/*.docx >/dev/null
# lệnh SX, dán mẫu lưu
cp "$TMP"/2-*/*.docx "$O/2. LỆNH SẢN XUẤT 21.09.2026.docx"
cp "$TMP"/4-*/*.docx "$O/DÁN MẪU LƯU 21.09.2026.docx"
# phiếu QD7 -> .xls như mẫu
(cd "$TMP"/3-* && soffice --headless --convert-to xls --outdir "$O" *.xlsx >/dev/null 2>&1)
# biểu mẫu 2–12 gộp 1 file, mỗi biểu mẫu sang trang mới
python3 -I "$B/compact.py" "$TMP"/5-*/*.docx >/dev/null
BMD=(); for i in 2 3 4 5 6 7 8 9 10 11 12; do BMD+=("$TMP"/5-*/"$i."*.docx); done
python3 -I "$B/gop_bieu_mau.py" "$O/BIỂU MẪU 12 QUY ĐỊNH 21.09.2026.docx" --ngat-trang "${BMD[@]}" >/dev/null
python3 -I "$B/bm_moi_phieu.py" "$O/BIỂU MẪU 12 QUY ĐỊNH 21.09.2026.docx" >/dev/null
python3 -I "$B/viet_thuong.py" "$O"/*.docx >/dev/null
cd "$O"; mkdir -p PDF
for f in *.docx *.xls; do soffice --headless --convert-to pdf --outdir PDF "$f" >/dev/null 2>&1; done
for f in PDF/*.pdf; do echo "$(pdfinfo "$f" | awk '/Pages/{print $2}') trang: $f"; done
