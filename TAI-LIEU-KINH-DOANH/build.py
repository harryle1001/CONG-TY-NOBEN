#!/usr/bin/env python3
"""Dựng bảng giá Noben 2026 + catalogue Noben & Thủy Sản Tím (HTML web, PDF A4, Excel).

Nguồn dữ liệu:
  data/bang-gia-noben-2026.json            (chép từ ảnh bảng giá giấy)
  ../../thuysannoben/content/products.json (104 SP Noben, ảnh trong public/images/products)
  ../../Thuysantim/nhan/san-pham.json      (15 SP Tím, ảnh trong public/img/products)
Chạy:  python3 build.py          (sửa giá trong JSON rồi chạy lại)
Tỷ lệ vàng: --phi 1.61803, thang chữ 10/16/26/42/68, khoảng cách 6/10/16/26/42/68.
"""
import base64, html, io, json, os, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOME = ROOT.parent.parent
NOBEN = HOME / 'thuysannoben'
TIM = HOME / 'Thuysantim'
OUT = ROOT
PHI = 1.61803
NGAY = '01/05/2026'

e = lambda s: html.escape(str(s or ''), quote=True)
def money(v): return f"{v:,.0f}".replace(',', '.')
def norm(s):
    s = unicodedata.normalize('NFD', s.upper()).replace('Đ', 'D')
    s = re.sub(r'[^A-Z0-9]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))
    return re.sub(r'NEW$', '', s)

GIA = json.loads((ROOT / 'data/bang-gia-noben-2026.json').read_text())
NOBEN_SP = json.loads((NOBEN / 'content/products.json').read_text())
NOBEN_CAT = json.loads((NOBEN / 'content/categories.json').read_text())
NOBEN_CO = json.loads((NOBEN / 'content/company.json').read_text())
TIM_DATA = json.loads((TIM / 'nhan/san-pham.json').read_text())

# ---------- khớp giá ----------
ALIAS = {'PROTICBEST': ['PROBITICBEST'], 'MIRALN8': ['MRIRALN08'], 'BETA13': ['BETA1316GLUCAN'],
         'HEPATIC': ['HEPATICSHRIMP'], 'HUFA': ['HUFASHRIMP'], 'NBSORBITOLB12': ['NBSORBITOLB12SHRIMP'],
         'G7': ['G7THAODUOC'], 'BENXID3000': ['BENXID3000'], 'BENBKC': ['BENBKC80']}
UU_TIEN = ['A', 'T', 'B']   # Bảng giá Noben 2026 > Bảng giá tôm 02-03 > Báo giá (B)
IDX = {}
for b in GIA['bang']:
    for g in b['nhom']:
        for s in g['sp']:
            IDX.setdefault((b['id'], norm(s['ten'])), []).append(s)

def tim_gia(ten):
    keys = [norm(ten)] + ALIAS.get(norm(ten), [])
    for bid in UU_TIEN:
        for k in keys:
            if (bid, k) in IDX:
                return bid, IDX[(bid, k)]
    return None, []

def img64(path, h=380, bg=None):
    """Ảnh thu nhỏ dạng data URI; bg='#rrggbb' -> JPEG nền đặc (PDF nhẹ hơn nhiều)."""
    from PIL import Image
    try:
        im = Image.open(path).convert('RGBA')
    except Exception:
        return ''
    im.thumbnail((h, h))
    buf = io.BytesIO()
    if bg:
        flat = Image.new('RGB', im.size, bg); flat.paste(im, mask=im.split()[3])
        flat.save(buf, 'JPEG', quality=80, optimize=True, progressive=True)
        return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
    im.save(buf, 'WEBP', quality=74)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()

def svg64(path):
    return 'data:image/svg+xml;base64,' + base64.b64encode(Path(path).read_bytes()).decode()

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&'
         'family=Playfair+Display:wght@600;700&family=Cormorant+Garamond:wght@500;600;700&display=swap">')

# ---------- CSS chung (giấy in, một giao diện sáng có chủ đích) ----------
BASE_CSS = """
:root{--phi:1.61803;--t0:10px;--t1:16px;--t2:26px;--t3:42px;--t4:68px;
 --s1:6px;--s2:10px;--s3:16px;--s4:26px;--s5:42px;--s6:68px;--dur:262ms;
 --body:'Be Vietnam Pro',system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--desk);color:var(--ink);font-family:var(--body);font-size:var(--t1);line-height:1.618;
 padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:var(--s4)}
h1,h2,h3{text-wrap:balance;margin:0}
.page{background:var(--paper);max-width:1100px;margin:0 auto var(--s4);padding:var(--s5) var(--s4);border-radius:var(--s1);
 box-shadow:0 1px 2px rgb(0 0 0/.06),0 var(--s3) var(--s5) -var(--s4) rgb(0 0 0/.12);position:relative;overflow:hidden}
.num{font-variant-numeric:tabular-nums}
.tools{max-width:1100px;margin:0 auto var(--s3);display:flex;gap:var(--s2);flex-wrap:wrap;align-items:center}
.tools input{flex:1 1 260px;min-width:0;font:inherit;font-size:var(--t1);padding:var(--s2) var(--s3);border:1px solid var(--line);
 border-radius:999px;background:var(--paper);color:var(--ink)}
.tools input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.tools span{font-size:13px;color:var(--muted)}
.pgfoot{display:none}
@media print{
 @page{size:A4;margin:0}
 body{background:#fff;padding:0;font-size:var(--t0)}
 .tools{display:none}
 .page{width:210mm;height:297mm;max-width:none;margin:0;border-radius:0;box-shadow:none;padding:12mm 11mm 14mm;
  break-after:page;page-break-after:always}
 .page:last-child{break-after:auto}
 .pgfoot{display:flex;position:absolute;left:11mm;right:11mm;bottom:6mm;justify-content:space-between;font-size:8px;
  color:var(--muted);letter-spacing:.04em;border-top:.5px solid var(--line);padding-top:4px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

SEARCH_JS = """<script>
(function(){var q=document.getElementById('q');if(!q)return;var items=[].slice.call(document.querySelectorAll('[data-k]'));
var out=document.getElementById('qn');function run(){var v=q.value.trim().toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/đ/g,'d');
var n=0;items.forEach(function(it){var ok=!v||it.getAttribute('data-k').indexOf(v)>-1;it.hidden=!ok;if(ok)n++});
document.querySelectorAll('[data-sec]').forEach(function(s){s.hidden=!!v&&!s.querySelector('[data-k]:not([hidden])')});
if(out)out.textContent=v?n+' kết quả':''}q.addEventListener('input',run)})();
</script>"""

def key(*parts):
    s = ' '.join(str(p) for p in parts).lower()
    s = unicodedata.normalize('NFD', s).replace('đ', 'd')
    return e(''.join(c for c in s if unicodedata.category(c) != 'Mn'))

# =====================================================================
# 1. BẢNG GIÁ
# =====================================================================
def build_bang_gia():
    css = BASE_CSS + """
