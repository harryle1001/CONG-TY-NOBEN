"""JARVIS HTTP server. Stdlib only. Step 4: graph UI + tools + conversation + ElevenLabs voice.

Run:  python3 agent/main.py        -> http://localhost:8618
"""
import json, mimetypes, os, sys, time, threading
from collections import deque
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent


def load_env():
    """.env next to agent/: KEY=value lines. Never sent to the browser. Real env vars win."""
    f = ROOT / ".env"
    if f.is_file():
        for line in f.read_text("utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env()
sys.path.insert(0, str(Path(__file__).resolve().parent))
import vault, tools, llm, memory, voice
UI = ROOT / "ui"
HOST = os.environ.get("JARVIS_HOST", "127.0.0.1")
PORT = int(os.environ.get("JARVIS_PORT", "8618"))

t0 = time.time()
V = vault.Vault()
print(f"[jarvis] indexed {len(V.nodes)} nodes / {len(V.edges)} edges in {time.time() - t0:.1f}s ({vault.data.mode()})")
T = tools.Tools(V)
print(f"[jarvis] model: {llm.model_name() or 'NONE (keyword routing)'}")
print(f"[jarvis] voice: {'ElevenLabs' if voice.available() else 'OFF (no ELEVENLABS_API_KEY)'}")
HISTORY_TURNS = 10
SESSIONS, PENDING_WEB, LOCK = {}, {}, threading.Lock()
YES = __import__("re").compile(r"^\s*(yes|yeah|yep|ok|okay|sure|go( ahead)?|do it|please do|có|co|ừ|uh|ok luôn|đồng ý|dong y|làm đi|lam di|tìm đi|tim di)\b", 2)


def ask(sid, text):
    with LOCK:
        hist = SESSIONS.setdefault(sid, deque(maxlen=HISTORY_TURNS * 2))
    cards, used, said = [], [], []
    # Guardrail "never spend": a paid web search runs only after sir says yes to the question we asked last turn.
    approved = bool(PENDING_WEB.pop(sid, None)) and bool(YES.match(text))

    def run_tool(name, args):
        if name == "research_web" and not approved:
            PENDING_WEB[sid] = args.get("query", "")
            used.append("research_web (awaiting yes)")
            return {"needs_confirmation": True,
                    "spoken_hint": f"That needs a paid web search for “{args.get('query', '')}”. Shall I, sir?"}, False
        res, err = T.run(name, args)
        if name == "remember" and not err: said.append(res["say"])
        if res.get("card"): cards.append(res["card"])
        used.append(name)
        # the model sees the card too, so it knows what is already on screen and won't read it out
        return {"spoken_hint": res["say"], "card_on_screen": res.get("card"), **res.get("data", {})}, err

    model, error, say = llm.model_name(), None, None
    if model:
        try:
            say = llm.chat(tools.load_prompt(), list(hist) + [{"role": "user", "text": text}], tools.SPECS, run_tool)
        except llm.ModelError as e:
            error, model, cards, used = str(e), None, [], []
    if say is None:   # no model, or it failed: route by scoring against the files, and say so on screen
        name, args, reply = T.route(text)
        if name:
            res, _ = T.run(name, args)
            say = res["say"]
            said.clear()
            if res.get("card"): cards.append(res["card"])
            used.append(name)
        else:
            say = reply
    say = say or "…"
    # Guardrail "never write to memory silently": the exact write is always spoken, whatever the model chose to say.
    for line in said:
        if line not in say: say = (say + " " + line).strip()
    hist.append({"role": "user", "text": text})
    hist.append({"role": "assistant", "text": say})
    return {"say": say, "cards": cards, "tools": used, "model": model, "model_error": error}


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        p = u.path
        if p == "/api/graph":
            return self._send(200, V.graph())
        if p == "/api/note":
            n = V.note(q.get("id", ""))
            return self._send(200, n) if n else self._send(404, {"error": "not found"})
        if p == "/api/path":
            return self._send(200, {"path": V.path(q.get("a", ""), q.get("b", ""))})
        if p == "/api/search":
            return self._send(200, {"results": V.search(q.get("q", ""), int(q.get("k", 8)))})
        if p == "/api/status":
            return self._send(200, {"mode": vault.data.mode(), "model": llm.model_name(), "voice": voice.available(), "step": 4,
                                    "inbox": bool(vault.data.inbox_dir()), "calendar": bool(vault.data.calendar_file())})
        if p == "/api/memory":
            return self._send(200, {"facts": memory.all_facts()})
        # static UI (no directory traversal)
        f = (UI / ("index.html" if p in ("/", "") else p.lstrip("/"))).resolve()
        if UI.resolve() not in f.parents or not f.is_file():
            return self._send(404, b"not found", "text/plain")
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype.endswith("javascript"):
            ctype += "; charset=utf-8"
        self._send(200, f.read_bytes(), ctype)

    def do_POST(self):
        u = urlparse(self.path)
        # other websites must not drive this API: JSON content-type forces a CORS preflight (never answered),
        # and the Host check blocks DNS rebinding.
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        ctype = self.headers.get("Content-Type") or ""
        if host not in ("localhost", "127.0.0.1", "[::1]") or not (ctype.startswith("application/json") or ctype.startswith("audio/")):
            return self._send(403, {"error": "forbidden"})
        if u.path == "/api/listen":   # raw audio body -> {text}
            n = int(self.headers.get("Content-Length", 0))
            if not ctype.startswith("audio/") or n > 12_000_000: return self._send(413, {"error": "bad audio"})
            try:
                return self._send(200, {"text": voice.listen(self.rfile.read(n), ctype)})
            except voice.VoiceError as e:
                return self._send(502, {"error": str(e)})
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 64_000: return self._send(413, {"error": "too large"})
            body = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._send(400, {"error": "bad json"})
        if u.path == "/api/ask":
            text = str(body.get("text", "")).strip()[:2000]
            if not text: return self._send(400, {"error": "empty"})
            return self._send(200, ask(str(body.get("session", "default"))[:64], text))
        if u.path == "/api/speak":   # {text} -> mp3
            try:
                return self._send(200, voice.speak(body.get("text", "")), "audio/mpeg")
            except voice.VoiceError as e:
                return self._send(502, {"error": str(e)})
        if u.path.startswith("/api/tool/"):
            name = u.path.rsplit("/", 1)[-1]
            if name not in {"brief_me", "plan_day", "read_inbox"}: return self._send(404, {"error": "unknown tool"})
            res, err = T.run(name, {})
            return self._send(200, {"say": res["say"], "cards": [res["card"]] if res.get("card") else [], "tools": [name],
                                    "model": None, "error": err})
        self._send(404, {"error": "not found"})


if __name__ == "__main__":
    print(f"[jarvis] http://localhost:{PORT}")
    ThreadingHTTPServer((HOST, PORT), H).serve_forever()
