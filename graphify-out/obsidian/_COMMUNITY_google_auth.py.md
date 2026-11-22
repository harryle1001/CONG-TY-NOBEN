---
type: community
cohesion: 0.05
members: 77
---

# google_auth.py

**Cohesion:** 0.05 - loosely connected
**Members:** 77 nodes

## Members
- [[dot-_google()]] - code - jarvis-pro/agent/main.py
- [[dot-_page()]] - code - jarvis-pro/agent/main.py
- [[dot-_redirect()]] - code - jarvis-pro/agent/main.py
- [[dot-_send()]] - code - jarvis-pro/agent/main.py
- [[dot-do_GET()]] - code - jarvis-pro/agent/main.py
- [[dot-do_POST()]] - code - jarvis-pro/agent/main.py
- [[dot-env next to agent KEY=value lines. Never sent to the browser. Real env vars…]] - rationale - jarvis-pro/agent/main.py
- [[dot-log_message()]] - code - jarvis-pro/agent/main.py
- [[Audio bytes - transcript (Scribe, language auto-detected Vietnamese or…]] - rationale - jarvis-pro/agent/voice.py
- [[BaseHTTPRequestHandler]] - code
- [[ElevenLabs speech in and out. The key lives here, on the server; the browser…]] - rationale - jarvis-pro/agent/voice.py
- [[Exception]] - code
- [[Exception_1]] - code
- [[Exception_2]] - code
- [[Fake Google (OAuth + Gmail + Calendar) on localhost, for testing without a real…]] - rationale - jarvis-pro/tests/fake_google.py
- [[GET only this module has no way to send, delete or change anything in Gmail or…]] - rationale - jarvis-pro/agent/google_auth.py
- [[Google OAuth for an installed app (loopback redirect, PKCE, state). Stdlib…]] - rationale - jarvis-pro/agent/google_auth.py
- [[GoogleError]] - code - jarvis-pro/agent/google_auth.py
- [[H]] - code - jarvis-pro/agent/main.py
- [[Handle code&state (or error). Exchanges the code and stores the token. Raises…]] - rationale - jarvis-pro/agent/google_auth.py
- [[JARVIS HTTP server. Stdlib only. Step 4 graph UI + tools + conversation +…]] - rationale - jarvis-pro/agent/main.py
- [[Loopback OAuth. Only from this machine; state is one-time, kept server-side AND…]] - rationale - jarvis-pro/agent/main.py
- [[Model access over raw HTTPS (stdlib only). Keys come from the environment …]] - rationale - jarvis-pro/agent/llm.py
- [[ModelError]] - code - jarvis-pro/agent/llm.py
- [[Shown to sir as-is say what broke and what to do.]] - rationale - jarvis-pro/agent/google_auth.py
- [[URL of Google's consent screen. PKCE (S256) + one-time state kept server-side.]] - rationale - jarvis-pro/agent/google_auth.py
- [[VoiceError]] - code - jarvis-pro/agent/voice.py
- [[_anthropic()]] - code - jarvis-pro/agent/llm.py
- [[_chat_anthropic()]] - code - jarvis-pro/agent/llm.py
- [[_chat_gemini()]] - code - jarvis-pro/agent/llm.py
- [[_client()]] - code - jarvis-pro/agent/google_auth.py
- [[_dedupe()]] - code - jarvis-pro/agent/llm.py
- [[_fail()]] - code - jarvis-pro/agent/google_auth.py
- [[_gemini()]] - code - jarvis-pro/agent/llm.py
- [[_load()]] - code - jarvis-pro/agent/google_auth.py
- [[_post()]] - code - jarvis-pro/agent/llm.py
- [[_req()]] - code - jarvis-pro/agent/voice.py
- [[_save()]] - code - jarvis-pro/agent/google_auth.py
- [[_store()]] - code - jarvis-pro/agent/google_auth.py
- [[_token_request()]] - code - jarvis-pro/agent/google_auth.py
- [[_web_anthropic()]] - code - jarvis-pro/agent/llm.py
- [[_web_gemini()]] - code - jarvis-pro/agent/llm.py
- [[access_token()]] - code - jarvis-pro/agent/google_auth.py
- [[ask()]] - code - jarvis-pro/agent/main.py
- [[available()]] - code - jarvis-pro/agent/voice.py
- [[b64()]] - code - jarvis-pro/tests/fake_google.py
- [[callback()]] - code - jarvis-pro/agent/google_auth.py
- [[chat()]] - code - jarvis-pro/agent/llm.py
- [[collections]] - concept
- [[configured()]] - code - jarvis-pro/agent/google_auth.py
- [[fake_google.py]] - code - jarvis-pro/tests/fake_google.py
- [[get_json()]] - code - jarvis-pro/agent/google_auth.py
- [[google_auth.py]] - code - jarvis-pro/agent/google_auth.py
- [[hashlib]] - concept
- [[history {role userassistant, text}, last item is the new user turn.…]] - rationale - jarvis-pro/agent/llm.py
- [[http_server]] - concept
- [[json]] - concept
- [[listen()]] - code - jarvis-pro/agent/voice.py
- [[llm.py]] - code - jarvis-pro/agent/llm.py
- [[load_env()]] - code - jarvis-pro/agent/main.py
- [[main.py]] - code - jarvis-pro/agent/main.py
- [[mimetypes]] - concept
- [[model_name()]] - code - jarvis-pro/agent/llm.py
- [[provider()]] - code - jarvis-pro/agent/llm.py
- [[run_tool()]] - code - jarvis-pro/agent/main.py
- [[secrets]] - concept
- [[speak()]] - code - jarvis-pro/agent/voice.py
- [[start()_1]] - code - jarvis-pro/agent/google_auth.py
- [[status()]] - code - jarvis-pro/agent/google_auth.py
- [[threading]] - concept
- [[time]] - concept
- [[urllib_error]] - concept
- [[urllib_parse]] - concept
- [[urllib_request]] - concept
- [[uuid]] - concept
- [[voice.py]] - code - jarvis-pro/agent/voice.py
- [[web()]] - code - jarvis-pro/agent/llm.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/google_authpy
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_re]]
- 7 edges to [[_COMMUNITY_Document Processing Utilities]]
- 4 edges to [[_COMMUNITY_TAI-LIEU-KINH-DOANHbuild.py]]
- 2 edges to [[_COMMUNITY_API Request Handler]]
- 2 edges to [[_COMMUNITY_Product Profile Generator]]
- 2 edges to [[_COMMUNITY_Document Extraction Tools]]
- 1 edge to [[_COMMUNITY_Agent Tooling Framework]]

## Top bridge nodes
- [[fake_google.py]] - degree 13, connects to 4 communities
- [[google_auth.py]] - degree 26, connects to 3 communities
- [[json]] - degree 13, connects to 3 communities
- [[llm.py]] - degree 20, connects to 2 communities
- [[main.py]] - degree 20, connects to 2 communities