"""Generate first-return walks from the ground state without a full state graph."""

JAVASCRIPT = r"""
function primitivePeriod(values) {
  for (let p = 1; p <= values.length; p++) {
    if (values.length % p === 0 && values.every((value, i) => value === values[i % p])) return p;
  }
}
/* Siteswap digits: 0-9, then a-z for 10-35, then the Greek alphabet for 36-59. */
const GREEK = [..."αβγδεζηθικλμνξοπρστυφχψω"];
const MAX_THROW = 35 + GREEK.length;
function formatSiteswapValue(value) {
  if (value >= 10 && value < 36) return String.fromCharCode(87 + value);
  if (value >= 36 && value <= MAX_THROW) return GREEK[value - 36];
  return String(value);
}
function parseSiteswapValue(text) {
  const value = String(text).trim();
  if (/^[a-z]$/i.test(value)) return value.toLowerCase().charCodeAt(0) - 87;
  if (GREEK.includes(value)) return 36 + GREEK.indexOf(value);
  if (/^[0-9]+$/.test(value)) return Number(value);
  return NaN;
}
function cycleSignature(cycle) {
  let first = 0;
  for (let i = 1; i < cycle.length; i++) if (cycle[i] < cycle[first]) first = i;
  return Array.from({length: cycle.length}, (_, i) => cycle[(first + i) % cycle.length].toString(36)).join(".");
}
function simpleCycleAtEnd(states) {
  const end = states.length - 1, finish = states[end];
  for (let start = end - 1; start >= 0; start--) {
    if (states[start] !== finish) continue;
    const cycle = states.slice(start, end);
    return new Set(cycle).size === cycle.length ? cycleSignature(cycle) : null;
  }
  return null;
}
function hasRepeatedCycle(states) {
  const used = new Set();
  for (let end = 1; end < states.length; end++) {
    const signature = simpleCycleAtEnd(states.slice(0, end + 1));
    if (signature === null) continue;
    if (used.has(signature)) return true;
    used.add(signature);
  }
  return false;
}
function validateChallenge({balls, height, minimum, maximum}) {
  for (const [label, value, limit] of [["Balls", balls, 16], ["Max Throw", height, MAX_THROW], ["Min Period", minimum, 64], ["Max Period", maximum, 64]]) {
    if (!Number.isInteger(value) || value < 1 || value > limit) throw Error(`${label} must be an integer from 1 to ${limit}.`);
  }
  if (minimum > maximum) throw Error("Min Period cannot exceed Max Period.");
  if (balls > height) throw Error("No pattern matches these settings: Max Throw cannot be less than Balls.");
  if (balls === height && minimum > 1) throw Error("No pattern matches these settings: when Balls equals Max Throw, only the period-1 constant pattern is possible.");
}
function* searchSiteswap(settings, random = Math.random) {
  validateChallenge(settings);
  const {balls, height, minimum, maximum} = settings;
  const allowZero = settings.allowZero !== false;
  const primeOnly = settings.primeOnly === true;
  const pick = count => Math.floor(random() * count);
  if (balls === height) return [balls];
  if (balls === 1) {
    if (!allowZero) {
      if (minimum <= 1 && maximum >= 1) return [1];
      throw Error("No pattern without a 0 matches these settings. Include period 1 or increase Balls.");
    }
    const last = Math.min(maximum, height);
    if (minimum > last) throw Error("No first-return pattern matches these settings. Shorten the period or increase Max Throw.");
    const period = minimum + pick(last - minimum + 1);
    return [period, ...Array(period - 1).fill(0)];
  }
  const shuffle = values => {
    for (let i = values.length - 1; i > 0; i--) {
      const j = pick(i + 1); [values[i], values[j]] = [values[j], values[i]];
    }
    return values;
  };
  const ground = (1n << BigInt(balls)) - 1n;
  const path = [], states = [ground], usedCycles = new Set();
  let work = 0;
  function* visit(state, remaining) {
    /* An existing landing beyond the final ground-state horizon cannot move. */
    if ((state >> BigInt(balls + remaining)) !== 0n) return null;
    const shifted = state >> 1n;
    const choices = (state & 1n) === 0n ? (allowZero ? [0] : []) : shuffle(Array.from({length: height}, (_, i) => i + 1).filter(h => !(shifted & (1n << BigInt(h - 1)))));
    for (const h of choices) {
      if (++work > 150000) throw Error("The search is too large and found no result yet. Reduce Max Throw or narrow the period range.");
      if (work % 1000 === 0) yield;
      const next = h ? shifted | (1n << BigInt(h - 1)) : shifted;
      if ((remaining === 1) !== (next === ground)) continue;
      if (primeOnly && next !== ground && states.includes(next)) continue;
      path.push(h); states.push(next);
      /* The repeated-cycle constraint depends on the entire prefix, so failed
         (state, remaining) pairs cannot be memoized across different paths. */
      const cycle = simpleCycleAtEnd(states);
      const repeated = cycle !== null && usedCycles.has(cycle);
      const added = cycle !== null && !repeated;
      if (added) usedCycles.add(cycle);
      const suffix = repeated ? null : remaining === 1 ? [] : yield* visit(next, remaining - 1);
      if (added) usedCycles.delete(cycle);
      path.pop(); states.pop();
      if (suffix) return [h, ...suffix];
    }
    return null;
  }
  for (const period of shuffle(Array.from({length: maximum - minimum + 1}, (_, i) => minimum + i))) {
    const result = yield* visit(ground, period);
    if (result) return result;
  }
  const constraint = primeOnly ? "requiring a prime loop" : "avoiding intermediate ground states and repeated cycles";
  throw Error(`No pattern matches these settings while ${constraint}. Adjust Max Throw or the period range.`);
}
function generateSiteswap(settings, random = Math.random) {
  const search = searchSiteswap(settings, random);
  let step;
  do { step = search.next(); } while (!step.done);
  return step.value;
}
function alternatingHands(values) {
  const period = values.length * (values.length % 2 === 0 ? 1 : 2);
  return Array.from({length: period}, (_, t) => {
    const duration = values[t % values.length], columns = [[], []];
    if (duration) columns[t % 2].push([(t + duration) % 2, duration]);
    return columns;
  });
}
function qualifyRoutine(values, balls) {
  const qualifyBeats = 2 * balls;
  const basic = Array(qualifyBeats).fill(balls);
  return {
    values: [...basic, ...values, ...basic],
    qualifyBeats,
    challengeStart: qualifyBeats,
    challengeEnd: qualifyBeats + values.length,
    basicName: balls === 1 ? "One-Ball Alternation" : balls === 2 ? "Two-Ball Hold" : balls % 2 ? "Cascade" : "Fountain"
  };
}
globalThis.SiteswapChallenge = {primitivePeriod, formatSiteswapValue, parseSiteswapValue, cycleSignature, simpleCycleAtEnd, hasRepeatedCycle, validateChallenge, searchSiteswap, generateSiteswap, alternatingHands, qualifyRoutine};
"""
