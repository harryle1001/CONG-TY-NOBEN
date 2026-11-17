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


# ---------------- inbox + calendar (read-only) ----------------
import datetime as _dt
import time, urllib.parse
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
    """Maildir-style folder (new/ = unread, cur/ = read), a flat folder of .eml, or Gmail. Never writes."""
    if google_source("JARVIS_INBOX"):
        return _gmail_inbox(limit)
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
    """Events from today for `days` days, from an .ics file or Google Calendar. Never writes."""
    if google_source("JARVIS_CALENDAR"):
        return _gcal(days)
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


# ---------------- Google (Gmail + Calendar), read-only, JARVIS_INBOX=google / JARVIS_CALENDAR=google ----------------
import base64 as _b64
from concurrent.futures import ThreadPoolExecutor as _Pool

CACHE_S = float(os.environ.get("JARVIS_GOOGLE_CACHE_S", "60"))  # BRIEF + PLAN + INBOX in a row hit Google once, not three times
_cache = {}


def google_source(var):
    """True only in real mode. Demo mode never touches Google."""
    return not DEMO and os.environ.get(var, "").strip().lower() == "google"


def google_status():
    """For the UI badge. Never contains a token or secret."""
    on = google_source("JARVIS_INBOX") or google_source("JARVIS_CALENDAR")
    if not on:
        return {"enabled": False}
    import google_auth
    return {"enabled": True, **google_auth.status()}


def _cached(key, fn):
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < CACHE_S:
        return hit[1]
    val = fn()
    _cache[key] = (time.time(), val)
    return val


def google_reset():
    _cache.clear()


def _b64text(data):
    return _b64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", "replace")


def _gmail_body(payload):
    """Prefer text/plain; fall back to text/html stripped to text."""
    found = {}

    def walk(p):
        mt = p.get("mimeType", "")
        data = (p.get("body") or {}).get("data")
        if data and mt in ("text/plain", "text/html") and mt not in found and not (p.get("filename") or ""):
            found[mt] = _b64text(data)
        for c in p.get("parts") or []:
            walk(c)
    walk(payload)
    if "text/plain" in found:
        return found["text/plain"]
    return html_text(found["text/html"]) if "text/html" in found else ""


def _gmail_inbox(limit):
    import google_auth as g

    def fetch():
        ids = g.get_json(g.GMAIL_API + "/users/me/messages", {"labelIds": "INBOX", "maxResults": limit}).get("messages") or []

        def one(mid):
            m = g.get_json(g.GMAIL_API + f"/users/me/messages/{urllib.parse.quote(mid['id'])}", {"format": "full"})
            pl = m.get("payload") or {}
            h = {x.get("name", "").lower(): x.get("value", "") for x in pl.get("headers") or []}
            name, addr = _pa(h.get("from", ""))
            try:
                when = _pdt(h["date"]) if h.get("date") else None
            except (TypeError, ValueError):
                when = None
            if not when and m.get("internalDate"):
                when = _dt.datetime.fromtimestamp(int(m["internalDate"]) / 1000, _dt.timezone.utc).astimezone()
            body = _gmail_body(pl) or htmllib.unescape(m.get("snippet", ""))
            return {"from": name or addr, "addr": addr, "subject": h.get("subject", ""),
                    "date": when.isoformat() if when else "", "unread": "UNREAD" in (m.get("labelIds") or []),
                    "body": body.strip()[:1200]}
        with _Pool(6) as pool:
            out = list(pool.map(one, ids))
        out.sort(key=lambda x: x["date"], reverse=True)
        return out[:limit]
    return _cached(("gmail", limit), fetch)


def _gcal(days):
    import google_auth as g

    def fetch():
        t0 = _dt.datetime.combine(today(), _dt.time()).astimezone()
        q = {"timeMin": t0.isoformat(), "timeMax": (t0 + _dt.timedelta(days=days)).isoformat(),
             "singleEvents": "true", "orderBy": "startTime", "maxResults": 100}
        out = []
        for e in g.get_json(g.CALENDAR_API + "/calendars/primary/events", q).get("items") or []:
            if e.get("status") == "cancelled":
                continue
            s = e.get("start") or {}
            try:
                if s.get("dateTime"):
                    start = _dt.datetime.fromisoformat(s["dateTime"]).astimezone().replace(tzinfo=None)
                else:
                    start = _dt.datetime.strptime(s["date"], "%Y-%m-%d")
            except (KeyError, ValueError):
                continue
            out.append({"start": start.isoformat(timespec="minutes"), "title": e.get("summary") or "(no title)"})
        return sorted(out, key=lambda e: e["start"])
    return _cached(("gcal", days, today()), fetch)
