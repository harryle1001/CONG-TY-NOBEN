"""Google OAuth for an "installed app" (loopback redirect, PKCE, state). Stdlib only, READ-ONLY scopes.

Holds the token; never reads mail or calendar itself. data.py calls get_json() for that.
The client secret and tokens stay in this process and in .google_token.json (chmod 600): never sent to the browser.

Base URLs can be overridden (tests use a fake Google on localhost):
  GOOGLE_AUTH_URL, GOOGLE_TOKEN_URL, GOOGLE_GMAIL_API, GOOGLE_CALENDAR_API
  or GOOGLE_API_BASE=http://127.0.0.1:9xxx  (sets all four under one host)
"""
import base64, hashlib, json, os, secrets, threading, time
import urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN_FILE = Path(os.environ.get("JARVIS_GOOGLE_TOKEN", ROOT / ".google_token.json"))
SCOPES = ("https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/calendar.readonly")
STATE_TTL = 600          # a consent screen left open longer than 10 min must be restarted
TIMEOUT = 20

_base = os.environ.get("GOOGLE_API_BASE", "").rstrip("/")
AUTH_URL = os.environ.get("GOOGLE_AUTH_URL") or (_base + "/o/oauth2/v2/auth" if _base else "https://accounts.google.com/o/oauth2/v2/auth")
TOKEN_URL = os.environ.get("GOOGLE_TOKEN_URL") or (_base + "/token" if _base else "https://oauth2.googleapis.com/token")
GMAIL_API = os.environ.get("GOOGLE_GMAIL_API") or (_base + "/gmail/v1" if _base else "https://gmail.googleapis.com/gmail/v1")
CALENDAR_API = os.environ.get("GOOGLE_CALENDAR_API") or (_base + "/calendar/v3" if _base else "https://www.googleapis.com/calendar/v3")

_PENDING, _LOCK = {}, threading.Lock()   # state -> (pkce verifier, redirect_uri, created)
_last_error = None


class GoogleError(Exception):
    """Shown to sir as-is: say what broke and what to do."""


def _client():
    cid, sec = os.environ.get("GOOGLE_CLIENT_ID", "").strip(), os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    return cid, sec


def configured():
    return all(_client())


def _load():
    try:
        return json.loads(TOKEN_FILE.read_text("utf-8"))
    except (OSError, ValueError):
        return None


def _save(tok):
    tmp = TOKEN_FILE.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(tok, f)
    os.chmod(tmp, 0o600)
    os.replace(tmp, TOKEN_FILE)


def status():
    tok = _load()
    return {"configured": configured(), "connected": bool(tok and tok.get("refresh_token")), "error": _last_error}


def _fail(msg):
    global _last_error
    _last_error = msg
    raise GoogleError(msg)


# ---------------- consent ----------------
def start(redirect_uri):
    """URL of Google's consent screen. PKCE (S256) + one-time state kept server-side."""
    cid, _ = _client()
    if not configured():
        _fail("Google is not configured: set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env, then restart.")
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(32)
    now = time.time()
    with _LOCK:
        for s in [s for s, v in _PENDING.items() if now - v[2] > STATE_TTL]:
            del _PENDING[s]
        _PENDING[state] = (verifier, redirect_uri, now)
    q = {"client_id": cid, "redirect_uri": redirect_uri, "response_type": "code", "scope": " ".join(SCOPES),
         "state": state, "code_challenge": challenge, "code_challenge_method": "S256",
         "access_type": "offline", "prompt": "consent", "include_granted_scopes": "false"}
    return AUTH_URL + "?" + urllib.parse.urlencode(q), state


def callback(params, state_cookie=None):
    """Handle ?code&state (or ?error). Exchanges the code and stores the token. Raises GoogleError."""
    global _last_error
    if params.get("error"):
        _fail(f"Google refused the connection: {params['error']}.")
    state = params.get("state", "")
    with _LOCK:
        pend = _PENDING.pop(state, None)
    if not pend or not secrets.compare_digest(state, state_cookie or "") or time.time() - pend[2] > STATE_TTL:
        _fail("Login link invalid or expired (state mismatch). Start again from the GOOGLE badge.")
    verifier, redirect_uri, _ = pend
    if not params.get("code"):
        _fail("Google sent no authorization code.")
    cid, sec = _client()
    tok = _token_request({"grant_type": "authorization_code", "code": params["code"], "redirect_uri": redirect_uri,
                          "client_id": cid, "client_secret": sec, "code_verifier": verifier})
    granted = set((tok.get("scope") or "").split())
    if granted and not granted <= set(SCOPES) | {"openid"}:
        _fail(f"Google granted more than read-only access ({' '.join(sorted(granted - set(SCOPES)))}); refusing to store it.")
    if not tok.get("refresh_token"):
        _fail("Google sent no refresh token. Remove Jarvis at myaccount.google.com/permissions and connect again.")
    _store(tok)
    _last_error = None


def _store(tok, old=None):
    out = {"access_token": tok["access_token"], "expires_at": time.time() + int(tok.get("expires_in", 3600)),
           "refresh_token": tok.get("refresh_token") or (old or {}).get("refresh_token"),
           "scope": tok.get("scope") or (old or {}).get("scope", "")}
    _save(out)
    return out


def _token_request(form):
    req = urllib.request.Request(TOKEN_URL, data=urllib.parse.urlencode(form).encode(), method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read()).get("error", "")
        except Exception:
            err = ""
        if err == "invalid_grant":
            _fail("Google token expired or revoked. Reconnect from the GOOGLE badge.")
        _fail(f"Google token endpoint error: HTTP {e.code} {err}".strip())
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        _fail(f"Cannot reach Google ({getattr(e, 'reason', e)}).")


# ---------------- access ----------------
def access_token(force=False):
    tok = _load()
    if not tok or not tok.get("refresh_token"):
        _fail("Google not connected. Click the GOOGLE badge (top right) to connect, read-only.")
    if force or time.time() > tok.get("expires_at", 0) - 60:
        cid, sec = _client()
        if not configured():
            _fail("GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET missing from .env: cannot refresh the Google token.")
        new = _token_request({"grant_type": "refresh_token", "refresh_token": tok["refresh_token"],
                              "client_id": cid, "client_secret": sec})
        tok = _store(new, tok)
    return tok["access_token"]


def get_json(url, params=None):
    """GET only: this module has no way to send, delete or change anything in Gmail or Calendar."""
    global _last_error
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    for attempt in (0, 1):
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + access_token(force=attempt == 1),
                                                   "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                _last_error = None
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 401 and attempt == 0:
                continue                      # access token stale: refresh once and retry
            try:
                msg = json.loads(e.read()).get("error", {})
                msg = msg.get("message", "") if isinstance(msg, dict) else str(msg)
            except Exception:
                msg = ""
            hint = " (is the API enabled in Google Cloud Console?)" if e.code == 403 else ""
            _fail(f"Google API error HTTP {e.code}{hint}: {msg}".strip(": "))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            _fail(f"Cannot reach Google ({getattr(e, 'reason', e)}).")
