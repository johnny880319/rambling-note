"""Generate first-return walks from the ground state without a full state graph."""

JAVASCRIPT = r"""
function primitivePeriod(values) {
  for (let p = 1; p <= values.length; p++) {
    if (values.length % p === 0 && values.every((value, i) => value === values[i % p])) return p;
  }
}
function endsWithRepeatedLoop(values, states) {
  const end = values.length;
  for (let width = 1; width * 2 <= end; width++) {
    if (states[end] !== states[end - width] || states[end] !== states[end - 2 * width]) continue;
    let same = true;
    for (let i = end - width; i < end; i++) {
      if (values[i] !== values[i - width]) { same = false; break; }
    }
    if (same) return true;
  }
  return false;
}
function validateChallenge({balls, height, minimum, maximum}) {
  for (const [label, value, limit] of [["球數", balls, 16], ["最大高度", height, 64], ["最小週期", minimum, 64], ["最大週期", maximum, 64]]) {
    if (!Number.isInteger(value) || value < 1 || value > limit) throw Error(`${label}必須是 1 到 ${limit} 的整數。`);
  }
  if (minimum > maximum) throw Error("最小週期不能大於最大週期。");
  if (balls > height) throw Error("找不到符合設定的 pattern：最大高度不能小於球數。");
  if (balls === height && minimum > 1) throw Error("找不到符合設定的 pattern：球數等於最大高度時，只能有週期為 1 的固定高度投擲。");
}
function* searchSiteswap(settings, random = Math.random) {
  validateChallenge(settings);
  const {balls, height, minimum, maximum} = settings;
  const pick = count => Math.floor(random() * count);
  if (balls === height) return [balls];
  if (balls === 1) {
    const last = Math.min(maximum, height);
    if (minimum > last) throw Error("找不到符合設定的首次回到基態的 pattern；請縮短週期或提高最大高度。");
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
  const path = [], states = [ground];
  let work = 0;
  function* visit(state, remaining) {
    /* An existing landing beyond the final ground-state horizon cannot move. */
    if ((state >> BigInt(balls + remaining)) !== 0n) return null;
    const shifted = state >> 1n;
    const choices = (state & 1n) === 0n ? [0] : shuffle(Array.from({length: height}, (_, i) => i + 1).filter(h => !(shifted & (1n << BigInt(h - 1)))));
    for (const h of choices) {
      if (++work > 150000) throw Error("這組設定的搜尋量較大，尚未找到結果；請縮小高度或週期範圍後重試。");
      if (work % 1000 === 0) yield;
      const next = h ? shifted | (1n << BigInt(h - 1)) : shifted;
      if ((remaining === 1) !== (next === ground)) continue;
      path.push(h); states.push(next);
      /* The repeated-loop constraint depends on the entire prefix, so failed
         (state, remaining) pairs cannot be memoized across different paths. */
      const repeated = endsWithRepeatedLoop(path, states);
      const suffix = repeated ? null : remaining === 1 ? [] : yield* visit(next, remaining - 1);
      path.pop(); states.pop();
      if (suffix) return [h, ...suffix];
    }
    return null;
  }
  for (const period of shuffle(Array.from({length: maximum - minimum + 1}, (_, i) => minimum + i))) {
    const result = yield* visit(ground, period);
    if (result) return result;
  }
  throw Error("找不到符合設定、途中不經過基態且沒有連續重複循環的 pattern；請調整高度或週期範圍。");
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
    basicName: balls === 1 ? "單球交替" : balls === 2 ? "雙球持球" : balls % 2 ? "Cascade" : "Fountain"
  };
}
globalThis.SiteswapChallenge = {primitivePeriod, endsWithRepeatedLoop, validateChallenge, searchSiteswap, generateSiteswap, alternatingHands, qualifyRoutine};
"""
