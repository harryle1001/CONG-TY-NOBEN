"""Model access over raw HTTPS (stdlib only). Keys come from the environment / .env, never the browser.

JARVIS_LLM=anthropic | gemini | none   (default: whichever key is present, Anthropic first)
ANTHROPIC_API_KEY  -> Claude (claude-opus-5-5, low effort: this is chat, latency matters)
GEMINI_API_KEY     -> Gemini (gemini-2.5-flash)
"""
import json, os, urllib.request, urllib.error

ANTHROPIC_MODEL = os.environ.get("JARVIS_ANTHROPIC_MODEL", "claude-opus-5-5")
GEMINI_MODEL = os.environ.get("JARVIS_GEMINI_MODEL", "gemini-2.5-flash")
TIMEOUT = 90
MAX_TOOL_ROUNDS = 5


def provider():
    p = os.environ.get("JARVIS_LLM", "").lower()
    if p in ("anthropic", "gemini", "none"):
        return None if p == "none" else p
    if os.environ.get("ANTHROPIC_API_KEY"): return "anthropic"
    if os.environ.get("GEMINI_API_KEY"): return "gemini"
    return None


def model_name():
    p = provider()
    return {"anthropic": ANTHROPIC_MODEL, "gemini": GEMINI_MODEL}.get(p)


class ModelError(Exception):
    pass


def _post(url, headers, body):
    req = urllib.request.Request(url, json.dumps(body).encode(), {"content-type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise ModelError(f"HTTP {e.code}: {e.read()[:300].decode('utf-8', 'replace')}")
    except (urllib.error.URLError, TimeoutError) as e:
        raise ModelError(f"unreachable: {e}")


# ---------------- Anthropic ----------------
def _anthropic(body):
    return _post("https://api.anthropic.com/v1/messages", {
        "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "anthropic-version": "2026-10-21",
        "anthropic-beta": "server-side-fallback-2026-07-01",
    }, {"model": ANTHROPIC_MODEL, "max_tokens": 16000, "fallbacks": "default",
        "output_config": {"effort": "low"}, **body})


def _chat_anthropic(system, history, specs, run_tool):
    tools = [{"name": s["name"], "description": s["description"], "input_schema": s["params"]} for s in specs]
    msgs = [{"role": h["role"], "content": h["text"]} for h in history]
    for _ in range(MAX_TOOL_ROUNDS + 1):
        r = _anthropic({"system": system, "tools": tools, "messages": msgs})
        if r.get("stop_reason") == "refusal":
            return "I can't help with that one, sir."
        msgs.append({"role": "assistant", "content": r["content"]})   # unchanged, thinking blocks included
        if r.get("stop_reason") == "pause_turn":
            continue
        calls = [b for b in r["content"] if b.get("type") == "tool_use"]
        if not calls:
            return "".join(b.get("text", "") for b in r["content"] if b.get("type") == "text").strip()
        results = []
        for c in calls:
            out, err = run_tool(c["name"], c.get("input") or {})
            results.append({"type": "tool_result", "tool_use_id": c["id"], "content": json.dumps(out, ensure_ascii=False),
                            **({"is_error": True} if err else {})})
        msgs.append({"role": "user", "content": results})
    return "That took more steps than I allow myself, sir. Ask me again more narrowly."


def _web_anthropic(query):
    msgs = [{"role": "user", "content": f"Search the web and answer briefly with figures and dates: {query}"}]
    for _ in range(3):
        r = _anthropic({"tools": [{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}], "messages": msgs})
        if r.get("stop_reason") != "pause_turn":
            break
        msgs.append({"role": "assistant", "content": r["content"]})
    text, sources = "", []
    for b in r.get("content", []):
        if b.get("type") == "text":
            text += b.get("text", "")
            for c in b.get("citations") or []:
                if c.get("url"): sources.append({"title": c.get("title") or c["url"], "url": c["url"]})
        if b.get("type") == "web_search_tool_result" and isinstance(b.get("content"), list):
            sources += [{"title": x.get("title", ""), "url": x.get("url", "")} for x in b["content"][:5]]
    return text.strip(), _dedupe(sources)


# ---------------- Gemini ----------------
def _gemini(body):
    base = "https://generativelanguage.googleapis.com/v1beta/models"
    return _post(f"{base}/{GEMINI_MODEL}:generateContent", {"x-goog-api-key": os.environ.get("GEMINI_API_KEY", "")}, body)


def _chat_gemini(system, history, specs, run_tool):
    decls = [{"name": s["name"], "description": s["description"], "parameters": s["params"]} for s in specs]
    contents = [{"role": "model" if h["role"] == "assistant" else "user", "parts": [{"text": h["text"]}]} for h in history]
    for _ in range(MAX_TOOL_ROUNDS + 1):
        r = _gemini({"systemInstruction": {"parts": [{"text": system}]}, "contents": contents,
                     "tools": [{"functionDeclarations": decls}]})
        cand = (r.get("candidates") or [{}])[0]
        content = cand.get("content") or {"role": "model", "parts": []}
        contents.append(content)                              # unchanged: keeps thought signatures
        calls = [p["functionCall"] for p in content.get("parts", []) if "functionCall" in p]
        if not calls:
            text = "".join(p.get("text", "") for p in content.get("parts", []) if not p.get("thought")).strip()
            if not text and cand.get("finishReason") not in (None, "STOP"):
                return f"The model stopped early ({cand.get('finishReason')}), sir."
            return text
        parts = []
        for c in calls:
            out, err = run_tool(c["name"], c.get("args") or {})
            parts.append({"functionResponse": {"name": c["name"], "response": {"error": out} if err else out}})
        contents.append({"role": "user", "parts": parts})
    return "That took more steps than I allow myself, sir. Ask me again more narrowly."


def _web_gemini(query):
    r = _gemini({"contents": [{"role": "user", "parts": [{"text": f"Answer briefly with figures and dates: {query}"}]}],
                 "tools": [{"google_search": {}}]})
    cand = (r.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts", []))
    chunks = (cand.get("groundingMetadata") or {}).get("groundingChunks") or []
    sources = [{"title": c["web"].get("title", ""), "url": c["web"].get("uri", "")} for c in chunks if "web" in c]
    return text.strip(), _dedupe(sources)


def _dedupe(src):
    seen, out = set(), []
    for s in src:
        if s["url"] and s["url"] not in seen:
            seen.add(s["url"]); out.append(s)
    return out[:6]


# ---------------- public ----------------
def chat(system, history, specs, run_tool):
    """history: [{role: user|assistant, text}], last item is the new user turn. Returns the spoken reply."""
    p = provider()
    if not p: raise ModelError("no model configured")
    return (_chat_anthropic if p == "anthropic" else _chat_gemini)(system, history, specs, run_tool)


def web(query):
    p = provider()
    if not p: raise ModelError("no model configured")
    return (_web_anthropic if p == "anthropic" else _web_gemini)(query)
