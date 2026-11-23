"""Gom mỗi sản phẩm Noben thành 1 nút chuẩn trong graphify-out/graph.json.
Nguồn danh mục: ho-so-san-pham/data.json (ma, ten, TCCS).
- Nút "khái niệm sản phẩm" trùng tên (catalogue, bảng giá, profile...) -> nhập vào nút chuẩn.
- Nút tài liệu/ảnh/hồ sơ lô/lệnh SX nhắc tới sản phẩm -> nối cạnh tới nút chuẩn.
Được gọi từ tools/graphify-merge.py."""
import json, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOISE = r"\b(sản phẩm|san pham|product( profile| concept| label( image)?| variant.*)?|catalogue|label \d+|" \
        r"powder|liquid|batch record.*|mã tiếp nhận.*|hình ảnh bao bì|nhãn)\b"


def norm(s):
    s = unicodedata.normalize("NFC", s or "").lower()
    s = re.sub(r"\(.*?\)", " ", s)
    return re.sub(r"\s+", " ", re.sub(r"[^\w%\. ]", " ", s)).strip()


def core(label):
    return re.sub(r"\s+", " ", re.sub(NOISE, " ", norm(label))).strip()


def apply(g):
    data = json.loads((ROOT / "ho-so-san-pham" / "data.json").read_text(encoding="utf-8"))
    prods = []
    for p in data:
        ten, ma = (p.get("ten") or "").strip(), (p.get("ma") or "").strip()
        if not ten or not ma:
            continue
        tccs = (p.get("f1") or {}).get("Số tiêu chuẩn công bố áp dụng (TCCS AA:YYYY/XX)", "")
        prods.append({"ma": ma, "ten": ten, "tccs": tccs, "n": norm(ten),
                      "id": "noben_sp_" + ma.replace("-", "_")})
    prods.sort(key=lambda p: -len(p["n"]))  # tên dài khớp trước (C MAX 25% trước C MAX)

    nodes = {n["id"]: n for n in g["nodes"]}
    remap, links_new, merged, linked = {}, [], 0, 0
    for p in prods:
        label = f"{p['ten']} (MS {p['ma']})"
        nodes.setdefault(p["id"], {"id": p["id"], "file_type": "concept",
                                   "source_file": "ho-so-san-pham/data.json", "source_location": None})
        nodes[p["id"]].update(label=label, ma_so=p["ma"], tccs=p["tccs"] or None)

    pat = [(p, re.compile(r"(?<![\w])" + re.escape(p["n"]) + r"(?![\w%])")) for p in prods]
    code_pat = [(p, re.compile(re.escape(p["ma"]))) for p in prods]
    for nid, n in list(nodes.items()):
        if nid.startswith("noben_sp_"):
            continue
        lab = n.get("label", "")
        hit = next((p for p, rx in code_pat if rx.search(lab)), None) \
            or next((p for p, rx in pat if rx.search(norm(lab))), None)
        if not hit:
            continue
        is_file = n.get("file_type") in ("document", "image", "paper", "code") or re.search(r"\.(md|docx?|pdf|jpg|png|webp)\b", lab, re.I)
        if not is_file and core(lab) == hit["n"]:
            remap[nid] = hit["id"]
            src = nodes[hit["id"]].setdefault("source_files", [])
            if n.get("source_file") and n["source_file"] not in src:
                src.append(n["source_file"])
            del nodes[nid]
            merged += 1
        else:
            links_new.append({"source": nid, "target": hit["id"], "relation": "references",
                              "confidence": "INFERRED", "confidence_score": 0.85,
                              "source_file": n.get("source_file"), "weight": 1.0, "_origin": "products"})
            linked += 1
    return nodes, remap, links_new, merged, linked
