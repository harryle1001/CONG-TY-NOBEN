"""JARVIS HTTP server. Stdlib only. Step 2: graph UI + read-only graph API (no voice, no model yet).

Run:  python3 agent/main.py        -> http://localhost:8618
"""
import json, mimetypes, os, sys, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vault

ROOT = Path(__file__).resolve().parent.parent
UI = ROOT / "ui"
HOST = os.environ.get("JARVIS_HOST", "127.0.0.1")
PORT = int(os.environ.get("JARVIS_PORT", "8618"))

t0 = time.time()
V = vault.Vault()
print(f"[jarvis] indexed {len(V.nodes)} nodes / {len(V.edges)} edges in {time.time() - t0:.1f}s ({vault.data.mode()})")


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
            return self._send(200, {"mode": vault.data.mode(), "model": False, "voice": False, "step": 2})
        # static UI (no directory traversal)
        f = (UI / ("index.html" if p in ("/", "") else p.lstrip("/"))).resolve()
        if UI.resolve() not in f.parents or not f.is_file():
            return self._send(404, b"not found", "text/plain")
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype.endswith("javascript"):
            ctype += "; charset=utf-8"
        self._send(200, f.read_bytes(), ctype)


if __name__ == "__main__":
    print(f"[jarvis] http://localhost:{PORT}")
    ThreadingHTTPServer((HOST, PORT), H).serve_forever()
