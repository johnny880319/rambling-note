"""Self-contained browser animation, embedded for both marimo and WASM export.

The quotient graph pairs incoming and outgoing copies of each multiset slot.
Each directed cycle of total duration L lifts to L / p persistent balls. The
renderer samples those trajectories analytically, so seeking and long playback
never lose balls through accumulated integration error.

Use block comments and explicit semicolons in JavaScript: mo.iframe removes
newlines while serializing srcdoc.
"""

from animation_parser import JAVASCRIPT
from juggling_editor import CSS as EDITOR_CSS
from juggling_editor import DEFAULT_PATTERN_JSON
from juggling_editor import JAVASCRIPT as EDITOR_JAVASCRIPT

HTML = r"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Juggling Simulation</title>
<style>
:root { color-scheme: light dark; --bg: #f7f9fc; --panel: #fff; --ink: #23344a; --muted: #596a81; --line: #d7e0eb; --accent: #2768ba; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #141e2d; --panel: #1c293c; --ink: #e0e9f5; --muted: #a2b3cb; --line: #3b4d65; --accent: #8fbeff; }
}
* { box-sizing: border-box; }
body { margin: 0; padding: 12px; background: var(--bg); color: var(--ink); font: 14px/1.6 system-ui, sans-serif; }
button, select, input, textarea { font: inherit; color: inherit; }
button, select, input[type=number], textarea { background: var(--panel); border: 1px solid var(--line); border-radius: 7px; padding: 5px 9px; }
button { cursor: pointer; } button:hover { border-color: var(--accent); }
button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.primary { color: var(--panel); background: var(--accent); border-color: var(--accent); }
.row { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 16px; margin-bottom: 10px; }
label { display: inline-flex; align-items: center; gap: 6px; }
input[type=range] { width: 110px; accent-color: var(--accent); }
input[type=checkbox] { accent-color: var(--accent); }
input[type=number] { width: 72px; }
#stage { display: block; width: 100%; aspect-ratio: 5 / 3; touch-action: none; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); }
#stats { font-variant-numeric: tabular-nums; color: var(--accent); }
#clock { margin-left: auto; font-variant-numeric: tabular-nums; }
p { margin: 7px 0 12px; }
.hint { font-size: 13px; color: var(--muted); }
__EDITOR_CSS__
#message { margin: 8px 0; min-height: 22px; overflow-wrap: anywhere; }
#message.error { color: light-dark(#b42318, #ffada5); }
details { margin-top: 12px; border-top: 1px solid var(--line); padding-top: 10px; }
summary { cursor: pointer; font-weight: 600; }
#coordinates { margin-top: 10px; }
#animation { margin-top: 18px; }
#scrub { width: 100%; }
@media (max-width: 480px) { body { padding: 8px; } .row { gap: 8px; } #clock { margin-left: 0; } }
</style>
</head>
<body>
<div id="patternEditor"></div>
<div class="row">
  <button id="apply" class="primary">套用並播放</button>
  <button id="restore">還原目前資料</button>
  <span id="stats"></span>
</div>
<p id="message" role="status" aria-live="polite"></p>
<details id="geometrySettings">
  <summary>調整平台位置</summary>
  <p class="hint">圓點是接球點，菱形是拋球點；顏色與平台相同。選擇手與拍次後，可以修改座標或直接拖曳動畫中的控制點。</p>
<div id="coordinates">
  <div class="row">
    <label>手 <select id="hand" aria-label="編輯哪一隻手"></select></label>
    <label>位置套用到 <select id="phase" aria-label="位置套用的拍次"></select></label>
    <button id="resetGeometry">重設位置</button>
  </div>
  <div class="row">
    <label>接球 x <input id="catchX" type="number" min="5" max="95" step="0.5"></label>
    <label>y <input id="catchY" type="number" min="35" max="90" step="0.5" aria-label="接球點 y 座標"></label>
    <label>拋球 x <input id="throwX" type="number" min="5" max="95" step="0.5"></label>
    <label>y <input id="throwY" type="number" min="35" max="90" step="0.5" aria-label="拋球點 y 座標"></label>
  </div>
  <p class="hint">座標是畫面百分比，y 向下增加。「所有拍」會把修改的點套用到該手的整個週期；選單一拍可以安排交叉、高低交替的路徑。空拍的位置不參與拋接。</p>
</div>
</details>
<div id="animation">
<div class="row">
  <button id="play" class="primary">暫停</button>
  <button id="restart">從頭播放</button>
  <label>速度 <input id="speed" type="range" min="0.25" max="2" step="0.05" value="1"><output id="speedValue">1.00×</output></label>
  <label>持球 <input id="dwell" type="range" min="0.1" max="0.8" step="0.05" value="0.35"><output id="dwellValue">0.35 拍</output></label>
</div>
<div class="row">
  <label><input id="guides" type="checkbox" checked>顯示控制點</label>
  <label><input id="trails" type="checkbox" checked>球的尾跡</label>
  <label><input id="dip" type="checkbox" checked>接球下沉</label>
</div>
<canvas id="stage" width="1000" height="600" role="img" aria-label="雜耍動畫：彩色球在各平台間拋接。可拖曳接球圓點與拋球菱形，或使用上方的平台位置設定。"></canvas>
<div class="row" style="margin-top: 8px">
  <label for="scrub">時間（拖曳會暫停）</label>
  <output id="clock"></output>
</div>
<input id="scrub" type="range" min="0" max="6" step="0.001" value="0" aria-label="動畫時間，單位為拍">
<p class="hint">球的顏色與編號會持續跟著同一顆球。圓點可拖曳接球位置，菱形可拖曳拋球位置。</p>
</div>
<script>
"use strict";
const mod = (x, n) => ((x % n) + n) % n;
const smooth = x => x * x * (3 - 2 * x);
const mix = (a, b, t) => a + (b - a) * t;

__PARSER__

function buildPattern(beats) {
  const hands = beats[0].length, period = beats.length;
  const outgoing = Array.from({length: period}, () => Array.from({length: hands}, () => []));
  const incoming = Array.from({length: period}, () => Array.from({length: hands}, () => []));
  const edges = [];
  beats.forEach((columns, phase) => {
    columns.forEach((slots, source) => slots.forEach(([destination, duration], rank) => {
      const edge = {destination, duration, source, phase, rank, id: edges.length};
      edges.push(edge);
      outgoing[phase][source].push(edge);
      incoming[(phase + duration) % period][destination].push(edge);
    }));
  });
  if (edges.length > 2048) throw Error("一個週期最多支援 2048 次拋球。");
  for (let t = 0; t < period; t++) for (let h = 0; h < hands; h++) {
    const arrivals = incoming[t][h], departures = outgoing[t][h];
    if (arrivals.length !== departures.length) throw Error(`不符合 balance：第 ${t} 拍，手 ${h + 1} 接到 ${arrivals.length} 顆，卻拋出 ${departures.length} 顆。`);
    /* Pair individual copies, not just distinct destinations, at each vertex. */
    arrivals.forEach((edge, rank) => { edge.next = departures[rank]; edge.landingRank = rank; });
  }
  const objects = edges.reduce((sum, edge) => sum + edge.duration, 0) / period;
  if (objects > 256) throw Error(`這個 pattern 有 ${objects} 顆球，超過動畫的 256 顆上限。`);
  const seen = new Set(), balls = [];
  for (const first of edges) {
    if (seen.has(first.id)) continue;
    const segments = [];
    let edge = first, length = 0;
    do {
      seen.add(edge.id);
      segments.push({edge, start: length});
      length += edge.duration;
      edge = edge.next;
    } while (edge !== first);
    /* A quotient cycle winds length / period times around the time cylinder. */
    for (let k = 0; k < length / period; k++) {
      balls.push({id: balls.length, segments, length, origin: first.phase + k * period});
    }
  }
  const active = Array.from({length: hands}, (_, h) => outgoing.flatMap((row, t) => row[h].length ? [t] : []));
  const maxDuration = Math.max(1, ...edges.map(edge => edge.duration));
  return {hands, period, outgoing, edges, balls, objects, active, maxDuration};
}

function defaultGeometry(pattern) {
  return Array.from({length: pattern.hands}, (_, h) => {
    const centre = 12 + (h + 0.5) * 76 / pattern.hands;
    const spread = Math.min(7, 22 / pattern.hands);
    const direction = h % 2 === 0 ? 1 : -1;
    return Array.from({length: pattern.period}, () => ({
      catch: {x: centre - direction * spread, y: 76},
      throw: {x: centre + direction * spread, y: 76}
    }));
  });
}

function handPosition(pattern, geometry, hand, time, dwell, dip) {
  const active = pattern.active[hand];
  if (!active.length) return geometry[hand][0].catch;
  const phase = mod(time, pattern.period);
  let previous = active.filter(t => t <= phase).at(-1);
  let next = active.find(t => t > phase);
  if (previous === undefined) previous = active.at(-1) - pattern.period;
  if (next === undefined) next = active[0] + pattern.period;
  const elapsed = phase - previous;
  const start = geometry[hand][mod(previous, pattern.period)];
  let a, b, progress, bend;
  if (elapsed < dwell) {
    a = start.catch; b = start.throw; progress = elapsed / dwell;
    bend = dip ? 3 * Math.sin(Math.PI * progress) ** 2 : 0;
  } else {
    a = start.throw; b = geometry[hand][mod(next, pattern.period)].catch;
    progress = (elapsed - dwell) / (next - previous - dwell);
    bend = -2 * Math.sin(Math.PI * progress) ** 2;
  }
  return {x: mix(a.x, b.x, smooth(progress)), y: mix(a.y, b.y, smooth(progress)) + bend};
}

function slotOffset(rank, count) {
  return (rank - (count - 1) / 2) * Math.min(2.1, 12 / Math.max(1, count));
}

function flightGravity(pattern, geometry, dwell) {
  const lowestY = Math.min(...geometry.flatMap(hand => hand.flatMap(points => [points.catch.y, points.throw.y])));
  return 8 * (lowestY - 10) / (pattern.maxDuration - dwell) ** 2;
}

function ballPosition(pattern, geometry, ball, time, dwell, dip, gravity = flightGravity(pattern, geometry, dwell)) {
  const local = mod(time - ball.origin, ball.length);
  const segment = ball.segments.findLast(segment => segment.start <= local);
  const edge = segment.edge, age = local - segment.start;
  const count = pattern.outgoing[edge.phase][edge.source].length;
  const offset = slotOffset(edge.rank, count);
  if (age < dwell) {
    const point = handPosition(pattern, geometry, edge.source, time, dwell, dip);
    return {x: point.x + offset, y: point.y - 1.8, held: true, edge};
  }
  const a = geometry[edge.source][edge.phase].throw;
  const arrival = (edge.phase + edge.duration) % pattern.period;
  const b = geometry[edge.destination][arrival].catch;
  const landingOffset = slotOffset(edge.landingRank, pattern.outgoing[arrival][edge.destination].length);
  const flight = edge.duration - dwell, elapsed = age - dwell;
  const progress = elapsed / flight;
  /* One acceleration for every ball, scaled to fit all edited endpoints. */
  return {x: mix(a.x + offset, b.x + landingOffset, progress),
    y: mix(a.y, b.y, progress) - gravity * elapsed * (flight - elapsed) / 2 - 1.8,
    held: false, edge};
}

globalThis.Juggling = {parseThrows, buildPattern, defaultGeometry, handPosition, ballPosition};
</script>
<script>
"use strict";
const $ = id => document.getElementById(id);
__EDITOR_JAVASCRIPT__
const defaultPattern = __DEFAULT_PATTERN__;
createPatternEditor($("patternEditor"), {value: defaultPattern, hint: "修改後按「套用並播放」。", describedBy: "message"});
let pattern, geometry, source, time = 0, lastStamp = null;
let running = !matchMedia("(prefers-reduced-motion: reduce)").matches;
let drag = null, resumeAfterDrag = false, frame = null;
const canvas = $("stage"), context = canvas.getContext("2d");
const dwell = () => Number($("dwell").value);
const handColor = h => `hsl(${(h * 137.508 + 210) % 360} 64% 53%)`;
const ballColor = id => `hsl(${(id * 137.508 + 32) % 360} 80% 53%)`;
function option(value, name) { const item = document.createElement("option"); item.value = value; item.textContent = name; return item; }

function updatePlay() { $("play").textContent = running ? "暫停" : "播放"; }
function message(text, error = false) { $("message").textContent = text; $("message").classList.toggle("error", error); }
function selectedPhase() { return $("phase").value === "all" ? 0 : Number($("phase").value); }
function syncCoordinates() {
  const points = geometry[Number($("hand").value)][selectedPhase()];
  for (const kind of ["catch", "throw"]) for (const axis of ["x", "y"]) {
    $(kind + axis.toUpperCase()).value = Number(points[kind][axis].toFixed(1));
  }
}
function setPoint(hand, kind, point) {
  const phases = $("phase").value === "all" ? geometry[hand] : [geometry[hand][selectedPhase()]];
  for (const entry of phases) entry[kind] = {...point};
  syncCoordinates(); draw();
}
function load(text) {
  /* Validate before replacing a working animation or its edited geometry. */
  const candidate = buildPattern(parseThrows(text));
  const nextGeometry = geometry && pattern.hands === candidate.hands && pattern.period === candidate.period
    ? structuredClone(geometry) : defaultGeometry(candidate);
  pattern = candidate; geometry = nextGeometry; source = text; time = 0; lastStamp = null;
  $("editor").value = text;
  $("stats").textContent = `${pattern.hands} 隻手 · ${pattern.period} 拍 · ${pattern.objects} 顆球`;
  $("hand").replaceChildren(...Array.from({length: pattern.hands}, (_, h) => option(h, `手 ${h + 1}`)));
  $("phase").replaceChildren(option("all", "所有拍"), ...Array.from({length: pattern.period}, (_, t) => option(t, `第 ${t} 拍`)));
  $("scrub").max = pattern.period;
  message(`已通過 causality 與 balance 檢查；N = ${pattern.edges.reduce((n, edge) => n + edge.duration, 0)} / ${pattern.period} = ${pattern.objects}。`);
  syncCoordinates(); updatePlay(); draw();
}

function screenPoint(point) { return {x: point.x * 10, y: point.y * 6}; }
function circle(point, radius, color) {
  const p = screenPoint(point); context.beginPath(); context.arc(p.x, p.y, radius, 0, 2 * Math.PI); context.fillStyle = color; context.fill();
}
function guidePoints() {
  const phase = selectedPhase();
  return geometry.flatMap((hand, h) => ["catch", "throw"].map(kind => ({hand: h, kind, point: hand[phase][kind]})));
}
function draw() {
  if (!pattern) return;
  const ratio = devicePixelRatio || 1;
  const width = Math.round(canvas.clientWidth * ratio);
  const height = Math.round(canvas.clientWidth * 0.6 * ratio);
  if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height; }
  context.setTransform(canvas.width / 1000, 0, 0, canvas.height / 600, 0, 0);
  context.clearRect(0, 0, 1000, 600);
  const style = getComputedStyle(document.documentElement);
  const muted = style.getPropertyValue("--muted"), line = style.getPropertyValue("--line");
  context.strokeStyle = line; context.lineWidth = 1;
  for (let y = 100; y < 600; y += 100) { context.beginPath(); context.moveTo(0, y); context.lineTo(1000, y); context.stroke(); }
  if ($("guides").checked) {
    for (let h = 0; h < pattern.hands; h++) {
      const points = geometry[h][selectedPhase()];
      const a = screenPoint(points.catch), b = screenPoint(points.throw);
      context.strokeStyle = handColor(h); context.globalAlpha = 0.35; context.setLineDash([5, 6]);
      context.beginPath(); context.moveTo(a.x, a.y); context.lineTo(b.x, b.y); context.stroke();
    }
    context.setLineDash([]); context.globalAlpha = 1;
  }
  const currentDwell = dwell(), useDip = $("dip").checked;
  const gravity = flightGravity(pattern, geometry, currentDwell);
  for (let h = 0; h < pattern.hands; h++) {
    const p = screenPoint(handPosition(pattern, geometry, h, time, currentDwell, useDip));
    const capacity = Math.max(1, ...pattern.outgoing.map(row => row[h].length));
    const halfWidth = Math.max(24, Math.abs(slotOffset(0, capacity)) * 10 + 12);
    context.fillStyle = handColor(h); context.beginPath(); context.roundRect(p.x - halfWidth, p.y, halfWidth * 2, 9, 4); context.fill();
    context.fillStyle = muted; context.font = "16px system-ui"; context.textAlign = "center";
    context.fillText(`手 ${h + 1}`, p.x, p.y + 31);
  }
  for (const ball of pattern.balls) {
    const color = ballColor(ball.id);
    if ($("trails").checked) {
      for (let back = 6; back > 0; back--) {
        context.globalAlpha = (7 - back) / 30;
        circle(ballPosition(pattern, geometry, ball, time - back * 0.035, currentDwell, useDip, gravity), 5, color);
      }
      context.globalAlpha = 1;
    }
    const point = ballPosition(pattern, geometry, ball, time, currentDwell, useDip, gravity);
    circle(point, 10, color);
    const p = screenPoint(point);
    context.fillStyle = "#172333"; context.font = "bold 11px system-ui"; context.textAlign = "center";
    context.fillText(ball.id + 1, p.x, p.y + 4);
  }
  if ($("guides").checked) for (const guide of guidePoints()) {
    const p = screenPoint(guide.point), selected = guide.hand === Number($("hand").value);
    context.strokeStyle = handColor(guide.hand); context.lineWidth = selected ? 3 : 1.5;
    context.fillStyle = style.getPropertyValue("--panel"); context.globalAlpha = selected ? 1 : 0.55;
    context.beginPath();
    if (guide.kind === "catch") context.arc(p.x, p.y, 8, 0, Math.PI * 2);
    else { context.moveTo(p.x, p.y - 10); context.lineTo(p.x + 10, p.y); context.lineTo(p.x, p.y + 10); context.lineTo(p.x - 10, p.y); context.closePath(); }
    context.fill(); context.stroke();
    context.fillStyle = handColor(guide.hand); context.font = "14px system-ui";
    context.fillText(`${guide.hand + 1} ${guide.kind === "catch" ? "接" : "拋"}`, p.x, p.y + (guide.kind === "catch" ? 48 : -17));
    context.globalAlpha = 1;
  }
  $("clock").textContent = `t = ${time.toFixed(2)} · 第 ${mod(Math.floor(time), pattern.period)} 拍`;
  $("scrub").value = mod(time, pattern.period);
}

