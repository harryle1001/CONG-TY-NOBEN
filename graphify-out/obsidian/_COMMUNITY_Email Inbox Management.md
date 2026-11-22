---
type: community
cohesion: 0.15
members: 14
---

# Email Inbox Management

**Cohesion:** 0.15 - loosely connected
**Members:** 14 nodes

## Members
- [[Maildir-style folder (new = unread, cur = read), a flat folder of .eml, or…]] - rationale - jarvis-pro/agent/data.py
- [[Prefer textplain; fall back to texthtml stripped to text.]] - rationale - jarvis-pro/agent/data.py
- [[Title written inside the file markdown front-matter  first H1, HTML title …]] - rationale - jarvis-pro/agent/vault.py
- [[_b64text()]] - code - jarvis-pro/agent/data.py
- [[_cached()]] - code - jarvis-pro/agent/data.py
- [[_gmail_body()]] - code - jarvis-pro/agent/data.py
- [[_gmail_inbox()]] - code - jarvis-pro/agent/data.py
- [[fetch()]] - code - jarvis-pro/agent/data.py
- [[html_text()]] - code - jarvis-pro/agent/data.py
- [[inbox()]] - code - jarvis-pro/agent/data.py
- [[inbox_dir()]] - code - jarvis-pro/agent/data.py
- [[one()]] - code - jarvis-pro/agent/data.py
- [[title_from()]] - code - jarvis-pro/agent/vault.py
- [[walk()]] - code - jarvis-pro/agent/data.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Email_Inbox_Management
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Document Extraction Tools]]
- 3 edges to [[_COMMUNITY_Agent Tooling Framework]]
- 3 edges to [[_COMMUNITY_Calendar Integration Service]]
- 2 edges to [[_COMMUNITY_Data Parsing Utilities]]
- 1 edge to [[_COMMUNITY_File System Automation]]

## Top bridge nodes
- [[inbox()]] - degree 9, connects to 3 communities
- [[title_from()]] - degree 5, connects to 2 communities
- [[_cached()]] - degree 3, connects to 2 communities
- [[_gmail_body()]] - degree 5, connects to 1 community
- [[html_text()]] - degree 5, connects to 1 community