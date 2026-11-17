"""THE ONLY FILE THAT TOUCHES REAL DATA.

JARVIS_DEMO=1 (default) -> invented fixtures in data/demo/
JARVIS_DEMO=0           -> the folders in JARVIS_SOURCES (read-only, never written)
"""
import io, os, re, zipfile, zlib, html as htmllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = os.environ.get("JARVIS_DEMO", "1") != "0"
MAX_BYTES = 2 * 1024 * 1024
SKIP_DIRS = {"jarvis-pro", "node_modules", ".git", "__pycache__", ".next", "dist", "build", "vendor"}
TEXT_EXT = {".md", ".markdown", ".txt", ".csv"}
DOC_EXT = TEXT_EXT | {".html", ".htm", ".pdf", ".docx", ".xlsx", ".doc", ".xls"}


def sources():
    if DEMO:
        return [ROOT / "data" / "demo"]
    raw = os.environ.get("JARVIS_SOURCES", "")
    return [Path(p).expanduser() for p in raw.split(os.pathsep) if p.strip()]


def mode():
    return "demo" if DEMO else "real"


def iter_documents():
    """Yield (source_root, relative_path, text). Read-only."""
    for src in sources():
        if not src.is_dir():
            print(f"[data] missing source: {src}")
            continue
        for dirpath, dirnames, files in os.walk(src):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for f in files:
                p = Path(dirpath) / f
                ext = p.suffix.lower()
                if ext not in DOC_EXT:
                    continue
                try:
                    if p.stat().st_size > MAX_BYTES:
                        continue
                    text = extract(p, ext)
                except Exception as e:  # unreadable file: skip, never crash
                    print(f"[data] skip {p}: {e}")
                    continue
                if text and text.strip():
                    yield src, p.relative_to(src), text