:root{--desk:#e9edf3;--paper:#ffffff;--ink:#0b1b33;--muted:#5b6a80;--line:#d6dde8;--navy:#0b2347;--gold:#ffc20e;--accent:#1b4db1;--band:#f3f6fb}
.hd{display:grid;grid-template-columns:61.8fr 38.2fr;gap:var(--s4);align-items:end;border-bottom:3px solid var(--navy);padding-bottom:var(--s3);margin-bottom:var(--s3)}
.hd img{height:52px;width:auto}
.co{font-size:13px;color:var(--muted);line-height:1.5}
.co b{color:var(--ink)}
.ttl{text-align:right}
.ttl h1{font-family:'Playfair Display',Georgia,serif;font-size:var(--t2);color:var(--navy);line-height:1.2}
.ttl p{margin:var(--s1) 0 0;font-size:13px;color:var(--muted)}
.tw{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.4;min-width:640px}
th{background:var(--navy);color:#fff;font-weight:600;text-align:left;padding:var(--s1) var(--s2);font-size:12px;letter-spacing:.06em;text-transform:uppercase}
th.r,td.r{text-align:right}
td{padding:var(--s1) var(--s2);border-bottom:1px solid var(--line);vertical-align:top}
tr.g td{background:var(--band);font-weight:700;color:var(--navy);text-transform:uppercase;letter-spacing:.05em;font-size:12px;padding-top:var(--s2)}
tr.g td::before{content:'';display:inline-block;width:var(--s2);height:var(--s2);background:var(--gold);margin-right:var(--s2);border-radius:2px;vertical-align:0}
td.n{font-weight:700;color:var(--navy);white-space:nowrap}
td.n small{display:block;font-weight:500;color:var(--muted);font-size:12px}
td.p{font-weight:700;white-space:nowrap;font-variant-numeric:tabular-nums}
td.s{color:var(--muted);width:2.5em}
.flag{color:#b4232c;font-weight:700}
.note{font-size:12px;color:var(--muted);margin-top:var(--s3)}
@media (max-width:640px){.hd{grid-template-columns:1fr}.ttl{text-align:left}}
td.q{white-space:nowrap}
@media print{@page{size:A4;margin:10mm 0 12mm}.page{height:auto;min-height:0;padding:0 11mm}table{font-size:9.5px;min-width:0}th{font-size:8px}tr.g td{font-size:8.5px}
 td{padding:3px 6px}td.n small{font-size:8px}.co{font-size:9px}.ttl p{font-size:9px}.hd img{height:40px}
 tr{break-inside:avoid}.note{font-size:8.5px}}
"""
    logo = svg64(NOBEN / 'public/images/brand/golden/noben-lockup.svg')
    pages = []
    for b in GIA['bang']:
        rows = []
        for g in b['nhom']:
            rows.append(f'<tr class="g" data-sec><td colspan="6">{e(g["ten"])}</td></tr>')
            for s in g['sp']:
                n = len(s['v'])
                k = key(s['ten'], s.get('phu', ''), s['cd'])
                for i, (qc, dt, gia) in enumerate(s['v']):
                    first = i == 0
                    cells = ''
                    if first:
                        sub = f'<small>{e(s["phu"])}</small>' if s.get('phu') else ''
                        flag = ' <span class="flag" title="Ảnh gốc mờ hoặc ô gộp, cần đối chiếu">*</span>' if s.get('kiem') else ''
                        cells += f'<td class="s num" rowspan="{n}">{s["stt"]}</td><td class="n" rowspan="{n}">{e(s["ten"])}{flag}{sub}</td>'
                    cells += f'<td class="q">{e(qc)}</td><td class="q">{e(dt)}</td>'
                    if first:
                        cells += f'<td rowspan="{n}">{e(s["cd"])}</td>'
                    cells += f'<td class="p r">{money(gia)}</td>'
                    rows.append(f'<tr data-k="{k}">{cells}</tr>')
        pages.append(f"""<section class="page" id="bang-{b['id'].lower()}">
<header class="hd"><div><img src="{logo}" alt="Noben"><div class="co"><b>CÔNG TY TNHH NOBEN</b><br>
228/9 Nguyễn Thị Lắng, Ấp Phú Lợi A, Xã Củ Chi, TP. Hồ Chí Minh<br>
ĐT: 028 3796 6039 · Fax: 028 3796 6038 · Hotline: 0911 88 39 79<br>thuocthuysannoben@gmail.com · thuocthuysannoben.com</div></div>
<div class="ttl"><h1>{e(b['ten'])}</h1><p>{e(b['hieu_luc'])}</p></div></header>
<div class="tw"><table><thead><tr><th>STT</th><th>Tên sản phẩm</th><th>Quy cách</th><th>Đóng thùng</th><th>Công dụng</th><th class="r">Giá bán (đ)</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p class="note">Đơn vị: đồng Việt Nam. Dấu <span class="flag">*</span>: số liệu cần đối chiếu lại bản gốc. Liên hệ để được tư vấn sử dụng và chính sách đại lý.</p>
</section>""")
    nav = ' · '.join(f'<a href="#bang-{b["id"].lower()}">{e(b["ten"].title())}</a>' for b in GIA['bang'])
    doc = f"""<title>Bảng giá Noben 2026</title>
<meta name="claude:viewport-fit-sides" content="cover">{FONTS}<style>{css}
.tools a{{color:var(--accent);font-size:14px}}</style>
<div class="tools"><input id="q" type="search" placeholder="Tìm sản phẩm, công dụng… (vd: yucca, phân trắng)" aria-label="Tìm sản phẩm"><span id="qn"></span></div>
<div class="tools">{nav}</div>
{''.join(pages)}{SEARCH_JS}"""
    (OUT / 'BANG-GIA-NOBEN-2026.html').write_text(doc)
    return OUT / 'BANG-GIA-NOBEN-2026.html'

# =====================================================================
# 2. CATALOGUE NOBEN
# =====================================================================
BANG_TAG = {'A': 'BG 2026', 'T': 'BG Tôm', 'B': 'BG (B)'}
MERGE = {'SUPERCUTALGA': 'SUPERCUTALGAE'}          # cùng sản phẩm, khác cách viết giữa các bảng
CAT_OVERRIDE = {'TANGKIEM': 'khoang-chat', 'BLUEMAX': 'tri-benh', 'NBCLEARFORFISH': 'tri-benh'}

def catalogue_items():
    """Mỗi tên trong 3 bảng giá = 1 thẻ; ghép ảnh/công dụng/mã số từ dữ liệu web nếu trùng tên."""
    web = {norm(p['name']): p for p in NOBEN_SP}
    back = {pk: wk for wk, pks in ALIAS.items() for pk in pks}
    items = {}
    for b in GIA['bang']:
        for g in b['nhom']:
            gl = g['ten'].lower()
            for sp in g['sp']:
                k = MERGE.get(norm(sp['ten']), norm(sp['ten']))
                k = k if k in web else back.get(k, k)
                w = web.get(k)
                if k not in items:
                    cat = (w or {}).get('category') or CAT_OVERRIDE.get(k) or (
                        'tri-benh' if 'thảo dược' in gl else 'thuc-an-bo-sung' if ('dinh dưỡng' in gl or 'mới' in gl) else 'sinh-hoc')
                    items[k] = {'ten': w['name'] if w else sp['ten'], 'web': w, 'cd': sp['cd'], 'cat': cat, 'gia': []}
                items[k]['gia'].append(dict(sp, _b=b['id']))
    return list(items.values())

def price_block(ten):
    bid, sps = tim_gia(ten)
    if not sps:
        return '<div class="pr ask">Liên hệ báo giá</div>', bid
    li = []
    for s in sps:
        lab = f'<i>{e(s["phu"])}</i> ' if s.get('phu') and len(sps) > 1 else ''
        for qc, dt, gia in s['v']:
            li.append(f'<li>{lab}<span>{e(qc)} · {e(dt)}</span><b class="num">{money(gia)}đ</b></li>')
    return f'<ul class="pr">{"".join(li)}</ul>', bid

def build_noben():
    css = BASE_CSS + """
:root{--desk:#e7ebf1;--paper:#fffefb;--ink:#0b1b33;--muted:#5b6a80;--line:#dfe3ea;--navy:#0b2347;--gold:#ffc20e;--gold-d:#9a6b00;--accent:#1b4db1;
 --c-sinh-hoc:#1f7a4d;--c-khoang-chat:#0e6c8a;--c-thuc-an-bo-sung:#9a5a00;--c-tri-benh:#7a3b8f;--disp:'Playfair Display',Georgia,'Times New Roman',serif}
.cover{background:var(--navy);color:#fff;display:grid;grid-template-rows:61.8fr 38.2fr;min-height:640px;padding:0}
.cover .top{padding:var(--s6) var(--s5);display:flex;flex-direction:column;justify-content:space-between;gap:var(--s5);position:relative}
.cover img.logo{width:min(380px,80%);height:auto}
.cover h1{font-family:var(--disp);font-size:var(--t4);line-height:1.05;font-weight:700}
.cover h1 em{font-style:normal;color:var(--gold)}
.cover .sub{font-size:var(--t1);color:#c9d4e6;max-width:34em}
.cover .bot{background:var(--gold);color:var(--navy);padding:var(--s5);display:grid;grid-template-columns:61.8fr 38.2fr;gap:var(--s4);align-items:end}
.cover .bot b{font-size:var(--t2);font-family:var(--disp);display:block;line-height:1.2}
.cover .bot p{margin:0;font-size:14px}
.spiral{position:absolute;right:var(--s5);top:var(--s5);width:42%;opacity:.16}
.intro{display:grid;grid-template-columns:61.8fr 38.2fr;gap:var(--s5)}
.intro h2,.sec-h h2{font-family:var(--disp);font-size:var(--t3);color:var(--navy);line-height:1.15}
.intro p{margin:var(--s3) 0 0;font-size:15px}
.facts{display:grid;gap:var(--s3);align-content:start}
.fact{border-top:2px solid var(--gold);padding-top:var(--s2)}
.fact b{display:block;font-family:var(--disp);font-size:var(--t2);color:var(--navy);line-height:1.2}
.fact span{font-size:13px;color:var(--muted)}
.toc{margin-top:var(--s5);display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:var(--s3)}
.toc a{display:block;text-decoration:none;color:var(--ink);padding:var(--s3);border:1px solid var(--line);border-radius:var(--s1);border-left:var(--s1) solid var(--c)}
.toc a b{display:block;color:var(--c)}
.toc a span{font-size:13px;color:var(--muted)}
.contact{margin-top:var(--s5);font-size:14px;color:var(--muted);border-top:1px solid var(--line);padding-top:var(--s3)}
.contact b{color:var(--ink)}
.sec-h{display:flex;justify-content:space-between;align-items:baseline;gap:var(--s3);border-bottom:2px solid var(--c);padding-bottom:var(--s2);margin-bottom:var(--s3);flex-wrap:wrap}
.sec-h small{color:var(--c);font-weight:700;letter-spacing:.12em;text-transform:uppercase;font-size:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,440px),1fr));gap:var(--s3)}
.card{display:grid;grid-template-columns:38.2fr 61.8fr;gap:var(--s3);padding:var(--s3);border:1px solid var(--line);border-radius:var(--s1);background:#fff;min-width:0}
.card .ph{display:grid;place-items:center;aspect-ratio:1/1.618;max-width:100%;overflow:hidden}
.card .ph img{max-height:100%;max-width:100%;object-fit:contain}
.card.noimg{grid-template-columns:1fr}
.card .tx{min-width:0;display:flex;flex-direction:column;gap:var(--s1)}
.card h3{font-size:var(--t1);color:var(--navy);font-weight:700;line-height:1.25;letter-spacing:.01em}
.card .tag{font-size:13px;color:var(--c);font-weight:600;line-height:1.4}
.card ul.u{margin:0;padding-left:1.1em;font-size:13px;line-height:1.45}
.card ul.u li::marker{color:var(--gold-d)}
.reg{font-size:11px;color:var(--muted);letter-spacing:.02em}
ul.pr{list-style:none;margin:auto 0 0;padding:var(--s1) 0 0;border-top:1px dashed var(--line);font-size:13px}
ul.pr li{display:flex;justify-content:space-between;gap:var(--s2)}
ul.pr li span{color:var(--muted)}
ul.pr li i{font-style:normal;color:var(--ink);font-weight:600}
ul.pr.g li{display:grid;grid-template-columns:4.2em 1fr auto;gap:0 var(--s2);align-items:baseline}
ul.pr.g li i{display:block}
ul.pr li em{font-style:normal;font-size:.78em;font-weight:700;color:var(--gold-d);letter-spacing:.04em;white-space:nowrap;margin-right:.4em}
ul.pr li span{flex:1}
ul.pr li b{color:var(--navy);white-space:nowrap}
.pr.ask{margin-top:auto;font-size:13px;font-weight:600;color:var(--gold-d);border-top:1px dashed var(--line);padding-top:var(--s1)}
@media (max-width:640px){.intro,.cover .bot{grid-template-columns:1fr}.cover h1{font-size:var(--t3)}.cover .top{padding:var(--s5) var(--s4)}}
@media print{
 .cover{min-height:0;padding:0}.cover .top{padding:20mm 16mm}.cover .bot{padding:12mm 16mm}
 .intro p{font-size:10.5px}.fact span,.toc a span,.contact{font-size:9.5px}.intro h2,.sec-h h2{font-size:var(--t2)}
 .grid{grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:4mm;height:247mm}
 .card{padding:3.5mm;gap:3.5mm;overflow:hidden}.card .ph{aspect-ratio:auto;height:100%}
 .card h3{font-size:12px}.card .tag{font-size:9px}.card ul.u{font-size:8.6px;line-height:1.38}
 .card ul.u{padding-left:0;list-style:none}.card ul.u li{padding-left:.9em;position:relative;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
 .card ul.u li::before{content:'•';position:absolute;left:0;color:var(--gold-d)}
 ul.pr,.pr.ask{font-size:8.6px}.reg{font-size:7.5px}.sec-h{margin-bottom:3mm}.sec-h small{font-size:8px}
}
"""
    co = NOBEN_CO
    logo = svg64(NOBEN / 'public/images/brand/golden/noben-lockup-dark.svg')
    spiral = svg64(NOBEN / 'public/images/brand/golden/noben-construction.svg')
    ITEMS = catalogue_items()
    cats = [dict(c, count=sum(1 for it in ITEMS if it['cat'] == c['slug'])) for c in NOBEN_CAT]
    cover = f"""<section class="page cover"><div class="top">
<img class="logo" src="{logo}" alt="Noben">
<div><h1>Catalogue<br>sản phẩm <em>2026</em></h1>
<p class="sub">{len(ITEMS)} sản phẩm thuốc thủy sản, chế phẩm sinh học, khoáng chất và thức ăn bổ sung cho tôm, cá. Sản xuất tại nhà máy Noben, Củ Chi, TP. Hồ Chí Minh.</p></div></div>
<div class="bot"><div><b>Công ty TNHH Noben</b><p>{e(co['address'])}</p></div>
<div><p>Hotline <b class="num" style="font-size:var(--t1);display:inline">0911 88 39 79</b><br>thuocthuysannoben.com</p></div></div></section>"""
    toc = ''.join(f'<a href="#{c["slug"]}" style="--c:var(--c-{c["slug"]})"><b>{e(c["name"])}</b><span>{c["count"]} sản phẩm · {e(c["blurb"])}</span></a>' for c in cats)
    ov = co.get('overview') or []
    intro = f"""<section class="page"><div class="intro"><div><small style="color:var(--gold-d);font-weight:700;letter-spacing:.12em;font-size:12px">VỀ NOBEN</small>
<h2>Đồng hành cùng người nuôi từ năm {e(co.get('founded_year','2002'))}</h2>
{''.join(f'<p>{e(x)}</p>' for x in ov[:2])}<p><b>Sứ mệnh.</b> {e(co.get('mission',''))}</p></div>
<div class="facts"><div class="fact"><b class="num">{e(co.get('founded_year','2002'))}</b><span>Năm thành lập</span></div>
<div class="fact"><b class="num">{len(ITEMS)}</b><span>Sản phẩm trong bảng giá 2026</span></div>
<div class="fact"><b>ISO 9001:2015</b><span>Hệ thống quản lý chất lượng</span></div></div></div>
<nav class="toc">{toc}</nav>
<p class="contact"><b>Liên hệ:</b> {e(co['address'])} · ĐT {' · '.join(e(p) for p in co.get('phones', []))} · {e(co.get('email',''))}<br>
Giá in trong catalogue lấy đúng theo 3 bảng giá hiệu lực từ {NGAY}: BG 2026 = Bảng giá Noben 2026, BG Tôm = Bảng giá tôm 02-03, BG (B) = Bảng báo giá Noben (B). Liên hệ để được tư vấn và chính sách đại lý.</p>
<div class="pgfoot"><span>NOBEN · CATALOGUE 2026</span><span>2</span></div></section>"""
    pages, pg, rows = [], 3, []
    per = 6
    for c in cats:
        items = [it for it in ITEMS if it['cat'] == c['slug']]
        cards = []
        for it in items:
            p = it['web'] or {}
            img = ''
            if p:
                slug = Path(p['images'][0]['src']).stem if p.get('images') else ''
                cut = NOBEN / f'public/images/products-cutout/{slug}.webp'
                img = img64(cut if cut.exists() else NOBEN / ('public' + p['images'][0]['src']), bg='#ffffff')
            nl = sum(len(sp['v']) for sp in it['gia'])
            uses = [re.sub(r'<[^>]+>', '', u) for u in (p.get('uses') or [])] or [it['cd']]
            uses = uses[:max(1, 3 - max(0, nl - 2) // 2)]
            tag = p.get('tagline') or ''
            reg = p.get('registration') or {}
            li = []
            for sp in it['gia']:
                lab = f'<i>{e(sp["phu"])}</i>' if sp.get('phu') else ''
                for qc, dt, gia in sp['v']:
                    li.append(f'<li><em>{BANG_TAG[sp["_b"]]}</em><span>{lab}{e(qc)} · {e(dt)}</span><b class="num">{money(gia)}đ</b></li>')
            pb = f'<ul class="pr g">{"".join(li)}</ul>'
            rows.append(('Noben', c['name'], it['ten'], tag, '; '.join(uses), reg.get('code', ''), reg.get('tccs', ''), ', '.join(dict.fromkeys(BANG_TAG[sp['_b']] for sp in it['gia'])), it['gia']))
            regt = ' · '.join(x for x in [f"Mã số {reg['code']}" if reg.get('code') else '', f"TCCS {reg['tccs']}" if reg.get('tccs') else ''] if x)
            cards.append(f"""<article class="card{'' if img else ' noimg'}" data-k="{key(it['ten'], tag, ' '.join(uses), c['name'])}">
{f'<div class="ph"><img src="{img}" alt="{e(it["ten"])}" loading="lazy"></div>' if img else ''}
<div class="tx"><h3>{e(it['ten'])}</h3>{f'<div class="tag">{e(tag)}</div>' if tag else ''}
<ul class="u">{''.join(f'<li>{e(u)}</li>' for u in uses)}</ul><div class="reg">{e(regt)}</div>{pb}</div></article>""")
        for i in range(0, len(cards), per):
            chunk = cards[i:i + per]
            head = f'<div class="sec-h"><h2>{e(c["name"])}</h2><small>{c["count"]} sản phẩm</small></div>' if i == 0 else f'<div class="sec-h"><h2 style="font-size:var(--t1)">{e(c["name"])} (tiếp)</h2><small>{c["count"]} sản phẩm</small></div>'
            pages.append(f'<section class="page" data-sec {"id=" + chr(34) + c["slug"] + chr(34) if i == 0 else ""} style="--c:var(--c-{c["slug"]})">{head}<div class="grid">{"".join(chunk)}</div>'
                         f'<div class="pgfoot"><span>NOBEN · {e(c["name"].upper())}</span><span>{pg}</span></div></section>')
            pg += 1
    doc = f"""<title>Catalogue Noben 2026</title>
<meta name="claude:viewport-fit-sides" content="cover">{FONTS}<style>{css}</style>
{cover}{intro}
<div class="tools"><input id="q" type="search" placeholder="Tìm trong {len(ITEMS)} sản phẩm (vd: gan, khí độc, cứng vỏ)" aria-label="Tìm sản phẩm"><span id="qn"></span></div>
{''.join(pages)}{SEARCH_JS}"""
    (OUT / 'CATALOGUE-NOBEN-2026.html').write_text(doc)
    return OUT / 'CATALOGUE-NOBEN-2026.html', rows

# =====================================================================
# 3. CATALOGUE THỦY SẢN TÍM
# =====================================================================
def tim_pb(ten, hotline):
    """Giá Tím = giá trong bảng giá Noben của sản phẩm cùng tên."""
    _, sps = tim_gia(ten)
    if not sps:
        return f'<div class="ask"><span>Giá bán</span><b>Liên hệ báo giá · {e(hotline)}</b></div>'
    li = ''.join(f'<li><span>{e(qc)} · {e(dt)}</span><b class="num">{money(v)}đ</b></li>' for sp in sps for qc, dt, v in sp['v'])
    return f'<div class="pz"><span>Giá bán</span><ul>{li}</ul></div>'

def build_tim():
    css = BASE_CSS + """
:root{--desk:#ece8f3;--paper:#fdfcff;--ink:#160d2a;--muted:#635a78;--line:#e2dcec;--violet:#5b3aa6;--plum:#2a1650;--gold:#d9b977;--gold-d:#8a6a2e;--accent:#5b3aa6;
 --disp:'Cormorant Garamond','Playfair Display',Georgia,serif}
.cover{background:var(--plum);color:#fff;min-height:640px;display:grid;grid-template-columns:61.8fr 38.2fr;padding:0}
.cover .l{padding:var(--s6) var(--s5);display:flex;flex-direction:column;justify-content:space-between;gap:var(--s5)}
.cover .r{background:var(--violet);display:grid;place-items:center;padding:var(--s5)}
.cover .r img{width:100%;max-width:260px;height:auto}
.cover .eb{font-size:13px;letter-spacing:.24em;text-transform:uppercase;color:var(--gold)}
.cover h1{font-family:var(--disp);font-weight:600;font-size:var(--t4);line-height:1}
.cover h1 em{color:var(--gold);font-style:italic}
.cover p{margin:0;color:#d8cdef;max-width:30em}
.cover .ct{font-size:14px;color:#d8cdef;border-top:1px solid rgb(255 255 255/.2);padding-top:var(--s3)}
.cover .ct b{color:#fff}
.sec-h{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--gold);padding-bottom:var(--s2);margin-bottom:var(--s4);gap:var(--s3);flex-wrap:wrap}
.sec-h h2{font-family:var(--disp);font-size:var(--t3);color:var(--plum);font-weight:600;line-height:1.1}
.sec-h small{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--gold-d);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,460px),1fr));gap:var(--s4)}
.card{display:grid;grid-template-columns:38.2fr 61.8fr;gap:var(--s4);min-width:0;padding-bottom:var(--s4);border-bottom:1px solid var(--line)}
.card .ph{display:grid;place-items:center;aspect-ratio:1/1.618;max-width:100%;overflow:hidden}
.card .ph img{max-width:100%;max-height:100%;object-fit:contain}
.card .tx{min-width:0;display:flex;flex-direction:column;gap:var(--s2)}
.card h3{font-family:var(--disp);font-size:var(--t2);font-weight:700;color:var(--plum);line-height:1.1}
.card .sub{font-size:14px;color:var(--c);font-weight:600;line-height:1.4}
.chips{display:flex;gap:var(--s1);flex-wrap:wrap}
.chips span{font-size:11px;padding:2px var(--s2);border-radius:999px;background:color-mix(in srgb,var(--c) 12%,white);color:var(--c);font-weight:600}
.blk b{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold-d);margin-bottom:2px}
.blk ul{margin:0;padding-left:1.1em;font-size:13px;line-height:1.45}
.meta{font-size:12px;color:var(--muted);display:grid;grid-template-columns:auto 1fr;gap:2px var(--s2)}
.meta dt{font-weight:600;color:var(--ink)}.meta dd{margin:0}
.ask{margin-top:auto;display:flex;justify-content:space-between;align-items:center;gap:var(--s2);border-top:1px dashed var(--line);padding-top:var(--s2);font-size:13px}
.ask b{color:var(--violet)}
.pz{margin-top:auto;border-top:1px dashed var(--line);padding-top:var(--s2);font-size:13px}
.pz>span{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold-d);font-weight:600}
.pz ul{list-style:none;margin:0;padding:0}.pz li{display:flex;justify-content:space-between;gap:var(--s2)}
.pz li span{color:var(--muted)}.pz li b{color:var(--violet);white-space:nowrap}
@media (max-width:640px){.cover{grid-template-columns:1fr}.cover h1{font-size:var(--t3)}.cover .l{padding:var(--s5) var(--s4)}}
@media print{
 .cover{min-height:0}.cover .l{padding:22mm 16mm}
 .sec-h{margin-bottom:4mm}.sec-h h2{font-size:var(--t2)}
 .grid{grid-template-columns:1fr;grid-template-rows:repeat(3,1fr);height:250mm;gap:4mm}
 .card{gap:5mm;padding-bottom:4mm;overflow:hidden}.card .ph{aspect-ratio:auto;height:100%}
 .card h3{font-size:20px}.card .sub{font-size:10px}.blk ul{font-size:8.8px;line-height:1.38}.blk b{font-size:7.5px}
 .meta,.ask,.pz{font-size:8.5px}.pz>span{font-size:7.5px}.chips span{font-size:7.5px}
 .cols{display:grid;grid-template-columns:61.8fr 38.2fr;gap:4mm}
}
.cols{display:grid;gap:var(--s2)}
"""
    pp, sx = TIM_DATA['phan_phoi'], TIM_DATA['san_xuat']
    logo = svg64(TIM / 'public/brand/logo-tim-4k/svg/logo-tim-trang.svg')
    sps = TIM_DATA['san_pham']
    cover = f"""<section class="page cover"><div class="l"><div class="eb">{e(pp['ten'])}</div>
<div><h1>Catalogue<br>sản phẩm<br><em>2026</em></h1></div>
<p>{len(sps)} sản phẩm xử lý môi trường ao nuôi và thức ăn bổ sung cho tôm, cá. Sản xuất bởi {e(sx['ten'].title())}.</p>
<div class="ct"><b>Hotline {e(pp['hotline'])}</b> · {e(pp['web'])}<br>{e(pp['dia_chi'])}</div></div>
<div class="r"><img src="{logo}" alt="Thủy Sản Tím"></div></section>"""
    groups = [('moi-truong', 'Xử lý môi trường ao nuôi'), ('thuc-an', 'Thức ăn bổ sung')]
    pages, rows, pg = [], [], 2
    for slug, name in groups:
        items = [s for s in sps if s['nhom'] == slug]
        cards = []
        for s in items:
            cut = ROOT / f"assets/tim-cutout/{s['slug']}.webp"
            img = img64(cut if cut.exists() else TIM / f"public/img/products/{s['slug']}.webp", bg='#fdfcff')
            cd = s.get('cong_dung', [])[:3]
            tp = [t for t in s.get('thanh_phan', [])][:4]
            hd = s.get('huong_dan', [])[:2]
            rows.append(('Thủy Sản Tím', name, s['ten'], s.get('phu_de', ''), '; '.join(s.get('cong_dung', [])), s.get('ma_so', ''), s.get('tccs', ''), tim_gia(s['ten'])[0] or '', (s.get('quy_cach', ''), tim_gia(s['ten'])[1])))
            cards.append(f"""<article class="card" style="--c:{e(s.get('mau','#5b3aa6'))}" data-k="{key(s['ten'], s.get('phu_de',''), ' '.join(s.get('cong_dung',[])), ' '.join(s.get('nhan_phu',[])))}">
<div class="ph">{f'<img src="{img}" alt="{e(s["ten"])}" loading="lazy">' if img else ''}</div>
<div class="tx"><h3>{e(s['ten'])}</h3><div class="sub">{e(s.get('phu_de',''))}</div>
<div class="chips">{''.join(f'<span>{e(t)}</span>' for t in s.get('nhan_phu', []))}</div>
<div class="cols"><div class="blk"><b>Công dụng</b><ul>{''.join(f'<li>{e(x)}</li>' for x in cd)}</ul></div>
<div class="blk"><b>Thành phần</b><ul>{''.join(f'<li>{e(x)}</li>' for x in tp)}</ul></div></div>
<dl class="meta">{f'<dt>Quy cách</dt><dd>{e(s["quy_cach"])}</dd>' if s.get('quy_cach') else ''}<dt>Mã số</dt><dd>{e(s.get('ma_so') or 'Đang cập nhật')}</dd><dt>TCCS</dt><dd>{e(s.get('tccs',''))}</dd></dl>
{tim_pb(s['ten'], pp['hotline'])}</div></article>""")
        for i in range(0, len(cards), 3):
            head = f'<div class="sec-h"><h2>{e(name)}</h2><small>{len(items)} sản phẩm</small></div>'
            pages.append(f'<section class="page" data-sec>{head}<div class="grid">{"".join(cards[i:i+3])}</div>'
                         f'<div class="pgfoot"><span>THỦY SẢN TÍM · CATALOGUE 2026</span><span>{pg}</span></div></section>')
            pg += 1
    doc = f"""<title>Catalogue Thủy Sản Tím 2026</title>
<meta name="claude:viewport-fit-sides" content="cover">{FONTS}<style>{css}</style>
{cover}
<div class="tools"><input id="q" type="search" placeholder="Tìm sản phẩm (vd: vi sinh, gan, tảo)" aria-label="Tìm sản phẩm"><span id="qn"></span></div>
{''.join(pages)}{SEARCH_JS}"""
    (OUT / 'CATALOGUE-THUY-SAN-TIM-2026.html').write_text(doc)
    return OUT / 'CATALOGUE-THUY-SAN-TIM-2026.html', rows

# =====================================================================
# 4. EXCEL
# =====================================================================
def build_excel(noben_rows, tim_rows):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    navy, gold, band = '0B2347', 'FFC20E', 'F3F6FB'
    thin = Side(style='thin', color='D6DDE8')
    B = Border(bottom=thin)
    def head(ws, r, cols, fill=navy):
        for i, c in enumerate(cols, 1):
            x = ws.cell(r, i, c); x.font = Font(bold=True, color='FFFFFF'); x.fill = PatternFill('solid', fgColor=fill)
            x.alignment = Alignment(vertical='center', wrap_text=True)
    def widths(ws, ws_w):
        for i, w in enumerate(ws_w, 1): ws.column_dimensions[get_column_letter(i)].width = w

    wb = Workbook(); wb.remove(wb.active)
    flat = wb.create_sheet('Tong hop')
    head(flat, 1, ['Bảng', 'Nhóm', 'STT', 'Tên sản phẩm', 'Ghi chú tên', 'Quy cách', 'Đóng thùng', 'Giá bán (đ)', 'Công dụng', 'Cần đối chiếu'])
    fr = 2
    for b in GIA['bang']:
        ws = wb.create_sheet({'A': 'Bang gia Noben 2026', 'T': 'Bang gia Tom 02-03', 'B': 'Bao gia Noben (B)'}[b['id']])
        ws.merge_cells('A1:F1'); ws['A1'] = 'CÔNG TY TNHH NOBEN · ' + b['ten']; ws['A1'].font = Font(bold=True, size=16, color=navy)
        ws.merge_cells('A2:F2'); ws['A2'] = b['hieu_luc']; ws['A2'].font = Font(italic=True, color='5B6A80')
        ws.merge_cells('A3:F3'); ws['A3'] = '228/9 Nguyễn Thị Lắng, Ấp Phú Lợi A, Xã Củ Chi, TP.HCM · ĐT 028 3796 6039 · Hotline 0911 88 39 79'
        head(ws, 5, ['STT', 'Tên sản phẩm', 'Quy cách', 'Đóng thùng', 'Công dụng', 'Giá bán (đ)'])
        r = 6
        for g in b['nhom']:
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
            c = ws.cell(r, 1, g['ten'].upper()); c.font = Font(bold=True, color=navy); c.fill = PatternFill('solid', fgColor=band)
            r += 1
            for s in g['sp']:
                start = r
                for i, (qc, dt, gia) in enumerate(s['v']):
                    if i == 0:
                        ws.cell(r, 1, s['stt'])
                        ws.cell(r, 2, s['ten'] + (f" ({s['phu']})" if s.get('phu') else '') + (' *' if s.get('kiem') else '')).font = Font(bold=True, color=navy)
                        ws.cell(r, 5, s['cd'])
                    ws.cell(r, 3, qc); ws.cell(r, 4, dt)
                    p = ws.cell(r, 6, gia); p.number_format = '#,##0'; p.font = Font(bold=True)
                    for col in range(1, 7):
                        ws.cell(r, col).border = B; ws.cell(r, col).alignment = Alignment(vertical='top', wrap_text=True)
                    flat.append([b['ten'], g['ten'], s['stt'], s['ten'], s.get('phu', ''), qc, dt, gia, s['cd'], 'Có' if s.get('kiem') else ''])
                    flat.cell(fr, 8).number_format = '#,##0'; fr += 1
                    r += 1
                if r - start > 1:
                    for col in (1, 2, 5):
                        ws.merge_cells(start_row=start, start_column=col, end_row=r - 1, end_column=col)
        ws.cell(r + 1, 1, 'Đơn vị: đồng. Dấu *: số liệu cần đối chiếu bản gốc.').font = Font(italic=True, color='5B6A80')
        widths(ws, [6, 30, 14, 16, 62, 14]); ws.freeze_panes = 'A6'
        ws.page_setup.orientation = 'portrait'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.print_title_rows = '5:5'
    widths(flat, [28, 30, 6, 26, 18, 14, 16, 14, 70, 10]); flat.freeze_panes = 'A2'; flat.auto_filter.ref = f'A1:J{fr-1}'
    wb.move_sheet('Tong hop', offset=3)
    wb.save(OUT / 'BANG-GIA-NOBEN-2026.xlsx')

    wb = Workbook(); wb.remove(wb.active)
    for title, rows, fill in (('Noben', noben_rows, navy), ('Thuy San Tim', tim_rows, '5B3AA6')):
        ws = wb.create_sheet(title)
        cols = ['STT', 'Thương hiệu', 'Nhóm', 'Tên sản phẩm', 'Mô tả ngắn', 'Công dụng', 'Mã số', 'TCCS']
        cols += ['Bảng giá', 'Quy cách & giá (đ)'] if title == 'Noben' else ['Quy cách', 'Giá bán (đ)']
        head(ws, 1, cols, fill)
        for i, row in enumerate(rows, 1):
            brand, nhom, ten, tag, cd, ma, tccs, bid, extra = row
            if title == 'Noben':
                gia = '; '.join(f"[{BANG_TAG[s['_b']]}] {qc} ({dt}): {money(v)}" for s in extra for qc, dt, v in s['v'])
                ws.append([i, brand, nhom, ten, tag, cd, ma, tccs, bid, gia])
            else:
                qcs, sps = extra
                gia = '; '.join(f"{qc} ({dt}): {money(v)}" for sp in sps for qc, dt, v in sp['v']) or 'Liên hệ báo giá'
                ws.append([i, brand, nhom, ten, tag, cd, ma, tccs, qcs, gia])
            for col in range(1, len(cols) + 1):
                ws.cell(i + 1, col).alignment = Alignment(vertical='top', wrap_text=True); ws.cell(i + 1, col).border = B
        widths(ws, [5, 14, 26, 24, 40, 70, 12, 16, 14, 46]); ws.freeze_panes = 'A2'; ws.auto_filter.ref = f'A1:{get_column_letter(len(cols))}{len(rows)+1}'
    wb.save(OUT / 'DANH-MUC-SAN-PHAM-NOBEN-TIM-2026.xlsx')

# =====================================================================
# 5. PDF (Chromium headless)
# =====================================================================
def to_pdf(files):
    import subprocess
    subprocess.run(['node', str(ROOT / 'pdf.js'), *map(str, files)], check=True)

if __name__ == '__main__':
    bg = build_bang_gia()
    nb, nrows = build_noben()
    tm, trows = build_tim()
    build_excel(nrows, trows)
    hit = sum(1 for r in nrows if r[7])
    print(f'Noben: {len(nrows)} SP (từ bảng giá); Tím: {len(trows)} SP')
    if '--no-pdf' not in sys.argv:
        to_pdf([bg, nb, tm])
