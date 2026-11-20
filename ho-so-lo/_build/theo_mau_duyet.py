# Áp các chỉnh sửa anh chủ duyệt (bản C MAX 25% sửa tay 20/11/2026) cho file 1-lô:
#  1) khung tiêu đề hồ sơ lô + bảng chữ ký gộp 1 bảng; 2) bỏ khung tiêu đề HD 05, HD 07 trong phần biểu mẫu;
#  3) tên phiếu xuất/lưu kho thành phẩm và ngày cùng 1 dòng.
import sys, copy, docx
from docx.oxml.ns import qn
txt = lambda e: ''.join(t.text or '' for t in e.iter(qn('w:t')))
for f in sys.argv[1:]:
    d = docx.Document(f); b = d.element.body
    t = b.findall(qn('w:tbl'))
    t1, t2 = t[0], t[1]
    if t1.getnext() is t2:
        for tr in t2.findall(qn('w:tr')): t1.append(tr)
        b.remove(t2)
    for tb in list(b.findall(qn('w:tbl'))):
        s = ' '.join(txt(tb).split())
        if s.startswith(("QUY ĐỊNH KIỂM SOÁT THÀNH PHẨM", "QUY ĐỊNH KIỂM SOÁT SẢN PHẨM KHÔNG PHÙ HỢP")) and ("HD 05" in s or "HD 07" in s):
            b.remove(tb)
    for p in list(b.findall(qn('w:p'))):
        if txt(p).strip() in ("PHIẾU XUẤT KHO THÀNH PHẨM", "PHIẾU LƯU KHO THÀNH PHẨM"):
            n = p.getnext()
            if n is not None and n.tag == qn('w:p') and txt(n).strip().startswith(("Ngày xuất kho", "NGÀY:")):
                r0 = next(r for r in p.findall(qn('w:r')) if txt(r).strip())
                gap = copy.deepcopy(r0)
                for x in gap.findall(qn('w:t')): gap.remove(x)
                for x in gap.findall(qn('w:tab')): gap.remove(x)
                tt = gap.makeelement(qn('w:t'), {}); tt.text = "     "; tt.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); gap.append(tt)
                p.append(gap)
                for r in n.findall(qn('w:r')):
                    for x in r.findall(qn('w:tab')): r.remove(x)
                    p.append(r)
                b.remove(n)
    for p in b.findall(qn('w:p')):  # dòng chấm dưới "Khắc phục sự cố": ngắn lại vừa 1 dòng
        if txt(p).strip().startswith("Khắc phục sự cố"):
            n = p.getnext()
            ts = [t for t in n.iter(qn('w:t'))] if n is not None else []
            if ts and set(txt(n).strip()) == {"…"}:
                ts[0].text = "…" * 39
                for t in ts[1:]: t.text = ""
    d.save(f); print("đã áp mẫu:", f)
