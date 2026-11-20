# Dựng bộ hồ sơ đi kèm ngày SX 21.09.2026 (lệnh SX, QD7, dán mẫu lưu, 12 biểu mẫu)
# theo mẫu ngày 04.09.2026. Chạy: python3 build_2109.py <thư mục mẫu> <thư mục ra>
import copy, re, sys, datetime, shutil, os
import docx, openpyxl
from docx.oxml.ns import qn
from docx.shared import Pt, Mm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement

PHI = 1.61803
REF, OUT = sys.argv[1], sys.argv[2]
NGAY, NGAY_HSD, DDMMYY = "21/09/2026", "21/09/2028", "210926"

# Thứ tự theo giờ bắt đầu trong hồ sơ lô (2 đội chạy song song)
SP = [
 dict(ten="C MAX 25%", hq="47", doi="bot", qc="HŨ 1KG", sl="30 HŨ", luu=("Gói lưu mẫu: túi 100g", "1"), kl_luu="100G",
      nl=[("ASCORBIC ACID (Vitamin C)", "0,94 kg", ""), ("Dextrose monohydrate", "29,16 kg", ""),
          ("Hũ 1kg", "", "30 cái"), ("Túi PE 1kg", "", "30 cái"), ("Túi lưu mẫu 100g", "", "1 cái"),
          ("Thùng chứa", "", "2 cái"), ("Nhãn C MAX 25% – 1 KG", "", "32 cái")]),
 dict(ten="YUCCA 99", hq="43", doi="nuoc", qc="CHAI 1 LÍT", sl="100 CHAI", luu=("Chai lưu mẫu: chai 100ml", "1"), kl_luu="100ML",
      nl=[("DK Yucca Liquid", "33,3 kg", ""), ("Nước lọc (RO) vừa đủ", "100,1 lít", ""),
          ("Chai BVT2 – 1 lít", "", "100 bộ"), ("Chai 100ml", "", "1 bộ"),
          ("Thùng chứa", "", "5 cái"), ("Nhãn YUCCA 99 – 1 LÍT", "", "105 cái")]),
 dict(ten="BZT", hq="38", doi="bot", qc="GÓI 500G", sl="20 GÓI", luu=("Gói lưu mẫu: túi 100g", "1"), kl_luu="100G",
      nl=[("BACILLUS SUBTILIS (OKT1816)", "1,02 kg", ""), ("Dextrose monohydrate", "9,08 kg", ""),
          ("Túi PE 500g", "", "20 cái"), ("Túi lưu mẫu 100g", "", "1 cái"),
          ("Thùng chứa", "", "1 cái"), ("Nhãn BZT – 500 G", "", "21 cái")]),
 dict(ten="IODINE 99", hq="09", doi="nuoc", qc="CHAI 1 LÍT", sl="15 CHAI", luu=("Chai lưu mẫu: chai 100ml", "1"), kl_luu="100ML",
      nl=[("PVP Iodine", "1,8 kg", ""), ("Nước lọc (RO) vừa đủ", "15,1 lít", ""),
          ("Chai TT-01 – 1 lít", "", "15 bộ"), ("Chai 100ml", "", "1 bộ"),
          ("Thùng chứa", "", "1 cái"), ("Nhãn IODINE 99 – 1 LÍT", "", "16 cái")]),
 dict(ten="EDTA 99", hq="10", doi="bot", qc="GÓI 3KG", sl="70 GÓI", luu=("Gói lưu mẫu: túi 100g", "1"), kl_luu="100G",
      nl=[("EDTA 4Na", "2,1 kg", ""), ("Dextrose monohydrate", "208,0 kg", ""),
          ("Túi 3kg", "", "70 cái"), ("Túi lưu mẫu 100g", "", "1 cái"),
          ("Thùng chứa", "", "7 cái"), ("Nhãn EDTA 99 – 3 KG", "", "77 cái")]),
 dict(ten="BEN COPPER 500", hq="20", doi="nuoc", qc="CHAI 250ML", sl="15 CHAI", luu=("Chai lưu mẫu: chai 100ml", "1"), kl_luu="100ML",
      nl=[("CuSO4.5H2O", "60,8 g", ""), ("Nước lọc (RO) vừa đủ", "3,85 lít", ""),
          ("Chai 250ml", "", "15 bộ"), ("Chai 100ml", "", "1 bộ"),
          ("Thùng chứa", "", "1 cái"), ("Nhãn BEN COPPER 500 – 250 ML", "", "16 cái")]),
]
for s in SP: s["lo"] = f'{s["hq"]}-{DDMMYY}'

