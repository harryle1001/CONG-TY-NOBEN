import copy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
from data import PRODUCTS, BL, DATE

TEMPLATE = sys.argv[1]
OUT = sys.argv[2]


def uc(row):
    out, prev = [], None
    for c in row.cells:
        if c._tc is prev:
            continue
        prev = c._tc
        out.append(c)
    return out


def set_par(p, text):
    runs = p.runs
    if not runs:
        r = p.add_run(text)
        ppr = p._p.pPr
        if ppr is not None:
            mark = ppr.find(qn("w:rPr"))
            if mark is not None:
                r._r.insert(0, copy.deepcopy(mark))
        return
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def set_cell(c, text):
    ps = c.paragraphs
    lines = text.split("\n")
    for p in ps[1:]:
        p._p.getparent().remove(p._p)
    p0 = ps[0]
    set_par(p0, lines[0])
    prev = p0._p
    for ln in lines[1:]:
        np_ = copy.deepcopy(p0._p)
        prev.addnext(np_)
        prev = np_
        from docx.text.paragraph import Paragraph
        set_par(Paragraph(np_, p0._parent), ln)


def resize_rows(table, n_data, header_rows=1, proto_idx=1):
    rows = table.rows
    data = list(rows[header_rows:])
    proto = rows[proto_idx]._tr
    while len(data) < n_data:
        new = copy.deepcopy(proto)
        data[-1]._tr.addnext(new)
        data = list(table.rows[header_rows:])
    while len(data) > n_data:
        tr = data[-1]._tr
        tr.getparent().remove(tr)
        data = list(table.rows[header_rows:])
    return list(table.rows[header_rows:])


def add_note_after(elem, text):
    p = OxmlElement("w:p")
    ppr = OxmlElement("w:pPr")
    sp = OxmlElement("w:spacing"); sp.set(qn("w:before"), "60"); sp.set(qn("w:after"), "60")
    ppr.append(sp)
    jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "both"); ppr.append(jc)
    p.append(ppr)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    f = OxmlElement("w:rFonts")
    for a in ("w:ascii", "w:hAnsi", "w:cs"):
        f.set(qn(a), "Times New Roman")
    rpr.append(f)
    rpr.append(OxmlElement("w:i"))
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "20"); rpr.append(sz)
    r.append(rpr)
    t = OxmlElement("w:t"); t.text = text; t.set(qn("xml:space"), "preserve")
    r.append(t)
    p.append(r)
    elem.addnext(p)


