# Gộp các biểu mẫu thành 1 file chạy liền (ít trang): khung tiêu đề trang (logo, mã tài liệu)
# của từng biểu mẫu được đưa vào thân văn bản ở đầu biểu mẫu đó.
# Dùng: python3 gop_bieu_mau.py <file ra.docx> <biểu mẫu 1.docx> <biểu mẫu 2.docx> ...
import sys, copy, docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

R_ATTRS = [qn('r:embed'), qn('r:id'), qn('r:link')]

def copy_rels(el, src_part, dst_part):
    """Ảnh/quan hệ trong phần tử: tạo quan hệ tương ứng ở tài liệu đích."""
    for node in el.iter():
        for a in R_ATTRS:
            rid = node.get(a)
            if not rid or rid not in src_part.rels: continue
            rel = src_part.rels[rid]
            if rel.is_external:
                node.set(a, dst_part.relate_to(rel.target_ref, rel.reltype, is_external=True))
            elif rel.reltype.endswith('/image'):
                import io
                rid2, _ = dst_part.get_or_add_image(io.BytesIO(rel.target_part.blob)); node.set(a, rid2)
            else:
                node.set(a, dst_part.relate_to(rel.target_part, rel.reltype))

def blank_par():
    p = OxmlElement('w:p'); return p

out, files = sys.argv[1], sys.argv[2:]
base = docx.Document(files[0])
body = base.element.body
sect = body.find(qn('w:sectPr'))
for e in [e for e in body if e is not sect]: body.remove(e)
# không dùng tiêu đề trang nữa
for r in sect.findall(qn('w:headerReference')) + sect.findall(qn('w:footerReference')): sect.remove(r)
tp = sect.find(qn('w:titlePg'))
if tp is not None: sect.remove(tp)

STYLE_REFS = [qn('w:pStyle'), qn('w:rStyle'), qn('w:tblStyle'), qn('w:basedOn'), qn('w:next'), qn('w:link'), qn('w:numStyleLink'), qn('w:styleLink')]
base_styles = base.styles.element

def doi_style(el, pre):
    for n in el.iter():
        if n.tag in STYLE_REFS and n.get(qn('w:val')): n.set(qn('w:val'), pre + n.get(qn('w:val')))

def nhap_style(d, pre):
    """Chép toàn bộ style của biểu mẫu vào tài liệu gộp với tiền tố riêng (không đè nhau)."""
    for st in d.styles.element.findall(qn('w:style')):
        c = copy.deepcopy(st); c.set(qn('w:styleId'), pre + st.get(qn('w:styleId')))
        c.attrib.pop(qn('w:default'), None)
        nm = c.find(qn('w:name'))
        if nm is not None: nm.set(qn('w:val'), pre + nm.get(qn('w:val')))
        doi_style(c, pre); base_styles.append(c)

for k, f in enumerate(files):
    d = docx.Document(f)
    pre = f"bm{k}_"
    nhap_style(d, pre)
    hdr = d.sections[0].header
    blocks = []
    for e in hdr._element:
        if e.tag in (qn('w:tbl'), qn('w:p')):
            if e.tag == qn('w:p') and not ''.join(t.text or '' for t in e.iter(qn('w:t'))).strip() \
               and e.find('.//' + qn('w:drawing')) is None: continue
            c = copy.deepcopy(e); copy_rels(c, hdr.part, base.part); doi_style(c, pre); blocks.append(c)
    for e in d.element.body:
        if e.tag == qn('w:sectPr'): continue
        c = copy.deepcopy(e)
        for sp in c.iter(qn('w:sectPr')): sp.getparent().remove(sp)
        copy_rels(c, d.part, base.part); doi_style(c, pre); blocks.append(c)
    if k: sect.addprevious(blank_par())
    for c in blocks: sect.addprevious(c)
base.save(out)
print("gộp", len(files), "biểu mẫu ->", out)
