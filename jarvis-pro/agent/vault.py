"""Folders -> searchable graph. Gets files only through data.py."""
import json, math, re, sys, unicodedata
from collections import Counter, defaultdict, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data

WIKI = re.compile(r"\[\[([^\]|#]+)")
MDLINK = re.compile(r"\]\(([^)#?\s]+)")
TOKEN = re.compile(r"\w{2,}")
WORD = re.compile(r"\w+")
# Vietnamese (accent-stripped) + English function words: they say nothing about which file is meant
STOP = set("""
bao nhieu la cua va cac mot nhung nhu nao gi tai voi duoc trong thi ma hay nay toi anh em minh chung ta oi
vay roi nua cung rat neu cai kia sao
the is are was of and or to in on at for by with from how much many what which who when where why
does did can could would should please me my you your it its this that these those be been have has
tell show find give get about any some
""".split())
GENERIC = set("""
index readme claude license changelog robots sitemap home about contact footer header main app style styles
script test demo sample template page pages note notes todo untitled new copy document ban sao
""".split())


MARKS = re.compile(r"[\u0300-\u036f]")


def norm(s):
    """lowercase, no accents, đ -> d: 'Đại lý' -> 'dai ly'."""
    return MARKS.sub("", unicodedata.normalize("NFD", s.lower().replace("đ", "d")))


NUM_PREFIX = re.compile(r"^\s*(?:\d{1,2}\.\d{1,2}|\d{1,3})(?:\s*[-_.)]\s*|\s+)(?=\S)")


def title_of(rel):
    """Clean title from a file name: drop '05.11 ' / '10-' numbering, turn slugs into words."""
    t = Path(rel).stem
    t = NUM_PREFIX.sub("", t, count=1).strip() or t
    if " " not in t and re.search(r"[-_]", t):
        t = re.sub(r"[-_]+", " ", t).strip()
        if t.islower(): t = t[:1].upper() + t[1:]
    else:
        t = re.sub(r"_+", " ", t)
    return re.sub(r"\s+", " ", t).strip() or Path(rel).stem


def title_from(raw, ext):
    """Title written inside the file: markdown front-matter / first H1, HTML <title> / <h1>."""
    if not raw:
        return ""
    t = ""
    if ext in (".md", ".markdown"):
        m = re.match(r"﻿?---\s*\n(.*?)\n---", raw, re.S)
        if m:
            fm = re.search(r"(?m)^title:\s*[\"']?(.+?)[\"']?\s*$", m.group(1))
            t = fm.group(1) if fm else ""
        if not t:
            h = re.search(r"(?m)^#\s+(.+?)\s*#*\s*$", raw)
            t = h.group(1) if h else ""
        t = re.sub(r"[*_`]|\[([^\]]*)\]\([^)]*\)", r"\1", t)
    elif ext in (".html", ".htm"):
        m = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw) or re.search(r"(?is)<h1[^>]*>(.*?)</h1>", raw)
        if m:
            t = data.html_text(m.group(1)).replace("\n", " ")
            t = re.split(r"\s+\|\s+", t)[0]          # "Bảng giá | Dream Labs" -> "Bảng giá"
    t = re.sub(r"\s+", " ", t).strip()
    if "{{" in t or "<%" in t or len(t) < 3:
        return ""
    return t[:89].rstrip() + "…" if len(t) > 90 else t


def type_of(rel, ext):
    p = norm(str(rel))
    if "tccs" in p or "san-pham" in p or "san pham" in p or "product" in p: return "product"
    if "/ai/" in p or "chuan hoa ai" in p: return "ai"
    if "ky-thuat" in p or "kien-thuc" in p or "/knowledge/" in p: return "know-how"
    if "bao gia" in p or "price" in p or "pricing" in p: return "pricing"
    if "bao cao" in p or "report" in p: return "report"
    if "client" in p or "khach" in p: return "client"
    if "game" in p or "rubik" in p or "school" in p: return "game"
    if ext in (".xlsx", ".xls", ".csv"): return "sheet"
    if ext in (".html", ".htm"): return "web"
    if ext == ".pdf": return "pdf"
    return "note"


