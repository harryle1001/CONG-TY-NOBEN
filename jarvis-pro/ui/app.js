// ---- Voice tuning: change these to taste ----
const SILENCE_MS = 900;        // quiet this long after speech = end of your turn
const SPEECH_LEVEL = 0.035;    // RMS level that counts as speech (raise in a noisy room)
const MIN_SPEECH_MS = 300;     // ignore blips shorter than this
const MAX_TURN_MS = 30000;     // hard stop for one turn
const LEVEL_POLL_MS = 50;      // setInterval, not rAF: rAF stops in background tabs and the mic goes deaf

// JARVIS UI glue. Step 2: graph, inspector, hubs, filters. Voice + tools come later.
const $ = (id) => document.getElementById(id);
const EXAMPLES = [
  "What's the dealer price of Iodine Shield?",
  "Giá đại lý sản phẩm xử lý môi trường là bao nhiêu?",
  "Which clients still owe money?",
  "Plan my day, sir-style.",
  "Brief me.",
];

function toast(msg) {
  const t = $("toast"); t.textContent = msg; t.hidden = false;
  clearTimeout(toast.h); toast.h = setTimeout(() => (t.hidden = true), 6854);
}

let ex = 0;
function rotatePlaceholder() { $("q").placeholder = EXAMPLES[ex++ % EXAMPLES.length]; }
rotatePlaceholder(); setInterval(rotatePlaceholder, 4236);

async function getJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url} → ${r.status}`);
  return r.json();
}

function esc(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

async function openNote(id) {
  const box = $("inspector");
  if (!id) { box.innerHTML = '<p class="mute">Click a node to open it.</p>'; return; }
  try {
    const n = await getJSON("/api/note?id=" + encodeURIComponent(id));
    box.innerHTML = `<h2>${esc(n.title)}</h2>
      <div class="meta">${esc(n.type)} · ${n.degree} links<br>${esc(n.path)}</div>
      <pre>${esc(n.text || "(folder)").slice(0, 4000)}</pre>`;
  } catch (e) { box.innerHTML = `<p class="mute">Couldn't open this note: ${esc(e.message)}</p>`; }
}

function renderHubs(nodes) {
  const ol = $("hubs"); ol.innerHTML = "";
  nodes.filter(n => n.type !== "folder").sort((a, b) => b.degree - a.degree).slice(0, 10).forEach(n => {
    const li = document.createElement("li");
    li.innerHTML = `<span>${esc(n.title)}</span><span class="num">${n.degree}</span>`;
    li.onclick = () => Graph.focus(n.id);
    ol.append(li);
  });
}

function renderFilters(nodes) {
  const counts = {}; nodes.forEach(n => (counts[n.type] = (counts[n.type] || 0) + 1));
  const hidden = new Set(), ul = $("filters"); ul.innerHTML = "";
  Object.entries(counts).sort((a, b) => b[1] - a[1]).forEach(([t, c]) => {
    const li = document.createElement("li");
    li.innerHTML = `<span><i class="dot" style="background:${Graph.colors[t] || "#999"}"></i>${esc(t)}</span><span class="num">${c}</span>`;
    li.onclick = () => { hidden.has(t) ? hidden.delete(t) : hidden.add(t); li.classList.toggle("off"); Graph.setHidden(new Set(hidden)); };
    ul.append(li);
  });
}

Graph.onSelect = openNote;
Graph.onPath = (ids, a, b) => {
  if (!ids) return toast("No path between those two notes.");
  $("caption").textContent = `Path: ${ids.length - 1} hops`;
};

(async () => {
  try {
    const g = await getJSON("/api/graph");
    Graph.load(g); renderHubs(g.nodes); renderFilters(g.nodes);
    const m = $("mode"); m.textContent = g.mode === "demo" ? "DEMO DATA" : "LIVE DATA";
    if (g.mode !== "demo") m.classList.add("warn");
  } catch (e) {
    toast("Can't reach the Jarvis server. Is `python3 agent/main.py` running?");
  }
})();

// ---------------- conversation ----------------
const reactor = (st) => { $("reactor").dataset.state = st; $("state").textContent = st.toUpperCase(); };
window.Jarvis = { reactor, onReply: null };

function row(left, right, id) {
  const d = document.createElement("div"); d.className = "row" + (id ? " link" : "");
  d.innerHTML = `<span>${esc(left)}</span>${right ? `<span class="sub">${esc(right)}</span>` : ""}`;
  if (id) d.onclick = () => Graph.focus(id);
  return d;
}

