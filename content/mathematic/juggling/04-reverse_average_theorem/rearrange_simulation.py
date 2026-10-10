"""Rearrange an integer-mean sequence into a siteswap by Polster's construction, one step at a time."""

from juggling_simulation import make_html

# Pure functions, shared with check-rearrange.py.  Everything is mod p.
#
# Outer loop (Polster, The Mathematics of Juggling, section 2.6): start from
# the juggling sequence 0...0 and walk left to right through the target;
# each step changes two entries, the first mismatched position to its target
# value and the next position to whatever keeps the sum zero mod p.
#
# Inner loop, the lemma: given a juggling sequence with two entries removed
# and two new values b0, b1 to insert, keep an auxiliary array with the two
# empty columns a0, a1 and the two free landings c0, c1.  If a0 + b0 or
# a0 + b1 is one of the free landings the values drop into place; otherwise
# column x = c0 - b0 takes b0 and hands its own value out, and the check
# repeats.  The values of x never repeat, so this ends within p - 2 rounds.
JAVASCRIPT = r"""
const GREEK = [..."αβγδεζηθικλμνξοπρστυφχψω"];
function formatValue(value) {
  if (value >= 10 && value < 36) return String.fromCharCode(87 + value);
  if (value >= 36 && value < 36 + GREEK.length) return GREEK[value - 36];
  return String(value);
}
function parseValue(token) {
  if (/^[a-z]$/i.test(token)) return token.toLowerCase().charCodeAt(0) - 87;
  if (GREEK.includes(token)) return 36 + GREEK.indexOf(token);
  if (/^[0-9]+$/.test(token)) return Number(token);
  throw Error(`Cannot read the value “${token}”.`);
}
function parseSequence(text) {
  const tokens = text.trim().split(/[\s,]+/).filter(Boolean);
  if (tokens.length === 0) throw Error("Enter at least one value.");
  if (tokens.length > 64) throw Error("At most 64 values.");
  const values = tokens.map(parseValue);
  if (values.some(value => value > 64)) throw Error("Values are at most 64.");
  const total = values.reduce((sum, value) => sum + value, 0);
  if (total % values.length !== 0) {
    throw Error(`The mean ${total}/${values.length} is not an integer, so no rearrangement is a siteswap.`);
  }
  return values;
}
const modp = (n, p) => ((n % p) + p) % p;
function isSiteswap(values) {
  const p = values.length;
  return new Set(values.map((value, t) => modp(t + value, p))).size === p;
}
/* One round of the lemma on an auxiliary array.  Returns either a placement
   or an exchange, and mutates the array accordingly. */
function auxiliaryRound(aux) {
  const {p, a0, a1, b0, b1, c0, c1} = aux;
  const s00 = modp(a0 + b0, p), s01 = modp(a0 + b1, p);
  for (const [sum, first, second, label] of [[s00, b0, b1, "v0"], [s01, b1, b0, "v1"]]) {
    for (const [c, name] of [[c0, "ℓ0"], [c1, "ℓ1"]]) {
      if (sum !== c) continue;
      aux.values[a0] = first; aux.values[a1] = second; aux.a0 = aux.a1 = null;
      return {kind: "place", sum, via: label, target: name, at0: first, at1: second, s00, s01};
    }
  }
  const x = modp(c0 - b0, p), b2 = aux.values[x], c2 = modp(x + b2, p);
  aux.values[x] = b0;
  Object.assign(aux, {b0: b2, c0: c1, c1: c2});
  return {kind: "exchange", s00, s01, x, b2, c2, placed: b0, landing: c0};
}
/* The lemma run to completion: a juggling sequence with columns q0, q1
   replaced by b0, b1 of the same sum mod p. */
function substitute(values, q0, q1, b0, b1) {
  const p = values.length;
  const aux = {p, values: [...values], a0: q0, a1: q1, b0, b1, c0: modp(q0 + values[q0], p), c1: modp(q1 + values[q1], p)};
  aux.values[q0] = aux.values[q1] = null;
  let rounds = 0;
  while (auxiliaryRound(aux).kind !== "place") rounds++;
  return {values: aux.values, rounds};
}
/* The whole construction as a step machine for the page. */
function createRearrangement(target) {
  const p = target.length;
  const state = {p, target, bookkeeping: Array(p).fill(0), values: Array(p).fill(0), aux: null,
    position: 0, substitutions: 0, exchanges: 0, done: p === 1, count: 0};
  if (p === 1) state.values = [...target];
  state.step = () => {
    if (state.done) return {kind: "done"};
    state.count++;
    if (state.aux) {
      const event = auxiliaryRound(state.aux);
      if (event.kind === "exchange") { state.exchanges++; return event; }
      state.values = state.aux.values; state.aux = null;
      return event;
    }
    const C = state.bookkeeping, T = state.target;
    while (state.position < p - 1) {
      const i = state.position, last = i === p - 2;
      if (C[i] === T[i] && (!last || C[i + 1] === T[i + 1])) { state.position++; continue; }
      const b0 = T[i], b1 = last ? T[i + 1] : modp(C[i + 1] + C[i] - T[i], p);
      const q0 = state.values.indexOf(C[i]);
      const q1 = state.values.findIndex((value, j) => j !== q0 && value === C[i + 1]);
      const old0 = C[i], old1 = C[i + 1];
      C[i] = b0; C[i + 1] = b1; state.position++; state.substitutions++;
      state.aux = {p, values: [...state.values], a0: q0, a1: q1, b0, b1,
        c0: modp(q0 + state.values[q0], p), c1: modp(q1 + state.values[q1], p)};
      state.aux.values[q0] = state.aux.values[q1] = null;
      return {kind: "substitute", index: i, q0, q1, old0, old1, b0, b1, c0: state.aux.c0, c1: state.aux.c1, last};
    }
    state.done = true;
    return {kind: "finished"};
  };
  return state;
}
function rearrange(target) {
  const machine = createRearrangement(target);
  while (!machine.done) machine.step();
  return machine.values;
}
function alternatingHands(values) {
  const period = values.length * (values.length % 2 === 0 ? 1 : 2);
  return Array.from({length: period}, (_, t) => {
    const duration = values[t % values.length], columns = [[], []];
    if (duration) columns[t % 2].push([(t + duration) % 2, duration]);
    return columns;
  });
}
"""

