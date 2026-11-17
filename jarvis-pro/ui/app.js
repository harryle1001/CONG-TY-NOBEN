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

$("ask").addEventListener("submit", (e) => { e.preventDefault(); toast("Conversation arrives in step 3."); });
["mic", "mute", "brief", "plan", "memory"].forEach(id => $(id).addEventListener("click", () => toast(`${id.toUpperCase()} arrives in a later step.`)));