function renderCard(c) {
  const el = document.createElement("div"); el.className = "card" + (c.kind === "error" || c.kind === "notice" ? " error" : "");
  el.innerHTML = `<div class="k">${esc(c.kind)} · ${esc(c.title || "")}</div>`;
  const ids = [];
  if (c.kind === "search") {
    if (!c.hits.length) el.append(row("No matching file.", ""));
    c.hits.forEach(h => { ids.push(h.id); el.append(row(h.title, h.id.split("/")[0], h.id));
      const s = document.createElement("div"); s.className = "snip"; s.textContent = h.snippet; el.append(s); });
  } else if (c.kind === "inbox") {
    c.mails.forEach(m => { el.append(row(`${m.unread ? "● " : ""}${m.from} — ${m.subject}`, m.known ? "in files" : "new", m.known)); if (m.known) ids.push(m.known); });
  } else if (c.kind === "brief") {
    c.today.forEach(e => el.append(row(e.title, e.time)));
    c.slipped.forEach(e => el.append(row("Slipped: " + e.title, e.date)));
    c.unread.forEach(m => el.append(row("● " + m.subject, m.from)));
    (c.errors || []).forEach(x => el.append(row("Unavailable — " + x, "")));
  } else if (c.kind === "plan") {
    c.items.forEach((it, i) => el.append(row(`${i + 1}. ${it.task}`, it.why)));
  } else if (c.kind === "web") {
    const p = document.createElement("div"); p.className = "snip"; p.textContent = c.text; el.append(p);
    c.sources.forEach(s => el.append(row(s.title, new URL(s.url).hostname)));
  } else if (c.kind === "memory") {
    el.append(row(c.text, c.file));
  } else if (c.kind === "facts") {
    if (!c.facts.length) el.append(row("Memory is empty.", ""));
    c.facts.forEach(f => el.append(row(f.fact, f.file)));
  } else {
    el.append(row(c.text || "", ""));
  }
  return { el, ids };
}

function showReply(res) {
  $("reply").hidden = false; $("say").textContent = res.say || "";
  const box = $("cards"); box.innerHTML = ""; let ids = [];
  (res.cards || []).forEach(c => { const r = renderCard(c); box.append(r.el); ids = ids.concat(r.ids); });
  Graph.highlight(ids);
  setModelBadge(res.model, res.error);
}

function setModelBadge(ok, err) {
  const b = $("modelBadge"); b.textContent = ok ? "MODEL ONLINE" : "MODEL MISSING"; b.classList.toggle("warn", !ok);
  if (err) toast("Model unavailable: " + err.slice(0, 160));
}

let busy = false;
async function send(text) {
  text = text.trim(); if (!text || busy) return;
  busy = true; reactor("thinking"); $("caption").textContent = text; $("q").value = "";
  try {
    const r = await fetch("/api/ask", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ text }) });
    if (!r.ok) throw new Error("server " + r.status);
    const res = await r.json(); showReply(res);
    if (window.Jarvis.onReply) await window.Jarvis.onReply(res);
  } catch (e) { toast("Jarvis didn't answer: " + e.message); }
  busy = false; reactor(V.on ? "listening" : "idle");
}
window.Jarvis.send = send;

$("ask").addEventListener("submit", (e) => { e.preventDefault(); send($("q").value); });
$("brief").onclick = () => send("Brief me.");
$("plan").onclick = () => send("Plan my day.");
$("memory").onclick = async () => {
  try { showReply({ say: "Here's what I remember, sir.", cards: [{ kind: "facts", title: "memory/", facts: await getJSON("/api/memory") }], model: true }); }
  catch (e) { toast("Couldn't read memory: " + e.message); }
};
fetch("/api/status").then(r => r.json()).then(s => setModelBadge(s.model)).catch(() => {});


// ---------------- voice (ElevenLabs via our server; the key never reaches the browser) ----------------
const V = { stream: null, ctx: null, analyser: null, buf: null, rec: null, chunks: [], on: false,
  speaking: false, audio: null, speechStart: 0, lastLoud: 0, turnStart: 0, muted: false, timer: null };
try { V.muted = localStorage.getItem("jarvis-muted") === "1"; } catch (e) {}
const bars = [...document.querySelectorAll("#bars i")];
const caption = (t) => { $("caption").textContent = t; };

function setMuteUI() { $("mute").setAttribute("aria-pressed", String(V.muted)); $("mute").textContent = V.muted ? "MUTED" : "MUTE"; }
setMuteUI();