CONTROLS = r"""
<style>
#rearrangeForm { display: flex; flex-wrap: wrap; gap: 10px 14px; align-items: end; }
#rearrangeForm label { display: flex; flex-direction: column; align-items: start; gap: 3px; flex: 1 1 260px; }
#rearrangeForm input { width: 100%; box-sizing: border-box; font: 500 16px/1.4 ui-monospace, monospace; }
#rearrangeForm .buttons { display: flex; gap: 8px; flex-wrap: wrap; }
#searchStats { display: block; color: var(--accent); margin-top: 10px; }
.caption { margin: 10px 0 2px; font-weight: 600; }
#target { display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0 8px; }
#target span { font: 600 18px/1.5 ui-monospace, monospace; padding: 2px 9px; border: 1px solid var(--line); border-radius: 6px; }
#target span[data-state=done] { border-color: var(--accent); color: var(--accent); }
#target span[data-state=active] { color: var(--panel); background: var(--accent); border-color: var(--accent); }
#auxiliary { overflow-x: auto; }
#auxiliary table { border-collapse: collapse; margin: 6px 0 8px; font: 500 16px/1.5 ui-monospace, monospace; }
#auxiliary th, #auxiliary td { border: 1px solid var(--line); padding: 3px 9px; text-align: center; min-width: 30px; }
#auxiliary th { font-weight: 600; text-align: right; border: none; padding-right: 12px; }
#auxiliary td.empty { color: var(--muted, #888); border-style: dashed; }
#auxiliary td.gap { border: none; min-width: 18px; }
#auxiliary td.out { border-color: var(--accent); color: var(--accent); }
#auxiliary td.swap { color: var(--panel); background: var(--danger, #c0392b); border-color: var(--danger, #c0392b); }
#auxiliary td.placed { color: var(--panel); background: var(--accent); border-color: var(--accent); }
#current { font: 600 19px/1.5 ui-monospace, monospace; margin: 4px 0 8px; }
#stepLog { margin: 0 0 12px; padding-left: 20px; max-height: 11em; overflow-y: auto; }
#stepLog li { margin: 2px 0; }
#stepLog li:last-child { font-weight: 600; }
</style>
<form id="rearrangeForm">
  <label>Sequence<input id="sequence" type="text" value="0 2 3 3 5 5" aria-describedby="sequenceHint" required></label>
  <div class="buttons">
    <button id="reset" type="submit" class="primary">Reset</button>
    <button id="back" type="button">◀ Back</button>
    <button id="next" type="button">Next ▶</button>
    <button id="run" type="button">Run</button>
    <button id="random" type="button">Random</button>
  </div>
</form>
<p id="sequenceHint" class="hint">Non-negative integers separated by spaces, or a–z for 10–35 and α–ω for 36–59. The mean must be an integer.</p>
<output id="searchStats" aria-live="polite"></output>
<p class="caption">Target</p>
<div id="target" aria-label="Target values; filled ones are already in the sequence"></div>
<p class="caption">Auxiliary array</p>
<div id="auxiliary"><table aria-label="Beats, values, and landings mod p, with the two pending values and free landings on the right"><tbody></tbody></table></div>
<p class="caption">Juggling sequence</p>
<div id="current"></div>
<ol id="stepLog" aria-label="Construction steps" aria-live="polite"></ol>
<span id="stats" class="hint"></span>
"""

