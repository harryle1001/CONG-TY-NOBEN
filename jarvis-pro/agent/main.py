"""JARVIS HTTP server + API. Python stdlib only.  Run:  python3 agent/main.py"""
import json, mimetypes, os, re, sys, urllib.error, urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent


def load_env():
    f = ROOT / ".env"
    if not f.exists():
        return
    if os.name == "posix" and f.stat().st_mode & 0o077:
        print("[jarvis] WARNING: .env is readable by other users. Run: chmod 600 .env")
    for line in f.read_text("utf-8").splitlines():
        m = re.match(r"\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)\s*$", line)
        if m and m.group(1) not in os.environ:
            os.environ[m.group(1)] = m.group(2).strip().strip('"').strip("'")


load_env()  # before data.py reads JARVIS_DEMO
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vault import Vault, norm
import data, memory, voice
from tools import TOOLS, Tools, for_model

UI = ROOT / "ui"
PORT = int(os.environ.get("JARVIS_PORT", "1618"))
MODEL = os.environ.get("JARVIS_MODEL", "claude-opus-5-5")
API = "https://api.anthropic.com/v1/messages"
HISTORY_TURNS = 10

print("[jarvis] indexing…")
VAULT = Vault()
print(f"[jarvis] {len(VAULT.nodes)} nodes, {len(VAULT.edges)} edges, mode={data.mode()}")


