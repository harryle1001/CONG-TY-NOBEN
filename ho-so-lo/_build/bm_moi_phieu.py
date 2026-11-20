# Biểu mẫu 12 quy định: mỗi phiếu sang trang mới (ngắt trang thay cho dòng trống), có khung tiêu đề (logo, mã tài liệu) của biểu mẫu đó
# — theo bản anh chủ sửa tay 20/11/2026. Dùng: python3 bm_moi_phieu.py <file biểu mẫu gộp.docx>
import sys, copy, docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
PHIEU = ["BIÊN BẢN KHẮC PHỤC SỰ CỐ HIỆN TRẠNG CẤP NƯỚC", "PHIẾU XUẤT KHO NGUYÊN LI", "PHIẾU CHUYỂN TRẢ LẠI DO KHÔNG ĐẠT",
         "PHIẾU XUẤT KHO BAO BÌ", "PHIẾU TRẢ LẠI BAO BÌ KHÔNG ĐẠT", "PHIẾU XUẤT KHO THÀNH PHẨM", "PHIẾU LƯU KHO THÀNH PHẨM",
         "BIÊN BẢN BÀN GIAO SẢN PHẨM KHÔNG PHÙ HỢP", "KIỂM SOÁT QUÁ TRÌNH SẢN XUẤT NƯỚC",
         "BIỂU MẪU GIÁM SÁT CÔN TRÙNG MỐI MỌT", "BIỂU MẪU THU GOM RÁC NGUY HẠI", "BIỂU MẪU GIAO NHẬN RÁC", "RÁC THÔNG THƯỜNG"]
txt = lambda e: ''.join(t.text or '' for t in e.iter(qn('w:t')))
f = sys.argv[1]; d = docx.Document(f); b = d.element.body
def sang_trang():
    br = OxmlElement('w:p'); pPr = OxmlElement('w:pPr'); pPr.append(OxmlElement('w:pageBreakBefore'))
    sp = OxmlElement('w:spacing'); sp.set(qn('w:before'), '0'); sp.set(qn('w:after'), '0'); sp.set(qn('w:line'), '20'); sp.set(qn('w:lineRule'), 'exact'); pPr.append(sp)
    br.append(pPr); return br
hdr = None; da_gap = set()
for e in list(b):
    if e.tag == qn('w:tbl') and 'Mã số tài liệu' in txt(e):
        if hdr is not None:  # đầu biểu mẫu mới: bỏ dòng trống/ngắt trang cũ, sang trang bằng đoạn "sang trang trước"
            pv = e.getprevious()
            while pv is not None and pv.tag == qn('w:p') and not txt(pv).strip():
                nx = pv.getprevious(); b.remove(pv); pv = nx
            e.addprevious(sang_trang())
        hdr = e; continue
    if e.tag != qn('w:p') or hdr is None: continue
    t = txt(e).strip()
    if not any(t.startswith(k) for k in PHIEU): continue
    if t.startswith("BIÊN BẢN BÀN GIAO SẢN PHẨM KHÔNG PHÙ HỢP") and "BBGSPKPH" in da_gap: continue  # chỉ lần đầu
    if t.startswith("BIÊN BẢN BÀN GIAO SẢN PHẨM KHÔNG PHÙ HỢP"): da_gap.add("BBGSPKPH")
    if t.startswith("RÁC THÔNG THƯỜNG") and "RTT" in da_gap: continue
    if t.startswith("RÁC THÔNG THƯỜNG"): da_gap.add("RTT")
    # bỏ dòng trống ngay trước (tránh tràn sang trang trắng), rồi đoạn rỗng "sang trang trước" + khung tiêu đề
    pv = e.getprevious()
    while pv is not None and pv.tag == qn('w:p') and not txt(pv).strip() and 'w:type="page"' not in pv.xml:
        nx = pv.getprevious(); b.remove(pv); pv = nx
    e.addprevious(sang_trang()); e.addprevious(copy.deepcopy(hdr))
d.save(f); print("đã tách phiếu:", f)
