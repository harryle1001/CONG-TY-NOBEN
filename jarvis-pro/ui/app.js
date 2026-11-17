// UI wiring: graph, inspector, hubs, filters, conversation + tool cards. Voice lives in voice.js.
"use strict";
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const norm = s => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/đ/g, "d");
const EXAMPLES = [
  "Sản phẩm nào xử lý khí độc NH3?",
  "What did I promise Trại tôm Sao Biển?",
  "Brief me on today",
  "Giá đại lý Aqua Probio bao nhiêu?",
  "Plan my day",
];
let G;

function fail(msg) { const e = $("#error"); e.textContent = msg; e.hidden = false; }

async function api(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path} → HTTP ${r.status}`);
  return r.json();
}

async function boot() {
  let data;
  try { data = await api("/api/graph"); }
  catch (e) { return fail("Không tải được đồ thị: " + e.message + ". Server đang chạy chưa? (python3 agent/main.py)"); }
  const m = $("#b-mode");
  m.textContent = data.mode === "demo" ? "DEMO DATA" : "REAL DATA";
  m.className = "badge " + (data.mode === "demo" ? "demo" : "warn");
  $("#b-stats").textContent = `${data.nodes.length} nodes · ${data.edges.length} links`;
  G = new Graph($("#graph"), data, { onFocus: inspect });
  renderHubs(); renderFilters(); rotatePlaceholder(); status();
}

async function status() {
  try {
    const s = await api("/api/status");
    setModel(s.model, null);
    const v = $("#b-voice");
    v.textContent = s.voice ? "VOICE" : "VOICE OFF"; v.className = "badge " + (s.voice ? "dim" : "warn");
    v.title = s.voice ? "ElevenLabs connected" : "No ELEVENLABS_API_KEY: text only";
    Voice.init(s.voice);
  } catch (e) { setModel(null, "status: " + e.message); }
}
function setModel(model, error) {
  const b = $("#b-model");
  if (error) { b.textContent = "MODEL ERROR"; b.className = "badge err"; b.title = error; }
  else if (model) { b.textContent = model; b.className = "badge dim"; b.title = "Model connected"; }
  else { b.textContent = "NO MODEL"; b.className = "badge warn"; b.title = "No model: answers come from keyword routing over your files, not from an AI."; }
}

function renderHubs() {
  const top = [...G.nodes].sort((a, b) => b.degree - a.degree).slice(0, 10);
  $("#hubs").innerHTML = top.map(n =>
    `<li data-id="${esc(n.id)}"><span class="dot" style="background:${colorOf(n.type)}"></span><span class="t">${esc(n.title)}</span><span class="n">${n.degree}</span></li>`).join("");
  $("#hubs").onclick = e => { const li = e.target.closest("li"); if (li) G.setFocus(G.byId.get(li.dataset.id)); };
}

function renderFilters() {
  const total = {}, shown = {};
  for (const n of G.nodes) total[n.type] = (total[n.type] || 0) + 1;
  const types = Object.keys(total).sort((a, b) => total[b] - total[a]);
  const lit = G.match;
  for (const n of G.nodes) if (!lit || lit.has(n)) shown[n.type] = (shown[n.type] || 0) + 1;
  $("#filters").innerHTML = types.map(t =>
    `<li data-t="${t}" class="${G.hidden.has(t) ? "off" : ""}"><span class="dot" style="background:${colorOf(t)}"></span><span class="t">${t}</span><span class="n">${lit ? (shown[t] || 0) + "/" : ""}${total[t]}</span></li>`).join("");
  $("#filters").onclick = e => {
    const li = e.target.closest("li"); if (!li) return;
    const t = li.dataset.t; G.hidden.has(t) ? G.hidden.delete(t) : G.hidden.add(t);
    if (G.focus && G.hidden.has(G.focus.type)) G.setFocus(null);
    G.heat(0.15); renderFilters();
  };
  $("#f-all").onclick = () => { G.hidden.clear(); renderFilters(); };
}

async function inspect(n, path) {
  const box = $("#insp-body");
  if (!n) { box.className = "empty"; box.textContent = "Bấm một node để xem nội dung. Shift-bấm node thứ hai để tìm đường ngắn nhất."; return; }
  box.className = "";
  let pathHtml = "";
  if (path && path.length) pathHtml = `<div class="path-row">Đường ngắn nhất · ${path.length - 1} bước</div><div class="chips" style="margin-bottom:16px">${path.map(chip).join("")}</div>`;
  box.innerHTML = `<div class="insp-title">${esc(n.title)}</div><div class="insp-meta">${esc(n.type)} · ${n.degree} links · ${esc(n.path)}</div>${pathHtml}<div class="insp-text">…</div>`;
  try {
    const d = await api("/api/note?id=" + encodeURIComponent(n.id));
    if (G.focus !== n) return;
    const text = d.text ? d.text.slice(0, 1600) + (d.text.length > 1600 ? " …" : "") : (n.type === "folder" ? "Thư mục." : "(không có chữ)");
    box.querySelector(".insp-text").textContent = text;
    box.insertAdjacentHTML("beforeend", `<h2>LINKS</h2><div class="chips">${d.links.map(id => chip(G.byId.get(id))).join("")}</div>`);
  } catch (e) { box.querySelector(".insp-text").textContent = "Lỗi tải ghi chú: " + e.message; }
  box.onclick = e => { const c = e.target.closest(".chip"); if (c) G.setFocus(G.byId.get(c.dataset.id)); };
}
function chip(n) { return n ? `<button class="chip" data-id="${esc(n.id)}" ><span class="dot" style="background:${colorOf(n.type)};display:inline-block;width:6px;height:6px;margin-right:6px;vertical-align:middle"></span>${esc(n.title)}</button>` : ""; }

// ---------- conversation ----------
let SESSION = "s" + Math.random().toString(36).slice(2);
try { SESSION = sessionStorage.getItem("jarvis-session") || SESSION; sessionStorage.setItem("jarvis-session", SESSION); } catch (e) {}

function rotatePlaceholder() {
  const a = $("#ask"); let i = 0;
  const set = () => { a.placeholder = EXAMPLES[i++ % EXAMPLES.length]; };
  set(); setInterval(() => { if (!a.value) set(); }, 4236);
}
function setState(s) {
  $("#reactor").className = "reactor " + s;
  $("#state").textContent = s.toUpperCase();
}
async function post(path, body) {
  const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  if (!r.ok) throw new Error(`${path} → HTTP ${r.status}`);
  return r.json();
}
// One round trip: think, show the card, speak the line, then hand the mic back if a voice conversation is running.
async function run(label, path, body) {
  if (Voice.state === "speaking") Voice.bargeIn();
  const wasOn = Voice.on;
  if (wasOn) Voice.discard();          // a typed question while listening: drop the half-recorded turn
  Voice.set("thinking"); $("#error").hidden = true;
  showReply(label, null, []);
  try {
    const d = await post(path, body);
    if (d.model_error) setModel(null, d.model_error);
    else if (path === "/api/ask") setModel(d.model, null);
    showReply(label, d, d.cards || []);
    await Voice.say(d.say);
  } catch (e) { fail("Jarvis không trả lời: " + e.message); $("#reply").hidden = true; }
  if (Voice.on) Voice.listen(); else Voice.set("idle");
}
const ask = text => run(text, "/api/ask", { text, session: SESSION });
function showReply(q, d, cards) {
  const box = $("#reply"); box.hidden = false;
  const who = d ? (d.model ? "" : `<span class="tag">${d.model_error ? "MODEL ERROR · " : ""}NO MODEL · keyword routing</span>`) : "";
  const say = d ? esc(d.say) : '<span class="dots">…</span>';
  box.innerHTML = `<button class="close" aria-label="Đóng">×</button><div class="q">${esc(q)}</div><div class="say">${say} ${who}</div>` +
    cards.map(c => `<div class="card"><h2>${esc(c.title)}</h2>${(c.items || []).map(it =>
      `<div class="item${it.id ? " link-node" : ""}" ${it.id ? `data-id="${esc(it.id)}"` : ""}>${it.url ? `<a href="${esc(it.url)}" target="_blank" rel="noopener noreferrer">${esc(it.title)}</a>` : `<b>${esc(it.title)}</b>`}<span>${esc(it.sub || "")}</span></div>`).join("")}${c.note ? `<p class="note">${esc(c.note)}</p>` : ""}</div>`).join("");
  const ids = cards.flatMap(c => (c.items || []).map(i => i.id)).filter(id => id && G.byId.has(id));
  G.match = ids.length ? new Set(ids.map(id => G.byId.get(id))) : null;
  renderFilters();
}
$("#reply").addEventListener("click", e => {
  if (e.target.closest(".close")) { $("#reply").hidden = true; G.match = null; renderFilters(); return; }
  const it = e.target.closest(".link-node"); if (it) G.setFocus(G.byId.get(it.dataset.id));
});
$("#ask-form").addEventListener("submit", e => {
  e.preventDefault();
  const q = $("#ask").value.trim(); if (!q || !G) return;
  $("#ask").value = "";
  ask(q);
});
$("#t-brief").onclick = () => run("Brief me", "/api/tool/brief_me");
$("#t-plan").onclick = () => run("Plan my day", "/api/tool/plan_day");
$("#t-inbox").onclick = () => run("Inbox", "/api/tool/read_inbox");
$("#t-memory").onclick = async () => {
  try {
    const d = await api("/api/memory");
    showReply("Memory", { say: d.facts.length ? `${d.facts.length} facts on file, sir.` : "Nothing remembered yet, sir.", model: "-" },
      [{ title: "memory/", items: d.facts.map(f => ({ title: f.fact, sub: f.file })) }]);
  } catch (e) { fail("Không đọc được memory: " + e.message); }
};
addEventListener("keydown", e => {
  if (e.key === "Escape") { $("#ask").value = ""; $("#reply").hidden = true; G.match = null; G.setFocus(null); renderFilters(); $("#error").hidden = true; }
  if (e.key === "/" && document.activeElement !== $("#ask")) { e.preventDefault(); $("#ask").focus(); }
});

boot();