# Bảng kê chi tiết HĐ đã sử dụng 30/9–31/10/2026 (gộp theo ngày + khách)
BANG_KE = [
 ("02/10/2026", "Công Ty TNHH Công Nghệ Nuôi 45", [("BEN COPPER 500", "15 CHAI")]),
 ("13/10/2026", "HỘ KINH DOANH ÔNG NGỌC LỘC", [("EDTA 99", "70 GÓI")]),
 ("23/10/2026", "Dương Thị Mỹ Hương", [("YUCCA 99", "40 CHAI"), ("C MAX 25%", "30 HŨ")]),
 ("28/10/2026", "HỘ KINH DOANH KHỞI ÂN", [("IODINE 99", "15 CHAI"), ("BZT", "20 GÓI"), ("YUCCA 99", "20 CHAI")]),
 ("29/10/2026", "ĐẶNG CƯƠNG TRỰC - CƠ SỞ: PHI GIAO", [("YUCCA 99", "20 CHAI")]),
]

# ---------- tiện ích ----------
def ptext(p): return ''.join(t.text or '' for t in p.iter(qn('w:t')))

def set_par_text(p, text):
    """Ghi text vào đoạn, giữ định dạng run đầu tiên."""
    runs = p.findall(qn('w:r'))
    keep = next((r for r in runs if r.find(qn('w:t')) is not None), runs[0] if runs else None)
    for r in runs:
        if r is not keep: p.remove(r)
    if keep is None:
        keep = OxmlElement('w:r'); p.append(keep)
    for t in keep.findall(qn('w:t')): keep.remove(t)
    t = OxmlElement('w:t'); t.text = text; t.set(qn('xml:space'), 'preserve'); keep.append(t)

def set_cell(tc, text):
    ps = tc.findall(qn('w:p'))
    for p in ps[1:]: tc.remove(p)
    set_par_text(ps[0], text)

def replace_all(root, pairs):
    """Thay chuỗi trong mọi đoạn (kể cả trong bảng, khung chữ); gộp run khi chuỗi bị tách."""
    for p in root.iter(qn('w:p')):
        if p.find('.//' + qn('w:txbxContent')) is not None: continue  # đoạn chứa khung: xử lý đoạn con
        full = ptext(p)
        new = full
        for a, b in pairs: new = new.replace(a, b)
        if new == full: continue
        done = False
        for t in p.iter(qn('w:t')):  # thử thay trong từng run
            for a, b in pairs:
                if t.text and a in t.text: t.text = t.text.replace(a, b)
        if ptext(p) != new: set_par_text(p, new)

def rows(tbl): return tbl.findall(qn('w:tr'))
def cells(tr): return tr.findall(qn('w:tc'))

def fill_rows(tbl, start, data, proto_idx=None):
    """Ghi data (list các list) vào bảng từ hàng start; thiếu hàng thì nhân bản, dư thì xóa trắng."""
    rs = rows(tbl)
    proto = rs[proto_idx if proto_idx is not None else start]
    need = start + len(data)
    while len(rows(tbl)) < need:
        rs = rows(tbl); rs[-1].addnext(copy.deepcopy(proto))
    rs = rows(tbl)
    for i, vals in enumerate(data):
        cs = cells(rs[start + i])
        for j, c in enumerate(cs):
            set_cell(c, vals[j] if j < len(vals) else "")
    for r in rs[need:]:
        for c in cells(r): set_cell(c, "")

