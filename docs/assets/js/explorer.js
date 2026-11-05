// The point explorer of a case's Validation page: a scatter of measured against modelled values beside a 3D view of the
// same points. Hover a point in either view and it is marked in both; where the case has the three velocity components, the
// measured and the modelled vector are drawn at the point, with the difference between them. Click pins a point.
//
// It reads what the site serves: assets/explorer/<case>.json (written by scripts/build_api.py: which columns to use), the pairs
// files under api/cases/<case>/pairs/ and the STL geometry. Nothing is computed here that the pairs do not hold.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const LOW = [0x21, 0x66, 0xac], MID = [0xf7, 0xf7, 0xf7], HIGH = [0xb2, 0x18, 0x2b];   // model low | agrees | model high
const HEAVY = 4e6;                                                                      // bytes of STL loaded only on request
const ERROR_COLOUR = "#d62728";
// The page carries the explorer's whole skeleton (docs/_includes/explorer.html) at its final size, with its styles: the script
// fills it and never adds or removes anything that changes its height, so the page does not move under the reader.

const num = (v) => (v === undefined || v === "" || v === "nan" || v === "NaN" ? NaN : Number(v));
const fmt = (v, d = 3) => (Number.isFinite(v) ? (Math.abs(v) >= 1000 || (Math.abs(v) < 0.001 && v !== 0) ? v.toExponential(2) : v.toFixed(d)) : "–");

function parseCSV(text) {
  const lines = text.replace(/\r/g, "").trim().split("\n");
  const head = lines[0].split(",");
  return lines.slice(1).map((l) => {
    const c = l.split(",");
    const o = {};
    head.forEach((h, i) => (o[h] = c[i]));
    return o;
  });
}

function parseSTL(buf) {
  const dv = new DataView(buf);
  const n = buf.byteLength >= 84 ? dv.getUint32(80, true) : 0;
  let pos;
  if (84 + n * 50 === buf.byteLength) {                         // binary
    pos = new Float32Array(n * 9);
    for (let i = 0; i < n; i++) for (let v = 0; v < 3; v++) for (let k = 0; k < 3; k++) pos[i * 9 + v * 3 + k] = dv.getFloat32(84 + i * 50 + 12 + v * 12 + k * 4, true);
  } else {                                                      // ASCII
    const text = new TextDecoder().decode(buf);
    const out = [];
    const re = /vertex\s+(\S+)\s+(\S+)\s+(\S+)/g;
    let m;
    while ((m = re.exec(text))) out.push(+m[1], +m[2], +m[3]);
    pos = new Float32Array(out);
  }
  return pos;
}

const lerp = (a, b, t) => a.map((x, i) => Math.round(x + (b[i] - x) * t));
function diverging(t) {                                         // t in [-1, 1]
  const c = t < 0 ? lerp(MID, LOW, -t) : lerp(MID, HIGH, t);
  return c;
}
const css = (c) => `rgb(${c[0]},${c[1]},${c[2]})`;

function niceTicks(lo, hi, n = 5) {
  const span = hi - lo, step0 = span / n, mag = Math.pow(10, Math.floor(Math.log10(step0)));
  const step = [1, 2, 2.5, 5, 10].map((s) => s * mag).find((s) => s >= step0) || mag * 10;
  const out = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi + 1e-9; t += step) out.push(+t.toPrecision(12));
  return out;
}

