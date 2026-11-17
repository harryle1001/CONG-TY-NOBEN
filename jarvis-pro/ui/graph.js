// Canvas force graph. Grid-bucketed repulsion with a distance cutoff -> near-linear per tick.
"use strict";
const PHI = 1.61803;
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));
const REPULSE_CUTOFF = 160;       // world units; also the grid cell size
const PULSE_EVERY_MS = 2618;      // idle pulse along a random link
const PULSE_MS = 1618;
const ALPHA_FLOOR = 0.012;        // never fully stops: the graph keeps breathing
const DIM = 0.1;                  // opacity of everything not lit on hover/focus

const TYPE_COLORS = {
  product: "#57c7ff", "know-how": "#4fe0b0", client: "#ff7eb6", ai: "#c39bff", game: "#ffb86b",
  pricing: "#ffd76b", report: "#ff8a8a", web: "#8b9cff", sheet: "#7ee787", pdf: "#f0a6ff",
  note: "#9aa8ba", folder: "#435064",
};
const colorOf = t => TYPE_COLORS[t] || "#9aa8ba";

class Graph {
  constructor(canvas, data, hooks = {}) {
    this.c = canvas; this.ctx = canvas.getContext("2d"); this.hooks = hooks;
    this.view = { x: 0, y: 0, k: 1 };
    this.hidden = new Set(); this.hover = null; this.focus = null; this.path = [];
    this.match = null; this.pulses = []; this.alpha = 1; this.lastPulse = 0;
    this.load(data);
    this.resize(); addEventListener("resize", () => this.resize());
    this.bind();
    requestAnimationFrame(t => this.frame(t));
  }

  load({ nodes, edges }) {
    const order = [...nodes].sort((a, b) => b.degree - a.degree);
    this.nodes = order.map((n, i) => {
      const r = Math.sqrt(i + 0.5) * 22;              // phyllotaxis seed: hubs start in the centre
      return { ...n, x: Math.cos(i * GOLDEN_ANGLE) * r, y: Math.sin(i * GOLDEN_ANGLE) * r, vx: 0, vy: 0,
               r: 3 + Math.sqrt(n.degree) * PHI };
    });
    this.byId = new Map(this.nodes.map(n => [n.id, n]));
    this.edges = edges.map(([a, b]) => [this.byId.get(a), this.byId.get(b)]).filter(([a, b]) => a && b);
    this.adj = new Map(this.nodes.map(n => [n, new Set()]));
    for (const [a, b] of this.edges) { this.adj.get(a).add(b); this.adj.get(b).add(a); }
    const pre = Math.min(300, Math.ceil(240000 / Math.max(1, this.nodes.length)));
    for (let i = 0; i < pre; i++) this.tick();          // settle before first paint (capped for big graphs)
    this.alpha = 0.3;
    this.fit();
  }

