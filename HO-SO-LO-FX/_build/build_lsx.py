import copy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.table import Table
from docx.text.paragraph import Paragraph
from data import PRODUCTS, BL, DATE
from build_hso import set_par, set_cell, resize_rows, uc

LSX_TPL, DAN_TPL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

d = docx.Document(LSX_TPL)
body = d.element.body
children = list(body)
block = [copy.deepcopy(c) for c in children[0:9]]
lsx_sect = body.find(qn("w:sectPr"))
for c in children:
    if c is not lsx_sect:
        body.remove(c)


def page_break():
    p = OxmlElement("w:p")
    r = OxmlElement("w:r")
    br = OxmlElement("w:br"); br.set(qn("w:type"), "page")
    r.append(br); p.append(r)
    return p


for i, P in enumerate(PRODUCTS):
    if i:
        lsx_sect.addprevious(page_break())
    els = [copy.deepcopy(c) for c in block]
    for e in els:
        lsx_sect.addprevious(e)
    info = Table(els[1], d._body)
    mat = Table(els[3], d._body)
    c = info.cell(0, 0).paragraphs[0]
    set_par(c, f"Tên sản phẩm: {P['name']} (TCCS {P['tccs']})")
    r = info.cell(0, 1).paragraphs[0].runs
    r[1].text = DATE; r[2].text = ""; r[3].text = ""
    r = info.cell(1, 1).paragraphs[0].runs
    r[1].text = "100 "
    rows_spec = [(n, kl, "") for (n, kl, sp, dt) in P["nl"]] + [
        ("Chai 1 LÍT (BVT2) + nắp", "", "100 bộ"),
        ("Màng siu nắp chai 1 lít", "", "100 cái"),
        ("Chai 100ml (lưu mẫu)", "", "1 bộ"),
        ("Màng co ngoài 1 lít", "", "100 cái"),
        ("Thùng chứa SỐ 6", "", "5 cái"),
        ("Băng keo", "", "1/2 cuộn"),
        (f"Nhãn {P['name']} (1L)", "", "105 cái"),
    ]
    rows = resize_rows(mat, len(rows_spec))
    for k, (row, (a, b, cc)) in enumerate(zip(rows, rows_spec), 1):
        cs = uc(row)
        set_cell(cs[0], str(k)); set_cell(cs[1], a); set_cell(cs[2], b); set_cell(cs[3], cc)

# ---------- Tem dan mau luu ----------
dd = docx.Document(DAN_TPL)
lab_p = copy.deepcopy(dd.element.body[0])
dan_sect = copy.deepcopy(dd.element.body.find(qn("w:sectPr")))
for ref in list(dan_sect):
    if ref.tag in (qn("w:headerReference"), qn("w:footerReference")):
        dan_sect.remove(ref)

# end LSX section with a section-break paragraph
sp = OxmlElement("w:p"); ppr = OxmlElement("w:pPr")
ppr.append(copy.deepcopy(lsx_sect)); sp.append(ppr)
lsx_sect.addprevious(sp)

# title for label page
tp = OxmlElement("w:p")
tppr = OxmlElement("w:pPr"); jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "center"); tppr.append(jc); tp.append(tppr)
tr = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
f = OxmlElement("w:rFonts")
for a in ("w:ascii", "w:hAnsi", "w:cs"):
    f.set(qn(a), "Times New Roman")
rpr.append(f); rpr.append(OxmlElement("w:b"))
sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "26"); rpr.append(sz); tr.append(rpr)
t = OxmlElement("w:t"); t.text = "TEM DÁN MẪU LƯU – 7 SẢN PHẨM F.X (2 tem/sản phẩm)"; tr.append(t); tp.append(tr)
lsx_sect.addprevious(tp)

MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent"
label_runs = [r for r in lab_p.findall(qn("w:r")) if r.find(MC) is not None]
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
def pos(run):
    a = next(run.iter(WP + "anchor"))
    h = int(a.find(WP + "positionH").find(WP + "posOffset").text)
    v = int(a.find(WP + "positionV").find(WP + "posOffset").text)
    return (round(v / 300000), h)
label_runs.sort(key=pos)
names = [P["name"] for P in PRODUCTS for _ in range(2)]
for k, run in enumerate(label_runs):
    if k >= len(names):
        lab_p.remove(run)
        continue
    for tb in run.iter(qn("w:txbxContent")):
        for p in tb.iter(qn("w:p")):
            par = Paragraph(p, None)
            tx = par.text
            if tx.startswith("TÊN MẪU LƯU"):
                set_par(par, "TÊN MẪU LƯU: " + names[k])
            elif tx.startswith("SỐ LÔ"):
                set_par(par, "SỐ LÔ: ……………")
            elif tx.startswith("NSX"):
                set_par(par, "NSX: " + DATE)
            elif tx.startswith("HSD"):
                set_par(par, "HSD: " + DATE)
            elif tx.startswith("K.LƯỢNG"):
                set_par(par, "K.LƯỢNG MẪU LƯU: 100ml")
lsx_sect.addprevious(lab_p)
# final section = label page layout
body.remove(lsx_sect)
body.append(dan_sect)

d.core_properties.title = "Lệnh sản xuất và tem mẫu lưu 7 SP F.X"
d.save(OUT)
print("ok", OUT, len(label_runs))
