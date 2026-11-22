"""Gộp nút trùng trong graphify-out/graph.json theo tools/graphify-aliases.json.
Chạy sau mỗi lần dựng lại đồ thị:  python3 tools/graphify-merge.py
(tự chạy lại cluster-only để cập nhật GRAPH_REPORT.md, graph.html và vault Obsidian)."""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / "graphify-out" / "graph.json"
aliases = json.loads((ROOT / "tools" / "graphify-aliases.json").read_text(encoding="utf-8"))
g = json.loads(GRAPH.read_text(encoding="utf-8"))
nodes = {n["id"]: n for n in g["nodes"]}

remap, merged = {}, 0
for keep, spec in aliases.items():
    if keep.startswith("_"):
        continue
    dups = [d for d in spec.get("gop", []) if d in nodes and d != keep]
    if keep not in nodes:
        if not dups:
            continue
        nodes[keep] = dict(nodes[dups[0]], id=keep)  # nút giữ lại chưa có: lấy nút trùng đầu tiên làm gốc
    k = nodes[keep]
    k["label"] = spec.get("label", k["label"])
    srcs = {k.get("source_file")} | {nodes[d].get("source_file") for d in dups}
    k["source_files"] = sorted(s for s in srcs if s)
    for d in dups:
        remap[d] = keep
        del nodes[d]
        merged += 1

seen, links = set(), []
for e in g["links"]:
    e["source"] = remap.get(e["source"], e["source"])
    e["target"] = remap.get(e["target"], e["target"])
    if e["source"] == e["target"]:
        continue
    key = (e["source"], e["target"], e.get("relation"))
    if key in seen:
        continue
    seen.add(key)
    links.append(e)
for h in g.get("hyperedges", []):
    h["nodes"] = list(dict.fromkeys(remap.get(x, x) for x in h.get("nodes", [])))

g["nodes"], g["links"] = list(nodes.values()), links
GRAPH.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Gộp {merged} nút trùng.")
if merged and "--no-rebuild" not in sys.argv:
    subprocess.run(["graphify", "cluster-only", str(ROOT)], check=False)
    subprocess.run(["graphify", "export", "obsidian", "--dir", str(ROOT / "graphify-out" / "obsidian")], check=False)