  // ---------- physics ----------
  tick() {
    const N = this.nodes, a = this.alpha, C = REPULSE_CUTOFF, grid = new Map();
    for (const n of N) {
      const key = ((n.x / C) | 0) + "," + ((n.y / C) | 0);
      (grid.get(key) || grid.set(key, []).get(key)).push(n);
    }
    for (const n of N) {
      const gx = (n.x / C) | 0, gy = (n.y / C) | 0;
      for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) {
        const cell = grid.get((gx + dx) + "," + (gy + dy)); if (!cell) continue;
        for (const m of cell) {
          if (m === n) continue;
          let x = n.x - m.x, y = n.y - m.y, d2 = x * x + y * y;
          if (d2 > C * C) continue;
          if (d2 < 1) { x = Math.random() - .5; y = Math.random() - .5; d2 = 1; }
          const f = (900 * a) / d2;
          n.vx += x * f; n.vy += y * f;
        }
      }
    }
    for (const [s, t] of this.edges) {
      const x = t.x - s.x, y = t.y - s.y, d = Math.sqrt(x * x + y * y) || 1;
      const L = 26 + (s.r + t.r) * PHI;
      const k = ((d - L) / d) * 0.06 * a / Math.min(this.adj.get(s).size, this.adj.get(t).size);
      s.vx += x * k; s.vy += y * k; t.vx -= x * k; t.vy -= y * k;
    }
    let mv = 0;
    for (const n of N) {
      n.vx -= n.x * 0.004 * a; n.vy -= n.y * 0.004 * a;
      if (n.fixed) { n.vx = n.vy = 0; continue; }
      n.vx *= 0.6; n.vy *= 0.6;
      n.x += n.vx; n.y += n.vy;
      mv = Math.max(mv, Math.abs(n.vx) + Math.abs(n.vy));
    }
    this.drift = (this.drift || 0) + mv;       // world units moved since the edge layer was drawn
    this.alpha = Math.max(ALPHA_FLOOR, this.alpha * 0.97);
  }
  heat(v = 0.3) { this.alpha = Math.max(this.alpha, v); }

  // ---------- view ----------
  resize() {
    const d = this.dpr = Math.min(devicePixelRatio || 1, 2);
    this.w = innerWidth; this.h = innerHeight;
    this.c.width = this.w * d; this.c.height = this.h * d;
    this.layer = null;
  }
  fit() {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const n of this.nodes) { x0 = Math.min(x0, n.x); y0 = Math.min(y0, n.y); x1 = Math.max(x1, n.x); y1 = Math.max(y1, n.y); }
    const w = innerWidth, h = innerHeight;
    const k = Math.max(0.1, Math.min(2.4, 0.8 * Math.min(w / (x1 - x0 + 80), h / (y1 - y0 + 80))));
    this.view = { k, x: w / 2 - (x0 + x1) / 2 * k, y: h / 2 - (y0 + y1) / 2 * k };
  }
  toWorld(sx, sy) { return [(sx - this.view.x) / this.view.k, (sy - this.view.y) / this.view.k]; }
  visible(n) { return !this.hidden.has(n.type); }
  hit(sx, sy) {
    const [x, y] = this.toWorld(sx, sy), pad = 6 / this.view.k;
    let best = null, bd = Infinity;
    for (const n of this.nodes) {
      if (!this.visible(n)) continue;
      const d = Math.hypot(n.x - x, n.y - y);
      if (d < n.r + pad && d < bd) { best = n; bd = d; }
    }
    return best;
  }
  centerOn(n) {
    const k = Math.max(this.view.k, 1.2);
    this.anim = { from: { ...this.view }, to: { k, x: this.w * 0.5 - n.x * k, y: this.h * 0.5 - n.y * k }, t0: performance.now(), dur: 424 };
  }

  // ---------- selection ----------
  setFocus(n) {
    this.focus = n; this.path = [];
    if (n) this.centerOn(n);
    this.hooks.onFocus && this.hooks.onFocus(n, []);
  }
  tracePath(a, b) {
    const prev = new Map([[a, null]]), q = [a];
    while (q.length) {
      const x = q.shift(); if (x === b) break;
      for (const y of this.adj.get(x)) if (!prev.has(y) && this.visible(y)) { prev.set(y, x); q.push(y); }
    }
    if (!prev.has(b)) return [];
    const out = [b]; while (prev.get(out[0])) out.unshift(prev.get(out[0]));
    return out;
  }
  lit() {  // set of nodes in full colour, or null for "everything"
    if (this.path.length) return new Set(this.path);
    const n = this.hover || this.focus;
    if (n) return new Set([n, ...this.adj.get(n)]);
    if (this.match) return this.match;
    return null;
  }

  // ---------- input ----------
  bind() {
    const c = this.c, pts = new Map();
    let down = null, pinch = null;
    c.addEventListener("pointerdown", e => {
      c.setPointerCapture(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]);
      if (pts.size === 2) {
        const [p, q] = [...pts.values()];
        pinch = { d: Math.hypot(p[0] - q[0], p[1] - q[1]), k: this.view.k, cx: (p[0] + q[0]) / 2, cy: (p[1] + q[1]) / 2 };
        down = null; return;
      }
      const n = this.hit(e.clientX, e.clientY);
      down = { x: e.clientX, y: e.clientY, vx: this.view.x, vy: this.view.y, node: n, moved: false, shift: e.shiftKey };
      if (n) n.fixed = true;
      c.classList.add("dragging");
    });
    c.addEventListener("pointermove", e => {
      if (pts.has(e.pointerId)) pts.set(e.pointerId, [e.clientX, e.clientY]);
      if (pinch && pts.size === 2) {
        const [p, q] = [...pts.values()], d = Math.hypot(p[0] - q[0], p[1] - q[1]);
        this.zoomAt(pinch.cx, pinch.cy, (pinch.k * d / pinch.d) / this.view.k); return;
      }
      if (!down) {
        const h = this.hit(e.clientX, e.clientY);
        if (h !== this.hover) { this.hover = h; c.classList.toggle("hovering", !!h); }
        return;
      }
      const dx = e.clientX - down.x, dy = e.clientY - down.y;
      if (Math.hypot(dx, dy) > 4) down.moved = true;
      if (!down.moved) return;
      if (down.node) {
        const [x, y] = this.toWorld(e.clientX, e.clientY);
        down.node.x = x; down.node.y = y; this.heat(0.2);
      } else { this.view.x = down.vx + dx; this.view.y = down.vy + dy; }
    });
    const up = e => {
      pts.delete(e.pointerId); if (pts.size < 2) pinch = null;
      c.classList.remove("dragging");
      if (!down) return;
      const d = down; down = null;
      if (d.node) d.node.fixed = false;
      if (d.moved) return;
      if (!d.node) { this.focus = null; this.path = []; this.hooks.onFocus && this.hooks.onFocus(null, []); return; }
      if ((d.shift || e.shiftKey) && this.focus && this.focus !== d.node) {
        this.path = this.tracePath(this.focus, d.node);
        this.hooks.onFocus && this.hooks.onFocus(this.focus, this.path);
      } else this.setFocus(d.node);
    };
    c.addEventListener("pointerup", up);
    c.addEventListener("pointercancel", up);
    c.addEventListener("pointerleave", () => { if (!down) this.hover = null; });
    c.addEventListener("wheel", e => {
      e.preventDefault();
      this.zoomAt(e.clientX, e.clientY, Math.exp(-e.deltaY * 0.0016));
    }, { passive: false });
    c.addEventListener("dblclick", () => this.fit());
  }
  zoomAt(sx, sy, f) {
    const k = Math.max(0.08, Math.min(this.view.k * f, 6)); f = k / this.view.k;
    this.view.x = sx - (sx - this.view.x) * f; this.view.y = sy - (sy - this.view.y) * f; this.view.k = k;
  }

  // ---------- render ----------
  frame(t) {
    this.tick();
    if (this.anim) {
      const a = this.anim, p = Math.min(1, (t - a.t0) / a.dur), e = 1 - Math.pow(1 - p, 3);
      for (const k of ["x", "y", "k"]) this.view[k] = a.from[k] + (a.to[k] - a.from[k]) * e;
      if (p >= 1) this.anim = null;
    }
    if (t - this.lastPulse > PULSE_EVERY_MS && this.edges.length) {
      this.lastPulse = t;
      const vis = this.edges.filter(([a, b]) => this.visible(a) && this.visible(b));
      if (vis.length) this.pulses.push({ e: vis[(Math.random() * vis.length) | 0], t0: t });
    }
    this.draw(t);
    requestAnimationFrame(tt => this.frame(tt));
  }

  draw(t) {
    const g = this.ctx, v = this.view, lit = this.lit();
    g.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    g.clearRect(0, 0, this.w, this.h);
    g.translate(v.x, v.y); g.scale(v.k, v.k);
    const lw = 1 / v.k;
    // edges: the dim layer is the expensive part (thousands of strokes), so it is cached in an offscreen
    // canvas and only redrawn when the layout really moved, the view settled, or the highlight changed.
    const litEdges = [];
    for (const e of this.edges) if (lit && lit.has(e[0]) && lit.has(e[1]) && this.visible(e[0]) && this.visible(e[1])) litEdges.push(e);
    this.drawEdgeLayer(lit, t);
    if (litEdges.length) {
      const onPath = this.path.length ? new Set(this.path.slice(1).map((n, i) => [this.path[i], n])) : null;
      g.strokeStyle = "rgba(111,227,255,.55)"; g.lineWidth = 1.4 * lw; g.beginPath();
      for (const [a, b] of litEdges) { g.moveTo(a.x, a.y); g.lineTo(b.x, b.y); }
      g.stroke();
      if (onPath) {
        g.strokeStyle = "#6fe3ff"; g.lineWidth = 2.6 * lw; g.beginPath();
        for (let i = 1; i < this.path.length; i++) { g.moveTo(this.path[i - 1].x, this.path[i - 1].y); g.lineTo(this.path[i].x, this.path[i].y); }
        g.stroke();
      }
    }
    // pulses
    this.pulses = this.pulses.filter(p => t - p.t0 < PULSE_MS);
    for (const p of this.pulses) {
      const [a, b] = p.e, s = (t - p.t0) / PULSE_MS, x = a.x + (b.x - a.x) * s, y = a.y + (b.y - a.y) * s;
      const fade = Math.sin(Math.PI * s);
      g.fillStyle = `rgba(111,227,255,${0.8 * fade})`;
      g.beginPath(); g.arc(x, y, 2.6 * lw * 1.6, 0, 7); g.fill();
    }
    // nodes: one path per (colour, dim) batch instead of one fill per node; off-screen nodes skipped
    const [x0, y0] = this.toWorld(-20, -20), [x1, y1] = this.toWorld(this.w + 20, this.h + 20);
    const batches = new Map(), bigs = [];
    for (const n of this.nodes) {
      if (!this.visible(n) || n.x + n.r < x0 || n.x - n.r > x1 || n.y + n.r < y0 || n.y - n.r > y1) continue;
      if (n === this.hover || n === this.focus) { bigs.push(n); continue; }
      const key = (!lit || lit.has(n) ? "1" : "0") + colorOf(n.type);
      (batches.get(key) || batches.set(key, []).get(key)).push(n);
    }
    for (const [key, ns] of [...batches].sort((p, q) => p[0] < q[0] ? -1 : 1)) {   // dim batches first
      g.globalAlpha = key[0] === "1" ? 1 : DIM; g.fillStyle = key.slice(1);
      g.beginPath();
      for (const n of ns) { g.moveTo(n.x + n.r, n.y); g.arc(n.x, n.y, n.r, 0, 7); }
      g.fill();
      if (ns[0].type === "folder") { g.strokeStyle = "rgba(160,180,210,.5)"; g.lineWidth = lw; g.stroke(); }
    }
    g.globalAlpha = 1;
    for (const n of bigs) {
      const r = n.r * 1.382;
      g.fillStyle = "rgba(111,227,255,.14)";
      g.beginPath(); g.arc(n.x, n.y, r + 8 * lw * 2, 0, 7); g.fill();
      g.fillStyle = colorOf(n.type);
      g.beginPath(); g.arc(n.x, n.y, r, 0, 7); g.fill();
      if (n.type === "folder") { g.strokeStyle = "rgba(160,180,210,.5)"; g.lineWidth = lw; g.stroke(); }
    }
    g.globalAlpha = 1;
    this.drawLabels(lit);
  }

  edgeKey(lit) {
    const h = this.hover, f = this.focus;
    return `${h ? h.id : ""}|${f ? f.id : ""}|${this.path.length}|${lit ? lit.size : 0}|${[...this.hidden]}`;
  }
  drawEdgeLayer(lit, t) {
    const v = this.view, d = this.dpr, key = this.edgeKey(lit), L = this.layer;
    const viewMoved = !L || L.v.k !== v.k || L.v.x !== v.x || L.v.y !== v.y;
    if (viewMoved) this.lastView = t;
    const fresh = L && L.key === key && L.match === this.match && this.drift * v.k < PHI;   // edges may trail nodes by < 1.6 px: invisible under the dots
    const g = this.ctx;
    if (fresh && (!viewMoved || t - this.lastView < 162)) {
      // reuse: same pixels, or (while panning/zooming) the old pixels moved by the view change
      const s = v.k / L.v.k;
      g.save(); g.setTransform(1, 0, 0, 1, 0, 0);
      g.drawImage(L.c, (v.x - L.v.x * s) * d, (v.y - L.v.y * s) * d, L.c.width * s, L.c.height * s);
      g.restore();
      return;
    }
    const c = (L && L.c.width === this.c.width && L.c.height === this.c.height) ? L.c : Object.assign(document.createElement("canvas"), { width: this.c.width, height: this.c.height });
    const e = c.getContext("2d");
    e.setTransform(d, 0, 0, d, 0, 0); e.clearRect(0, 0, this.w, this.h);
    e.translate(v.x, v.y); e.scale(v.k, v.k);
    const [x0, y0] = this.toWorld(0, 0), [x1, y1] = this.toWorld(this.w, this.h);
    e.lineWidth = 1 / v.k; e.strokeStyle = `rgba(140,190,240,${lit ? 0.03 : 0.09})`;
    e.beginPath();
    for (const [a, b] of this.edges) {
      if (!this.visible(a) || !this.visible(b)) continue;
      if (lit && lit.has(a) && lit.has(b)) continue;
      if ((a.x < x0 && b.x < x0) || (a.x > x1 && b.x > x1) || (a.y < y0 && b.y < y0) || (a.y > y1 && b.y > y1)) continue;
      e.moveTo(a.x, a.y); e.lineTo(b.x, b.y);
    }
    e.stroke();
    this.layer = { c, key, match: this.match, v: { ...v } };
    this.drift = 0;
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.drawImage(c, 0, 0); g.restore();
  }

  // Most-connected first; skip any label whose box collides with one already placed.
  drawLabels(lit) {
    const g = this.ctx, v = this.view;
    g.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    g.font = "11px ui-sans-serif, system-ui, sans-serif"; g.textBaseline = "middle";
    g.lineWidth = 3; g.lineJoin = "round"; g.strokeStyle = "rgba(5,8,12,.82)";
    const placed = [], max = 80;
    const pri = n => (n === this.focus || n === this.hover ? 1e6 : 0) + (lit && lit.has(n) ? 1e4 : 0) + n.degree;
    const cand = this.nodes.filter(n => this.visible(n) && (!lit || lit.has(n)))
      .sort((a, b) => pri(b) - pri(a));
    for (const n of cand) {
      if (placed.length >= max) break;
      const sx = n.x * v.k + v.x, sy = n.y * v.k + v.y;
      if (sx < -100 || sy < -20 || sx > this.w + 100 || sy > this.h + 20) continue;
      if (!lit && n.r * v.k < 4.2 && placed.length > 12) continue;   // tiny nodes need zoom to earn a label
      const label = n.title.length > 34 ? n.title.slice(0, 33) + "…" : n.title;
      const w = g.measureText(label).width, y = sy;
      let x = sx + n.r * v.k + 5;
      if (x + w > this.w - 10) x = sx - n.r * v.k - 5 - w;           // near the right edge: label on the left
      if (x < 10) continue;
      const box = [x - 2, y - 8, x + w + 2, y + 8];
      if (placed.some(b => box[0] < b[2] && box[2] > b[0] && box[1] < b[3] && box[3] > b[1])) continue;
      placed.push(box);
      const strong = n === this.focus || n === this.hover || (this.path.length && lit.has(n));
      g.strokeText(label, x, y);                          // dark halo: readable over nodes and edges
      g.fillStyle = strong ? "#eaf6ff" : "rgba(200,214,230,.72)";
      g.fillText(label, x, y);
    }
  }
}
