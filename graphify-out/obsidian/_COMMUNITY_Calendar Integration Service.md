---
type: community
cohesion: 0.16
members: 14
---

# Calendar Integration Service

**Cohesion:** 0.16 - loosely connected
**Members:** 14 nodes

## Members
- [[dot-graph()]] - code - jarvis-pro/agent/vault.py
- [[Events from today for `days` days, from an .ics file or Google Calendar. Never…]] - rationale - jarvis-pro/agent/data.py
- [[For the UI badge. Never contains a token or secret.]] - rationale - jarvis-pro/agent/data.py
- [[True only in real mode. Demo mode never touches Google.]] - rationale - jarvis-pro/agent/data.py
- [[_gcal()]] - code - jarvis-pro/agent/data.py
- [[calendar()]] - code - jarvis-pro/agent/data.py
- [[calendar_file()]] - code - jarvis-pro/agent/data.py
- [[fetch()_1]] - code - jarvis-pro/agent/data.py
- [[get()]] - code - jarvis-pro/agent/data.py
- [[google_source()]] - code - jarvis-pro/agent/data.py
- [[google_status()]] - code - jarvis-pro/agent/data.py
- [[load_prompt()]] - code - jarvis-pro/agent/tools.py
- [[mode()]] - code - jarvis-pro/agent/data.py
- [[today()]] - code - jarvis-pro/agent/data.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Calendar_Integration_Service
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Document Extraction Tools]]
- 5 edges to [[_COMMUNITY_Agent Tooling Framework]]
- 3 edges to [[_COMMUNITY_Email Inbox Management]]
- 1 edge to [[_COMMUNITY_Data Parsing Utilities]]
- 1 edge to [[_COMMUNITY_File System Automation]]
- 1 edge to [[_COMMUNITY_LLM Integration Layer]]
- 1 edge to [[_COMMUNITY_HTTP Request Handling]]
- 1 edge to [[_COMMUNITY_Product Profile Generator]]

## Top bridge nodes
- [[today()]] - degree 8, connects to 3 communities
- [[load_prompt()]] - degree 5, connects to 3 communities
- [[calendar()]] - degree 9, connects to 2 communities
- [[_gcal()]] - degree 6, connects to 2 communities
- [[google_source()]] - degree 5, connects to 2 communities