"""ElevenLabs speech in (Scribe) and out (TTS). The key stays here, server-side; the browser never sees it."""
import json, os, urllib.error, urllib.request, uuid

API = "https://api.elevenlabs.io/v1"
VOICE_ID = os.environ.get("ELEVEN_VOICE_ID", "onwK4e9ZLuTAKqWW03F9")   # "Daniel": British, formal, steady (premade)
TTS_MODEL = os.environ.get("ELEVEN_TTS_MODEL", "eleven_multilingual_v2")
STT_MODEL = os.environ.get("ELEVEN_STT_MODEL", "scribe_v1")


class VoiceError(RuntimeError):
    pass


def _key():
    k = os.environ.get("ELEVENLABS_API_KEY", "")
    if not k:
        raise VoiceError("no ELEVENLABS_API_KEY in .env")
    return k


def available():
    return bool(os.environ.get("ELEVENLABS_API_KEY"))


def _post(url, data, headers, timeout=60):
    req = urllib.request.Request(url, data, {"xi-api-key": _key(), **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        raise VoiceError(f"ElevenLabs {e.code}: {e.read()[:240].decode('utf-8', 'replace')}")
    except urllib.error.URLError as e:
        raise VoiceError(f"ElevenLabs unreachable: {e.reason}")


def speak(text):
    """Text -> mp3 bytes."""
    text = text.strip()[:2500]
    if not text:
        raise VoiceError("nothing to say")
    body = json.dumps({"text": text, "model_id": TTS_MODEL,
                       "voice_settings": {"stability": 0.62, "similarity_boost": 0.8, "style": 0.0}}).encode()
    return _post(f"{API}/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128", body,
                 {"content-type": "application/json", "accept": "audio/mpeg"})


def listen(audio, mime="audio/webm"):
    """Recorded audio -> transcript. Language is auto-detected (Vietnamese or English)."""
    if len(audio) < 1200:
        return ""
    ext = {"audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "m4a", "audio/mpeg": "mp3", "audio/wav": "wav"}.get(mime.split(";")[0], "webm")
    b = uuid.uuid4().hex
    parts = [
        f'--{b}\r\nContent-Disposition: form-data; name="model_id"\r\n\r\n{STT_MODEL}\r\n'.encode(),
        f'--{b}\r\nContent-Disposition: form-data; name="tag_audio_events"\r\n\r\nfalse\r\n'.encode(),
        f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="turn.{ext}"\r\nContent-Type: {mime.split(";")[0]}\r\n\r\n'.encode(),
        audio, f"\r\n--{b}--\r\n".encode(),
    ]
    out = json.loads(_post(f"{API}/speech-to-text", b"".join(parts), {"content-type": f"multipart/form-data; boundary={b}"}))
    return (out.get("text") or "").strip()