def build(P):
    d = docx.Document(TEMPLATE)
    T = d.tables
    name = P["name"]
    nl = P["nl"]

    # ---- Header
    h = d.sections[0].header.tables[0]
    hp = h.cell(1, 1).paragraphs
    set_par(hp[1], name)
    set_par(h.cell(1, 3).paragraphs[1], DATE)
    set_par(h.cell(2, 3).paragraphs[1], DATE)
    set_par(h.cell(3, 1).paragraphs[0], "Lô SX: " + BL)
    npar = h.cell(3, 2).paragraphs
    npar[0].runs[1].text = DATE
    npar[1].runs[1].text = DATE
    set_par(h.cell(3, 3).paragraphs[0], "Lần ban hành: 01")

    # ---- Cover approvals
    for c in uc(T[0].rows[4]):
        set_par(c.paragraphs[0], "Ngày " + DATE)

    # ---- I. Thong tin chung
    t5 = T[1]
    c00 = t5.cell(0, 0)
    set_par(c00.paragraphs[1], "MSTN: Chưa có")
    newp = copy.deepcopy(c00.paragraphs[1]._p)
    c00.paragraphs[1]._p.addnext(newp)
    set_par(c00.paragraphs[2], "TCCS " + P["tccs"])
    set_par(t5.cell(1, 0).paragraphs[0], "Mã HQ: " + BL)
    r = t5.cell(1, 1).paragraphs[0].runs
    r[2].text = DATE + f" ({P['hsd']} tháng kể từ NSX)"
    r = t5.cell(1, 2).paragraphs[0].runs
    r[1].text = "100"
    r = t5.cell(2, 0).paragraphs[0].runs
    r[1].text = DATE + "     "
    r[3].text = DATE

    # ---- 1. Cong thuc
    rows = resize_rows(T[2], len(nl))
    for k, (row, (n, kl, sp, dt)) in enumerate(zip(rows, nl), 1):
        cs = uc(row)
        set_cell(cs[0], str(k)); set_cell(cs[1], n); set_cell(cs[2], BL); set_cell(cs[3], kl)
    add_note_after(T[2]._tbl, P["note"])

    # ---- 2.1 TC nguyen lieu
    rows = resize_rows(T[3], len(nl))
    for row, (n, kl, sp, dt) in zip(rows, nl):
        cs = uc(row)
        set_cell(cs[1], n.replace(" vừa đủ", "")); set_cell(cs[2], sp)

    # ---- 2.2 TC thanh pham
    items = [("Tính chất cảm quan", P["camquan"]),
             ("Định tính", P["dinhtinh"]),
             ("Độ đồng đều thể tích", "Đạt")]
    if P["kimloai"]:
        items.append(("Kim loại nặng", P["kimloai"]))
    if P["visinh"]:
        items.append(("Vi sinh vật", P["visinh"]))
    items.append(("Định lượng", "90 - 110% so với hàm lượng ghi trên bao bì nhãn mác:\n" + P["dinhluong"]))
    set_cell(uc(T[4].rows[0])[2], "TIÊU CHUẨN CƠ SỞ\nTCCS " + P["tccs"])
    rows = resize_rows(T[4], len(items))
    for row, (a, b) in zip(rows, items):
        cs = uc(row)
        set_cell(cs[1], a); set_cell(cs[2], b)

    # ---- 1.1 checklist
    t = T[5]
    set_cell(uc(t.rows[0])[2], "Ngày " + DATE)
    for row in t.rows[2:]:
        cs = uc(row)
        set_cell(cs[2], BL)
        set_cell(cs[4], "")

    # ---- can nguyen lieu
    rows = resize_rows(T[6], len(nl))
    for row, (n, kl, sp, dt) in zip(rows, nl):
        cs = uc(row)
        set_cell(cs[1], n); set_cell(cs[2], kl); set_cell(cs[3], BL)
        set_cell(cs[4], BL); set_cell(cs[5], "")

    # ---- Paragraphs: times, san pham truoc
    for p in d.paragraphs:
        tx = p.text
        if tx.startswith("Thời gian bắt đầu:") or tx.startswith("Thời gian kết thúc:"):
            lab = tx.split(":")[0]
            set_par(p, f"{lab}: …… giờ …… phút  ngày: {DATE}")
        elif tx.startswith("-   Thời gian"):
            lab = tx.split(":")[0]
            set_par(p, f"{lab}: …… giờ …… phút  ngày: {DATE}")
        elif "Sản phẩm trước" in tx or tx.replace(" ", "").startswith("Sảnphẩmtrước"):
            pre = "-   " if tx.startswith("-") else ""
            set_par(p, pre + "Sản phẩm trước: " + BL * 3)

    # ---- Pha che table
    t = T[8]
    cs = uc(t.rows[1])
    for i in (3, 4, 5, 7, 8):
        set_cell(cs[i], BL)
    set_cell(cs[9], "")
    cs = uc(t.rows[3])
    set_cell(cs[5], BL); set_cell(cs[8], BL)

    # ---- Tong ket pha che
    cs = uc(T[9].rows[3])
    set_cell(cs[0], "100 lít")
    for i in (1, 2, 3):
        set_cell(cs[i], BL)

    # ---- Dong goi cap 1 dinh muc
    for row in T[11].rows[1:]:
        cs = uc(row)
        set_cell(cs[4], BL); set_cell(cs[5], "")
    cs = uc(T[11].rows[4]); set_cell(cs[0], "4"); set_cell(cs[3], "1")
    # Dong goi cap 1 thiet bi
    t = T[12]
    for ri in (1, 2):
        cs = uc(t.rows[ri])
        for i in (3, 4, 5, 8):
            set_cell(cs[i], BL if (cs[i].text.strip() or (ri == 1 and i in (3, 4))) else "")
    # Tong ket cap 1
    for row in T[13].rows[1:]:
        cs = uc(row)
        for i in (2, 3, 4, 5):
            set_cell(cs[i], BL)

    # ---- Cap 2 dinh muc
    t = T[15]
    rows = t.rows
    set_cell(uc(rows[1])[1], "Nhãn " + name)
    for row in rows[1:]:
        cs = uc(row)
        set_cell(cs[4], BL); set_cell(cs[5], ""); set_cell(cs[6], "")
    # 4.2 dan nhan
    t = T[16]
    cs = uc(t.rows[1]); set_cell(cs[1], name); set_cell(cs[2], "1 LÍT"); set_cell(cs[3], BL)
    cs = uc(t.rows[2]); set_cell(cs[3], BL)
    # Tong ket cap 2
    t = T[17]
    set_cell(uc(t.rows[1])[0], "Nhãn " + name)
    for row in t.rows[1:]:
        cs = uc(row)
        for i in (2, 3, 4, 5):
            set_cell(cs[i], BL)

    # ---- Tong ket san xuat
    cs = uc(T[19].rows[3])
    set_cell(cs[1], "100"); set_cell(cs[2], BL); set_cell(cs[9], BL)

    # ---- Textboxes hieu suat / ti le loai bo
    tbs = list(d.element.body.iter(qn("w:txbxContent")))
    for tb in tbs[:4]:
        ts = list(tb.iter(qn("w:t")))
        ts[0].text = "……%"
        for x in ts[1:]:
            x.text = ""

    d.core_properties.title = "Hồ sơ lô " + name
    d.save(OUT)


if __name__ == "__main__":
    outdir = OUT
    os.makedirs(outdir, exist_ok=True)
    for P in PRODUCTS:
        fn = os.path.join(outdir, f"HSO-LO-F.X-{P['key']}.docx")
        OUT = fn
        globals()["OUT"] = fn
        build(P)
        print("ok", fn)
