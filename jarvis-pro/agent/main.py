"""JARVIS HTTP server + API. Python stdlib only.  Run:  python3 agent/main.py"""
import json, mimetypes, os, sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vault import Vault

ROOT = Path(__file__).resolve().parent.parent
UI = ROOT / "ui"
PORT = int(os.environ.get("JARVIS_PORT", "1618"))

print("[jarvis] indexing…")
VAULT = Vault()
print(f"[jarvis] {len(VAULT.nodes)} nodes, {len(VAULT.edges)} edges")


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
        # static UI
        rel = "index.html" if u.path in ("/", "") else u.path.lstrip("/")
        f = (UI / rel).resolve()
        if UI.resolve() not in f.parents or not f.is_file():
            return self.send(404, {"error": "not found"})
        self.send(200, f.read_bytes(), (mimetypes.guess_type(f.name)[0] or "text/plain") + "; charset=utf-8")


if __name__ == "__main__":
    print(f"[jarvis] http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