DATE_PAIRS = [("04 THÁNG 09 NĂM 2026", "21 THÁNG 09 NĂM 2026"), ("13 THÁNG 06 NĂM 2026", "21 THÁNG 09 NĂM 2026"),
              ("04 tháng 09 năm 2026", "21 tháng 09 năm 2026"), ("04 Tháng 09 năm 2026", "21 Tháng 09 năm 2026"),
              ("04 tháng 09 Năm 2026", "21 tháng 09 Năm 2026"), ("04/092026", NGAY),
              ("04/09/2028", NGAY_HSD), ("04/09/2026", NGAY)]

def text_width(doc):
    s = doc.sections[0]; return s.page_width - s.left_margin - s.right_margin

def full_width(tbl_el, width_emu, ratios):
    """Bảng rộng đúng vùng chữ, cột theo tỷ lệ cho trước."""
    tw = int(width_emu / 635)  # EMU -> twip
    tot = sum(ratios); ws = [round(tw * r / tot) for r in ratios]
    tblPr = tbl_el.find(qn('w:tblPr'))
    for x in tblPr.findall(qn('w:tblpPr')): tblPr.remove(x)  # không bảng nổi
    w = tblPr.find(qn('w:tblW'))
    if w is None: w = OxmlElement('w:tblW'); tblPr.append(w)
    w.set(qn('w:w'), str(tw)); w.set(qn('w:type'), 'dxa')
    lay = tblPr.find(qn('w:tblLayout'))
    if lay is None: lay = OxmlElement('w:tblLayout'); tblPr.append(lay)
    lay.set(qn('w:type'), 'fixed')
    grid = tbl_el.find(qn('w:tblGrid'))
    for g in list(grid): grid.remove(g)
    for x in ws:
        g = OxmlElement('w:gridCol'); g.set(qn('w:w'), str(x)); grid.append(g)
    for tr in rows(tbl_el):
        for j, tc in enumerate(cells(tr)):
            pr = tc.find(qn('w:tcPr'))
            if pr is None: pr = OxmlElement('w:tcPr'); tc.insert(0, pr)
            cw = pr.find(qn('w:tcW'))
            if cw is None: cw = OxmlElement('w:tcW'); pr.insert(0, cw)
            span = pr.find(qn('w:gridSpan')); n = int(span.get(qn('w:val'))) if span is not None else 1
            cw.set(qn('w:w'), str(sum(ws[j:j + n]) if j + n <= len(ws) else ws[-1])); cw.set(qn('w:type'), 'dxa')

# ---------- 1. Lệnh sản xuất ----------
def lenh_sx():
    d = docx.Document(os.path.join(REF, "2. LỆNH SẢN XUẤT 04.09.2026.docx"))
    body = d.element.body
    els = [e for e in body if e.tag != qn('w:sectPr')]
    starts = [i for i, e in enumerate(els) if e.tag == qn('w:p') and ptext(e).strip().startswith("LỆNH SẢN XUẤT")]
    block = els[starts[0]:starts[1]]
    for e in els: body.remove(e)
    sect = body.find(qn('w:sectPr'))
    tw = text_width(d)
    for k, s in enumerate(SP):
        nb = [copy.deepcopy(e) for e in block]
        title = nb[0]
        if k:  # mỗi lệnh 1 trang
            pPr = title.find(qn('w:pPr'))
            if pPr is None: pPr = OxmlElement('w:pPr'); title.insert(0, pPr)
            pb = OxmlElement('w:pageBreakBefore'); pPr.insert(0, pb)
        t1, t2 = [e for e in nb if e.tag == qn('w:tbl')][:2]
        r = rows(t1)
        luu_cell = s["luu"][0]
        for (a, b), tr in zip([(f'Tên sản phẩm: {s["ten"]}', f'Ngày sản xuất: {NGAY}'),
                               (f'Quy cách đóng gói: {s["qc"]}', f'Số lượng: {s["sl"]}'),
                               (luu_cell, f'Số lượng: {s["luu"][1]}')], r):
            c = cells(tr); set_cell(c[0], a); set_cell(c[1], b)
        full_width(t1, tw, [PHI, 1])
        data = [[str(i + 1), n, h, q] for i, (n, h, q) in enumerate(s["nl"])]
        fill_rows(t2, 1, data, proto_idx=1)
        for tr in rows(t2)[1 + len(data):]: t2.remove(tr)
        full_width(t2, tw, [1, PHI ** 3, PHI ** 2, PHI ** 2])
        for e in nb: sect.addprevious(e)
    d.save(os.path.join(OUT, "2-Lenh-san-xuat", f"LỆNH SẢN XUẤT {NGAY.replace('/', '.')}.docx"))

