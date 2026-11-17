"""Writes to memory/ and nowhere else. One dated markdown file per fact."""
import re, unicodedata
from pathlib import Path

import data

DIR = Path(__file__).resolve().parent.parent / "memory"


def _slug(s):
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:48] or "fact"


def write(fact):
    fact = " ".join(str(fact).split())[:600]
    if not fact:
        raise ValueError("empty fact")
    DIR.mkdir(exist_ok=True)
    day = data.today().isoformat()
    p = DIR / f"{day}-{_slug(fact)}.md"
    i = 2
    while p.exists():
        p = DIR / f"{day}-{_slug(fact)}-{i}.md"; i += 1
    p.write_text(f"# {day}\n\n{fact}\n", "utf-8")
    return p.relative_to(DIR.parent).as_posix()


def all_facts():
    if not DIR.is_dir():
        return []
    out = []
    for p in sorted(DIR.glob("*.md"), reverse=True):
        body = p.read_text("utf-8", "replace").split("\n", 2)[-1].strip()
        out.append({"file": p.relative_to(DIR.parent).as_posix(), "fact": body})
    return out
