---
type: community
cohesion: 0.50
members: 4
---

# google_source

**Cohesion:** 0.50 - moderately connected
**Members:** 4 nodes

## Members
- [[For the UI badge. Never contains a token or secret.]] - rationale - jarvis-pro/agent/data.py
- [[True only in real mode. Demo mode never touches Google.]] - rationale - jarvis-pro/agent/data.py
- [[google_source()]] - code - jarvis-pro/agent/data.py
- [[google_status()]] - code - jarvis-pro/agent/data.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/google_source
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Agent Tooling Framework]]
- 2 edges to [[_COMMUNITY_Document Extraction Tools]]

## Top bridge nodes
- [[google_source()]] - degree 5, connects to 2 communities
- [[google_status()]] - degree 3, connects to 1 community