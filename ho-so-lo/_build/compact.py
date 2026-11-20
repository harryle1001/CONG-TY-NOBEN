# Gọn hồ sơ: xóa hàng bảng trống, gộp đoạn trống liên tiếp (tối đa 2), bỏ ngắt trang thừa.
# Dùng: python3 compact.py <file.docx|file.xlsx> ...
import sys, openpyxl, docx
from docx.oxml.ns import qn

def txt(el): return ''.join(t.text or '' for t in el.iter(qn('w:t'))).strip()

def empty_row(tr):
    return not txt(tr) and tr.find('.//' + qn('w:drawing')) is None and tr.find('.//' + qn('w:pict')) is None

def compact_docx(path):
    d = docx.Document(path); body = d.element.body
    for tbl in body.iter(qn('w:tbl')):
        trs = tbl.findall(qn('w:tr'))
        has_data = any(not empty_row(tr) for tr in trs[1:])
        keep_blank = 0 if has_data else 1  # bảng chưa có số liệu: chừa 1 hàng để ghi tay
        for tr in trs[1:]:
            if empty_row(tr):
                if keep_blank: keep_blank -= 1; continue
                # hàng trống mở đầu một ô gộp dọc: chuyển "restart" xuống hàng kế
                nxt = tr.getnext()
                for i, tc in enumerate(tr.findall(qn('w:tc'))):
                    vm = tc.find('.//' + qn('w:vMerge'))
                    if vm is not None and vm.get(qn('w:val')) == 'restart' and nxt is not None:
                        ntc = nxt.findall(qn('w:tc'))
                        if i < len(ntc):
                            nvm = ntc[i].find('.//' + qn('w:vMerge'))
                            if nvm is not None: nvm.set(qn('w:val'), 'restart')
                tbl.remove(tr)
    # bỏ "giữ liền đoạn sau" (làm nội dung nhảy trang, để trống cuối trang)
    for tag in ('w:keepNext', 'w:cantSplit', 'w:tblpPr'):  # + bỏ bảng nổi, cho hàng bảng sang trang
        for k in list(body.iter(qn(tag))): k.getparent().remove(k)
    # bảng nhỏ (chữ ký, ≤4 hàng): giữ trọn trên 1 trang
    from docx.oxml import OxmlElement
    for tbl in body.iter(qn('w:tbl')):
        trs = tbl.findall(qn('w:tr'))
        if len(trs) > 4: continue
        for tr in trs[:-1]:
            for p in tr.iter(qn('w:p')):
                pPr = p.find(qn('w:pPr'))
                if pPr is None: pPr = OxmlElement('w:pPr'); p.insert(0, pPr)
                pPr.insert(0, OxmlElement('w:keepNext'))
    # đoạn trống liên tiếp: sau dòng "Người thực hiện/phụ trách…" giữ 2 (chỗ ký), chỗ khác giữ 1
    run, limit = 0, 1
    for el in list(body):
        if el.tag == qn('w:p'):
            blank = not txt(el) and el.find('.//' + qn('w:drawing')) is None and el.find('.//' + qn('w:pict')) is None \
                    and el.find('.//' + qn('w:sectPr')) is None
            if blank and 'w:type="page"' not in el.xml:
                run += 1
                if run > limit: body.remove(el)
                continue
            limit = 2 if txt(el).lower().startswith(("người", "ký xác nhận", "bên nhận")) else 1
        else:
            limit = 1
        run = 0
    d.save(path)

def compact_xlsx(path):
    wb = openpyxl.load_workbook(path); ws = wb.worksheets[0]
    last = max(r for r in range(1, ws.max_row + 1) if ws.cell(r, 2).value not in (None, ""))
    if ws.max_row > last: ws.delete_rows(last + 1, ws.max_row - last)
    ws.print_area = f"A1:J{last}"
    wb.save(path)

for p in sys.argv[1:]:
    (compact_xlsx if p.endswith(".xlsx") else compact_docx)(p)
    print("gọn:", p)
