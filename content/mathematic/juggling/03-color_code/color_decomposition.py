"""Enumerate indecomposable periodic color decompositions in the browser."""

JAVASCRIPT = r"""
function colorEdgeTypes(pattern) {
  const groups = new Map();
  for (const edge of pattern.edges) {
    const key = `${edge.phase},${edge.source},${edge.destination},${edge.duration}`;
    if (!groups.has(key)) groups.set(key, {phase: edge.phase, source: edge.source,
      destination: edge.destination, duration: edge.duration, edgeIds: []});
    groups.get(key).edgeIds.push(edge.id);
  }
  return [...groups.values()].map((type, id) => ({...type, id,
    from: type.phase * pattern.hands + type.source,
    to: mod(type.phase + type.duration, pattern.period) * pattern.hands + type.destination}));
}

function simpleColorCycles(pattern, types, limits, budget) {
  const vertices = pattern.period * pattern.hands;
  const outgoing = Array.from({length: vertices}, () => []);
  for (const type of types) outgoing[type.from].push(type);
  for (const edges of outgoing) edges.sort((a, b) => a.id - b.id);
  const cycles = [];
  for (let start = 0; start < vertices; start++) {
    const visited = new Set([start]), path = [];
    const walk = vertex => {
      for (const edge of outgoing[vertex]) {
        if (++budget.steps > limits.maxSearch) throw Error("This pattern is too combinatorial to enumerate safely. Shorten it or reduce its multiplex capacity.");
        if (edge.to === start) {
          cycles.push([...path, edge.id]);
          if (cycles.length > limits.maxCycles) throw Error("This pattern has too many simple cycles to enumerate safely. Shorten it or reduce its multiplex capacity.");
        } else if (edge.to > start && !visited.has(edge.to)) {
          visited.add(edge.to); path.push(edge.id); walk(edge.to); path.pop(); visited.delete(edge.to);
        }
      }
    };
    walk(start);
  }
  cycles.sort((a, b) => {
    for (let i = 0; i < Math.min(a.length, b.length); i++) if (a[i] !== b[i]) return a[i] - b[i];
    return a.length - b.length;
  });
  return cycles;
}

function formatColorDuration(value) {
  return value >= 10 && value < 36 ? value.toString(36) : String(value);
}

function formatColorComponent(pattern, edgeIds) {
  const slots = Array.from({length: pattern.period}, () => Array.from({length: pattern.hands}, () => []));
  for (const id of edgeIds) {
    const edge = pattern.edges[id], duration = formatColorDuration(edge.duration);
    slots[edge.phase][edge.source].push(pattern.hands === 1 ? duration : `${duration}_${edge.destination + 1}`);
  }
  return slots.map(beat => beat.map(hand => `[${hand.join(", ")}]`).join(" | ")).join("\n");
}

function enumerateColorDecompositions(beats, requestedLimits = {}) {
  const limits = {maxEdges: 96, maxCycles: 4096, maxDecompositions: 2048,
    maxSearch: 500000, ...requestedLimits};
  const pattern = buildPattern(beats);
  if (pattern.edges.length > limits.maxEdges) throw Error(`This simulator can exhaustively decompose at most ${limits.maxEdges} throws in one period.`);
  const types = colorEdgeTypes(pattern), budget = {steps: 0};
  const cycles = simpleColorCycles(pattern, types, limits, budget);
  const candidates = Array.from({length: types.length}, () => []);
  cycles.forEach((cycle, index) => cycle.forEach(type => candidates[type].push(index)));
  if (types.some(type => !candidates[type.id].length)) throw Error("The pattern contains a throw that belongs to no balanced color component.");
  const remaining = types.map(type => type.edgeIds.length), chosen = [], solutions = [];
  const materialize = () => {
    const cursors = Array(types.length).fill(0);
    const edgeCycles = chosen.map(cycleIndex => cycles[cycleIndex].map(type => types[type].edgeIds[cursors[type]++]));
    return {edgeCycles, components: edgeCycles.map(edgeIds => ({edgeIds,
      objects: edgeIds.reduce((sum, id) => sum + pattern.edges[id].duration, 0) / pattern.period}))};
  };
  const search = () => {
    const pivot = remaining.findIndex(count => count > 0);
    if (pivot < 0) {
      solutions.push(materialize());
      if (solutions.length > limits.maxDecompositions) throw Error(`This pattern has more than ${limits.maxDecompositions} minimized decompositions. Narrow the input before listing all of them.`);
      return;
    }
    const fillPivot = minimum => {
      if (remaining[pivot] === 0) { search(); return; }
      for (const cycleIndex of candidates[pivot]) {
        if (cycleIndex < minimum) continue;
        const cycle = cycles[cycleIndex];
        if (cycle.some(type => remaining[type] === 0)) continue;
        if (++budget.steps > limits.maxSearch) throw Error("This pattern is too combinatorial to enumerate safely. Shorten it or reduce its multiplex capacity.");
        cycle.forEach(type => remaining[type]--); chosen.push(cycleIndex);
        fillPivot(cycleIndex);
        chosen.pop(); cycle.forEach(type => remaining[type]++);
      }
    };
    fillPivot(0);
  };
  search();
  if (!solutions.length) throw Error("No minimized color decomposition was found.");
  return {pattern, cycles, solutions, searchSteps: budget.steps};
}

globalThis.ColorDecomposition = {colorEdgeTypes, simpleColorCycles,
  formatColorComponent, enumerateColorDecompositions};
"""