async function start(root) {
  const base = root.dataset.base;
  const stamp = new URL(root.dataset.manifest, location.href).search;   // the build's ?v=, so a new release is not read from a cache
  const mf = await (await fetch(root.dataset.manifest)).json();
  if (!mf.views.length) return;
  const ui = root;
  const $ = (s) => ui.querySelector(s);
  const viewSel = $(".ex-view"), groupsEl = $(".ex-groups"), qEl = $(".ex-q"), readout = $(".ex-readout"), geoEl = $(".ex-geo");
  const canvas = $(".ex-scatter"), host3d = $(".ex-3d"), title2d = canvas.parentElement.querySelector(".ex-title");
  $(".ex-title3d").textContent = `${mf.title}: drag to turn, scroll to zoom`;
  mf.views.forEach((v, i) => viewSel.add(new Option(v.label, i)));
  if (mf.views.length === 1) viewSel.parentElement.style.display = "none";
  const textColour = getComputedStyle(root).color;

  // ---- state
  const cache = {};
  let view = mf.views[0], all = [], groupVals = {}, q = 0, items = [], hover = -1, pinned = -1, extent = 1, centre = new THREE.Vector3();
  const sel = () => (hover >= 0 ? hover : pinned);
  let line = null;                                              // the measurement line of the selected point: {axis, idx}
  const AXES = ["x", "y", "z"];
  // The points measured on one line with the selected one: those that share two of its coordinates, at least three of them. A
  // vertical profile (same x and y) is tried first, then a line along x, then along y; a point on a plane only is on no line.
  function lineOf(i) {
    const d = items[i];
    if (!d) return null;
    const tol = extent * 1e-4;
    for (const [axis, fixed] of [[2, [0, 1]], [0, [1, 2]], [1, [0, 2]]]) {
      const idx = [];
      items.forEach((e, j) => { if (fixed.every((k) => Math.abs(e.pos[k] - d.pos[k]) <= tol)) idx.push(j); });
      if (idx.length >= 3) return { axis, idx: idx.sort((a, b) => items[a].pos[axis] - items[b].pos[axis]) };
    }
    return null;
  }

  async function loadView(v) {
    view = v;
    cache[v.id] = cache[v.id] || parseCSV(await (await fetch(base + v.pairs + stamp)).text());
    all = cache[v.id];
    groupVals = {};
    groupsEl.innerHTML = "";
    for (const g of mf.groups) {
      const vals = [...new Set(all.map((r) => r[g]))];
      groupVals[g] = vals[0];
      const s = document.createElement("select");
      vals.forEach((x) => s.add(new Option(x, x)));
      s.onchange = () => { groupVals[g] = s.value; pinned = hover = -1; rebuild(); };
      const l = document.createElement("label");
      l.append(g.replace(/_/g, " ") + " ", s);
      groupsEl.append(l);
    }
    const pts = all.map(position).filter((p) => p.every(Number.isFinite));
    const lo = [0, 1, 2].map((k) => Math.min(...pts.map((p) => p[k]))), hi = [0, 1, 2].map((k) => Math.max(...pts.map((p) => p[k])));
    extent = Math.max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], 1e-9);
    centre.set((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2);
    pinned = hover = -1;
    frame();
    rebuild();
  }
  const position = (r) => mf.coordinates.map((c) => (c ? num(r[c]) : 0));

  function inGroup(r) { return mf.groups.every((g) => r[g] === groupVals[g]); }
  function available() {
    const rows = all.filter(inGroup);
    return mf.quantities.map((qq, i) => (rows.some((r) => Number.isFinite(num(r[qq.meas])) && Number.isFinite(num(r[qq.model]))) ? i : -1)).filter((i) => i >= 0);
  }

  function rebuild() {
    line = null;
    const av = available();
    if (!av.includes(q)) q = av[0] ?? 0;
    qEl.innerHTML = "";
    av.forEach((i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = mf.quantities[i].label;
      b.className = i === q ? "on" : "";
      b.onclick = () => { q = i; pinned = hover = -1; rebuild(); };
      qEl.append(b);
    });
    const Q = mf.quantities[q];
    items = [];
    all.forEach((r) => {
      if (!inGroup(r)) return;
      const m = num(r[Q.meas]), p = num(r[Q.model]), pos = position(r);
      if (Number.isFinite(m) && Number.isFinite(p) && pos.every(Number.isFinite)) items.push({ r, m, p, pos });
    });
    const maxAbs = Math.max(...items.map((d) => Math.abs(d.p - d.m)), 1e-12);
    items.forEach((d) => { d.t = Math.max(-1, Math.min(1, (d.p - d.m) / maxAbs)); d.col = diverging(d.t); });
    title2d.textContent = `${Q.label}: model against measurement (n ${items.length})`;
    drawScatter();
    build3d();
    showReadout();
    loadGeometry();
  }

  // ---- scatter
  const ctx = canvas.getContext("2d");
  let dom = [0, 1], W = 0, Hh = 0;
  const PAD = { l: 46, r: 12, t: 22, b: 36 };
  const sx = (v) => PAD.l + ((v - dom[0]) / (dom[1] - dom[0])) * (W - PAD.l - PAD.r);
  const sy = (v) => Hh - PAD.b - ((v - dom[0]) / (dom[1] - dom[0])) * (Hh - PAD.t - PAD.b);

  function drawScatter() {
    const dpr = window.devicePixelRatio || 1;
    W = canvas.parentElement.clientWidth; Hh = canvas.parentElement.clientHeight;   // the panel's size, never the canvas's own
    canvas.width = W * dpr; canvas.height = Hh * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, Hh);
    ctx.font = "11px sans-serif";
    if (!items.length) return;
    const vals = items.flatMap((d) => [d.m, d.p]);
    let lo = Math.min(...vals), hi = Math.max(...vals);
    const pad = (hi - lo || 1) * 0.06;
    dom = [lo - pad, hi + pad];
    ctx.strokeStyle = "rgba(128,128,128,.3)"; ctx.fillStyle = textColour; ctx.lineWidth = 1;
    for (const t of niceTicks(dom[0], dom[1])) {
      ctx.beginPath(); ctx.moveTo(sx(t), PAD.t); ctx.lineTo(sx(t), Hh - PAD.b); ctx.moveTo(PAD.l, sy(t)); ctx.lineTo(W - PAD.r, sy(t)); ctx.stroke();
      ctx.textAlign = "center"; ctx.fillText(fmt(t, 2).replace(/\.?0+$/, ""), sx(t), Hh - PAD.b + 14);
      ctx.textAlign = "right"; ctx.fillText(fmt(t, 2).replace(/\.?0+$/, ""), PAD.l - 5, sy(t) + 4);
    }
    ctx.textAlign = "center"; ctx.fillText("Measured", (PAD.l + W - PAD.r) / 2, Hh - 6);
    ctx.save(); ctx.translate(11, (PAD.t + Hh - PAD.b) / 2); ctx.rotate(-Math.PI / 2); ctx.fillText("Model", 0, 0); ctx.restore();
    ctx.strokeStyle = textColour; ctx.globalAlpha = 0.6;                       // 1:1
    ctx.beginPath(); ctx.moveTo(sx(dom[0]), sy(dom[0])); ctx.lineTo(sx(dom[1]), sy(dom[1])); ctx.stroke();
    ctx.globalAlpha = 1;
    const onLine = new Set(line ? line.idx : []);
    if (line) {                                                  // the selected point's line, in order along it
      ctx.beginPath();
      line.idx.forEach((j, k) => (k ? ctx.lineTo : ctx.moveTo).call(ctx, sx(items[j].m), sy(items[j].p)));
      ctx.strokeStyle = textColour; ctx.globalAlpha = 0.55; ctx.lineWidth = 1.2; ctx.stroke(); ctx.globalAlpha = 1;
    }
    const order = items.map((_, i) => i).sort((a, b) => onLine.has(a) - onLine.has(b));   // the line's points on top
    order.forEach((i) => {
      const d = items[i], hit = i === sel(), lit = hit || onLine.has(i);
      ctx.globalAlpha = line && !lit ? 0.2 : 1;
      ctx.beginPath(); ctx.arc(sx(d.m), sy(d.p), hit ? 6 : lit ? 4.6 : 3.6, 0, 7);
      ctx.fillStyle = css(d.col); ctx.fill();
      ctx.strokeStyle = lit ? textColour : "rgba(0,0,0,.45)"; ctx.lineWidth = hit ? 2 : lit ? 1.3 : 0.7; ctx.stroke();
    });
    ctx.globalAlpha = 1;
  }
  function nearest2d(ev) {
    const b = canvas.getBoundingClientRect(), x = ev.clientX - b.left, y = ev.clientY - b.top;
    let best = -1, bd = 12 * 12;
    items.forEach((d, i) => { const dd = (sx(d.m) - x) ** 2 + (sy(d.p) - y) ** 2; if (dd < bd) { bd = dd; best = i; } });
    return best;
  }
  canvas.addEventListener("pointermove", (e) => setHover(nearest2d(e)));
  canvas.addEventListener("pointerleave", () => setHover(-1));
  canvas.addEventListener("click", (e) => { const i = nearest2d(e); pinned = i === pinned ? -1 : i; update(); recentre(); });
  function setHover(i) { if (i !== hover) { hover = i; update(); } }
  function update() { line = lineOf(sel()); drawScatter(); selection3d(); showReadout(); dirty = true; }

  // ---- 3D
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  host3d.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.001, 1e6);
  camera.up.set(0, 0, 1);
  scene.add(new THREE.AmbientLight(0xffffff, 0.75));
  const sun = new THREE.DirectionalLight(0xffffff, 0.8); sun.position.set(-1, -2, 3); scene.add(sun);
  const controls = new OrbitControls(camera, renderer.domElement);
  let dirty = true;
  controls.addEventListener("change", () => (dirty = true));
  const dot = (() => {                                        // a round point with a dark rim
    const c = document.createElement("canvas"); c.width = c.height = 64;
    const x = c.getContext("2d");
    x.fillStyle = "#555"; x.beginPath(); x.arc(32, 32, 30, 0, 7); x.fill();
    x.fillStyle = "#fff"; x.beginPath(); x.arc(32, 32, 23, 0, 7); x.fill();
    return new THREE.CanvasTexture(c);
  })();
  const geoGroup = new THREE.Group(), selGroup = new THREE.Group();
  let cloud = null, axes = null;
  scene.add(geoGroup, selGroup);

  function frame() {
    camera.position.copy(centre).add(new THREE.Vector3(-0.9, -1.6, 0.9).multiplyScalar(extent * 1.15));
    controls.target.copy(centre);
    controls.update();
    camera.near = extent / 500; camera.far = extent * 50; camera.updateProjectionMatrix();
    if (axes) scene.remove(axes);
    axes = new THREE.AxesHelper(extent * 0.15);
    scene.add(axes);
    dirty = true;
  }
  $(".ex-reset").onclick = frame;
  function recentre() {                                          // a pinned point becomes the centre of the 3D view
    const d = items[pinned];
    if (!d) return;
    const to = new THREE.Vector3(...d.pos), delta = to.clone().sub(controls.target);
    controls.target.copy(to); camera.position.add(delta); controls.update(); dirty = true;
  }

  function build3d() {
    if (cloud) { scene.remove(cloud); cloud.geometry.dispose(); }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(items.flatMap((d) => d.pos), 3));
    g.setAttribute("color", new THREE.Float32BufferAttribute(items.flatMap((d) => d.col.map((c) => c / 255)), 3));
    cloud = new THREE.Points(g, new THREE.PointsMaterial({ size: 9, sizeAttenuation: false, vertexColors: true, map: dot, alphaTest: 0.05, transparent: true }));
    scene.add(cloud);
    selection3d();
  }

  const arrow = (from, vec, colour, scale) => {
    const len = vec.length() * scale;
    if (len < extent * 1e-4) return;
    const dir = vec.clone().normalize(), head = Math.min(len * 0.4, extent * 0.03), r = extent * 0.0035;
    const mat = new THREE.MeshBasicMaterial({ color: colour });
    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len - head * 0.8, 8), mat);
    shaft.position.copy(from).addScaledVector(dir, (len - head * 0.8) / 2);
    const tip = new THREE.Mesh(new THREE.ConeGeometry(r * 3, head, 12), mat);
    tip.position.copy(from).addScaledVector(dir, len - head / 2);
    for (const m of [shaft, tip]) { m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir); selGroup.add(m); }
  };
  function vectors(d) {
    const g = (c) => num(d.r[c]);
    const [um, vm, wm, up, vp, wp] = mf.vector.map(g);
    return [um, vm, wm, up, vp, wp].every(Number.isFinite) ? [new THREE.Vector3(um, vm, wm), new THREE.Vector3(up, vp, wp)] : null;
  }
  function selection3d() {
    selGroup.clear();
    const d = items[sel()];
    if (cloud) cloud.material.opacity = d ? 0.3 : 1;            // the other points step back
    if (!d) return;
    const p = new THREE.Vector3(...d.pos);
    if (line) {                                                  // the whole line the point was measured on
      const pts = line.idx.map((j) => new THREE.Vector3(...items[j].pos));
      selGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: 0xff9f00 })));
      const bead = new THREE.SphereGeometry(extent * 0.007, 10, 8), beadMat = new THREE.MeshBasicMaterial({ color: 0xff9f00 });
      pts.forEach((q) => { const m = new THREE.Mesh(bead, beadMat); m.position.copy(q); selGroup.add(m); });
    }
    const ball = new THREE.Mesh(new THREE.SphereGeometry(extent * 0.014, 16, 12), new THREE.MeshBasicMaterial({ color: 0xffd400 }));
    ball.position.copy(p);
    selGroup.add(ball);
    if (mf.vector) {
      const vv = vectors(d);
      if (vv) {
        const [m, mo] = vv, scale = (extent * 0.2) / Math.max(m.length(), mo.length(), 1e-12);   // the longer of the two is a fifth of the view
        arrow(p, m, 0x222222, scale);
        arrow(p, mo, new THREE.Color(view.colour), scale);
        arrow(p.clone().addScaledVector(m, scale), mo.clone().sub(m), new THREE.Color(ERROR_COLOUR), scale);
      }
    }
  }

  function nearest3d(ev) {
    const b = renderer.domElement.getBoundingClientRect(), x = ev.clientX - b.left, y = ev.clientY - b.top;
    let best = -1, bd = 12 * 12;
    const v = new THREE.Vector3();
    items.forEach((d, i) => {
      v.set(...d.pos).project(camera);
      if (v.z > 1) return;
      const dd = ((v.x + 1) / 2 * b.width - x) ** 2 + ((1 - v.y) / 2 * b.height - y) ** 2;
      if (dd < bd) { bd = dd; best = i; }
    });
    return best;
  }
  let down = null;
  renderer.domElement.addEventListener("pointerdown", (e) => (down = [e.clientX, e.clientY]));
  renderer.domElement.addEventListener("pointermove", (e) => { if (!e.buttons) setHover(nearest3d(e)); });
  renderer.domElement.addEventListener("pointerleave", () => setHover(-1));
  renderer.domElement.addEventListener("pointerup", (e) => {
    if (down && Math.hypot(e.clientX - down[0], e.clientY - down[1]) < 4) { const i = nearest3d(e); pinned = i === pinned ? -1 : i; update(); recentre(); }
    down = null;
  });

  // ---- geometry
  const meshes = {};
  async function loadGeometry(force) {
    const wanted = mf.groups.includes("config") ? mf.geometry.find((g) => g.configuration === groupVals.config) : null;
    const g = wanted || mf.geometry.find((x) => x.default) || mf.geometry[0];
    geoEl.innerHTML = "";
    geoGroup.clear();
    if (!g) return;
    if (!meshes[g.path]) {
      if (g.bytes > HEAVY && !force) {
        const b = document.createElement("button");
        b.type = "button"; b.style.cssText = "font:inherit;font-size:.78rem";
        b.textContent = `Show the geometry (${(g.bytes / 1e6).toFixed(1)} MB)`;
        b.onclick = () => loadGeometry(true);
        geoEl.append(b);
        return;
      }
      geoEl.textContent = "loading geometry…";
      const pos = parseSTL(await (await fetch(base + g.path + stamp)).arrayBuffer());
      const geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
      geo.computeVertexNormals();
      const mesh = new THREE.Group();
      mesh.add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0x9aa0a6, side: THREE.DoubleSide, flatShading: true, transparent: true, opacity: 0.82 })));
      if (pos.length / 9 < 30000) mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo, 30), new THREE.LineBasicMaterial({ color: 0x444444 })));
      meshes[g.path] = mesh;
    }
    geoEl.innerHTML = "";
    geoGroup.add(meshes[g.path]);
    dirty = true;
  }

  // ---- readout
  function showReadout() {
    const d = items[sel()];
    if (!d) { readout.innerHTML = `<div class="ex-hint">Hover a point in either view; click pins it. Points are coloured by how far the model is from the measurement.</div>`; return; }
    const H = mf.H;
    const where = ["x", "y", "z"].map((a, k) => `${a} = ${fmt(d.pos[k], 3)}${H ? ` (${fmt(d.pos[k] / H, 2)} H)` : ""}`).join(", ");
    const grp = mf.groups.map((g) => `${g.replace(/_/g, " ")} ${d.r[g]}`).join(", ");
    let along = "";
    if (line) {
      const fixed = [0, 1, 2].filter((k) => k !== line.axis).map((k) => `${AXES[k]} = ${fmt(d.pos[k], 3)}${H ? ` (${fmt(d.pos[k] / H, 2)} H)` : ""}`).join(", ");
      const err = line.idx.map((j) => items[j].p - items[j].m), mean = err.reduce((a, b) => a + b, 0) / err.length;
      along = `<br><span class="key" style="background:#ff9f00"></span>On a ${line.axis === 2 ? "vertical profile" : `line along ${AXES[line.axis]}`} at ${fixed}:
        ${line.idx.length} points, mean model − measured of ${mf.quantities[q].label} ${fmt(mean)}.`;
    }
    const rows = mf.quantities.map((Q, i) => {
      const m = num(d.r[Q.meas]), p = num(d.r[Q.model]);
      if (!Number.isFinite(m) || !Number.isFinite(p)) return "";
      return `<tr${i === q ? ' style="font-weight:600"' : ""}><td>${Q.label}</td><td>${fmt(m)}</td><td>${fmt(p)}</td><td>${fmt(p - m)}</td><td>${m ? fmt(((p - m) / Math.abs(m)) * 100, 0) + " %" : "–"}</td></tr>`;
    }).join("");
    let vec = "";
    const vv = mf.vector ? vectors(d) : null;
    if (vv) {
      const [m, p] = vv, diff = p.clone().sub(m);
      const ang = (Math.acos(Math.max(-1, Math.min(1, m.dot(p) / (m.length() * p.length() || 1)))) * 180) / Math.PI;
      const key = (c) => `<span class="key" style="background:${c}"></span>`;
      vec = `<p>${key("#222")}measured |U| ${fmt(m.length())} ${key(view.colour)}model |U| ${fmt(p.length())} ${key(ERROR_COLOUR)}difference |ΔU| ${fmt(diff.length())}
        (${m.length() ? fmt((diff.length() / m.length()) * 100, 0) : "–"} % of the measured), direction apart by ${fmt(ang, 0)}°. The arrows in 3D are scaled to the longer of the two vectors at this point (a fifth of the view).</p>`;
    }
    readout.innerHTML = `<div class="ex-text"><p><b>${view.label}</b>${grp ? ", " + grp : ""}${d.r.point_id ? `, point ${d.r.point_id}` : ""}<br>${where}${mf.units ? ` in ${mf.units.split(" (")[0]}` : ""}${along}</p>${vec}</div>
      <table class="ex-table"><colgroup><col style="width:3.5rem"><col style="width:6.5rem"><col style="width:6.5rem"><col style="width:9.5rem"><col style="width:5rem"></colgroup>
      <tr><th></th><th>measured</th><th>model</th><th>model − measured</th><th></th></tr>${rows}</table>`;
  }

  // ---- loop and size
  function size() {
    const w = host3d.parentElement.clientWidth, h = host3d.parentElement.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    renderer.domElement.style.width = "100%"; renderer.domElement.style.height = "100%";
    camera.aspect = w / h; camera.updateProjectionMatrix();
    drawScatter();
    dirty = true;
  }
  ui.querySelectorAll(".ex-panel").forEach((panel) => new ResizeObserver(size).observe(panel));
  renderer.setAnimationLoop(() => { if (dirty) { renderer.render(scene, camera); dirty = false; } });
  root.explorer = { scene, selGroup, camera, get items() { return items; } };   // for tests and the console
  viewSel.onchange = () => loadView(mf.views[+viewSel.value]);
  size();
  await loadView(mf.views[0]);
  size();
}

document.querySelectorAll(".explorer").forEach((root) => start(root).catch((e) => {
  console.error(e);
  const r = root.querySelector(".ex-readout");                 // into the reserved box, so the page does not move
  if (r) r.innerHTML = `<div class="ex-hint">The explorer could not start (${e.message}). The figures on this page show the same points.</div>`;
}));
