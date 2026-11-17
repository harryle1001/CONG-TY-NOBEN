"""Fake Google (OAuth + Gmail + Calendar) on localhost, for testing without a real account. Stdlib only.

  python3 tests/fake_google.py 9618        then run Jarvis with GOOGLE_API_BASE=http://127.0.0.1:9618

Checks what real Google checks that matters here: client id/secret, redirect_uri, PKCE S256, read-only scopes,
Bearer token, expiry. Any non-GET to the APIs is a test failure (Jarvis must never write).
Control (tests only): GET /_control?expire=1 (access tokens expire now), ?revoke=1 (refresh token dies), ?log=1.
"""
import base64, datetime as dt, hashlib, json, secrets, sys, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode

CLIENT_ID, CLIENT_SECRET = "fake-client.apps.googleusercontent.com", "fake-secret"
SCOPES = {"https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/calendar.readonly"}
CODES, ACCESS, REFRESH, LOG = {}, {}, set(), []
WRITES = []


def b64(s):
    return base64.urlsafe_b64encode(s.encode()).decode().rstrip("=")


TODAY = dt.date.today()
MAILS = [
    {"id": "m1", "labelIds": ["INBOX", "UNREAD"], "internalDate": "1700000000000",
     "payload": {"mimeType": "multipart/alternative", "headers": [
         {"name": "From", "value": "Trại tôm Sao Biển <saobien@example.com>"},
         {"name": "Subject", "value": "Đặt 20 thùng Aqua Probio"},
         {"name": "Date", "value": "Tue, 17 Nov 2026 07:30:00 +0700"}],
         "parts": [{"mimeType": "text/plain", "body": {"data": b64("Anh gửi báo giá giúp em, giao trước thứ Sáu.")}},
                   {"mimeType": "text/html", "body": {"data": b64("<p>HTML version</p>")}}]}},
    {"id": "m2", "labelIds": ["INBOX"], "internalDate": "1699990000000",
     "payload": {"mimeType": "text/html", "headers": [
         {"name": "From", "value": "Đại lý Minh Phú <minhphu@example.com>"},
         {"name": "Subject", "value": "Đã chuyển khoản"},
         {"name": "Date", "value": "Mon, 16 Nov 2026 15:00:00 +0700"}],
         "body": {"data": b64("<div>Đã chuyển <b>12.000.000đ</b>.</div>")}}},
]


def events():
    d = TODAY.isoformat()
    return [{"summary": "Gọi HTX Cà Mau", "status": "confirmed", "start": {"dateTime": f"{d}T09:00:00+07:00"}},
            {"summary": "Tập BJJ", "status": "confirmed", "start": {"date": d}},
            {"summary": "Đã huỷ", "status": "cancelled", "start": {"dateTime": f"{d}T11:00:00+07:00"}}]


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _auth(self):
        tok = (self.headers.get("Authorization") or "").removeprefix("Bearer ")
        exp = ACCESS.get(tok)
        if not exp or exp < time.time():
            self._json(401, {"error": {"code": 401, "message": "Invalid Credentials"}})
            return False
        return True

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        LOG.append(("GET", u.path))
        if u.path == "/_control":
            if q.get("expire"):
                for k in ACCESS: ACCESS[k] = 0
            if q.get("revoke"):
                REFRESH.clear()
            return self._json(200, {"log": LOG[-40:], "writes": WRITES, "access": len(ACCESS), "refresh": len(REFRESH)})
        if u.path == "/o/oauth2/v2/auth":   # consent screen: auto-approve, but validate the request first
            if q.get("client_id") != CLIENT_ID: return self._json(400, {"error": "invalid_client"})
            if set(q.get("scope", "").split()) != SCOPES: return self._json(400, {"error": "invalid_scope", "got": q.get("scope")})
            if q.get("code_challenge_method") != "S256" or not q.get("code_challenge") or not q.get("state"):
                return self._json(400, {"error": "pkce_or_state_missing"})
            code = secrets.token_urlsafe(16)
            CODES[code] = (q["code_challenge"], q["redirect_uri"])
            self.send_response(302)
            self.send_header("Location", q["redirect_uri"] + "?" + urlencode({"code": code, "state": q["state"], "scope": q["scope"]}))
            self.send_header("Content-Length", "0")
            return self.end_headers()
        if u.path == "/gmail/v1/users/me/messages":
            if not self._auth(): return
            if q.get("labelIds") != "INBOX": return self._json(400, {"error": {"message": "expected INBOX"}})
            return self._json(200, {"messages": [{"id": m["id"]} for m in MAILS][: int(q.get("maxResults", 100))]})
        if u.path.startswith("/gmail/v1/users/me/messages/"):
            if not self._auth(): return
            m = next((m for m in MAILS if m["id"] == u.path.rsplit("/", 1)[1]), None)
            return self._json(200, m) if m else self._json(404, {"error": {"message": "not found"}})
        if u.path == "/calendar/v3/calendars/primary/events":
            if not self._auth(): return
            if q.get("singleEvents") != "true" or "timeMin" not in q: return self._json(400, {"error": {"message": "bad query"}})
            return self._json(200, {"items": events()})
        self._json(404, {"error": {"message": "no route " + u.path}})

    def do_POST(self):
        u = urlparse(self.path)
        LOG.append(("POST", u.path))
        n = int(self.headers.get("Content-Length", 0))
        f = {k: v[0] for k, v in parse_qs(self.rfile.read(n).decode()).items()}
        if u.path != "/token":
            WRITES.append(u.path)
            return self._json(403, {"error": "fake google: Jarvis tried to write " + u.path})
        if f.get("client_id") != CLIENT_ID or f.get("client_secret") != CLIENT_SECRET:
            return self._json(401, {"error": "invalid_client"})
        if f.get("grant_type") == "authorization_code":
            c = CODES.pop(f.get("code", ""), None)
            if not c: return self._json(400, {"error": "invalid_grant"})
            challenge = base64.urlsafe_b64encode(hashlib.sha256(f.get("code_verifier", "").encode()).digest()).rstrip(b"=").decode()
            if challenge != c[0]: return self._json(400, {"error": "invalid_grant", "error_description": "PKCE"})
            if f.get("redirect_uri") != c[1]: return self._json(400, {"error": "redirect_uri_mismatch"})
            rt = secrets.token_urlsafe(16); REFRESH.add(rt)
        elif f.get("grant_type") == "refresh_token":
            if f.get("refresh_token") not in REFRESH: return self._json(400, {"error": "invalid_grant"})
            rt = None
        else:
            return self._json(400, {"error": "unsupported_grant_type"})
        at = secrets.token_urlsafe(16); ACCESS[at] = time.time() + 3600
        out = {"access_token": at, "expires_in": 3600, "token_type": "Bearer", "scope": " ".join(sorted(SCOPES))}
        if rt: out["refresh_token"] = rt
        self._json(200, out)

    do_PUT = do_DELETE = do_PATCH = do_POST


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9618
    print(f"[fake-google] http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
