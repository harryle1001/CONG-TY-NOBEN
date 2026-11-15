#!/usr/bin/env python3
"""Tạo index.html (hồ sơ nhãn & thông tin sản phẩm Noben) từ data.json.
Chạy lại sau khi sửa data.json:  python3 build.py
"""
import json, html, datetime, pathlib

ROOT = pathlib.Path(__file__).parent
data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
data.sort(key=lambda r: (r["nhom"], r["ten"]))
esc = lambda s: html.escape(str(s or ""))
nl = lambda s: esc(s).replace("\n", "<br>")


def field(r, prefix):
    for k, v in (r.get("f1") or {}).items():
        if k.startswith(prefix):
            return v
    return ""


def table(t, title):
    if not t or len(t.get("rows", [])) < 2:
        return ""
    rows = t["rows"]
    cols = [i for i in range(len(rows[0]))
            if i == 0 or any(len(r) > i and str(r[i]).strip() for r in rows[1:])]
    cols = [i for i in cols if str(rows[0][i]).strip() or i == 0]
    head = "".join(f"<th>{esc(rows[0][i])}</th>" for i in cols)
    body = "".join("<tr>" + "".join(f"<td>{nl(r[i] if i < len(r) else '')}</td>" for i in cols) + "</tr>" for r in rows[1:])
    return f'<h3>{title}</h3><div class="tw"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def tbl(r, key, idx):
    arr = r.get(key) or []
    return arr[idx] if len(arr) > idx else None


groups = {}
for r in data:
    groups.setdefault(r["nhom"], []).append(r)

toc, pages, n = [], [], 0
for g, rs in groups.items():
    toc.append(f'<tr class="grp"><td colspan="4">{esc(g)} · {len(rs)} sản phẩm</td></tr>')
    for r in rs:
        n += 1
        toc.append(f'<tr data-q="{esc((r["ten"] + " " + r["ma"] + " " + r["loai"]).lower())}"><td>{n}</td>'
                   f'<td><a href="#p-{esc(r["ma"])}">{esc(r["ten"])}</a></td><td>{esc(r["ma"])}</td><td>{esc(r["loai"])}</td></tr>')
        co = ""
        t1 = tbl(r, "t1", 0)
        if t1 and len(t1["rows"]) > 1:
            co = "<br>".join(f"{esc(x[1])} — {esc(x[2])}" for x in t1["rows"][1:] if len(x) > 2)
        imgs = "".join(f'<a href="nhan/{esc(f)}" target="_blank"><img loading="lazy" src="nhan/{esc(f)}" alt="Nhãn {esc(r["ten"])}"></a>' for f in r.get("nhan", [])) \
            or '<p class="muted">Chưa có ảnh nhãn trên CSDL</p>'
        pham_vi = ", ".join(x for x in (r.get("radios") or []) if "Khai báo" not in x)
        pages.append(f'''
<section class="prod" id="p-{esc(r["ma"])}">
 <header><span class="no">{n:03d}</span><div><div class="cat">{esc(r["nhom"])} · {esc(r["loai"])}</div><h2>{esc(r["ten"])}</h2></div></header>
 <div class="meta">
  <div><span>Mã số tiếp nhận</span><b>{esc(r["ma"])}</b></div>
  <div><span>Tiêu chuẩn cơ sở</span><b>{esc(field(r, "Số tiêu chuẩn"))}</b></div>
  <div><span>Ngày công bố TCCS</span><b>{esc(r["tccsDate"])}</b></div>
  <div><span>Cập nhật gần nhất</span><b>{esc(r["capnhat"])}</b></div>
  <div><span>Phạm vi · Tình trạng</span><b>{esc(pham_vi)}</b></div>
 </div>
 <div class="grid">
  <div class="labels">{imgs}</div>
  <div class="info">
   {table(tbl(r, "t2", 0), "Thành phần")}
   {table(tbl(r, "t3", 0), "Chỉ tiêu chất lượng")}
   {table(tbl(r, "t3", 1), "Chỉ tiêu an toàn")}
   {table(tbl(r, "t3", 2), "Chỉ tiêu cảm quan")}
  </div>
 </div>
 <div class="text">
  <h3>Hướng dẫn sử dụng</h3><p>{nl(field(r, "Hướng dẫn sử dụng")) or "—"}</p>
  <div class="two"><div><h3>Bảo quản</h3><p>{nl(field(r, "Hướng dẫn bảo quản")) or "—"}</p></div>
  <div><h3>Ngừng sử dụng trước thu hoạch</h3><p>{nl(field(r, "Thời gian ngừng")) or "—"}</p></div></div>
  <h3>Cảnh báo an toàn</h3><p>{nl(field(r, "Cảnh báo")) or "—"}</p>
  {f"<h3>Cơ sở sản xuất</h3><p>{co}</p>" if co else ""}
 </div>
 <a class="top" href="#top">↑ Mục lục</a>
</section>''')

