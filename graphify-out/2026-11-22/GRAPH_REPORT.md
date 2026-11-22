# Graph Report - CONG-TY-NOBEN  (2026-11-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 398 nodes · 803 edges · 21 communities (15 shown, 6 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cf941bef`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19

## God Nodes (most connected - your core abstractions)
1. `Graph` - 21 edges
2. `norm()` - 13 edges
3. `Tools` - 12 edges
4. `_xls()` - 10 edges
5. `Vault` - 9 edges
6. `H` - 9 edges
7. `calendar()` - 9 edges
8. `inbox()` - 9 edges
9. `_card()` - 8 edges
10. `today()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `_save()` --indirect_call--> `f()`  [INFERRED]
  jarvis-pro/agent/google_auth.py → ho-so-lo/_build/sua_hsl_2109.py
- `load_prompt()` --calls--> `mode()`  [EXTRACTED]
  jarvis-pro/agent/tools.py → jarvis-pro/agent/data.py
- `write()` --calls--> `today()`  [EXTRACTED]
  jarvis-pro/agent/memory.py → jarvis-pro/agent/data.py
- `load_prompt()` --calls--> `today()`  [EXTRACTED]
  jarvis-pro/agent/tools.py → jarvis-pro/agent/data.py
- `injected()` --calls--> `norm()`  [EXTRACTED]
  jarvis-pro/agent/tools.py → jarvis-pro/agent/vault.py

## Import Cycles
- None detected.

## Communities (21 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (11): html_links(), mode(), read_raw(), _card(), injected(), _short(), Tools, norm() (+3 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (15): compact_docx(), compact_xlsx(), empty_row(), txt(), copy_rels(), doi_style(), nhap_style(), bo_ma() (+7 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (19): doi_gio(), f(), access_token(), callback(), _client(), configured(), _fail(), get_json() (+11 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (22): _anthropic(), chat(), _chat_anthropic(), _chat_gemini(), _dedupe(), _gemini(), model_name(), ModelError (+14 more)

### Community 4 - "Community 4"
Cohesion: 0.15
Nodes (15): _slug(), write(), build_bang_gia(), build_excel(), build_noben(), build_tim(), catalogue_items(), img64() (+7 more)

### Community 5 - "Community 5"
Cohesion: 0.19
Nodes (3): colorOf(), Graph, TYPE_COLORS

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (12): { chromium }, fs, os, path, procs, ROOT, sleep(), { spawn } (+4 more)

### Community 7 - "Community 7"
Cohesion: 0.19
Nodes (13): bieu_mau(), cells(), dan_mau_luu(), dan_mau_luu_goc(), fill_rows(), full_width(), lenh_sx(), ptext() (+5 more)

### Community 8 - "Community 8"
Cohesion: 0.23
Nodes (17): api(), ask(), boot(), chip(), esc(), EXAMPLES, fail(), inspect() (+9 more)

### Community 9 - "Community 9"
Cohesion: 0.15
Nodes (11): _cfb(), _clean(), _doc(), _docx(), extract(), _local(), _num(), _ole_text() (+3 more)

### Community 11 - "Community 11"
Cohesion: 0.24
Nodes (9): _cached(), calendar(), calendar_file(), _gcal(), fetch(), _gmail_inbox(), fetch(), one() (+1 more)

### Community 12 - "Community 12"
Cohesion: 0.20
Nodes (6): google_source(), google_status(), html_text(), inbox(), inbox_dir(), title_from()

### Community 13 - "Community 13"
Cohesion: 0.42
Nodes (4): fixtures(), links(), main(), w()

### Community 14 - "Community 14"
Cohesion: 0.29
Nodes (6): _f(), _pdf(), cmap(), _pdf_ops(), dec(), _u16hex()

### Community 15 - "Community 15"
Cohesion: 0.50
Nodes (3): _b64text(), _gmail_body(), walk()

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `norm()` connect `Community 0` to `Community 4`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.058001397624039136 - nodes in this community are weakly interconnected._
- **Why does `H` connect `Community 3` to `Community 2`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.08078231292517007 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.07536231884057971 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.08562367864693446 - nodes in this community are weakly interconnected._
- **Should `Community 4` be split into smaller, more focused modules?**
  _Cohesion score 0.1477832512315271 - nodes in this community are weakly interconnected._