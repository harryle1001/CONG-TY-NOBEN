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
  busy = false; reactor("idle"); $("caption").textContent = "";
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
