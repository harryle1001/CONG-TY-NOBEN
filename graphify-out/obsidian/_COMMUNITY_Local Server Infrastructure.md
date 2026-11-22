---
type: community
cohesion: 0.15
members: 15
---

# Local Server Infrastructure

**Cohesion:** 0.15 - loosely connected
**Members:** 15 nodes

## Members
- [[dot-env next to agent KEY=value lines. Never sent to the browser. Real env vars…]] - rationale - jarvis-pro/agent/main.py
- [[Fake Google (OAuth + Gmail + Calendar) on localhost, for testing without a real…]] - rationale - jarvis-pro/tests/fake_google.py
- [[JARVIS HTTP server. Stdlib only. Step 4 graph UI + tools + conversation +…]] - rationale - jarvis-pro/agent/main.py
- [[b64()]] - code - jarvis-pro/tests/fake_google.py
- [[events()]] - code - jarvis-pro/tests/fake_google.py
- [[fake_google.py]] - code - jarvis-pro/tests/fake_google.py
- [[hashlib]] - concept
- [[http_server]] - concept
- [[load_env()]] - code - jarvis-pro/agent/main.py
- [[main.py]] - code - jarvis-pro/agent/main.py
- [[mimetypes]] - concept
- [[secrets]] - concept
- [[threading]] - concept
- [[time]] - concept
- [[urllib_parse]] - concept

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Local_Server_Infrastructure
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Google OAuth Integration]]
- 5 edges to [[_COMMUNITY_File System Automation]]
- 3 edges to [[_COMMUNITY_Voice Processing Module]]
- 2 edges to [[_COMMUNITY_API Request Handler]]
- 2 edges to [[_COMMUNITY_LLM Integration Layer]]
- 2 edges to [[_COMMUNITY_Data Parsing Utilities]]
- 2 edges to [[_COMMUNITY_Product Profile Generator]]
- 2 edges to [[_COMMUNITY_Document Processing Utilities]]
- 2 edges to [[_COMMUNITY_Document Extraction Tools]]
- 1 edge to [[_COMMUNITY_HTTP Request Handling]]

## Top bridge nodes
- [[main.py]] - degree 20, connects to 8 communities
- [[fake_google.py]] - degree 13, connects to 5 communities
- [[time]] - degree 4, connects to 2 communities
- [[urllib_parse]] - degree 4, connects to 2 communities
- [[hashlib]] - degree 2, connects to 1 community