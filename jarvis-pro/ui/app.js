// UI wiring for step 2: graph, inspector, hubs, filters, find-in-graph. No voice / model yet.
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
  renderHubs(); renderFilters(); rotatePlaceholder();
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

// Ask bar (step 2): find-in-graph only. Conversation arrives in step 3.
function rotatePlaceholder() {
  const a = $("#ask"); let i = 0;
  const set = () => { a.placeholder = EXAMPLES[i++ % EXAMPLES.length] + "   — tìm trong đồ thị"; };
  set(); setInterval(() => { if (!a.value) set(); }, 4236);
}
$("#ask").addEventListener("input", e => {
  const q = norm(e.target.value.trim());
  G.match = q.length < 2 ? null : new Set(G.nodes.filter(n => norm(n.title + " " + n.path).includes(q)));
  renderFilters();
});
$("#ask-form").addEventListener("submit", async e => {
  e.preventDefault();
  const q = $("#ask").value.trim(); if (!q || !G) return;
  let best = G.match && [...G.match].sort((a, b) => b.degree - a.degree)[0];
  if (!best) {
    try { const r = await api("/api/search?q=" + encodeURIComponent(q)); best = r.results[0] && G.byId.get(r.results[0].id); }
    catch (err) { return fail("Tìm kiếm lỗi: " + err.message); }
  }
  if (best) G.setFocus(best); else fail("Không có tài liệu nào khớp: " + q);
});
addEventListener("keydown", e => {
  if (e.key === "Escape") { $("#ask").value = ""; G.match = null; G.setFocus(null); renderFilters(); $("#error").hidden = true; }
  if (e.key === "/" && document.activeElement !== $("#ask")) { e.preventDefault(); $("#ask").focus(); }
});

boot();