STARTUP = (
    JAVASCRIPT
    + r"""
let frames = [], cursor = 0, runner = null;
const li = text => { const item = document.createElement("li"); item.textContent = text; return item; };
const show = formatValue;
/* Every step is recorded as a snapshot so the page can move back and forth. */
function snapshot(machine, event) {
  return {event, p: machine.p, target: machine.target, values: [...machine.values],
    aux: machine.aux ? {...machine.aux, values: [...machine.aux.values]} : null,
    position: machine.position, substitutions: machine.substitutions, exchanges: machine.exchanges, done: machine.done};
}
function record(values) {
  const machine = createRearrangement(values);
  const list = [snapshot(machine, null)];
  while (!machine.done) {
    const a0 = machine.aux ? machine.aux.a0 : null, a1 = machine.aux ? machine.aux.a1 : null;
    const event = machine.step();
    if (event.kind === "place") Object.assign(event, {column0: a0, column1: a1});
    list.push(snapshot(machine, event));
  }
  if (list.length === 1) list.push(snapshot(machine, {kind: "finished"}));
  return list;
}
function describe(frame) {
  const event = frame.event, p = frame.p, aux = frame.aux;
  if (!event) return `Start from the juggling sequence ${Array(p).fill("0").join(" ")} and work towards ${frame.target.map(show).join(" ")}, p = ${p}, mean ${frame.target.reduce((s, v) => s + v, 0) / p}.`;
  switch (event.kind) {
    case "substitute": {
      const both = `remove ${show(event.old0)} at beat ${event.q0} and ${show(event.old1)} at beat ${event.q1}, and hold v0 = ${show(event.b0)}, v1 = ${show(event.b1)} to insert`;
      const why = event.last ? `positions ${event.index} and ${event.index + 1} should be ${show(event.b0)} and ${show(event.b1)}`
        : `position ${event.index} should be ${show(event.b0)}, and ${show(event.b1)} at position ${event.index + 1} keeps the sum 0 mod ${p}`;
      return `Substitution ${frame.substitutions}: ${why}. In the juggling sequence ${both}. The freed landings are ℓ0 = ${event.c0}, ℓ1 = ${event.c1}.`;
    }
    case "exchange":
      return `e0 + v0 = ${event.s00} and e0 + v1 = ${event.s01} are neither ℓ0 nor ℓ1. Take x = ℓ0 − v0 = ${event.x}: beat ${event.x} gets ${show(event.placed)}, landing at ${event.landing}, and its old value ${show(event.b2)} with landing ${event.c2} becomes pending. Now v0 = ${show(aux.b0)}, ℓ0 = ${aux.c0}, ℓ1 = ${aux.c1}.`;
    case "place":
      return `e0 + ${event.via} = ${event.sum} = ${event.target}, so ${show(event.at0)} goes to beat e0 and ${show(event.at1)} to beat e1. Juggling sequence: ${frame.values.map(show).join(" ")}.`;
    case "finished":
      return `Every target value is in: ${frame.values.map(show).join(" ")} is a rearrangement of the input and a siteswap.`;
  }
  return "";
}
function cell(text, className = "", tag = "td") { const element = document.createElement(tag); element.textContent = text; if (className) element.className = className; return element; }
function render() {
  const frame = frames[cursor], p = frame.p, aux = frame.aux, event = frame.event;
  const matched = frame.position + (aux ? -1 : 0);
  $("target").replaceChildren(...frame.target.map((value, i) => {
    const span = document.createElement("span"); span.textContent = show(value);
    span.dataset.state = aux && (i === frame.position - 1 || i === frame.position) ? "active" : i < matched || frame.done ? "done" : "";
    return span;
  }));
  const values = aux ? aux.values : frame.values;
  const head = document.createElement("tr"), mid = document.createElement("tr"), foot = document.createElement("tr");
  head.append(cell("beat", "", "th")); mid.append(cell("value", "", "th")); foot.append(cell("landing", "", "th"));
  for (let x = 0; x < p; x++) {
    const empty = values[x] === null;
    let className = empty ? "empty" : "";
    if (event && event.kind === "exchange" && event.x === x) className = "swap";
    if (event && event.kind === "place" && (x === event.column0 || x === event.column1)) className = "placed";
    head.append(cell(String(x), empty ? "empty" : ""));
    mid.append(cell(empty ? (x === aux.a0 ? "e0" : "e1") : show(values[x]), className));
    foot.append(cell(empty ? "" : String(modp(x + values[x], p)), className));
  }
  if (aux) {
    for (const row of [head, mid, foot]) row.append(cell("", "gap"));
    head.append(cell("v0", "out"), cell("v1", "out"));
    mid.append(cell(show(aux.b0), "out"), cell(show(aux.b1), "out"));
    foot.append(cell(String(aux.c0), "out"), cell(String(aux.c1), "out"));
  }
  $("auxiliary").querySelector("tbody").replaceChildren(head, mid, foot);
  $("current").textContent = aux ? "…" : frame.values.map(show).join(" ");
  $("stepLog").replaceChildren(...frames.slice(0, cursor + 1).map(f => li(describe(f))));
  $("stepLog").lastElementChild.scrollIntoView({block: "nearest"});
  const mean = frame.target.reduce((s, v) => s + v, 0) / p;
  $("searchStats").textContent = `p = ${p} · mean b = ${mean} · step ${cursor} of ${frames.length - 1} · ${frame.substitutions} substitution${frame.substitutions === 1 ? "" : "s"} · ${frame.exchanges} exchange${frame.exchanges === 1 ? "" : "s"}` + (frame.done ? " · done" : "");
  $("back").disabled = cursor === 0;
  $("next").disabled = $("run").disabled = cursor === frames.length - 1;
}
function animateResult() {
  const values = frames[frames.length - 1].values;
  load(values.map(show).join(" "), alternatingHands(values), {holdTwos: true, handLabels: ["L", "R"], horizontalScale: 0.35});
  running = !matchMedia("(prefers-reduced-motion: reduce)").matches;
  schedule();
}
function goTo(index) {
  const arrived = index === frames.length - 1 && cursor !== index;
  cursor = Math.max(0, Math.min(frames.length - 1, index));
  render();
  if (cursor === frames.length - 1) stopRunner();
  if (arrived) animateResult();
}
function stopRunner() { if (runner) { clearInterval(runner); runner = null; } $("run").textContent = "Run"; }
function start(text, instant = false) {
  stopRunner();
  try {
    frames = record(parseSequence(text)); cursor = 0;
    message("Use Next and Back to follow the construction one move at a time, or Run to play it through.");
    goTo(instant ? frames.length - 1 : 0);
  } catch (error) {
    frames = []; message(error.message, true);
    for (const id of ["back", "next", "run"]) $(id).disabled = true;
  }
}
$("rearrangeForm").onsubmit = event => { event.preventDefault(); start($("sequence").value); };
$("back").onclick = () => { stopRunner(); goTo(cursor - 1); };
$("next").onclick = () => { stopRunner(); goTo(cursor + 1); };
$("run").onclick = () => {
  if (runner) { stopRunner(); return; }
  $("run").textContent = "Pause";
  runner = setInterval(() => goTo(cursor + 1), 900);
};
$("random").onclick = () => {
  const p = 4 + Math.floor(Math.random() * 4), b = 2 + Math.floor(Math.random() * 3);
  /* Random non-negative integers with mean b: draw p - 1 freely, then let the last absorb the remainder. */
  let values;
  do {
    values = Array.from({length: p - 1}, () => Math.floor(Math.random() * (2 * b + 1)));
    values.push(b * p - values.reduce((s, v) => s + v, 0));
  } while (values[p - 1] < 0 || values[p - 1] > 2 * b + 2);
  $("sequence").value = values.map(show).join(" ");
  start($("sequence").value);
};
$("guides").checked = false;
start($("sequence").value, true);
"""
)

HTML = make_html(controls=CONTROLS, startup=STARTUP)
