// Force-directed knowledge graph on canvas. Grid-bucketed repulsion keeps cost ~linear.
(() => {
  const PHI = 1.61803;
  const REPEL_CUTOFF = 110;          // px in world space; beyond this nodes ignore each other
  const PULSE_EVERY_MS = 2618;       // idle pulse travels a random link
  const COLORS = { product:"#6fd3ff", "know-how":"#7be3b5", web:"#a99cff", folder:"#4a5b6c", note:"#c7d3de",
    game:"#ffb35c", ai:"#ff7fae", client:"#ffd36f", report:"#8fb8ff", pricing:"#f2f27a", sheet:"#86c5c9", pdf:"#d9a6ff" };
  const cv = document.getElementById("graph"), ctx = cv.getContext("2d");
  let W = 0, H = 0, DPR = 1;
  let nodes = [], edges = [], byId = new Map(), adj = new Map();
  let view = { x: 0, y: 0, k: 1 }, alpha = 1;
  let hover = null, focus = null, pathSet = null, hidden = new Set();
  let drag = null, pan = null, moved = false, pulse = null;
  const api = { onSelect: () => {}, colors: COLORS };

  function resize() {
    DPR = Math.min(2, devicePixelRatio || 1);
    W = cv.clientWidth; H = cv.clientHeight;
    cv.width = W * DPR; cv.height = H * DPR;
  }
  addEventListener("resize", resize); resize();

  api.load = (g) => {
    nodes = g.nodes.map((n, i) => {
      const a = i * 2.39996, r = 10 * Math.sqrt(i);            // golden-angle spiral start
      return { ...n, x: Math.cos(a) * r, y: Math.sin(a) * r, vx: 0, vy: 0, r: 3 + Math.sqrt(n.degree) * PHI };
    });
    byId = new Map(nodes.map(n => [n.id, n]));
    edges = g.edges.map(([a, b]) => [byId.get(a), byId.get(b)]).filter(e => e[0] && e[1]);
    adj = new Map(nodes.map(n => [n, new Set()]));
    edges.forEach(([a, b]) => { adj.get(a).add(b); adj.get(b).add(a); });
    alpha = 1;
  };

  const visible = n => !hidden.has(n.type);

  function tick() {
    if (alpha < 0.004) alpha = 0.004;           // never fully freeze: keeps breathing
    const cell = REPEL_CUTOFF, grid = new Map();
    for (const n of nodes) {
      if (!visible(n)) continue;
      const key = Math.floor(n.x / cell) + "," + Math.floor(n.y / cell);
      (grid.get(key) || grid.set(key, []).get(key)).push(n);
    }
    for (const n of nodes) {
      if (!visible(n)) continue;
      const gx = Math.floor(n.x / cell), gy = Math.floor(n.y / cell);
      for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) {
        const b = grid.get((gx + dx) + "," + (gy + dy)); if (!b) continue;
        for (const m of b) {
          if (m === n) continue;
          let x = n.x - m.x, y = n.y - m.y, d2 = x * x + y * y || 0.01;
          if (d2 > cell * cell) continue;
          const f = 900 * alpha / d2; n.vx += x * f; n.vy += y * f;
        }
      }
      n.vx -= n.x * 0.002 * alpha; n.vy -= n.y * 0.002 * alpha;   // gentle gravity
    }
    for (const [a, b] of edges) {
      if (!visible(a) || !visible(b)) continue;
      const x = b.x - a.x, y = b.y - a.y, d = Math.hypot(x, y) || 1;
      const f = (d - 42) / d * 0.04 * alpha;
      a.vx += x * f; a.vy += y * f; b.vx -= x * f; b.vy -= y * f;
    }
    const t = performance.now() / 1000;
    for (const n of nodes) {
      if (n === drag) { n.vx = n.vy = 0; continue; }
      n.vx += Math.sin(t * 0.618 + n.r) * 0.003;                 // breathing drift
      n.vx *= 0.62; n.vy *= 0.62;
      n.x += n.vx; n.y += n.vy;
    }
    alpha *= 0.985;
  }

  const toScreen = (n) => [(n.x * view.k + view.x) + W / 2, (n.y * view.k + view.y) + H / 2];
  const toWorld = (sx, sy) => [((sx - W / 2) - view.x) / view.k, ((sy - H / 2) - view.y) / view.k];

  function lit(n) {
    if (pathSet) return pathSet.has(n);
    const c = hover || focus; if (!c) return true;
    return n === c || adj.get(c).has(n);
  }

  function draw() {
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const dim = !!(hover || focus || pathSet);
    ctx.lineWidth = 1;
    for (const [a, b] of edges) {
      if (!visible(a) || !visible(b)) continue;
      const on = pathSet ? pathSet.has(a) && pathSet.has(b) : (lit(a) && lit(b) && (!dim || a === (hover || focus) || b === (hover || focus)));
      ctx.strokeStyle = on && dim ? "rgba(111,211,255,.55)" : dim ? "rgba(140,190,230,.025)" : "rgba(140,190,230,.09)";
      const [x1, y1] = toScreen(a), [x2, y2] = toScreen(b);
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
    }
    if (pulse) {
      const p = Math.min(1, (performance.now() - pulse.t0) / 1618);
      const [x1, y1] = toScreen(pulse.a), [x2, y2] = toScreen(pulse.b);
      ctx.fillStyle = `rgba(111,211,255,${1 - p})`;
      ctx.beginPath(); ctx.arc(x1 + (x2 - x1) * p, y1 + (y2 - y1) * p, 2.6, 0, 7); ctx.fill();
      if (p >= 1) pulse = null;
    }
    const order = nodes.filter(visible).sort((a, b) => a.degree - b.degree);
    for (const n of order) {
      const [x, y] = toScreen(n), on = lit(n);
      const r = n.r * Math.sqrt(view.k) * (n === hover ? PHI : 1);
      ctx.globalAlpha = dim && !on ? 0.1 : 1;
      ctx.fillStyle = COLORS[n.type] || "#999";
      ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill();
      if (n === focus) { ctx.strokeStyle = "#fff"; ctx.lineWidth = 1.5; ctx.stroke(); ctx.lineWidth = 1; }
    }
    ctx.globalAlpha = 1;
    // labels: most-connected first, reject collisions
    const placed = [];
    ctx.font = "11px Inter, system-ui, sans-serif"; ctx.textBaseline = "middle";
    const cand = order.slice().reverse().filter(n => lit(n) || !dim);
    const priority = [hover, focus].filter(Boolean);
    for (const n of [...priority, ...cand]) {
      if (placed.length > 60) break;
      if (!dim && n.degree < 4 && view.k < 1.6) continue;
      const [x, y] = toScreen(n), w = ctx.measureText(n.title).width, r = n.r * Math.sqrt(view.k);
      const box = [x + r + 4, y - 8, w + 4, 16];
      if (box[0] > W || box[0] + box[2] < 0 || y < 0 || y > H) continue;
      if (placed.some(b => b[0] < box[0] + box[2] && box[0] < b[0] + b[2] && b[1] < box[1] + box[3] && box[1] < b[1] + b[3])) continue;
      placed.push(box);
      ctx.fillStyle = n === hover || n === focus ? "#fff" : "rgba(217,230,242,.72)";
      ctx.fillText(n.title.length > 42 ? n.title.slice(0, 40) + "…" : n.title, box[0], y);
    }
  }

  function loop() { tick(); draw(); requestAnimationFrame(loop); }
  requestAnimationFrame(loop);

  setInterval(() => {
    if (hover || focus || !edges.length) return;
    const e = edges[(Math.random() * edges.length) | 0];
    if (visible(e[0]) && visible(e[1])) pulse = { a: e[0], b: e[1], t0: performance.now() };
  }, PULSE_EVERY_MS);

  function pick(sx, sy) {
    const [wx, wy] = toWorld(sx, sy); let best = null, bd = Infinity;
    for (const n of nodes) {
      if (!visible(n)) continue;
      const d = Math.hypot(n.x - wx, n.y - wy);
      if (d < Math.max(n.r + 4 / view.k, 6 / view.k) && d < bd) { bd = d; best = n; }
    }
    return best;
  }

  function bfs(a, b) {
    const prev = new Map([[a, null]]), q = [a];
    while (q.length) {
      const x = q.shift(); if (x === b) break;
      for (const y of adj.get(x)) if (!prev.has(y) && visible(y)) { prev.set(y, x); q.push(y); }
    }
    if (!prev.has(b)) return null;
    const out = [b]; while (prev.get(out[out.length - 1])) out.push(prev.get(out[out.length - 1]));
    return out.reverse();
  }

  cv.addEventListener("pointerdown", (e) => {
    moved = false; const n = pick(e.offsetX, e.offsetY);
    if (n) { drag = n; alpha = Math.max(alpha, 0.3); }
    else pan = { x: e.clientX - view.x, y: e.clientY - view.y };
    cv.setPointerCapture(e.pointerId); cv.classList.add("dragging");
  });
  cv.addEventListener("pointermove", (e) => {
    if (drag) { const [x, y] = toWorld(e.offsetX, e.offsetY); drag.x = x; drag.y = y; moved = true; return; }
    if (pan) { view.x = e.clientX - pan.x; view.y = e.clientY - pan.y; moved = true; return; }
    hover = pick(e.offsetX, e.offsetY); cv.style.cursor = hover ? "pointer" : "grab";
  });
  cv.addEventListener("pointerup", (e) => {
    const n = drag; drag = null; pan = null; cv.classList.remove("dragging");
    if (moved) return;
    const hit = n || pick(e.offsetX, e.offsetY);
    if (!hit) { focus = null; pathSet = null; api.onSelect(null); return; }
    if (e.shiftKey && focus && hit !== focus) {
      const p = bfs(focus, hit);
      pathSet = p ? new Set(p) : null;
      api.onPath && api.onPath(p ? p.map(x => x.id) : null, focus.id, hit.id);
      return;
    }
    pathSet = null; focus = hit; api.onSelect(hit.id);
  });
  cv.addEventListener("pointerleave", () => { hover = null; });
  cv.addEventListener("wheel", (e) => {
    e.preventDefault();
    const k = Math.min(6, Math.max(0.15, view.k * Math.exp(-e.deltaY * 0.0015)));
    const mx = e.offsetX - W / 2, my = e.offsetY - H / 2;
    view.x = mx - (mx - view.x) * (k / view.k); view.y = my - (my - view.y) * (k / view.k); view.k = k;
  }, { passive: false });

  api.focus = (id) => {
    const n = byId.get(id); if (!n) return;
    focus = n; pathSet = null; view.x = -n.x * view.k; view.y = -n.y * view.k; api.onSelect(id);
  };
  api.setHidden = (set) => { hidden = set; alpha = Math.max(alpha, 0.3); };
  api.highlight = (ids) => { pathSet = ids && ids.length ? new Set(ids.map(i => byId.get(i)).filter(Boolean)) : null; };
  window.Graph = api;
})();