def extract(p, ext):
    b = p.read_bytes()
    if ext in TEXT_EXT:
        return b.decode("utf-8", "replace")
    if ext in (".html", ".htm"):
        return html_text(b.decode("utf-8", "replace"))
    if ext == ".pdf":
        return _pdf(b)
    if b[:2] == b"PK":                     # trust the bytes, not the name: many ".xls" are really .xlsx
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            names = set(z.namelist())
        return _docx(b) if "word/document.xml" in names else _xlsx(b) if "xl/workbook.xml" in names else ""
    if ext in (".doc", ".xls", ".docx", ".xlsx"):
        st = b[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
        return (_xls(b) if ext.startswith(".xls") else _doc(b)) if st else ""
    return ""


def html_text(s):
    s = re.sub(r"(?is)<(script|style|svg|noscript|template)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<!--.*?-->", " ", s)
    s = re.sub(r"(?i)<(br|/p|/div|/li|/h\d|/tr|/section|/article)[^>]*>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = htmllib.unescape(s)
    return re.sub(r"\s*\n\s*", "\n", re.sub(r"[ \t\r\f\v]+", " ", s)).strip()


def html_links(s):
    return re.findall(r'href="([^"#?]+)', s)


def _clean(s):
    """Collapse spaces, keep line breaks, drop control chars."""
    s = re.sub(r"[\x00-\x08\x0e-\x1f\x7f�]", " ", s)
    s = re.sub(r"[ \t\f\v]+", " ", s)
    return re.sub(r"\s*\n\s*", "\n", s).strip()


# ---- Office Open XML (.docx / .xlsx) ----
import struct, xml.etree.ElementTree as ET

def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _docx(b):
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    lines = []
    for para in root.iter():
        if _local(para.tag) != "p":
            continue
        t = "".join(x.text or "" if _local(x.tag) == "t" else "\t" if _local(x.tag) == "tab" else ""
                    for x in para.iter())
        if t.strip():
            lines.append(t)
    return _clean("\n".join(lines))


def _xlsx(b):
    """Rows as 'a | b | c' lines, shared strings substituted (prices stay next to product names)."""
    out = []
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        names = z.namelist()
        sst = []
        if "xl/sharedStrings.xml" in names:
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
                sst.append("".join(t.text or "" for t in si.iter() if _local(t.tag) == "t"))
        sheets = sorted((n for n in names if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)),
                        key=lambda n: int(re.findall(r"\d+", n)[-1]))
        for n in sheets:
            for row in ET.fromstring(z.read(n)).iter():
                if _local(row.tag) != "row":
                    continue
                cells = []
                for c in row:
                    if _local(c.tag) != "c":
                        continue
                    kind, val = c.get("t"), None
                    for x in c.iter():
                        if _local(x.tag) in ("v", "t") and x.text is not None:
                            val = x.text
                    if val is None:
                        continue
                    if kind == "s":
                        try: val = sst[int(val)]
                        except (ValueError, IndexError): continue
                    elif kind not in ("str", "inlineStr", "b", "e"):
                        val = _num(val)
                    val = val.strip()
                    if val:
                        cells.append(val)
                if cells:
                    out.append(" | ".join(cells))
    return _clean("\n".join(out))


def _num(v):
    try:
        f = float(v)
    except ValueError:
        return v
    return str(int(f)) if f == int(f) and abs(f) < 1e15 else f"{f:.4g}"


# ---- legacy OLE2 (.doc / .xls): compound file -> streams ----
def _cfb(b):
    """Streams of an OLE2 compound file as {name: bytes}. Stdlib-only, bounded loops."""
    if b[:8] != b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return {}
    u32 = lambda o: struct.unpack_from("<I", b, o)[0]
    ss, mss = 1 << struct.unpack_from("<H", b, 30)[0], 1 << struct.unpack_from("<H", b, 32)[0]
    nfat, dir0, cutoff, mfat0, nmfat, difat0, ndifat = (u32(o) for o in (44, 48, 56, 60, 64, 68, 72))
    sec = lambda i: b[(i + 1) * ss:(i + 2) * ss]
    fat_secs = [u32(76 + 4 * i) for i in range(109)]
    d = difat0
    for _ in range(min(ndifat, 1 << 16)):
        if d >= 0xFFFFFFFA: break
        x = sec(d); fat_secs += list(struct.unpack_from(f"<{ss // 4 - 1}I", x)); d = struct.unpack_from("<I", x, ss - 4)[0]
    fat = []
    for f in fat_secs[:nfat]:
        x = sec(f)
        fat += struct.unpack_from(f"<{len(x) // 4}I", x)
    def chain(s, table, limit):
        out = []
        while s < 0xFFFFFFFA and s < len(table) and len(out) < limit:
            out.append(s); s = table[s]
        return out
    lim = len(b) // ss + 2
    dirb = b"".join(sec(i) for i in chain(dir0, fat, lim))
    mfat = []
    for i in chain(mfat0, fat, lim):
        x = sec(i); mfat += struct.unpack_from(f"<{len(x) // 4}I", x)
    ents = []
    for o in range(0, len(dirb) - 127, 128):
        nl = struct.unpack_from("<H", dirb, o + 64)[0]
        name = dirb[o:o + max(0, nl - 2)].decode("utf-16-le", "ignore")
        typ, start, size = dirb[o + 66], struct.unpack_from("<I", dirb, o + 116)[0], struct.unpack_from("<I", dirb, o + 120)[0]
        ents.append((name, typ, start, size))
    if not ents:
        return {}
    root = ents[0]
    mini = b"".join(sec(i) for i in chain(root[2], fat, lim))
    out = {}
    for name, typ, start, size in ents:
        if typ != 2:
            continue
        if size < cutoff:
            data = b"".join(mini[i * mss:(i + 1) * mss] for i in chain(start, mfat, size // mss + 2))
        else:
            data = b"".join(sec(i) for i in chain(start, fat, size // ss + 2))
        out[name] = data[:size]
    return out


def _doc(b):
    """Word 97-2003: read the piece table, so Vietnamese text comes out whole."""
    st = _cfb(b)
    wd = st.get("WordDocument")
    if not wd:
        return _ole_text(b)
    try:
        flags = struct.unpack_from("<H", wd, 0x0A)[0]
        tbl = st.get("1Table" if flags & 0x0200 else "0Table") or b""
        csw = struct.unpack_from("<H", wd, 32)[0]; o = 34 + csw * 2
        cslw = struct.unpack_from("<H", wd, o)[0]; o += 2 + cslw * 4 + 2
        fc_clx, lcb_clx = struct.unpack_from("<II", wd, o + 33 * 8)
        i, end = fc_clx, fc_clx + lcb_clx
        while i < end and tbl[i] == 1:
            i += 3 + struct.unpack_from("<H", tbl, i + 1)[0]
        if tbl[i] != 2:
            raise ValueError("no piece table")
        lcb = struct.unpack_from("<I", tbl, i + 1)[0]; i += 5
        n = (lcb - 4) // 12
        cps = struct.unpack_from(f"<{n + 1}I", tbl, i)
        parts = []
        for k in range(n):
            fc = struct.unpack_from("<I", tbl, i + 4 * (n + 1) + 8 * k + 2)[0]
            cnt = cps[k + 1] - cps[k]
            if fc & 0x40000000:
                s0 = (fc & 0x3FFFFFFF) // 2
                parts.append(wd[s0:s0 + cnt].decode("cp1252", "replace"))
            else:
                parts.append(wd[fc:fc + 2 * cnt].decode("utf-16-le", "replace"))
        t = "".join(parts)
    except (struct.error, IndexError, ValueError):
        return _ole_text(b)
    t = re.sub(r"\x13[^\x13\x14\x15]*\x14", "", t)            # field: keep the result, drop the code
    t = re.sub(r"\x13[^\x13\x14\x15]*\x15", "", t)
    t = t.replace("\x07", "\t").replace("\r", "\n").replace("\x0b", "\n").replace("\x0c", "\n")
    t = re.sub(r"\t+\n", "\n", t).replace("\t", " | ")
    return _clean(t)


def _xls(b):
    """Excel 97-2003 (BIFF8): shared strings + text/number cells, one line per row."""
    st = _cfb(b)
    wb = st.get("Workbook") or st.get("Book")
    if not wb:
        return _ole_text(b)
    recs, i = [], 0
    while i + 4 <= len(wb):
        typ, ln = struct.unpack_from("<HH", wb, i)
        recs.append((typ, wb[i + 4:i + 4 + ln])); i += 4 + ln
    sst = []
    for k, (typ, body) in enumerate(recs):
        if typ == 0x00FC:
            chunks = [body[8:]]
            j = k + 1
            while j < len(recs) and recs[j][0] == 0x003C:
                chunks.append(recs[j][1]); j += 1
            sst = _sst(chunks, struct.unpack_from("<I", body, 4)[0])
            break
    rows, sheet = {}, -1
    def put(r, c, v):
        rows.setdefault((sheet, r), {})[c] = v
    for typ, body in recs:
        try:
            if typ == 0x0809:
                sheet += 1
            elif typ == 0x00FD:
                r, c, _, isst = struct.unpack_from("<HHHI", body)
                if isst < len(sst): put(r, c, sst[isst])
            elif typ == 0x0203:
                r, c, _, f = struct.unpack_from("<HHHd", body); put(r, c, _num(repr(f)))
            elif typ == 0x027E:
                r, c, _, rk = struct.unpack_from("<HHHI", body); put(r, c, _num(repr(_rk(rk))))
            elif typ == 0x00BD:
                r, c0 = struct.unpack_from("<HH", body)
                for q in range((len(body) - 6) // 6):
                    put(r, c0 + q, _num(repr(_rk(struct.unpack_from("<I", body, 4 + 6 * q + 2)[0]))))
            elif typ == 0x0204:
                r, c, _, n = struct.unpack_from("<HHHH", body)
                hi = body[8] & 1
                put(r, c, body[9:9 + n * (2 if hi else 1)].decode("utf-16-le" if hi else "latin-1", "replace"))
        except struct.error:
            continue
    lines = [" | ".join(v.strip() for _, v in sorted(cells.items()) if v.strip()) for _, cells in sorted(rows.items())]
    return _clean("\n".join(l for l in lines if l))


def _rk(rk):
    if rk & 2:
        v = (rk >> 2) - (1 << 30) if rk & 0x80000000 else rk >> 2
    else:
        v = struct.unpack("<d", struct.pack("<Q", (rk & 0xFFFFFFFC) << 32))[0]
    return v / 100 if rk & 1 else v


def _sst(chunks, count):
    """BIFF8 shared-string table, strings may span CONTINUE records."""
    out, ci, pos = [], 0, 0
    def need(n):
        nonlocal ci, pos
        while ci < len(chunks) and pos + n > len(chunks[ci]):
            if pos < len(chunks[ci]): return False
            ci += 1; pos = 0
        return ci < len(chunks)
    def take(n):
        nonlocal ci, pos
        buf = b""
        while n > 0 and ci < len(chunks):
            part = chunks[ci][pos:pos + n]; buf += part; n -= len(part); pos += len(part)
            if pos >= len(chunks[ci]): ci += 1; pos = 0
        return buf
    while len(out) < count and ci < len(chunks):
        head = take(3)
        if len(head) < 3: break
        cch, fl = struct.unpack("<HB", head)
        runs = struct.unpack("<H", take(2))[0] if fl & 8 else 0
        ext = struct.unpack("<I", take(4))[0] if fl & 4 else 0
        hi, s, left = fl & 1, "", cch
        while left > 0 and ci < len(chunks):
            room = len(chunks[ci]) - pos
            n = min(left, room // (2 if hi else 1))
            if n <= 0:
                ci += 1; pos = 0
                if ci < len(chunks): hi = chunks[ci][0] & 1; pos = 1
                continue
            raw = take(n * (2 if hi else 1))
            s += raw.decode("utf-16-le" if hi else "latin-1", "replace"); left -= n
            if left > 0 and pos == 0 and ci < len(chunks):
                hi = chunks[ci][0] & 1; pos = 1
        take(4 * runs + ext)
        out.append(s)
    return out


def _ole_text(b):
    """Fallback when the file is not a readable OLE2 Word/Excel: UTF-16 runs of Latin/Vietnamese letters."""
    out = []
    for off in (0, 1):
        u = b[off:len(b) - ((len(b) - off) % 2)].decode("utf-16-le", "replace")
        out += re.findall(r"[0-9A-Za-zÀ-ɏḀ-ỿ .,:;%()/\-]{8,}", u)
    good = [r for r in out if sum(ch.isalpha() for ch in r) >= len(r) * 0.6 and " " in r.strip()]
    return _clean("\n".join(good))


# ---- PDF: inflate streams, map glyph codes through each font's ToUnicode CMap ----
def _pdf(b):
    objs = {}
    for m in re.finditer(rb"(\d+)\s+\d+\s+obj\b(.*?)endobj", b, re.S):
        objs[int(m.group(1))] = m.group(2)
    def body(o):
        sm = re.search(rb"stream\r?\n", o)
        if not sm: return o, None
        head, data = o[:sm.start()], o[sm.end():]
        e = data.rfind(b"endstream")
        data = data[:e] if e >= 0 else data
        if b"FlateDecode" in head:
            try: data = zlib.decompressobj().decompress(data)
            except zlib.error: return head, None
        elif b"/Filter" in head:
            return head, None                      # images / other filters: not text
        return head, data
    parsed = {n: body(o) for n, o in objs.items()}
    # object streams (PDF 1.5+): unpack embedded objects
    for n, (head, data) in list(parsed.items()):
        if data and b"/ObjStm" in head:
            fm = re.search(rb"/First\s+(\d+)", head)
            if not fm: continue
            first = int(fm.group(1)); nums = list(map(int, data[:first].split()))
            for k in range(0, len(nums) - 1, 2):
                a = first + nums[k + 1]; z = first + nums[k + 3] if k + 3 < len(nums) else len(data)
                parsed.setdefault(nums[k], (data[a:z], None))
    cmaps = {}
    def cmap(ref):
        if ref in cmaps: return cmaps[ref]
        m, d = {}, (parsed.get(ref) or (b"", None))[1] or b""
        for blk in re.findall(rb"beginbfchar(.*?)endbfchar", d, re.S):
            for k, v in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]*)>", blk):
                m[k.upper()] = _u16hex(v)
        for blk in re.findall(rb"beginbfrange(.*?)endbfrange", d, re.S):
            for lo, hi, rest in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(\[[^\]]*\]|<[0-9A-Fa-f]*>)", blk):
                w, a, z = len(lo), int(lo, 16), int(hi, 16)
                if z - a > 65535: continue
                if rest.startswith(b"["):
                    for q, v in enumerate(re.findall(rb"<([0-9A-Fa-f]*)>", rest)):
                        m[b"%0*X" % (w, a + q)] = _u16hex(v)
                else:
                    base = _u16hex(rest[1:-1])
                    for q in range(z - a + 1):
                        m[b"%0*X" % (w, a + q)] = base[:-1] + chr(ord(base[-1]) + q) if base else ""
        cmaps[ref] = m
        return m
    font_map = {}                                   # font object -> cmap (or None)
    for n, (head, _) in parsed.items():
        if b"/Font" in head and b"/ToUnicode" in head:
            r = re.search(rb"/ToUnicode\s+(\d+)\s+\d+\s+R", head)
            if r: font_map[n] = cmap(int(r.group(1)))
    def fonts_in(d):
        out = {}
        fm = re.search(rb"/Font\s*(<<.*?>>|\d+\s+\d+\s+R)", d, re.S)
        if not fm: return out
        blk = fm.group(1)
        if blk.endswith(b"R"):
            blk = (parsed.get(int(blk.split()[0])) or (b"", None))[0]
        for name, ref in re.findall(rb"/([^\s/<>\[\]]+)\s+(\d+)\s+\d+\s+R", blk):
            out[name] = font_map.get(int(ref))
        return out
    global_fonts = {}
    for head, _ in parsed.values():
        if b"/Font" in head: global_fonts.update(fonts_in(head))
    pages = []
    for n, (head, _) in parsed.items():
        if re.search(rb"/Type\s*/Page\b", head):
            res = re.search(rb"/Resources\s+(\d+)\s+\d+\s+R", head)
            fonts = fonts_in((parsed.get(int(res.group(1))) or (b"", None))[0] if res else head) or global_fonts
            cm = re.search(rb"/Contents\s*(\[[^\]]*\]|\d+\s+\d+\s+R)", head)
            refs = [int(x) for x in re.findall(rb"(\d+)\s+\d+\s+R", cm.group(1))] if cm else []
            pages.append((n, fonts, refs))
    pages.sort()
    texts = []
    seen = set()
    for _, fonts, refs in pages:
        for r in refs:
            d = (parsed.get(r) or (b"", None))[1]
            if d: texts.append(_pdf_ops(d, fonts)); seen.add(r)
    if not pages:                                   # unusual layout: scan every stream with text operators
        for n, (head, d) in parsed.items():
            if d and re.search(rb"\bT[Jj]\b", d): texts.append(_pdf_ops(d, global_fonts))
    return _clean("\n".join(texts))


def _u16hex(h):
    h = h.decode() if isinstance(h, bytes) else h
    try: return bytes.fromhex(h + "0" * (len(h) % 2)).decode("utf-16-be", "replace")
    except ValueError: return ""


_PDF_TOK = re.compile(rb"\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f\s]*>|\[|\]|/[^\s/\[\]()<>]+|[-+]?\d*\.?\d+|[A-Za-z'\"*]+")

def _pdf_ops(d, fonts):
    out, stack, cmap_, arr = [], [], None, None
    def dec(tok):
        if tok.startswith(b"("):
            s = re.sub(rb"\\([nrtbf()\\]|[0-7]{1,3})", lambda m: {b"n": b"\n", b"r": b"", b"t": b" ", b"b": b"", b"f": b""}.get(
                m.group(1), bytes([int(m.group(1), 8) & 255]) if m.group(1)[:1].isdigit() else m.group(1)), tok[1:-1])
            if cmap_:
                return "".join(cmap_.get(b"%02X" % c, "") for c in s)
            return s.decode("latin-1")
        h = re.sub(rb"\s", b"", tok[1:-1]).upper()
        if not cmap_:
            return _u16hex(h) if len(h) % 4 == 0 else bytes.fromhex((h + b"0" * (len(h) % 2)).decode()).decode("latin-1")
        w = len(next(iter(cmap_))) if cmap_ else 2
        return "".join(cmap_.get(h[i:i + w], "") for i in range(0, len(h), w))
    for tok in _PDF_TOK.findall(d):
        if tok == b"[":
            arr = []; continue
        if tok == b"]":
            stack.append(arr); arr = None; continue
        if arr is not None:
            if tok[:1] in b"(<": arr.append(dec(tok))
            else:
                try:
                    if float(tok) < -180: arr.append(" ")
                except ValueError: pass
            continue
        if tok == b"Tf" and len(stack) >= 2:
            name = stack[-2]
            cmap_ = fonts.get(name[1:]) if isinstance(name, bytes) and name.startswith(b"/") else None
        elif tok in (b"Tj", b"'", b'"') and stack:
            x = stack[-1]
            if tok != b"Tj": out.append("\n")
            out.append(x if isinstance(x, str) else "")
        elif tok == b"TJ" and stack and isinstance(stack[-1], list):
            out.append("".join(stack[-1]))
        elif tok in (b"Td", b"TD", b"T*", b"Tm", b"ET"):
            if tok == b"ET" or tok == b"T*" or (tok in (b"Td", b"TD") and len(stack) >= 2 and _f(stack[-1]) != 0):
                out.append("\n")
            else:
                out.append(" ")
        if tok[:1] in b"(<":
            stack.append(dec(tok))
        elif tok[:1].isalpha() or tok in (b"'", b'"', b"*"):
            stack = []
        else:
            stack.append(tok)
        stack = stack[-8:]
    return "".join(out)


def _f(x):
    try: return float(x)
    except (TypeError, ValueError): return 0.0


def read_raw(src, rel):
    """Raw file text for link parsing (HTML / markdown only)."""
    p = Path(src) / rel
    if p.suffix.lower() in (".html", ".htm", ".md", ".markdown"):
        return p.read_text("utf-8", "replace")
    return ""


# ---------------- inbox + calendar (read-only) ----------------
import datetime as _dt
import email as _email
from email import policy as _policy
from email.utils import parsedate_to_datetime as _pdt, parseaddr as _pa

FIXTURES = ROOT / "data" / "fixtures"
FIXTURE_DAY = _dt.date(2026, 11, 17)   # in demo mode "today" is pinned to this day: same story every recording


def today():
    return FIXTURE_DAY if DEMO else _dt.date.today()


def inbox_dir():
    if DEMO:
        return FIXTURES / "inbox"
    p = os.environ.get("JARVIS_INBOX", "")
    return Path(p).expanduser() if p else None


def inbox(limit=30):
    """Maildir-style folder (new/ = unread, cur/ = read) or a flat folder of .eml. Never writes."""
    d = inbox_dir()
    if not d or not d.is_dir():
        return None
    files = []
    for sub, unread in (("new", True), ("cur", False), (".", False)):
        for f in (d / sub).glob("*"):
            if f.is_file() and (sub != "." or f.suffix.lower() == ".eml"):
                files.append((f, unread))
    out = []
    for f, unread in files:
        try:
            m = _email.message_from_bytes(f.read_bytes(), policy=_policy.default)
            part = m.get_body(preferencelist=("plain", "html"))
            body = part.get_content() if part else ""
            if part and part.get_content_type() == "text/html":
                body = html_text(body)
            name, addr = _pa(str(m.get("From", "")))
            when = _pdt(m.get("Date")) if m.get("Date") else None
            out.append({"from": name or addr, "addr": addr, "subject": str(m.get("Subject", "")),
                        "date": when.isoformat() if when else "", "unread": unread, "body": body.strip()[:1200]})
        except Exception as e:
            print(f"[data] skip mail {f}: {e}")
    out.sort(key=lambda x: x["date"], reverse=True)
    return out[:limit]


def calendar_file():
    if DEMO:
        return FIXTURES / "calendar.ics"
    p = os.environ.get("JARVIS_CALENDAR", "")
    return Path(p).expanduser() if p else None


def calendar(days=2):
    """Events from today for `days` days, from an .ics file. Never writes."""
    f = calendar_file()
    if not f or not f.is_file():
        return None
    text = re.sub(r"\r?\n[ \t]", "", f.read_text("utf-8", "replace"))
    t0, out = today(), []
    for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", text, re.S):
        def get(k):
            m = re.search(rf"^{k}[^:\n]*:(.*)$", block, re.M)
            return m.group(1).strip() if m else ""
        s = get("DTSTART")
        try:
            start = _dt.datetime.strptime(s[:15], "%Y%m%dT%H%M%S") if "T" in s else _dt.datetime.strptime(s[:8], "%Y%m%d")
        except ValueError:
            continue
        if t0 <= start.date() < t0 + _dt.timedelta(days=days):
            out.append({"start": start.isoformat(timespec="minutes"), "title": get("SUMMARY").replace("\\,", ",")})
    return sorted(out, key=lambda e: e["start"])
