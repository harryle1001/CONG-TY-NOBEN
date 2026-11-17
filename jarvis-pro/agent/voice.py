"""ElevenLabs speech in and out. The key lives here, on the server; the browser only ever sees audio bytes and text.

ELEVENLABS_API_KEY   required for voice
ELEVENLABS_VOICE_ID  default: "Daniel" (British, measured) — the closest premade voice to JARVIS
ELEVENLABS_TTS_MODEL default: eleven_multilingual_v2 (reads Vietnamese names correctly)
"""
import json, os, uuid, urllib.request, urllib.error

BASE = os.environ.get("JARVIS_ELEVEN_BASE", "https://api.elevenlabs.io")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "onwK4e9ZLuTAKqWW03F9")
TTS_MODEL = os.environ.get("ELEVENLABS_TTS_MODEL", "eleven_multilingual_v2")
STT_MODEL = "scribe_v1"
TIMEOUT = 60
MAX_TTS_CHARS = 600          # spoken lines are 1-2 sentences; this caps cost if something runs long


class VoiceError(Exception):
    pass


def available():
    return bool(os.environ.get("ELEVENLABS_API_KEY"))


def _req(path, data, ctype, accept="application/json"):
    if not available():
        raise VoiceError("ELEVENLABS_API_KEY is not set")
    req = urllib.request.Request(BASE + path, data, {"xi-api-key": os.environ["ELEVENLABS_API_KEY"],
                                                     "content-type": ctype, "accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        raise VoiceError(f"ElevenLabs HTTP {e.code}: {e.read()[:240].decode('utf-8', 'replace')}")
    except (urllib.error.URLError, TimeoutError) as e:
        raise VoiceError(f"ElevenLabs unreachable: {e}")


def speak(text):
    """Text -> mp3 bytes."""
    text = " ".join(str(text).split())[:MAX_TTS_CHARS]
    if not text:
        raise VoiceError("nothing to say")
    body = json.dumps({"text": text, "model_id": TTS_MODEL,
                       "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.15}}).encode()
    return _req(f"/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128", body, "application/json", "audio/mpeg")


def listen(audio, mime="audio/webm"):
    """Audio bytes -> transcript (Scribe, language auto-detected: Vietnamese or English)."""
    if len(audio) < 1200:
        return ""
    b = uuid.uuid4().hex
    ext = {"audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "m4a", "audio/wav": "wav"}.get(mime.split(";")[0], "webm")
    parts = [f'--{b}\r\nContent-Disposition: form-data; name="model_id"\r\n\r\n{STT_MODEL}\r\n'.encode(),
             f'--{b}\r\nContent-Disposition: form-data; name="tag_audio_events"\r\n\r\nfalse\r\n'.encode(),
             f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="turn.{ext}"\r\n'
             f'Content-Type: {mime.split(";")[0]}\r\n\r\n'.encode(), audio, f"\r\n--{b}--\r\n".encode()]
    out = json.loads(_req("/v1/speech-to-text", b"".join(parts), f"multipart/form-data; boundary={b}"))
    return (out.get("text") or "").strip()