function tick(stamp) {
  frame = null;
  if (running && lastStamp !== null) time += (stamp - lastStamp) / 1000 * 1.8 * Number($("speed").value);
  lastStamp = stamp; draw();
  if (running && !document.hidden) frame = requestAnimationFrame(tick);
}
function schedule() {
  lastStamp = null;
  if (frame === null && running && !document.hidden) frame = requestAnimationFrame(tick);
  updatePlay(); draw();
}
$("play").onclick = () => { running = !running; schedule(); };
$("restart").onclick = () => { time = 0; running = true; schedule(); };
$("scrub").oninput = () => { running = false; time = Number($("scrub").value); schedule(); };
$("speed").oninput = () => { $("speedValue").value = Number($("speed").value).toFixed(2) + "×"; };
$("dwell").oninput = () => { $("dwellValue").value = dwell().toFixed(2) + " 拍"; draw(); };
for (const id of ["guides", "trails", "dip"]) $(id).onchange = draw;
for (const id of ["hand", "phase"]) $(id).onchange = () => { syncCoordinates(); draw(); };
$("resetGeometry").onclick = () => { geometry = defaultGeometry(pattern); syncCoordinates(); draw(); };
$("apply").onclick = () => {
  try { load($("editor").value); running = true; schedule(); }
  catch (error) { message(error.message, true); }
};
$("restore").onclick = () => { $("editor").value = source; message("已還原目前播放的拋接資料。"); };
for (const kind of ["catch", "throw"]) for (const axis of ["x", "y"]) {
  const input = $(kind + axis.toUpperCase());
  input.onchange = () => {
    if (input.value === "" || !input.checkValidity()) { syncCoordinates(); return; }
    const hand = Number($("hand").value), point = {...geometry[hand][selectedPhase()][kind]};
    point[axis] = Number(input.value); setPoint(hand, kind, point);
  };
}
function pointerPoint(event) {
  const rect = canvas.getBoundingClientRect();
  return {x: (event.clientX - rect.left) / rect.width * 100, y: (event.clientY - rect.top) / rect.height * 100};
}
canvas.onpointerdown = event => {
  if (!$("guides").checked || drag || (event.pointerType === "mouse" && event.button !== 0)) return;
  const point = pointerPoint(event), rect = canvas.getBoundingClientRect();
  const hits = guidePoints().map(guide => ({...guide, distance: Math.hypot((point.x - guide.point.x) * rect.width / 100, (point.y - guide.point.y) * rect.height / 100)}));
  hits.sort((a, b) => a.distance - b.distance || Number(b.hand === Number($("hand").value)) - Number(a.hand === Number($("hand").value)));
  if (hits[0].distance > 20) return;
  drag = {...hits[0], pointer: event.pointerId};
  $("hand").value = drag.hand; syncCoordinates();
  resumeAfterDrag = running; running = false; updatePlay();
  canvas.setPointerCapture(event.pointerId); canvas.style.cursor = "grabbing"; draw();
};
canvas.onpointermove = event => {
  if (!drag || event.pointerId !== drag.pointer) return;
  const point = pointerPoint(event);
  setPoint(drag.hand, drag.kind, {x: Math.max(5, Math.min(95, point.x)), y: Math.max(35, Math.min(90, point.y))});
};
function endDrag(event) {
  if (!drag || event.pointerId !== drag.pointer) return;
  drag = null; canvas.style.cursor = ""; running = resumeAfterDrag; schedule();
}
canvas.onpointerup = endDrag;
canvas.onpointercancel = endDrag;
canvas.onlostpointercapture = endDrag;
document.addEventListener("visibilitychange", () => {
  if (document.hidden && frame !== null) { cancelAnimationFrame(frame); frame = null; }
  schedule();
});
new ResizeObserver(draw).observe(canvas);
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", draw);
load(defaultPattern); schedule();
</script>
</body>
</html>
""".replace("__PARSER__", JAVASCRIPT).replace("__EDITOR_CSS__", EDITOR_CSS).replace(
    "__EDITOR_JAVASCRIPT__", EDITOR_JAVASCRIPT
).replace("__DEFAULT_PATTERN__", DEFAULT_PATTERN_JSON)