class Vault:
    def __init__(self):
        self.nodes, self.edges, self.text = [], set(), {}
        self.build()

    def build(self):
        by_path, by_title = {}, defaultdict(list)
        docs, raws, keys = [], {}, {}
        for src, rel, text in data.iter_documents():
            nid = f"{Path(src).name}/{rel.as_posix()}"
            ext = rel.suffix.lower()
            raw = data.read_raw(src, rel)
            base = title_from(raw, ext) or title_of(rel)
            keys[nid] = norm(title_of(rel))             # file-name key: what other files call it ("AQUA BIOTIC")
            node = {"id": nid, "title": base, "type": type_of(nid, ext), "path": nid, "size": len(text)}
            docs.append((nid, text)); raws[nid] = raw
            self.nodes.append(node)
            self.text[nid] = text
            by_path[nid] = node
            by_title[norm(base)].append(nid)
        # same title in several places ("index", "README"): add the parent folder(s) until unique,
        # or the file name when they share a folder ("Ghi chú 2026-11-24 · ghi-chu-20")
        for ids in list(by_title.values()):
            if len(ids) < 2: continue
            labels = None
            for depth in (1, 2, 3):
                cand_ = {i: " / ".join(i.split("/")[-1 - depth:-1]) for i in ids}
                if len(set(cand_.values())) == len(ids): labels = cand_; break
            if labels is None:
                labels = {i: re.sub(r"^\d{4}-\d{2}-\d{2}[-_ ]*", "", Path(i).stem) or Path(i).stem for i in ids}
            for i in ids:
                by_path[i]["title"] = f"{by_path[i]['title']} · {labels[i]}"
        # folder hubs: file -> its folder -> parent folder ... -> source root
        folders = set()
        for n in list(self.nodes):
            parts = n["id"].split("/")
            child = n["id"]
            for i in range(len(parts) - 1, 0, -1):
                fid = "/".join(parts[:i]) + "/"
                if fid not in folders:
                    folders.add(fid)
                    self.nodes.append({"id": fid, "title": parts[i - 1], "type": "folder", "path": fid, "size": 0})
                self.edges.add(tuple(sorted((child, fid))))
                child = fid
        # search index (built once, reused by every query)
        normed = {nid: norm(t) for nid, t in docs}
        self.tok = {nid: TOKEN.findall(normed[nid]) for nid, _ in docs}
        self.tf = {nid: Counter(w) for nid, w in self.tok.items()}
        self.df = Counter(w for c in self.tf.values() for w in c)
        self.avgdl = sum(len(w) for w in self.tok.values()) / max(1, len(self.tok))
        self.joined = {nid: " ".join(w) for nid, w in self.tok.items()}
        self.ttok = {nid: set(TOKEN.findall(norm(by_path[nid]["title"]))) for nid, _ in docs}
        self.ntitle = {nid: norm(by_path[nid]["title"]) for nid, _ in docs}
        # mention edges: only distinctive names. Generic or very common names make noise, not knowledge.
        mention = defaultdict(list)
        for nid in by_path:
            for k in {keys[nid], norm(by_path[nid]["title"].split(" · ")[0])}:
                mention[k].append(nid)
        cand = {}
        for k, ids in mention.items():
            words = WORD.findall(k)
            ids = sorted(set(ids))
            if len(ids) > 2 or not words or len(k) < 5 or k in GENERIC: continue
            if len(words) == 1 and (len(k) < 6 or k in STOP or k.isdigit()): continue
            if all(w in STOP or w.isdigit() or len(w) < 2 for w in words): continue
            cand[tuple(words)] = ids
        # one pass per document over its word n-grams (fast, and respects word boundaries)
        sizes = defaultdict(set)
        for g in cand: sizes[g[0]].add(len(g))
        hits = defaultdict(list)
        for nid, _ in docs:
            w = WORD.findall(normed[nid]); seen = set()
            for i, x in enumerate(w):
                for n in sizes.get(x, ()):
                    g = tuple(w[i:i + n])
                    if g in cand and g not in seen:
                        seen.add(g); hits[g].append(nid)
        cap = max(12, len(docs) // 20)                    # named in >5% of files: a common word, not a name
        self.mention_edges = 0
        for g, srcs in hits.items():
            if len(srcs) > cap: continue
            for nid in srcs:
                for tid in cand[g]:
                    if nid != tid and tuple(sorted((nid, tid))) not in self.edges:
                        self._edge(nid, tid); self.mention_edges += 1
        for nid, text in docs:
            raw = raws[nid]
            # wikilinks + markdown/html links
            for t in WIKI.findall(raw or text):
                for tid in by_title.get(norm(title_of(t)), []) + mention.get(norm(title_of(t)), []):
                    self._edge(nid, tid)
            for href in MDLINK.findall(raw) + (data.html_links(raw) if raw else []):
                tgt = (Path(nid).parent / href).as_posix()
                tgt = re.sub(r"[^/]+/\.\./", "", tgt).replace("./", "")
                if tgt in by_path:
                    self._edge(nid, tgt)
        deg = Counter()
        for a, b in self.edges:
            deg[a] += 1; deg[b] += 1
        for n in self.nodes:
            n["degree"] = deg[n["id"]]
        self.by_id = {n["id"]: n for n in self.nodes}
        self.adj = defaultdict(set)
        for a, b in self.edges:
            self.adj[a].add(b); self.adj[b].add(a)

    def _edge(self, a, b):
        if a != b:
            self.edges.add(tuple(sorted((a, b))))

    # ---- search: BM25 over normalized words + phrase and title boosts ----
    def search(self, q, k=5):
        allq = TOKEN.findall(norm(q))
        terms = [w for w in dict.fromkeys(allq) if w not in STOP and w in self.df] or \
                [w for w in dict.fromkeys(allq) if w in self.df]
        if not terms: return []
        N = len(self.tf) or 1
        idf = {w: math.log(1 + (N - self.df[w] + 0.5) / (self.df[w] + 0.5)) for w in terms}
        # phrases: adjacent query words (stopwords split phrases), e.g. "aqua probio", "tao day"
        content = [w if w not in STOP else None for w in allq]
        phrases = []
        for n in (3, 2):
            for i in range(len(content) - n + 1):
                g = content[i:i + n]
                if all(g) and all(w in self.df for w in g): phrases.append(" ".join(g))
        qn = " ".join(allq)
        out = []
        for nid, tf in self.tf.items():
            L = len(self.tok[nid]) or 1
            s = sum(idf[w] * tf[w] * 2.2 / (tf[w] + 1.2 * (0.25 + 0.75 * L / self.avgdl)) for w in terms if w in tf)
            if s <= 0: continue
            low = self.joined[nid]
            for ph in phrases:
                c = low.count(ph)
                if c: s += sum(idf[w] for w in ph.split()) * min(c, 3) * 0.6
            tt = self.ttok[nid]
            covered = [w for w in terms if w in tt]
            s += 1.618 * sum(idf[w] for w in covered)
            t = self.ntitle[nid].split(" · ")[0]
            if len(t) >= 4 and re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", qn):
                s += 2.618 * sum(idf.get(w, 1) for w in TOKEN.findall(t))   # the question names this file
            out.append((s, nid))
        out.sort(reverse=True)
        return [{"id": n, "title": self.by_id[n]["title"], "score": round(s, 2),
                 "snippet": self.snippet(n, terms, phrases)} for s, n in out[:k]]

    def snippet(self, nid, terms, phrases=(), width=220):
        t = self.text[nid]; low = norm(t)
        idx = [low.find(p) for p in phrases if low.find(p) >= 0]
        if not idx:   # rarest term first: it is the one that says why this file matched
            for w in sorted(terms, key=lambda w: self.df.get(w, 0)):
                m = re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", low)
                if m: idx = [m.start()]; break
        i = idx[0] if idx else 0
        a = max(0, i - 60)
        return re.sub(r"\s+", " ", t[a:a + width]).strip()

    def path(self, a, b):
        prev, dq = {a: None}, deque([a])
        while dq:
            x = dq.popleft()
            if x == b: break
            for y in self.adj[x]:
                if y not in prev: prev[y] = x; dq.append(y)
        if b not in prev: return []
        out = [b]
        while prev[out[-1]]: out.append(prev[out[-1]])
        return out[::-1]

    def graph(self):
        return {"nodes": self.nodes, "edges": [list(e) for e in sorted(self.edges)], "mode": data.mode()}

    def note(self, nid):
        n = self.by_id.get(nid)
        if not n: return None
        return {**n, "text": self.text.get(nid, "")[:6000],
                "links": sorted(self.adj[nid], key=lambda x: -self.by_id[x]["degree"])[:30]}


if __name__ == "__main__":
    v = Vault()
    print(f"mode: {data.mode()}  sources: {[str(s) for s in data.sources()]}")
    print(f"nodes: {len(v.nodes)}  edges: {len(v.edges)}")
    for t, c in Counter(n["type"] for n in v.nodes).most_common():
        print(f"  {t:<8} {c}")
    print("top 10 hubs:")
    for n in sorted(v.nodes, key=lambda n: -n["degree"])[:10]:
        print(f"  {n['degree']:>4}  [{n['type']}] {n['id']}")