today = datetime.date.today().strftime("%d/%m/%Y")
CSS = """
:root{--phi:1.61803;--s1:6px;--s2:10px;--s3:16px;--s4:26px;--s5:42px;--s6:68px;
--f0:10px;--f1:13px;--f2:16px;--f3:26px;--f4:42px;--navy:#0b3d6e;--gold:#f2b705;--ink:#1b2430;--mute:#5f6f80;--line:#d9e1ea;--bg:#eef2f6}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font-family:"Be Vietnam Pro","Segoe UI",Roboto,Arial,sans-serif;color:var(--ink);background:var(--bg);font-size:var(--f1);line-height:var(--phi)}
.wrap{max-width:1100px;margin:0 auto;padding:var(--s3)}
.cover,.prod{background:#fff;border-radius:var(--s2);padding:var(--s4);margin-bottom:var(--s4);box-shadow:0 2px 16px rgba(11,61,110,.07)}
h1{font-size:var(--f4);line-height:1.15;margin:0;color:var(--navy)}
.sub{color:var(--mute);margin-top:var(--s1)}
.bar{height:4px;width:110px;background:linear-gradient(90deg,var(--navy) 61.8%,var(--gold) 61.8%);border-radius:2px;margin:var(--s3) 0}
.search{width:100%;padding:var(--s2) var(--s3);font-size:var(--f2);border:1px solid var(--line);border-radius:var(--s1);margin:var(--s2) 0 var(--s3)}
table{width:100%;border-collapse:collapse}th,td{border:1px solid var(--line);padding:var(--s1) var(--s2);text-align:left;vertical-align:top}
th{background:#f3f6fa;color:var(--navy);font-weight:600}.tw{overflow-x:auto}
tr.grp td{background:var(--navy);color:#fff;font-weight:600}a{color:var(--navy);text-decoration:none}a:hover{text-decoration:underline}
.prod header{display:flex;gap:var(--s3);align-items:center;border-bottom:2px solid var(--navy);padding-bottom:var(--s2);margin-bottom:var(--s3)}
.no{background:var(--navy);color:#fff;font-weight:700;border-radius:var(--s1);padding:var(--s1) var(--s2)}
.cat{color:var(--mute);font-size:11px;text-transform:uppercase;letter-spacing:.05em}
h2{font-size:var(--f3);margin:2px 0 0;color:var(--navy);line-height:1.2}
.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:var(--s2);margin-bottom:var(--s3)}
.meta div{background:#f6f8fb;border-radius:var(--s1);padding:var(--s1) var(--s2)}.meta span{display:block;font-size:11px;color:var(--mute)}
.grid{display:grid;grid-template-columns:61.8fr 38.2fr;gap:var(--s4)}
.labels img{width:100%;border:1px solid var(--line);border-radius:var(--s1);margin-bottom:var(--s2);display:block}
h3{font-size:var(--f1);color:var(--navy);margin:var(--s3) 0 var(--s1);text-transform:uppercase;letter-spacing:.04em}
.info h3:first-child{margin-top:0}p{margin:0 0 var(--s1)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:var(--s3)}.muted{color:var(--mute)}
.top{display:inline-block;margin-top:var(--s3);font-size:12px;color:var(--mute)}
.foot{color:var(--mute);font-size:12px;margin-top:var(--s3)}
@media(max-width:760px){.wrap{padding:var(--s2)}.cover,.prod{padding:var(--s3)}h1{font-size:var(--f3)}h2{font-size:22px}.grid,.two{grid-template-columns:1fr}}
@media print{@page{size:A4;margin:12mm}body{background:#fff;font-size:11.5px}.wrap{max-width:none;padding:0}
.cover,.prod{box-shadow:none;border-radius:0;padding:0;margin:0}.prod{page-break-before:always}.search,.top{display:none}
.grid{grid-template-columns:1fr}.labels img{max-height:140mm;width:auto;max-width:100%}table,tr,img{page-break-inside:avoid}}
"""
JS = """const q=document.getElementById('q');q.addEventListener('input',()=>{const v=q.value.trim().toLowerCase();
document.querySelectorAll('tr[data-q]').forEach(tr=>tr.style.display=!v||tr.dataset.q.includes(v)?'':'none')});"""

out = f'''<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Noben – Hồ sơ nhãn & thông tin sản phẩm</title><style>{CSS}</style></head>
<body><div class="wrap" id="top">
<section class="cover">
 <h1>Hồ sơ nhãn &amp; thông tin sản phẩm</h1>
 <div class="sub">CÔNG TY TNHH NOBEN · Nguồn: CSDL Cục Thủy sản và Kiểm ngư (csdl.tongcucthuysan.gov.vn) · Cập nhật {today}</div>
 <div class="bar"></div>
 <p><b>{len(data)}</b> sản phẩm đang kinh doanh, đã công bố (không gồm sản phẩm ngừng kinh doanh). Bấm tên để xem chi tiết; bấm ảnh nhãn để phóng to. In: Ctrl+P → A4, mỗi sản phẩm một trang.</p>
 <input id="q" class="search" placeholder="Tìm theo tên, mã số, loại…">
 <div class="tw"><table><thead><tr><th>#</th><th>Tên sản phẩm</th><th>Mã số tiếp nhận</th><th>Loại</th></tr></thead><tbody>{"".join(toc)}</tbody></table></div>
 <p class="foot">Thuốc thú y thủy sản (kháng sinh, trị bệnh) không thuộc CSDL này — đăng ký tại Cục Chăn nuôi và Thú y.</p>
</section>
{"".join(pages)}
</div><script>{JS}</script></body></html>'''
(ROOT / "index.html").write_text(out, encoding="utf-8")
print("OK", len(data), "sản phẩm")