# ---------- 2. Phiếu QD7 ----------
def qd7(xlsx_ref):
    wb = openpyxl.load_workbook(xlsx_ref)
    ws = wb["P.Theo dõi mẫu lưu"]
    ws["A2"] = ws["A2"].value.replace("04/09/2026", NGAY)
    ws["H2"] = "02-09/2026-LM"
    nsx = datetime.datetime(2026, 9, 21)
    moc = [nsx, datetime.datetime(2027, 3, 21), datetime.datetime(2027, 9, 21), datetime.datetime(2028, 3, 21), datetime.datetime(2028, 9, 21)]
    for col, v in zip("EFGHI", moc):
        ws[f"{col}6"] = v; ws[f"{col}6"].number_format = "DD/MM/YYYY"
    for i in range(8, 21):
        for col in "ABCDEFGHIJ": ws[f"{col}{i}"] = None
    for i, s in enumerate(SP):
        r = 8 + i
        ws[f"A{r}"] = i + 1; ws[f"B{r}"] = s["ten"]
        ws[f"C{r}"] = nsx; ws[f"D{r}"] = datetime.datetime(2028, 9, 21)
        ws[f"C{r}"].number_format = ws[f"D{r}"].number_format = "DD/MM/YYYY"
        ws[f"E{r}"] = "Đ"; ws[f"I{r}"] = "2 NĂM"
    wb.save(os.path.join(OUT, "3-Phieu-QD7", f"1. Phiếu QD7 - lưu mẫu {NGAY.replace('/', '.')}.xlsx"))

