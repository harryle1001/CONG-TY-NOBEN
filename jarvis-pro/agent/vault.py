"""Folders -> searchable graph. Gets files only through data.py."""
import json, math, re, sys, unicodedata
from collections import Counter, defaultdict, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data

WIKI = re.compile(r"\[\[([^\]|#]+)")
MDLINK = re.compile(r"\]\(([^)#?\s]+)")


def norm(s):
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def title_of(rel):
    t = Path(rel).stem
    return re.sub(r"^\s*\d+\s*[-_.]\s*", "", t).strip() or t


def type_of(rel, ext):
    p = norm(str(rel))
    if "tccs" in p or "san-pham" in p or "san pham" in p or "product" in p: return "product"
    if "/ai/" in p or "chuan hoa ai" in p: return "ai"
    if "ky-thuat" in p or "kien-thuc" in p: return "know-how"
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
        docs = list(data.iter_documents())
        for src, rel, text in docs:
            nid = f"{Path(src).name}/{rel.as_posix()}"
            ext = rel.suffix.lower()
            node = {"id": nid, "title": title_of(rel), "type": type_of(nid, ext),
                    "path": nid, "size": len(text)}
            self.nodes.append(node)
            self.text[nid] = text
            by_path[nid] = node
            by_title[norm(node["title"])].append(nid)
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
        titles = [(t, ids) for t, ids in by_title.items() if len(t) >= 5]
        for src, rel, text in docs:
            nid = f"{Path(src).name}/{rel.as_posix()}"
            raw = data.read_raw(src, rel)
            # wikilinks + markdown/html links
            for t in WIKI.findall(raw or text):
                for tid in by_title.get(norm(title_of(t)), []):
                    self._edge(nid, tid)
            for href in MDLINK.findall(raw) + (data.html_links(raw) if raw else []):
                tgt = (Path(nid).parent / href).as_posix()
                tgt = re.sub(r"[^/]+/\.\./", "", tgt).replace("./", "")
                if tgt in by_path:
                    self._edge(nid, tgt)
            # mentions of another document's title (product names etc.)
            low = norm(text)
            for t, ids in titles:
                if t in low:
                    for tid in ids:
                        self._edge(nid, tid)
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

    # ---- search: tiny BM25 over normalized words ----
    def search(self, q, k=5):
        terms = [w for w in re.findall(r"\w{2,}", norm(q))]
        if not terms: return []
        N = len(self.text) or 1
        df = Counter(w for t in self.text.values() for w in set(re.findall(r"\w{2,}", norm(t))) & set(terms))
        out = []
        for nid, t in self.text.items():
            words = re.findall(r"\w{2,}", norm(t)); L = len(words) or 1
            tf = Counter(w for w in words if w in df)
            s = sum(math.log(1 + N / df[w]) * tf[w] * 2.2 / (tf[w] + 1.2 * (0.25 + 0.75 * L / 400)) for w in tf)
            s += 3 * sum(w in norm(self.by_id[nid]["title"]) for w in terms)
            if s > 0: out.append((s, nid))
        out.sort(reverse=True)
        return [{"id": n, "title": self.by_id[n]["title"], "score": round(s, 2),
                 "snippet": self.snippet(n, terms)} for s, n in out[:k]]

    def snippet(self, nid, terms, width=220):
        t = self.text[nid]; low = norm(t)
        i = min([low.find(w) for w in terms if low.find(w) >= 0] or [0])
        return t[max(0, i - 60): i - 60 + width].strip()

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
        return {"nodes": self.nodes, "edges": [list(e) for e in self.edges], "mode": data.mode()}

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
