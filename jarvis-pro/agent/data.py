"""THE ONLY FILE THAT TOUCHES REAL DATA.

JARVIS_DEMO=1 (default) -> invented fixtures in data/demo/
JARVIS_DEMO=0           -> the folders in JARVIS_SOURCES (read-only, never written)
"""
import email, imaplib, io, json, os, re, urllib.request, zipfile, zlib, html as htmllib
from datetime import date, datetime
from email.header import decode_header, make_header
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
    if ext == ".docx":
        return _zip_xml(b, [r"word/document\.xml"])
    if ext == ".xlsx":
        return _zip_xml(b, [r"xl/sharedStrings\.xml", r"xl/worksheets/sheet\d+\.xml"])
    if ext == ".pdf":
        return _pdf(b)
    if ext in (".doc", ".xls"):
        return _ole_text(b)
    return ""


def html_text(s):
    s = re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", htmllib.unescape(s))


def html_links(s):
    return re.findall(r'href="([^"#?]+)', s)


def _zip_xml(b, patterns):
    out = []
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        for n in z.namelist():
            if any(re.fullmatch(pt, n) for pt in patterns):
                x = z.read(n).decode("utf-8", "replace")
                out.append(re.sub(r"<[^>]+>", " ", x))
    return re.sub(r"\s+", " ", htmllib.unescape(" ".join(out)))


def _pdf(b):
    """Crude stdlib PDF text: inflate streams, pull (...) strings from text ops."""
    chunks = []
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", b, re.S):
        data = m.group(1)
        try:
            data = zlib.decompress(data)
        except Exception:
            pass
        for t in re.findall(rb"\((.*?)(?<!\\)\)\s*T[Jj]", data):
            chunks.append(t.decode("latin-1", "replace"))
    return " ".join(chunks)


def _ole_text(b):
    """Crude text from legacy Word/Excel: UTF-16LE runs + 8-bit runs."""
    runs = re.findall(rb"(?:[\x20-\x7e\xc0-\xff][\x00-\x1f]|[\x20-\x7e]\x00){4,}", b)
    u = [r.decode("utf-16-le", "ignore") for r in runs]
    a = re.findall(rb"[\x20-\x7e]{6,}", b)
    text = " ".join(u) + " " + " ".join(x.decode("latin-1") for x in a)
    return re.sub(r"\s+", " ", text)


def read_raw(src, rel):
    """Raw file text for link parsing (HTML / markdown only)."""
    p = Path(src) / rel
    if p.suffix.lower() in (".html", ".htm", ".md", ".markdown"):
        return p.read_text("utf-8", "replace")
    return ""


# ---------- inbox & calendar (read-only) ----------
def inbox(limit=15):
    """Recent mail. Demo: fixtures. Real: IMAP, read-only (BODY.PEEK never marks as read)."""
    if DEMO:
        f = ROOT / "data" / "demo" / "_inbox.json"
        return json.loads(f.read_text("utf-8")) if f.exists() else []
    host, user, pw = (os.environ.get(k, "") for k in ("JARVIS_IMAP_HOST", "JARVIS_IMAP_USER", "JARVIS_IMAP_PASSWORD"))
    if not (host and user and pw):
        raise RuntimeError("inbox not configured (JARVIS_IMAP_HOST / USER / PASSWORD in .env)")
    out = []
    with imaplib.IMAP4_SSL(host) as m:
        m.login(user, pw)
        m.select("INBOX", readonly=True)
        _, ids = m.search(None, "ALL")
        ids = ids[0].split()[-limit:]
        _, unseen = m.search(None, "UNSEEN")
        unseen = set(unseen[0].split())
        for i in reversed(ids):
            _, d = m.fetch(i, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)] BODY.PEEK[TEXT]<0.600>)")
            hdr = email.message_from_bytes(d[0][1])
            body = d[1][1].decode("utf-8", "replace") if len(d) > 1 and isinstance(d[1], tuple) else ""
            dec = lambda v: str(make_header(decode_header(v or "")))
            out.append({"id": i.decode(), "from": dec(hdr["From"]), "subject": dec(hdr["Subject"]),
                        "date": hdr["Date"] or "", "unread": i in unseen, "body": re.sub(r"\s+", " ", body)[:400]})
    return out


def calendar():
    """Events. Demo: fixtures. Real: an .ics URL or file (JARVIS_ICS), read-only."""
    if DEMO:
        f = ROOT / "data" / "demo" / "_calendar.json"
        return json.loads(f.read_text("utf-8")) if f.exists() else []
    src = os.environ.get("JARVIS_ICS", "")
    if not src:
        raise RuntimeError("calendar not configured (JARVIS_ICS in .env)")
    raw = urllib.request.urlopen(src, timeout=15).read().decode("utf-8", "replace") if src.startswith("http") \
        else Path(src).expanduser().read_text("utf-8", "replace")
    raw = re.sub(r"\r?\n[ \t]", "", raw)
    events = []
    for blk in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", raw, re.S):
        get = lambda k: (re.search(rf"^{k}[^:]*:(.*)$", blk, re.M) or [None, ""])[1].strip()
        st = get("DTSTART")
        if len(st) < 8:
            continue
        events.append({"date": f"{st[:4]}-{st[4:6]}-{st[6:8]}", "time": f"{st[9:11]}:{st[11:13]}" if "T" in st else "",
                       "title": get("SUMMARY").replace("\\,", ",")})
    return sorted(events, key=lambda e: (e["date"], e["time"]))


def today():
    return os.environ.get("JARVIS_TODAY") or (("2026-11-18") if DEMO else date.today().isoformat())
