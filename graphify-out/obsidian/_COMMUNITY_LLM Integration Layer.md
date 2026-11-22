---
type: community
cohesion: 0.17
members: 21
---

# LLM Integration Layer

**Cohesion:** 0.17 - loosely connected
**Members:** 21 nodes

## Members
- [[Exception]] - code
- [[Model access over raw HTTPS (stdlib only). Keys come from the environment …]] - rationale - jarvis-pro/agent/llm.py
- [[ModelError]] - code - jarvis-pro/agent/llm.py
- [[_anthropic()]] - code - jarvis-pro/agent/llm.py
- [[_chat_anthropic()]] - code - jarvis-pro/agent/llm.py
- [[_chat_gemini()]] - code - jarvis-pro/agent/llm.py
- [[_dedupe()]] - code - jarvis-pro/agent/llm.py
- [[_gemini()]] - code - jarvis-pro/agent/llm.py
- [[_post()]] - code - jarvis-pro/agent/llm.py
- [[_web_anthropic()]] - code - jarvis-pro/agent/llm.py
- [[_web_gemini()]] - code - jarvis-pro/agent/llm.py
- [[ask()]] - code - jarvis-pro/agent/main.py
- [[chat()]] - code - jarvis-pro/agent/llm.py
- [[history {role userassistant, text}, last item is the new user turn.…]] - rationale - jarvis-pro/agent/llm.py
- [[llm.py]] - code - jarvis-pro/agent/llm.py
- [[model_name()]] - code - jarvis-pro/agent/llm.py
- [[provider()]] - code - jarvis-pro/agent/llm.py
- [[run_tool()]] - code - jarvis-pro/agent/main.py
- [[urllib_error]] - concept
- [[urllib_request]] - concept
- [[web()]] - code - jarvis-pro/agent/llm.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/LLM_Integration_Layer
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Voice Processing Module]]
- 2 edges to [[_COMMUNITY_HTTP Request Handling]]
- 2 edges to [[_COMMUNITY_Local Server Infrastructure]]
- 2 edges to [[_COMMUNITY_Google OAuth Integration]]
- 1 edge to [[_COMMUNITY_Agent Tooling Framework]]
- 1 edge to [[_COMMUNITY_Calendar Integration Service]]
- 1 edge to [[_COMMUNITY_File System Automation]]
- 1 edge to [[_COMMUNITY_Product Profile Generator]]

## Top bridge nodes
- [[llm.py]] - degree 20, connects to 4 communities
- [[ask()]] - degree 6, connects to 3 communities
- [[urllib_error]] - degree 3, connects to 2 communities
- [[urllib_request]] - degree 3, connects to 2 communities
- [[_post()]] - degree 5, connects to 1 community