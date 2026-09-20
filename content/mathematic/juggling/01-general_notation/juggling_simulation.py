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

_TEMPLATE = r"""<!doctype html>
<html lang="en">
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
#stage { display: block; width: 100%; aspect-ratio: 5 / 3; cursor: grab; touch-action: none; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); }
#stageResizeHandle { height: 18px; margin: -1px 0 2px; cursor: ns-resize; touch-action: none; position: relative; }
#stageResizeHandle::after { content: ""; position: absolute; left: calc(50% - 28px); top: 7px; width: 56px; border-top: 3px solid var(--line); border-radius: 2px; }
#stageResizeHandle:hover::after, #stageResizeHandle:focus-visible::after { border-color: var(--accent); }
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
__INPUT_CONTROLS__
<p id="message" role="status" aria-live="polite"></p>
<div id="animation">
<canvas id="stage" width="1000" height="600" role="img" aria-label="Juggling animation with colored balls moving between hand platforms. Drag the circular catch points and diamond throw points, or use the hand-path controls below."></canvas>
<div id="stageResizeHandle" tabindex="0" role="separator" aria-orientation="horizontal" aria-label="Drag to resize the animation viewport" aria-valuemin="220" aria-valuemax="800" aria-valuenow="360"></div>
<details id="geometrySettings" class="simulation-setting">
  <summary>Adjust Hand Paths</summary>
  <p class="hint">Circles mark catch points and diamonds mark throw points; their colors match the hand platforms. Select a hand and beat, then edit the coordinates or drag a control point in the animation.</p>
<div id="coordinates">
  <div class="row">
    <label>Hand <select id="hand" aria-label="Hand to edit"></select></label>
    <label>Apply to <select id="phase" aria-label="Beats that use these positions"></select></label>
    <button id="resetGeometry">Reset Positions</button>
  </div>
  <div class="row">
    <label>Catch x <input id="catchX" type="number" min="5" max="95" step="0.5"></label>
    <label>y <input id="catchY" type="number" min="35" max="90" step="0.5" aria-label="Catch-point y coordinate"></label>
    <label>Throw x <input id="throwX" type="number" min="5" max="95" step="0.5"></label>
    <label>y <input id="throwY" type="number" min="35" max="90" step="0.5" aria-label="Throw-point y coordinate"></label>
  </div>
  <p class="hint">Coordinates use the original scene, with y increasing downward; moving or scaling the camera does not change them. The camera stays fixed while a control point is dragged and refits when released. “All Beats” applies the point to the hand's entire period; selecting one beat allows crossing or alternating paths. Empty beats do not participate in throws or catches.</p>
</div>
</details>
<div id="timelineLabel" class="row" style="margin-top: 8px">
  <label for="scrub">Time (dragging pauses playback)</label>
  <output id="clock"></output>
</div>
<input id="scrub" type="range" min="0" max="6" step="0.001" value="0" aria-label="Animation time in beats">
<div id="playbackControls" class="row simulation-setting" style="margin-top: 12px">
  <button id="play" class="primary">Pause</button>
  <button id="restart">Restart</button>
  <label>Speed <input id="speed" type="range" min="0.25" max="2" step="0.05" value="1"><output id="speedValue">1.00×</output></label>
  <label>Dwell <input id="dwell" type="range" min="0.1" max="0.8" step="0.05" value="0.35"><output id="dwellValue">0.35 beats</output></label>
  <label>Gravity <input id="gravity" type="range" min="4" max="48" step="1" value="12" aria-label="Gravitational acceleration in y-coordinate units per beat squared"><output id="gravityValue">12</output></label>
</div>
<p id="physicsHint" class="hint simulation-setting">Gravity is measured in y-coordinate units per beat². For a fixed throw duration, stronger gravity produces a higher throw. The camera fits the entire trajectory proportionally and stays fixed during playback.</p>
<div id="displayControls" class="row simulation-setting">
  <label><input id="guides" type="checkbox" checked>Control Points</label>
  <label><input id="trails" type="checkbox" checked>Trails</label>
  <label><input id="dip" type="checkbox" checked>Catch Dip</label>
</div>
<div id="viewportControls" class="row simulation-setting" style="margin-top: 10px">
  <label>Viewport Height <input id="stageHeight" type="range" min="220" max="800" step="10" value="360"><output id="stageHeightValue">Auto</output></label>
  <button id="fitViewport" type="button">Fit View</button>
  <output id="zoomValue" aria-live="polite">100%</output>
</div>
<p id="interactionHint" class="hint simulation-setting">Use the mouse wheel or pinch to zoom, and drag empty space to pan. Drag the handle below the animation to resize the viewport. A ball keeps the same color and number throughout. Drag a circle to move a catch point or a diamond to move a throw point.</p>
</div>
<script>
"use strict";
const mod = (x, n) => ((x % n) + n) % n;
const smooth = x => x * x * (3 - 2 * x);
const mix = (a, b, t) => a + (b - a) * t;
const count = (value, unit) => `${value} ${unit}${value === 1 ? "" : "s"}`;

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
  if (edges.length > 2048) throw Error("One period can contain at most 2,048 throws.");
  for (let t = 0; t < period; t++) for (let h = 0; h < hands; h++) {
    const arrivals = incoming[t][h], departures = outgoing[t][h];
    if (arrivals.length !== departures.length) throw Error(`Balance fails at beat ${t}: hand ${h + 1} catches ${count(arrivals.length, "object")} but throws ${count(departures.length, "object")}.`);
    /* Pair individual copies, not just distinct destinations, at each vertex. */
    arrivals.forEach((edge, rank) => { edge.next = departures[rank]; edge.landingRank = rank; });
  }
  const objects = edges.reduce((sum, edge) => sum + edge.duration, 0) / period;
  if (objects > 256) throw Error(`This pattern has ${objects} objects, exceeding the animation limit of 256.`);
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
  const horizontalScale = pattern.horizontalScale ?? 1;
  return Array.from({length: pattern.hands}, (_, h) => {
    const centre = 50 + (12 + (h + 0.5) * 76 / pattern.hands - 50) * horizontalScale;
    const spread = Math.min(7, 22 / pattern.hands) * horizontalScale;
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

function ballPosition(pattern, geometry, ball, time, dwell, dip, gravity = 12) {
  const local = mod(time - ball.origin, ball.length);
  const segment = ball.segments.findLast(segment => segment.start <= local);
  const edge = segment.edge, age = local - segment.start;
  const count = pattern.outgoing[edge.phase][edge.source].length;
  const offset = slotOffset(edge.rank, count);
  if (age < dwell || (pattern.holdTwos && edge.duration === 2)) {
    const point = handPosition(pattern, geometry, edge.source, time, dwell, dip);
    return {x: point.x + offset, y: point.y - 1.8, held: true, edge};
  }
  const a = geometry[edge.source][edge.phase].throw;
  const arrival = (edge.phase + edge.duration) % pattern.period;
  const b = geometry[edge.destination][arrival].catch;
  const landingOffset = slotOffset(edge.landingRank, pattern.outgoing[arrival][edge.destination].length);
  const flight = edge.duration - dwell, elapsed = age - dwell;
  const progress = elapsed / flight;
  /* Solve the launch velocity for the prescribed flight time and endpoints. */
  return {x: mix(a.x + offset, b.x + landingOffset, progress),
    y: mix(a.y, b.y, progress) - gravity * elapsed * (flight - elapsed) / 2 - 1.8,
    held: false, edge};
}

function fitView(pattern, geometry, dwell, gravity, padding = 24, viewportHeight = 600) {
  let left = 0, right = 1000, top = 0, bottom = 600;
  geometry.forEach((hand, h) => {
    const capacity = Math.max(1, ...pattern.outgoing.map(row => row[h].length));
    const margin = Math.abs(slotOffset(0, capacity)) * 10 + 32;
    for (const points of hand) for (const point of [points.catch, points.throw]) {
      left = Math.min(left, point.x * 10 - margin);
      right = Math.max(right, point.x * 10 + margin);
      top = Math.min(top, point.y * 6 - 30);
      bottom = Math.max(bottom, point.y * 6 + 54);
    }
  });
  for (const edge of pattern.edges) {
    if (pattern.holdTwos && edge.duration === 2) continue;
    const a = geometry[edge.source][edge.phase].throw;
    const b = geometry[edge.destination][(edge.phase + edge.duration) % pattern.period].catch;
    const flight = edge.duration - dwell;
    /* Include the exact apex, also when the endpoints have unequal heights. */
    const elapsed = Math.max(0, Math.min(flight, flight / 2 - (b.y - a.y) / (gravity * flight)));
    const y = mix(a.y, b.y, elapsed / flight) - gravity * elapsed * (flight - elapsed) / 2 - 1.8;
    top = Math.min(top, y * 6 - 24);
  }
  const scale = Math.min(1, (1000 - 2 * padding) / (right - left), (viewportHeight - 2 * padding) / (bottom - top));
  return {scale, x: 500 - (left + right) * scale / 2, y: viewportHeight - padding - bottom * scale};
}
function viewPoint(point, view) {
  return {x: point.x * 10 * view.scale + view.x, y: point.y * 6 * view.scale + view.y};
}
function worldPoint(point, view) {
  return {x: (point.x - view.x) / (10 * view.scale), y: (point.y - view.y) / (6 * view.scale)};
}
globalThis.Juggling = {parseThrows, buildPattern, defaultGeometry, handPosition, ballPosition, fitView, viewPoint, worldPoint};
</script>
<script>
"use strict";
const $ = id => document.getElementById(id);
__EDITOR_JAVASCRIPT__
const defaultPattern = __DEFAULT_PATTERN__;
if ($("patternEditor")) createPatternEditor($("patternEditor"), {value: defaultPattern, hint: "Select Apply and Play after editing.", describedBy: "message"});
let pattern, geometry, source, time = 0, lastStamp = null, onFrame = null;
let running = !matchMedia("(prefers-reduced-motion: reduce)").matches;
let drag = null, pan = null, resumeAfterDrag = false, frame = null;
let view = {scale: 1, x: 0, y: 0};
let fittedScale = 1, customHeight = false, resizingStage = null;
const touchPoints = new Map();
let pinch = null;
const canvas = $("stage"), context = canvas.getContext("2d");
const dwell = () => Number($("dwell").value);
const gravity = () => Number($("gravity").value);
const logicalHeight = () => 1000 * canvas.clientHeight / canvas.clientWidth;
function updateZoom() { $("zoomValue").value = `${Math.round(view.scale / fittedScale * 100)}%`; }
function fitViewport() {
  if (pattern && !drag && !pan && canvas.clientWidth) {
    const padding = Math.min(100, Math.max(24, 24000 / canvas.clientWidth));
    view = fitView(pattern, geometry, dwell(), gravity(), padding, logicalHeight());
    fittedScale = view.scale; updateZoom();
  }
}
function canvasPoint(event) {
  const rect = canvas.getBoundingClientRect();
  return {x: (event.clientX - rect.left - canvas.clientLeft) / canvas.clientWidth * 1000,
    y: (event.clientY - rect.top - canvas.clientTop) / canvas.clientHeight * logicalHeight()};
}
function zoomFrom(base, centre, target, factor) {
  const scale = Math.max(fittedScale * 0.5, Math.min(fittedScale * 8, base.scale * factor));
  const world = {x: (centre.x - base.x) / base.scale, y: (centre.y - base.y) / base.scale};
  view = {scale, x: target.x - world.x * scale, y: target.y - world.y * scale};
  updateZoom(); draw();
}
const handColor = h => `hsl(${(h * 137.508 + 210) % 360} 64% 53%)`;
const ballColor = id => `hsl(${(id * 137.508 + 32) % 360} 80% 53%)`;
function option(value, name) { const item = document.createElement("option"); item.value = value; item.textContent = name; return item; }

function updatePlay() { $("play").textContent = running ? "Pause" : "Play"; }
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
  syncCoordinates(); fitViewport(); draw();
}
function load(text, beats = null, options = {}) {
  /* Validate before replacing a working animation or its edited geometry. */
  const candidate = Object.assign(buildPattern(beats ?? parseThrows(text)), options);
  const nextGeometry = geometry && pattern.hands === candidate.hands && pattern.period === candidate.period
    ? structuredClone(geometry) : defaultGeometry(candidate);
  pattern = candidate; geometry = nextGeometry; source = text; time = 0; lastStamp = null;
  if ($("editor")) $("editor").value = text;
  $("stats").textContent = `${count(pattern.hands, "hand")} · ${count(pattern.period, "beat")} · ${count(pattern.objects, "object")}`;
  $("hand").replaceChildren(...Array.from({length: pattern.hands}, (_, h) => option(h, pattern.handLabels?.[h] ?? `Hand ${h + 1}`)));
  $("phase").replaceChildren(option("all", "All Beats"), ...Array.from({length: pattern.period}, (_, t) => option(t, `Beat ${t}`)));
  $("scrub").max = pattern.period;
  message(`Causality and balance checks passed; b = ${pattern.edges.reduce((n, edge) => n + edge.duration, 0)} / ${pattern.period} = ${pattern.objects}.`);
  syncCoordinates(); fitViewport(); updatePlay(); draw();
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
  if (!pattern || !canvas.clientWidth) return;
  const ratio = devicePixelRatio || 1;
  const width = Math.round(canvas.clientWidth * ratio);
  const height = Math.round(canvas.clientHeight * ratio);
  const viewportHeight = logicalHeight();
  if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height; }
  context.setTransform(canvas.width / 1000, 0, 0, canvas.height / viewportHeight, 0, 0);
  context.clearRect(0, 0, 1000, viewportHeight);
  const style = getComputedStyle(document.documentElement);
  const muted = style.getPropertyValue("--muted"), line = style.getPropertyValue("--line");
  context.strokeStyle = line; context.lineWidth = 1;
  for (let y = 100; y < viewportHeight; y += 100) { context.beginPath(); context.moveTo(0, y); context.lineTo(1000, y); context.stroke(); }
  context.translate(view.x, view.y); context.scale(view.scale, view.scale);
  /* Keep markers readable while scaling their positions uniformly. */
  const pixelsPerUnit = view.scale * canvas.clientWidth / 1000;
  const ballRadius = Math.max(10, 5 / pixelsPerUnit);
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
  const currentGravity = gravity();
  for (let h = 0; h < pattern.hands; h++) {
    const p = screenPoint(handPosition(pattern, geometry, h, time, currentDwell, useDip));
    const capacity = Math.max(1, ...pattern.outgoing.map(row => row[h].length));
    const halfWidth = Math.max(24, 7 / pixelsPerUnit, Math.abs(slotOffset(0, capacity)) * 10 + 12);
    context.fillStyle = handColor(h); context.beginPath(); context.roundRect(p.x - halfWidth, p.y, halfWidth * 2, Math.max(9, 3 / pixelsPerUnit), 4); context.fill();
    context.fillStyle = muted; context.font = `${Math.max(16, 9 / pixelsPerUnit)}px system-ui`; context.textAlign = "center";
    context.fillText(pattern.handLabels?.[h] ?? `Hand ${h + 1}`, p.x, p.y + Math.max(31, 16 / pixelsPerUnit));
  }
  for (const ball of pattern.balls) {
    const color = ballColor(ball.id);
    if ($("trails").checked) {
      for (let back = 6; back > 0; back--) {
        context.globalAlpha = (7 - back) / 30;
        circle(ballPosition(pattern, geometry, ball, time - back * 0.035, currentDwell, useDip, currentGravity), ballRadius / 2, color);
      }
      context.globalAlpha = 1;
    }
    const point = ballPosition(pattern, geometry, ball, time, currentDwell, useDip, currentGravity);
    circle(point, ballRadius, color);
    const p = screenPoint(point);
    const fontSize = Math.max(11, 8 / pixelsPerUnit);
    context.fillStyle = "#172333"; context.font = `bold ${fontSize}px system-ui`; context.textAlign = "center";
    context.fillText(ball.id + 1, p.x, p.y + fontSize * 0.35);
  }
  if ($("guides").checked) for (const guide of guidePoints()) {
    const p = screenPoint(guide.point), selected = guide.hand === Number($("hand").value);
    context.strokeStyle = handColor(guide.hand); context.lineWidth = selected ? 3 : 1.5;
    context.fillStyle = style.getPropertyValue("--panel"); context.globalAlpha = selected ? 1 : 0.55;
    context.beginPath();
    if (guide.kind === "catch") context.arc(p.x, p.y, Math.max(8, 5 / pixelsPerUnit), 0, Math.PI * 2);
    else {
      const size = Math.max(10, 6 / pixelsPerUnit);
      context.moveTo(p.x, p.y - size); context.lineTo(p.x + size, p.y); context.lineTo(p.x, p.y + size); context.lineTo(p.x - size, p.y); context.closePath();
    }
    context.fill(); context.stroke();
    context.fillStyle = handColor(guide.hand); context.font = `${Math.max(14, 9 / pixelsPerUnit)}px system-ui`;
    context.fillText(`${guide.hand + 1} ${guide.kind}`, p.x, p.y + (guide.kind === "catch" ? Math.max(48, 20 / pixelsPerUnit) : -Math.max(17, 12 / pixelsPerUnit)));
    context.globalAlpha = 1;
  }
  $("clock").textContent = `t = ${time.toFixed(2)} · Beat ${mod(Math.floor(time), pattern.period)}`;
  $("scrub").value = mod(time, pattern.period);
  if (onFrame) onFrame(time);
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
$("dwell").oninput = () => { $("dwellValue").value = dwell().toFixed(2) + " beats"; fitViewport(); draw(); };
$("gravity").oninput = () => { $("gravityValue").value = String(gravity()); fitViewport(); draw(); };
$("fitViewport").onclick = () => { fitViewport(); draw(); };
function setStageHeight(height, custom = true) {
  const value = Math.max(Number($("stageHeight").min), Math.min(Number($("stageHeight").max), Math.round(height / 10) * 10));
  customHeight = custom; canvas.style.aspectRatio = "auto"; canvas.style.height = `${value}px`;
  $("stageHeight").value = value; $("stageHeightValue").value = `${value}px`;
  resizeHandle.setAttribute("aria-valuenow", value);
}
$("stageHeight").oninput = () => setStageHeight(Number($("stageHeight").value));
const resizeHandle = $("stageResizeHandle");
resizeHandle.onpointerdown = event => {
  if (event.button !== 0 && event.pointerType === "mouse") return;
  resizingStage = {pointer: event.pointerId, y: event.clientY, height: canvas.clientHeight};
  resizeHandle.setPointerCapture(event.pointerId);
};
resizeHandle.onpointermove = event => {
  if (!resizingStage || resizingStage.pointer !== event.pointerId) return;
  setStageHeight(resizingStage.height + event.clientY - resizingStage.y);
};
resizeHandle.onpointerup = resizeHandle.onpointercancel = event => {
  if (resizingStage?.pointer === event.pointerId) resizingStage = null;
};
resizeHandle.onkeydown = event => {
  if (!["ArrowUp", "ArrowDown"].includes(event.key)) return;
  event.preventDefault(); setStageHeight(canvas.clientHeight + (event.key === "ArrowDown" ? 20 : -20));
};
for (const id of ["guides", "trails", "dip"]) $(id).onchange = draw;
for (const id of ["hand", "phase"]) $(id).onchange = () => { syncCoordinates(); draw(); };
$("resetGeometry").onclick = () => { geometry = defaultGeometry(pattern); syncCoordinates(); fitViewport(); draw(); };
if ($("apply")) $("apply").onclick = () => {
  try { load($("editor").value); running = true; schedule(); }
  catch (error) { message(error.message, true); }
};
if ($("restore")) $("restore").onclick = () => { $("editor").value = source; message("Restored the pattern currently being played."); };
for (const kind of ["catch", "throw"]) for (const axis of ["x", "y"]) {
  const input = $(kind + axis.toUpperCase());
  input.onchange = () => {
    if (input.value === "" || !input.checkValidity()) { syncCoordinates(); return; }
    const hand = Number($("hand").value), point = {...geometry[hand][selectedPhase()][kind]};
    point[axis] = Number(input.value); setPoint(hand, kind, point);
  };
}
function pointerPoint(event) {
  return worldPoint(canvasPoint(event), view);
}
canvas.onpointerdown = event => {
  if (event.pointerType === "touch") {
    touchPoints.set(event.pointerId, canvasPoint(event)); canvas.setPointerCapture(event.pointerId);
    if (touchPoints.size === 2) {
      if (drag) { drag = null; canvas.style.cursor = ""; running = resumeAfterDrag; schedule(); }
      pan = null; canvas.style.cursor = "";
      const points = [...touchPoints.values()], centre = {x: (points[0].x + points[1].x) / 2, y: (points[0].y + points[1].y) / 2};
      pinch = {distance: Math.hypot(points[0].x - points[1].x, points[0].y - points[1].y), centre, view: {...view}};
      return;
    }
  }
  if (drag || pan || (event.pointerType === "mouse" && event.button !== 0)) return;
  if ($("guides").checked) {
    const point = pointerPoint(event);
    const hits = guidePoints().map(guide => ({...guide, distance: Math.hypot((point.x - guide.point.x) * view.scale * canvas.clientWidth / 100, (point.y - guide.point.y) * view.scale * canvas.clientWidth * 0.006)}));
    hits.sort((a, b) => a.distance - b.distance || Number(b.hand === Number($("hand").value)) - Number(a.hand === Number($("hand").value)));
    if (hits[0].distance <= 20) {
      drag = {...hits[0], pointer: event.pointerId, offset: {x: point.x - hits[0].point.x, y: point.y - hits[0].point.y}};
      $("hand").value = drag.hand; syncCoordinates();
      resumeAfterDrag = running; running = false; updatePlay();
      canvas.setPointerCapture(event.pointerId); canvas.style.cursor = "grabbing"; draw();
      return;
    }
  }
  pan = {pointer: event.pointerId, point: canvasPoint(event), view: {...view}};
  canvas.setPointerCapture(event.pointerId); canvas.style.cursor = "grabbing";
};
canvas.onpointermove = event => {
  if (event.pointerType === "touch" && touchPoints.has(event.pointerId)) {
    touchPoints.set(event.pointerId, canvasPoint(event));
    if (pinch && touchPoints.size >= 2) {
      const points = [...touchPoints.values()].slice(0, 2), target = {x: (points[0].x + points[1].x) / 2, y: (points[0].y + points[1].y) / 2};
      zoomFrom(pinch.view, pinch.centre, target, Math.hypot(points[0].x - points[1].x, points[0].y - points[1].y) / Math.max(1, pinch.distance));
      return;
    }
  }
  if (pan && event.pointerId === pan.pointer) {
    const point = canvasPoint(event);
    view = {...pan.view, x: pan.view.x + point.x - pan.point.x, y: pan.view.y + point.y - pan.point.y};
    draw(); return;
  }
  if (!drag || event.pointerId !== drag.pointer) return;
  const point = pointerPoint(event);
  setPoint(drag.hand, drag.kind, {x: Math.max(5, Math.min(95, point.x - drag.offset.x)), y: Math.max(35, Math.min(90, point.y - drag.offset.y))});
};
function endDrag(event) {
  if (event.pointerType === "touch") { touchPoints.delete(event.pointerId); if (touchPoints.size < 2) pinch = null; }
  if (pan?.pointer === event.pointerId) { pan = null; canvas.style.cursor = ""; return; }
  if (!drag || event.pointerId !== drag.pointer) return;
  drag = null; canvas.style.cursor = ""; fitViewport(); running = resumeAfterDrag; schedule();
}
canvas.onpointerup = endDrag;
canvas.onpointercancel = endDrag;
canvas.onlostpointercapture = endDrag;
canvas.addEventListener("wheel", event => {
  event.preventDefault(); const point = canvasPoint(event);
  zoomFrom({...view}, point, point, Math.exp(-event.deltaY * 0.0015));
}, {passive: false});
document.addEventListener("visibilitychange", () => {
  if (document.hidden && frame !== null) { cancelAnimationFrame(frame); frame = null; }
  schedule();
});
new ResizeObserver(() => {
  if (!customHeight) {
    $("stageHeight").value = Math.round(canvas.clientHeight / 10) * 10;
    $("stageHeightValue").value = "Auto";
    resizeHandle.setAttribute("aria-valuenow", Math.round(canvas.clientHeight));
  }
  fitViewport(); draw();
}).observe(canvas);
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", draw);
__STARTUP__
</script>
</body>
</html>
"""

_DEFAULT_CONTROLS = """<div id="patternEditor"></div>
<div class="row">
  <button id="apply" class="primary">Apply and Play</button>
  <button id="restore">Restore Current Pattern</button>
  <span id="stats"></span>
</div>
"""


def make_html(*, controls=None, startup="load(defaultPattern); schedule();"):
    """Embed alternative controls around the same animation engine and canvas."""
    return (
        _TEMPLATE.replace(
            "__INPUT_CONTROLS__", _DEFAULT_CONTROLS if controls is None else controls
        )
        .replace("__PARSER__", JAVASCRIPT)
        .replace("__EDITOR_CSS__", EDITOR_CSS)
        .replace("__EDITOR_JAVASCRIPT__", EDITOR_JAVASCRIPT)
        .replace("__DEFAULT_PATTERN__", DEFAULT_PATTERN_JSON)
        .replace("__STARTUP__", startup)
    )


HTML = make_html()