# ---------- 3. Dán mẫu lưu (bảng thường, không khung nổi) ----------
def dan_mau_luu():
    d = docx.Document()
    sec = d.sections[0]; sec.page_width, sec.page_height = Mm(210), Mm(297)
    for side in ("left_margin", "right_margin"): setattr(sec, side, Mm(16))
    sec.top_margin = sec.bottom_margin = Mm(16)
    st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(13)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
    h = d.add_paragraph(); h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = h.add_run(f"DÁN MẪU LƯU – NGÀY SẢN XUẤT {NGAY}"); r.bold = True; r.font.size = Pt(16)
    n = (len(SP) + 1) // 2
    t = d.add_table(rows=n, cols=2); t.style = "Table Grid"
    for i, s in enumerate(SP):
        c = t.cell(i // 2, i % 2); c.paragraphs[0].text = ""
        lines = [(f'TÊN MẪU LƯU: {s["ten"]}', True), (f'SỐ LÔ: {s["lo"]}', False), (f'NSX: {NGAY}', False),
                 (f'HSD: {NGAY_HSD}', False), (f'K.LƯỢNG MẪU LƯU: {s["kl_luu"]}', False),
                 ("Lưu ý: Lưu trên cùng chất liệu bao bì", False)]
        for j, (txt, b) in enumerate(lines):
            p = c.paragraphs[0] if j == 0 else c.add_paragraph()
            p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.3
            if j == 0: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            rr = p.add_run(txt); rr.bold = b
            if j == 5: rr.italic = True; rr.font.size = Pt(11)
        c.paragraphs[0].paragraph_format.space_before = Pt(6)
        c.paragraphs[-1].paragraph_format.space_after = Pt(6)
    full_width(t._tbl, text_width(d), [1, 1])
    d.save(os.path.join(OUT, "4-Dan-mau-luu", f"DÁN MẪU LƯU {NGAY.replace('/', '.')}.docx"))

# ---------- 4. 12 biểu mẫu ----------
def bieu_mau(src_dir):
    out = os.path.join(OUT, "5-Bieu-mau-12-quy-dinh")
    bot = [s for s in SP if s["doi"] == "bot"]; nuoc = [s for s in SP if s["doi"] == "nuoc"]
    for f in sorted(os.listdir(src_dir)):
        if not f.endswith(".docx"): continue
        d = docx.Document(os.path.join(src_dir, f)); b = d.element.body
        tb = b.findall('.//' + qn('w:tbl'))
        extra = []
        if f.startswith("8."):
            extra = [("MIRAL N.8; PREMIX KHOÁNG NEW, SUPER CAL; EDTA 99; BZT; PRAWNZYME", "; ".join(s["ten"] for s in bot)),
                     ("AMINOVIT; CANCI MILK; F.X ORGANIC; F.X ENZYME; LIVER-MAX; NO TOXIN; BEN MKC 4000", "; ".join(s["ten"] for s in nuoc))]
        replace_all(b, extra + DATE_PAIRS)
        if f.startswith("8."):  # giờ kết thúc theo hồ sơ lô: bột 9h50, nước 9h15
            ps = [p for p in b.iter(qn('w:p')) if ptext(p).startswith("Giờ kết thúc sản xuất")]
            set_par_text(ps[0], "Giờ kết thúc sản xuất: 9 giờ 50 phút")
            set_par_text(ps[1], "Giờ kết thúc sản xuất: 9 giờ 15 phút")
        if f.startswith("3."):  # phiếu xuất kho nguyên liệu
            data = [[NGAY, "DK Yucca Liquid", "33,3 kg", "Đ"], ["", "PVP Iodine", "1,8 kg", "Đ"],
                    ["", "CuSO4.5H2O", "60,8 g", "Đ"], ["", "ASCORBIC ACID (Vitamin C)", "0,94 kg", "Đ"],
                    ["", "BACILLUS SUBTILIS (OKT1816)", "1,02 kg", "Đ"], ["", "EDTA 4Na", "2,1 kg", "Đ"],
                    ["", "Dextrose monohydrate", "246,24 kg", "Đ"], ["", "Nước lọc (RO) vừa đủ", "119,05 lít", "Đ"]]
            fill_rows(tb[1], 1, data, proto_idx=2)
        if f.startswith("4."):  # phiếu xuất kho bao bì
            data = [["", NGAY, "Hũ 1kg (Lon H-AP)", "Cao: 145mm Đ/K: 115mm", "30 cái", "Đ"], ["", "", "Túi PE 1kg", "Cao: 300mm ngang: 210mm", "30 cái", "Đ"],
                    ["", "", "Túi PE 500g", "Cao: 270mm ngang: 170mm", "20 cái", "Đ"], ["", "", "Túi 3kg", "", "70 cái", "Đ"],
                    ["", "", "Chai BVT2 – 1 lít", "Cao: 238mm Đ/K: 86mm", "100 bộ", "Đ"], ["", "", "Chai TT-01 – 1 lít", "Cao: 227mm Đ/K: 98mm", "15 bộ", "Đ"],
                    ["", "", "Chai 250ml", "", "15 bộ", "Đ"], ["", "", "Túi 100g (lưu mẫu)", "", "3 cái", "Đ"],
                    ["", "", "Chai 100ml (lưu mẫu)", "", "3 cái", "Đ"], ["", "", "Thùng chứa", "", "17 cái", "Đ"]]
            for i, r in enumerate(data): r[0] = str(i + 1)
            fill_rows(tb[1], 1, data, proto_idx=2)
        if f.startswith("5."):  # nhập kho, xuất kho theo bảng kê HĐ tháng 10, lưu kho
            nsx = f"NSX: {NGAY} HSD: {NGAY_HSD}"
            ten = {s["ten"]: s for s in SP}
            data = [[nsx if i == 0 else "", f'{s["ten"]} – Lô {s["lo"]}', s["qc"], s["sl"], "Đ"] for i, s in enumerate(SP)]
            fill_rows(tb[0], 1, data, proto_idx=2)
            els = [e for e in b if e.tag != qn('w:sectPr')]
            heads = [i for i, e in enumerate(els) if e.tag == qn('w:p') and ptext(e).strip().startswith(("PHIẾU XUẤT KHO THÀNH PHẨM", "PHIẾU LƯU KHO"))]
            proto = els[heads[0]:heads[1]]; luu_title = els[heads[-1]]
            for e in els[heads[0]:heads[-1]]: b.remove(e)
            for ngay, kh, items in BANG_KE:
                nb = [copy.deepcopy(e) for e in proto]
                for e in nb:
                    if e.tag == qn('w:p') and ptext(e).startswith("Ngày xuất kho"): set_par_text(e, f"Ngày xuất kho: {ngay}")
                t = next(e for e in nb if e.tag == qn('w:tbl'))
                rowsd = [[nsx if i == 0 else "", f'{n} – Lô {ten[n]["lo"]}', ten[n]["qc"], q, kh if i == 0 else ""]
                         for i, (n, q) in enumerate(items)]
                fill_rows(t, 1, rowsd, proto_idx=2)
                for e in nb: luu_title.addprevious(e)
            tl = b.findall('.//' + qn('w:tbl'))[-1]
            data = [[nsx if i == 0 else "", f'{s["ten"]} – Lô {s["lo"]}', s["qc"], s["sl"], "Chờ xuất bán" if i == 0 else ""]
                    for i, s in enumerate(SP)]
            fill_rows(tl, 1, data, proto_idx=2)
        if f.startswith("12."):  # rác nguy hại: giẻ lau chỉ khi SX > 100 SP; bao bì nhựa cứng 1 kg / 5 SP
            tong = sum(int(s["sl"].split()[0]) for s in SP)
            kg = f'{len(SP) / 5:.1f}'.replace('.', ',') + " kg"
            for tr in b.iter(qn('w:tr')):
                cs = cells(tr); vals = [ptext(c).strip() for c in cs]
                if any(v.startswith("Rác giẻ lau") for v in vals) and tong <= 100:
                    for c in cs: set_cell(c, "")
                if any(v.startswith("Rác bao bì nhựa cứng") for v in vals):
                    set_cell(cs[3], kg)
        if f.startswith("10."):  # 21/09/2026 là thứ 2
            t = tb[1]
            for tr in rows(t)[1:]:
                cs = cells(tr); vals = [ptext(c) for c in cs]
                if "KHÔNG" in vals:
                    for c in cs[1:]: set_cell(c, "")
                    set_cell(cs[1], "KHÔNG")
        d.save(os.path.join(out, f))

if __name__ == "__main__":
    for sub in ["2-Lenh-san-xuat", "3-Phieu-QD7", "4-Dan-mau-luu", "5-Bieu-mau-12-quy-dinh"]:
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    lenh_sx(); qd7(os.path.join(REF, "1. Phiếu QD7 - lưu mẫu 04.09.2026.xlsx")); dan_mau_luu()
    bieu_mau(os.path.join(REF, "bieu-mau"))
    print("xong")
