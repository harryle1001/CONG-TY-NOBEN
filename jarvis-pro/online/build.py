"""Build the online JARVIS page (claude.ai Artifact) from the shared UI code + an index of a source folder.

  python3 online/build.py /path/to/source [out.html]

Embeds: ui/styles.css, ui/graph.js, and the knowledge index (titles, links, text excerpts) of the source folder.
Only point it at folders you are happy to have inside the published page.
"""
import json, os, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
src = sys.argv[1] if len(sys.argv) > 1 else str(ROOT.parent)
out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "jarvis-online.html"
os.environ["JARVIS_DEMO"] = "0"; os.environ["JARVIS_SOURCES"] = src
sys.path.insert(0, str(ROOT / "agent"))
import vault

v = vault.Vault()
skip = lambda i: "/jarvis/" in i or "/jarvis-pro/" in i
keep = {n["id"] for n in v.nodes if not skip(n["id"])}
kb = {"nodes": [{k: n[k] for k in ("id", "title", "type", "degree")} for n in v.nodes if n["id"] in keep],
      "edges": sorted([a, b] for a, b in v.edges if a in keep and b in keep),
      "text": {i: re.sub(r"\s+", " ", v.text[i])[:2400] for i in sorted(v.text) if i in keep}}
kb_json = json.dumps(kb, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
page = (HERE / "template.html").read_text("utf-8")
page = page.replace("/*STYLES*/", (ROOT / "ui" / "styles.css").read_text("utf-8"))
page = page.replace("/*GRAPH*/", (ROOT / "ui" / "graph.js").read_text("utf-8").replace("</script", "<\\/script"))
page = page.replace("/*KB*/", kb_json)
out.write_text(page, "utf-8")
print(f"{out}  {len(page.encode()) // 1024} KB  {len(kb['nodes'])} nodes  {len(kb['edges'])} links")