# ---------------- Claude (raw HTTP: the project is stdlib-only) ----------------
def claude(body, beta=None):
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError("no ANTHROPIC_API_KEY")
    headers = {"content-type": "application/json", "x-api-key": key, "anthropic-version": "2026-10-21"}
    if beta:
        headers["anthropic-beta"] = beta
    req = urllib.request.Request(API, json.dumps(body).encode(), headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Claude API {e.code}: {e.read()[:300].decode('utf-8', 'replace')}")


def system_prompt():
    tpl = (ROOT / "agent" / "prompt.md").read_text("utf-8")
    who = (ROOT / "CLAUDE.md").read_text("utf-8") if (ROOT / "CLAUDE.md").exists() else "(no CLAUDE.md yet)"
    facts = "\n".join(f"- {f['fact']} ({f['file']})" for f in memory.all_facts()) or "(nothing yet)"
    return tpl.replace("{CLAUDE_MD}", who).replace("{MEMORY}", facts)


def web_research(question):
    """Nested call with Anthropic's web search server tool. Only reached when JARVIS_WEB=1."""
    r = claude({"model": MODEL, "max_tokens": 16000, "output_config": {"effort": "low"},
                "tools": [{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}],
                "messages": [{"role": "user", "content": f"Research briefly and factually, with numbers: {question}"}]})
    text = " ".join(b.get("text", "") for b in r["content"] if b["type"] == "text").strip()
    srcs = []
    for b in r["content"]:
        if b["type"] == "web_search_tool_result" and isinstance(b.get("content"), list):
            srcs += [{"title": x.get("title", ""), "url": x.get("url", "")} for x in b["content"][:5]]
    return text, srcs


TOOLBOX = Tools(VAULT, web_research)
HISTORY = []  # plain text turns only: [{"role","content":str}] — append-only, oldest trimmed from the front


def ask_model(text):
    msgs = HISTORY[-2 * HISTORY_TURNS:] + [{"role": "user", "content": text}]
    sys_blocks = [{"type": "text", "text": system_prompt(), "cache_control": {"type": "ephemeral"}}]
    cards = []
    for _ in range(8):
        r = claude({"model": MODEL, "max_tokens": 16000, "system": sys_blocks, "tools": TOOLS,
                    "output_config": {"effort": "low"}, "fallbacks": "default", "messages": msgs},
                   beta="server-side-fallback-2026-07-01")
        if r.get("stop_reason") == "refusal":
            return {"say": "I can't help with that one, sir.", "cards": cards}
        msgs.append({"role": "assistant", "content": r["content"]})   # unchanged, thinking blocks included
        uses = [b for b in r["content"] if b["type"] == "tool_use"]
        if r.get("stop_reason") != "tool_use" or not uses:
            say = " ".join(b.get("text", "") for b in r["content"] if b["type"] == "text").strip()
            if r.get("stop_reason") == "max_tokens":
                say += " (cut off)"
            for c in cards:  # guardrail: memory writes are always said out loud, verbatim
                if c["kind"] == "memory" and c["text"] not in say:
                    say += f' I wrote to memory/{c["file"]}: "{c["text"]}"'
            return {"say": say or "Done, sir.", "cards": cards}
        results = []
        for u in uses:
            out = TOOLBOX.run(u["name"], u["input"] if isinstance(u["input"], dict) else {})
            cards.append(out["card"])
            results.append({"type": "tool_result", "tool_use_id": u["id"], "content": for_model(out),
                            **({"is_error": True} if out.get("error") else {})})
        msgs.append({"role": "user", "content": results})
    return {"say": "That took too many steps, sir. Ask me more narrowly.", "cards": cards}


# ---------------- no-model routing: never pretend to be the model ----------------
SMALLTALK = re.compile(r"^(hi|hello|hey|yo|xin chao|chao|alo|jarvis|can you hear|nghe khong|thanks|thank you|cam on|"
                       r"how are you|ban khoe|what do you think|why|tai sao|ok|okay)\b")


def route_without_model(text):
    q = norm(text).strip(" ?!.")
    if SMALLTALK.match(q):
        return {"say": "I'm here, sir — but my language model is offline, so I can only search your files for now.", "cards": []}
    if re.search(r"\b(brief|tom tat ngay|lich)\b", q):
        out = TOOLBOX.brief_me(); return {"say": out["say"], "cards": [out["card"]]}
    if re.search(r"\b(inbox|email|mail|thu)\b", q):
        out = TOOLBOX.read_inbox(); return {"say": out["say"], "cards": [out["card"]]}
    out = TOOLBOX.search_brain(text)
    hits = out["card"]["hits"]
    if hits and hits[0]["score"] >= 6:
        return {"say": f"Closest file: {hits[0]['title']}. Keyword match only — the model is offline.", "cards": [out["card"]]}
    return {"say": "Nothing in your files matches that, and my model is offline.", "cards": [out["card"]] if hits else []}


def ask(text):
    text = text.strip()[:4000]
    if not text:
        return {"say": "", "cards": [], "model": bool(os.environ.get("ANTHROPIC_API_KEY"))}
    model_ok, err = bool(os.environ.get("ANTHROPIC_API_KEY")), None
    if model_ok:
        try:
            res = ask_model(text)
        except Exception as e:
            model_ok, err = False, str(e)
            print(f"[jarvis] model error: {e}")
    if not model_ok:
        res = route_without_model(text)
    HISTORY.extend([{"role": "user", "content": text}, {"role": "assistant", "content": res["say"] or "…"}])
    del HISTORY[:-2 * HISTORY_TURNS]
    return {**res, "model": model_ok, "error": err}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        if not isinstance(body, (bytes, bytearray)):
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(min(n, 25 * 1024 * 1024))

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api/speak":
            try:
                text = json.loads(self.body() or b"{}").get("text", "")
                return self.send(200, voice.speak(text), "audio/mpeg")
            except (ValueError, voice.VoiceError) as e:
                return self.send(503, {"error": str(e)})
        if u.path == "/api/listen":
            try:
                return self.send(200, {"text": voice.listen(self.body(), self.headers.get("Content-Type", "audio/webm"))})
            except voice.VoiceError as e:
                return self.send(503, {"error": str(e)})
        if u.path == "/api/ask":
            try:
                text = json.loads(self.body() or b"{}").get("text", "")
            except ValueError:
                return self.send(400, {"error": "bad json"})
            return self.send(200, ask(text))
        self.send(404, {"error": "not found"})

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path == "/api/graph":
            return self.send(200, VAULT.graph())
        if u.path == "/api/note":
            n = VAULT.note(q.get("id", ""))
            return self.send(200 if n else 404, n or {"error": "not found"})
        if u.path == "/api/search":
            return self.send(200, VAULT.search(q.get("q", ""), 8))
        if u.path == "/api/status":
            return self.send(200, {"model": bool(os.environ.get("ANTHROPIC_API_KEY")), "model_id": MODEL, "mode": data.mode(),
                                   "web": os.environ.get("JARVIS_WEB") == "1", "voice": voice.available()})
        if u.path == "/api/memory":
            return self.send(200, memory.all_facts())
        rel = "index.html" if u.path in ("/", "") else u.path.lstrip("/")
        f = (UI / rel).resolve()
        if UI.resolve() not in f.parents or not f.is_file():
            return self.send(404, {"error": "not found"})
        self.send(200, f.read_bytes(), (mimetypes.guess_type(f.name)[0] or "text/plain") + "; charset=utf-8")


if __name__ == "__main__":
    print(f"[jarvis] model: {'ON (' + MODEL + ')' if os.environ.get('ANTHROPIC_API_KEY') else 'MISSING — keyword routing only'}")
    print(f"[jarvis] voice: {'ON (ElevenLabs)' if voice.available() else 'MISSING — set ELEVENLABS_API_KEY'}")
    print(f"[jarvis] http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
