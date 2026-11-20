#!/bin/bash
# Dựng lại toàn bộ hồ sơ 21.09.2026: python3/soffice/pdfunite. Dùng: lam_bo_2109.sh <thư mục mẫu 04.09> <thư mục tạm>
set -e
REF="$1"; TMP="$2"; R="$(cd "$(dirname "$0")/../.." && pwd)"; O="$R/ho-so-lo/HO-SO-21.09.2026"
python3 -I "$R/ho-so-lo/_build/build_2109.py" "$REF" "$O" >/dev/null
cp "$R"/ho-so-lo/word/*.docx "$O/1-Ho-so-lo/"
rm -f "$O"/5-*/BIEU-MAU-*.docx
python3 -I "$R/ho-so-lo/_build/compact.py" "$O"/*/*.docx "$O"/3-*/*.xlsx >/dev/null
BMD=(); for i in 2 3 4 5 6 7 8 9 10 11 12; do BMD+=("$O"/5-*/"$i."*.docx); done
GOP="$O/5-Bieu-mau-12-quy-dinh/BIEU-MAU-2-12-GOP-21.09.2026.docx"
python3 -I "$R/ho-so-lo/_build/gop_bieu_mau.py" "$GOP" "${BMD[@]}" >/dev/null
python3 -I "$R/ho-so-lo/_build/compact.py" "$GOP" >/dev/null
rm -rf "$TMP/pdf" && mkdir -p "$TMP/pdf" && cd "$O"
for f in 1-*/*.docx 2-*/*.docx 3-*/*.xlsx 4-*/*.docx 5-*/*.docx; do
  soffice --headless --convert-to pdf --outdir "$TMP/pdf/$(dirname "$f")" "$f" >/dev/null 2>&1; done
cd "$TMP/pdf"
pdfseparate -f 1 -l 1 3-*/*.pdf qd7p1.pdf; pdfseparate -f 1 -l 1 2-*/*.pdf lsx1.pdf
BM=(5-*/BIEU-MAU-2-12-GOP-21.09.2026.pdf)
H=1-Ho-so-lo
pdfunite "$H/HSO LÔ C MAX 25% 21.09.2026.pdf" "$H/HSO LÔ YUCCA 99 21.09.2026.pdf" "$H/HS BZT 21.09.2026.pdf" \
  "$H/HS LÔ IODIN 99 21.09.2026.pdf" "$H/HSO EDTA 99 21.09.2026.pdf" "$H/HSO LÔ BEN COPPER 500 21.09.2026.pdf" \
  2-*/*.pdf qd7p1.pdf 4-*/*.pdf "${BM[@]}" "$O/BO-HO-SO-21.09.2026.pdf"
pdfunite "$H/HSO LÔ C MAX 25% 21.09.2026.pdf" lsx1.pdf qd7p1.pdf 4-*/*.pdf "${BM[@]}" "$O/XEM-THU-1-BO-C-MAX-25.pdf"
for f in "$O"/*.pdf; do echo "$(pdfinfo "$f" | awk '/Pages/{print $2}') trang: $(basename "$f")"; done