function pickMime() {
  for (const m of ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg;codecs=opus"])
    if (window.MediaRecorder && MediaRecorder.isTypeSupported(m)) return m;
  return "";
}

async function micOn() {
  if (!navigator.mediaDevices || !window.MediaRecorder) {
    toast("This browser can't record audio (no MediaRecorder). Type instead."); return;
  }
  try {
    V.stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
  } catch (e) {
    const why = e.name === "NotAllowedError" ? "Microphone blocked. Allow it in the browser's site settings, then press MIC again."
      : e.name === "NotFoundError" ? "No microphone found." : "Microphone error: " + e.message;
    toast(why); caption(why); return;
  }
  V.ctx = new (window.AudioContext || window.webkitAudioContext)();
  const src = V.ctx.createMediaStreamSource(V.stream);
  V.analyser = V.ctx.createAnalyser(); V.analyser.fftSize = 1024; src.connect(V.analyser);
  V.buf = new Float32Array(V.analyser.fftSize);
  V.on = true; $("mic").setAttribute("aria-pressed", "true");
  V.timer = setInterval(poll, LEVEL_POLL_MS);
  startTurn();
}

function micOff() {
  V.on = false; $("mic").setAttribute("aria-pressed", "false");
  clearInterval(V.timer);
  if (V.rec && V.rec.state !== "inactive") { V.rec.onstop = null; V.rec.stop(); }
  V.stream && V.stream.getTracks().forEach(t => t.stop());
  V.ctx && V.ctx.close();
  V.stream = V.ctx = V.rec = null;
  bars.forEach(b => (b.style.height = "10%"));
  if (!V.speaking) { reactor("idle"); caption(""); }
}

function startTurn() {
  if (!V.on || V.speaking || (V.rec && V.rec.state === "recording")) return;
  V.chunks = []; V.speechStart = 0; V.lastLoud = 0; V.turnStart = performance.now();
  const mime = pickMime();
  V.rec = new MediaRecorder(V.stream, mime ? { mimeType: mime } : undefined);
  V.rec.ondataavailable = (e) => e.data.size && V.chunks.push(e.data);
  V.rec.onstop = endTurn;
  V.rec.start(250);
  reactor("listening"); caption("Listening…");
}

function level() {
  V.analyser.getFloatTimeDomainData(V.buf);
  let s = 0; for (const x of V.buf) s += x * x;
  return Math.sqrt(s / V.buf.length);
}

function poll() {
  if (!V.analyser) return;
  const lv = level(), now = performance.now();
  bars.forEach((b, i) => (b.style.height = Math.min(100, 10 + lv * 900 * (0.6 + 0.4 * Math.sin(now / 90 + i * 1.618))) + "%"));
  if (V.speaking || !V.rec || V.rec.state !== "recording") return;   // deaf while Jarvis talks
  if (lv > SPEECH_LEVEL) {
    if (!V.speechStart) V.speechStart = now;
    V.lastLoud = now; caption("● hearing you…");
  }
  const spoke = V.speechStart && V.lastLoud - V.speechStart > MIN_SPEECH_MS;
  if ((spoke && now - V.lastLoud > SILENCE_MS) || now - V.turnStart > MAX_TURN_MS) V.rec.stop();
  else if (!V.speechStart && now - V.turnStart > 8000) { V.rec.onstop = null; V.rec.stop(); startTurn(); } // keep buffers small while quiet
}

async function endTurn() {
  const spoke = V.speechStart && V.lastLoud - V.speechStart > MIN_SPEECH_MS;
  if (!spoke) return startTurn();
  const blob = new Blob(V.chunks, { type: V.rec.mimeType || "audio/webm" });
  reactor("thinking"); caption("Transcribing…");
  let text = "";
  try {
    const r = await fetch("/api/listen", { method: "POST", headers: { "content-type": blob.type }, body: blob });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || r.status);
    text = j.text;
  } catch (e) { toast("Transcriber unavailable: " + e.message); caption(""); return startTurn(); }
  if (!text) { caption("Didn't catch that."); return startTurn(); }
  caption("“" + text + "”");
  await send(text);          // send() speaks the reply via onReply, which restarts listening
  startTurn();
}

async function speak(text) {
  if (V.muted || !text) return;
  V.speaking = true; reactor("speaking");
  if (V.rec && V.rec.state === "recording") { V.rec.onstop = null; V.rec.stop(); }
  try {
    const r = await fetch("/api/speak", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ text }) });
    if (!r.ok) { const j = await r.json().catch(() => ({})); throw new Error(j.error || r.status); }
    const url = URL.createObjectURL(await r.blob());
    V.audio = new Audio(url);
    await new Promise((res) => { V.audio.onended = V.audio.onerror = V.audio.onpause = res; V.audio.play().catch(res); });
    URL.revokeObjectURL(url);
  } catch (e) { toast("Voice output unavailable: " + e.message); }
  V.audio = null; V.speaking = false;
  reactor(V.on ? "listening" : "idle");
  startTurn();
}

function bargeIn() { if (V.audio) V.audio.pause(); }   // stop talking now; listening resumes

window.Jarvis.onReply = (res) => speak(res.say);
$("mic").onclick = () => (V.on ? micOff() : micOn());
$("mute").onclick = () => { V.muted = !V.muted; try { localStorage.setItem("jarvis-muted", V.muted ? "1" : "0"); } catch (e) {} if (V.muted) bargeIn(); setMuteUI(); };
addEventListener("keydown", (e) => {
  if (e.target === $("q")) { if (e.key === "Escape") $("q").blur(); return; }
  if (e.code === "Space") { e.preventDefault(); if (V.speaking) bargeIn(); else (V.on ? micOff() : micOn()); }
  if (e.key === "Escape") { bargeIn(); if (V.on) micOff(); }
});
fetch("/api/status").then(r => r.json()).then(s => { if (!s.voice) { $("mic").title = "Voice offline: set ELEVENLABS_API_KEY"; toast("Voice is offline: no ELEVENLABS_API_KEY in .env. Text still works."); } }).catch(() => {});
