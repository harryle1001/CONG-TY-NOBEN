# Đơn vị số lượng viết thường (anh chủ 20/11/2026): "30 HŨ" -> "30 Hũ", "100 CHAI" -> "100 Chai", "20 GÓI" -> "20 Gói".
import sys, re, docx
from docx.oxml.ns import qn
RX = re.compile(r'(\d+\s*)(HŨ|CHAI|GÓI|BAO|THÙNG|CÁI|BỘ)\b')
for f in sys.argv[1:]:
    d = docx.Document(f); n = 0
    for part in [d.element.body] + [s.header._element for s in d.sections] + [s.footer._element for s in d.sections]:
        for t in part.iter(qn('w:t')):
            if t.text and RX.search(t.text):
                t.text, k = RX.subn(lambda m: m.group(1) + m.group(2).capitalize(), t.text); n += k
    d.save(f); print(n, f)
