# Tạo các phần phụ để gộp 1 file Word: phiếu QD7 (từ xlsx) và lệnh SX của 1 sản phẩm.
# Dùng: python3 mot_file.py <QD7.xlsx> <QD7 ra.docx> <LỆNH SX.docx> <tên SP> <LSX ra.docx>
import sys, copy, datetime, openpyxl, docx
from docx.shared import Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
qx, qo, lsx, sp, lo = sys.argv[1:6]

# --- QD7 -> Word
ws = openpyxl.load_workbook(qx).worksheets[0]
d = docx.Document(); s = d.sections[0]
s.page_width, s.page_height = Mm(210), Mm(297)
s.left_margin = s.right_margin = Mm(16); s.top_margin = s.bottom_margin = Mm(16)
st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
def par(t, b=False, sz=None, c=False):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = b
    if sz: r.font.size = Pt(sz)
    if c: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
fmt = lambda v: v.strftime("%d/%m/%Y") if isinstance(v, datetime.datetime) else ("" if v is None else str(v))
par("CÔNG TY TNHH NOBEN", True)
par(" ".join(fmt(ws["A2"].value).split()[:4]) + "        Số: " + fmt(ws["H2"].value))
par("PHIẾU THEO DÕI MẪU LƯU", True, 16, True)
moc = [fmt(ws[f"{c}6"].value) for c in "EFGHI"]
hdr = ["STT", "Tên mẫu", "NSX", "HSD"] + [f"Kiểm tra cảm quan {m} (Đ/K)" for m in moc[:4]] + [f"Hủy mẫu {moc[4]}", "Người thực hiện"]
rows = []
r = 8
while ws[f"B{r}"].value:
    rows.append([fmt(ws[f"{c}{r}"].value) for c in "ABCDEFGHIJ"]); r += 1
t = d.add_table(rows=1 + len(rows), cols=10); t.style = "Table Grid"
for j, h in enumerate(hdr):
    c = t.cell(0, j); c.text = ""; rr = c.paragraphs[0].add_run(h); rr.bold = True; rr.font.size = Pt(9)
for i, row in enumerate(rows):
    for j, v in enumerate(row):
        c = t.cell(i + 1, j); c.text = ""; rr = c.paragraphs[0].add_run(v); rr.font.size = Pt(10)
d.save(qo)

# --- Lệnh SX: chỉ giữ trang của sản phẩm
d = docx.Document(lsx); b = d.element.body
els = [e for e in b if e.tag != qn('w:sectPr')]
txt = lambda e: ''.join(x.text or '' for x in e.iter(qn('w:t')))
st = [i for i, e in enumerate(els) if e.tag == qn('w:p') and txt(e).strip().startswith("LỆNH SẢN XUẤT")] + [len(els)]
keep = None
for a, z in zip(st, st[1:]):
    if any(f"Tên sản phẩm: {sp}" in txt(e) for e in els[a:z]): keep = set(map(id, els[a:z]))
for e in els:
    if id(e) not in keep: b.remove(e)
for pb in b.iter(qn('w:pageBreakBefore')): pb.getparent().remove(pb)
d.save(lo)
