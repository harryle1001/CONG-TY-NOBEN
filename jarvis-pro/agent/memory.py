"""Writes to memory/ and nowhere else. One dated markdown file per fact."""
import re, unicodedata
from datetime import datetime
from pathlib import Path

MEM = Path(__file__).resolve().parent.parent / "memory"


def _slug(s):
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:48] or "fact"


def remember(fact):
    fact = " ".join(fact.split())
    if not fact:
        raise ValueError("empty fact")
    MEM.mkdir(exist_ok=True)
    stamp = datetime.now()
    p = MEM / f"{stamp:%Y-%m-%d}-{_slug(fact)}.md"
    n = 2
    while p.exists():
        p = MEM / f"{stamp:%Y-%m-%d}-{_slug(fact)}-{n}.md"; n += 1
    assert MEM.resolve() in p.resolve().parents  # never outside memory/
    p.write_text(f"---\ndate: {stamp:%Y-%m-%d %H:%M}\n---\n{fact}\n", "utf-8")
    return p.name


def all_facts():
    if not MEM.exists():
        return []
    out = []
    for p in sorted(MEM.glob("*.md")):
        body = p.read_text("utf-8").split("---", 2)[-1].strip()
        out.append({"file": p.name, "fact": body})
    return out
