# Sửa 6 hồ sơ lô 21.09.2026 (ho-so-lo/word): bỏ Mã HQ, TCCS; C MAX 25% thêm 10 phút, đội bột lùi giờ theo.
import re, glob, os, docx
from docx.oxml.ns import qn

W = os.path.join(os.path.dirname(__file__), "..", "word")

def ptext(p): return ''.join(t.text or '' for t in p.iter(qn('w:t')))

def bo_ma(doc):
    for tc in doc.element.body.iter(qn('w:tc')):
        ps = tc.findall(qn('w:p'))
        for p in ps:
            if ptext(p).strip().startswith(("Mã HQ", "TCCS:")):
                if len(tc.findall(qn('w:p'))) > 1: tc.remove(p)
                else:
                    for t in p.iter(qn('w:t')): t.text = ""

def doi_gio(doc, tu, phut):
    """Cộng `phut` cho mọi mốc giờ >= `tu` (phút trong ngày)."""
    def f(h, m):
        x = int(h) * 60 + int(m)
        return divmod(x + phut, 60) if x >= tu else (int(h), int(m))
    pats = [(re.compile(r'(\d{1,2}) giờ (\d{1,2}) phút'), lambda a, b: f"{a} giờ {b} phút"),
            (re.compile(r'(\d{1,2})H(\d{1,2})P'), lambda a, b: f"{a}H{b}P")]
    for t in doc.element.body.iter(qn('w:t')):
        s = t.text or ""
        for rx, fmt in pats:
            s = rx.sub(lambda m: fmt(*f(m.group(1), m.group(2))), s)
        t.text = s

KE = {  # file: (từ mốc, cộng thêm)
    "HSO LÔ C MAX 25% 21.09.2026.docx": (7 * 60 + 55, 10),   # đóng gói cấp 1 kéo dài thêm 10p
    "HS BZT 21.09.2026.docx": (0, 10),
    "HSO EDTA 99 21.09.2026.docx": (0, 10),
}
for f in sorted(glob.glob(os.path.join(W, "*.docx"))):
    d = docx.Document(f)
    bo_ma(d)
    k = KE.get(os.path.basename(f))
    if k: doi_gio(d, *k)
    d.save(f)
    print("đã sửa", os.path.basename(f))
