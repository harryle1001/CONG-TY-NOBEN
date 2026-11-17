// Voice: press the mic once, then just talk. Recording via MediaRecorder, transcription server-side (ElevenLabs Scribe),
// speech out via /api/speak. The key never reaches this page. No Web Speech API.
"use strict";
const SILENCE_MS = 900;       // quiet this long after speech = end of turn. Tune here.
const SPEECH_LEVEL = 0.022;   // RMS above this counts as talking. Raise it in a noisy room.
const MIN_SPEECH_MS = 260;    // ignore clicks and coughs shorter than this
const MAX_TURN_MS = 30000;    // hard cap on one turn
const TICK_MS = 50;           // level loop runs on setInterval, NOT requestAnimationFrame: RAF stops in background tabs
const BARS = 13;

const Voice = {
  available: false, on: false, muted: false, state: "idle",
  stream: null, ctx: null, inAn: null, outAn: null, rec: null, chunks: [], timer: null,
  speechStart: 0, lastLoud: 0, turnStart: 0, heard: false, audio: null, endSpeak: null,

  init(available) {
    this.available = available;
    const mic = $("#t-mic"), mute = $("#t-mute");
    mic.disabled = mute.disabled = false;
    if (!available) { mic.title = mute.title = "Voice off: set ELEVENLABS_API_KEY in .env and restart"; }
    mic.onclick = () => this.toggle();
    mute.onclick = () => { this.muted = !this.muted; mute.classList.toggle("on", this.muted); mute.textContent = this.muted ? "MUTED" : "MUTE"; if (this.muted) this.bargeIn(); };
    $("#bars").innerHTML = "<i></i>".repeat(BARS);
    addEventListener("keydown", e => {
      const typing = document.activeElement && document.activeElement.id === "ask";
      if ((e.key === " " && !typing) || e.key === "Escape") {
        if (this.state === "speaking") { e.preventDefault(); e.stopImmediatePropagation(); this.bargeIn(); }
      }
    }, true);
  },

  toggle() {
    if (!this.available) return fail("Giọng nói đang TẮT: chưa có ELEVENLABS_API_KEY trong file .env. Điền khóa rồi khởi động lại server.");
    if (this.state === "speaking") return this.bargeIn();
    this.on ? this.stop() : this.start();
  },

  async start() {
    if (!navigator.mediaDevices || !window.MediaRecorder) return fail("Trình duyệt này không ghi âm được (thiếu MediaRecorder). Dùng Chrome, Edge, Firefox hoặc Safari mới.");
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
    } catch (e) {
      const why = e.name === "NotAllowedError" ? "Micro đang bị CHẶN. Bấm biểu tượng ổ khóa trên thanh địa chỉ → cho phép Microphone, rồi bấm MIC lại."
        : e.name === "NotFoundError" ? "Không tìm thấy micro nào. Cắm micro hoặc kiểm tra thiết bị âm thanh."
        : "Không mở được micro: " + e.name + " " + e.message;
      return fail(why);
    }
    this.ctx = this.ctx || new AudioContext();
    if (this.ctx.state === "suspended") await this.ctx.resume();
    this.inAn = this.ctx.createAnalyser(); this.inAn.fftSize = 1024;
    this.ctx.createMediaStreamSource(this.stream).connect(this.inAn);
    const track = this.stream.getAudioTracks()[0];
    track.onended = () => { fail("Micro vừa bị ngắt (rút dây hoặc bị thu hồi quyền)."); this.stop(); };
    this.on = true; $("#t-mic").classList.add("on");
    clearInterval(this.timer); this.timer = setInterval(() => this.tick(), TICK_MS);
    this.listen();
  },

  stop() {
    this.on = false; $("#t-mic").classList.remove("on");
    try { this.rec && this.rec.state !== "inactive" && this.rec.stop(); } catch (e) {}
    this.rec = null;
    if (this.stream) this.stream.getTracks().forEach(t => t.stop());
    this.stream = null; this.inAn = null;
    clearInterval(this.timer); this.timer = null;
    this.bargeIn(); this.set("idle"); caption("");
    this.drawLevel(0, null);
  },

  set(s) { this.state = s; setState(s); },

  mime() {
    for (const m of ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4"])
      if (MediaRecorder.isTypeSupported(m)) return m;
    return "";
  },

  listen() {
    if (!this.on) return;
    this.set("listening"); caption("Listening…", "dim");
    this.chunks = []; this.heard = false; this.speechStart = 0; this.turnStart = performance.now();
    const m = this.mime();
    this.rec = new MediaRecorder(this.stream, m ? { mimeType: m } : undefined);
    this.rec.ondataavailable = e => e.data.size && this.chunks.push(e.data);
    this.rec.start(250);
  },

  rms(an) {
    const buf = new Float32Array(an.fftSize); an.getFloatTimeDomainData(buf);
    let s = 0; for (const v of buf) s += v * v;
    return Math.sqrt(s / buf.length);
  },

  tick() {
    const now = performance.now();
    if (this.state === "speaking" && this.outAn) return this.drawLevel(this.rms(this.outAn) * 2.2, this.outAn);
    if (this.state !== "listening" || !this.inAn) return this.drawLevel(0, null);   // deaf while thinking/speaking
    const lvl = this.rms(this.inAn);
    this.drawLevel(lvl, this.inAn);
    if (lvl > SPEECH_LEVEL) {
      if (!this.speechStart) this.speechStart = now;
      this.lastLoud = now;
      if (!this.heard && now - this.speechStart > MIN_SPEECH_MS) { this.heard = true; caption("Hearing you…"); }
    } else if (this.speechStart && !this.heard && now - this.lastLoud > SILENCE_MS) {
      this.speechStart = 0;   // a blip, not speech
    }
    const quietFor = now - this.lastLoud, turnFor = now - this.turnStart;
    if (this.heard && (quietFor > SILENCE_MS || turnFor > MAX_TURN_MS)) return this.endTurn();
    if (!this.heard && turnFor > MAX_TURN_MS) { this.discard(); this.listen(); }   // keep recordings short while idle
  },

  drawLevel(lvl, an) {
    $("#reactor").style.setProperty("--lvl", Math.min(1, lvl * 12).toFixed(3));
    const bars = $("#bars").children;
    if (!an) { for (const b of bars) b.style.transform = "scaleY(.06)"; return; }
    const f = new Uint8Array(an.frequencyBinCount); an.getByteFrequencyData(f);
    for (let i = 0; i < bars.length; i++) {
      const v = f[Math.floor(2 + i * (f.length / 3) / bars.length)] / 255;
      bars[i].style.transform = `scaleY(${Math.max(.06, v).toFixed(3)})`;
    }
  },

  discard() { try { this.rec.onstop = null; this.rec.stop(); } catch (e) {} this.rec = null; this.chunks = []; },

  async endTurn() {
    this.set("thinking"); caption("Transcribing…", "dim");
    const rec = this.rec; this.rec = null;
    const blob = await new Promise(res => { rec.onstop = () => res(new Blob(this.chunks, { type: rec.mimeType || "audio/webm" })); rec.stop(); });
    let text = "";
    try {
      const r = await fetch("/api/listen", { method: "POST", headers: { "Content-Type": blob.type || "audio/webm" }, body: blob });
      const d = await r.json();
      if (!r.ok) throw new Error(d.error || "HTTP " + r.status);
      text = d.text;
    } catch (e) {
      fail("Không chuyển giọng nói thành chữ được: " + e.message);
      if (this.on) this.listen();
      return;
    }
    if (!text) { caption("Didn't catch that.", "dim"); if (this.on) this.listen(); return; }
    caption("“" + text + "”");
    await ask(text);   // ask() speaks the reply, then hands back to listen()
  },

  // Speak a reply. Mic is deaf for the whole time (no recorder running, levels ignored).
  async say(text) {
    if (!this.available || this.muted || !text) return;
    this.set("speaking");
    let url;
    try {
      const r = await fetch("/api/speak", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error || "HTTP " + r.status);
      url = URL.createObjectURL(await r.blob());
    } catch (e) { fail("Jarvis không nói được (ElevenLabs): " + e.message); return; }
    this.ctx = this.ctx || new AudioContext();
    if (this.ctx.state === "suspended") await this.ctx.resume().catch(() => {});
    const a = this.audio = new Audio(url);
    try {
      const src = this.ctx.createMediaElementSource(a);
      this.outAn = this.ctx.createAnalyser(); this.outAn.fftSize = 1024;
      src.connect(this.outAn); this.outAn.connect(this.ctx.destination);
    } catch (e) { this.outAn = null; }
    if (!this.timer) this.timer = setInterval(() => this.tick(), TICK_MS);
    await new Promise(res => {
      this.endSpeak = res;
      a.onended = a.onerror = res;
      a.play().catch(err => { fail("Trình duyệt chặn phát âm thanh: " + err.message + ". Bấm vào trang một lần rồi thử lại."); res(); });
    });
    this.endSpeak = null; this.audio = null; this.outAn = null;
    URL.revokeObjectURL(url);
    if (!this.on) { clearInterval(this.timer); this.timer = null; this.drawLevel(0, null); }
  },

  bargeIn() {
    if (this.audio) { this.audio.pause(); }
    if (this.endSpeak) this.endSpeak();
  },
};

function caption(text, cls) {
  const c = $("#caption");
  c.textContent = text; c.className = "caption " + (cls || ""); c.hidden = !text;
}
