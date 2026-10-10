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
  for (const id of [...edgeIds].sort((a, b) => a - b)) {
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

function collapseHands(beats) {
  /* Keep every copy and every empty beat; only hand identities are forgotten. */
  const rows = beats.map(beat => beat.flatMap(hand => hand.map(([, duration]) => duration)).sort((a, b) => a - b));
  const signatures = rows.map(row => row.join(","));
  let period = rows.length;
  for (let p = 1; p <= rows.length; p++) {
    if (rows.length % p === 0 && signatures.every((row, t) => row === signatures[t % p])) { period = p; break; }
  }
  return rows.slice(0, period).map(row => [row.map(duration => [0, duration])]);
}

function enumerateHandMergedDecompositions(beats, requestedLimits = {}) {
  const limits = {maxEdges: 96, maxCycles: 4096, maxDecompositions: 2048,
    maxSearch: 500000, ...requestedLimits};
  const pattern = buildPattern(beats);
  if (pattern.edges.length > limits.maxEdges) throw Error(`This simulator can exhaustively decompose at most ${limits.maxEdges} throws in one period.`);
  const projected = enumerateColorDecompositions(collapseHands(beats), limits);
  const period = pattern.period, projectedPeriod = projected.pattern.period;
  const types = colorEdgeTypes(pattern), budget = {steps: projected.searchSteps};
  const cycles = simpleColorCycles(pattern, types, limits, budget);
  const solutions = [], seen = new Set(), solutionCounts = new Map();
  let coarsenedDecompositions = 0, partitionsSearched = 0;
  const spend = () => {
    if (++budget.steps > limits.maxSearch) throw Error("Restoring the hand-merged colors is too combinatorial to enumerate safely. Shorten the pattern or reduce its multiplex capacity.");
  };
  const slotKey = (color, phase, duration) => `${color},${phase},${duration}`;
  const isRefinement = (finer, coarser) => finer.every(part => coarser.some(other => (part & other) === part));

  const liftPartition = groups => {
    partitionsSearched++;
    const slots = [], candidates = new Map(), remainingSlots = new Map();
    groups.forEach((group, color) => {
      const quotas = new Map();
      for (const id of group.projectedEdgeIds) {
        const edge = projected.pattern.edges[id], key = `${edge.phase},${edge.duration}`;
        quotas.set(key, (quotas.get(key) ?? 0) + 1);
      }
      for (let t = 0; t < period; t++) for (const [key, copies] of quotas) {
        const [phase, duration] = key.split(",").map(Number);
        if (t % projectedPeriod !== phase) continue;
        const slot = slotKey(color, t, duration);
        slots.push(slot); candidates.set(slot, []); remainingSlots.set(slot, copies);
      }
    });
    const units = [];
    groups.forEach((group, color) => {
      for (const cycle of cycles) {
        spend();
        const costs = new Map();
        for (const id of cycle) {
          const type = types[id], slot = slotKey(color, type.phase, type.duration);
          costs.set(slot, (costs.get(slot) ?? 0) + 1);
        }
        if ([...costs].some(([slot, cost]) => cost > (remainingSlots.get(slot) ?? 0))) continue;
        const unit = {cycle, color, costs: [...costs]};
        units.push(unit);
        for (const [slot] of unit.costs) candidates.get(slot).push(units.length - 1);
      }
    });
    const remaining = types.map(type => type.edgeIds.length), chosen = [];
    let found = false;
    const materialize = () => {
      found = true;
      const colorCounts = groups.map(() => Array(types.length).fill(0));
      for (const unit of chosen) for (const type of unit.cycle) colorCounts[unit.color][type]++;
      const signature = colorCounts.map(counts => counts.join(",")).sort().join(";");
      if (seen.has(signature)) return;
      seen.add(signature);
      const cursors = Array(types.length).fill(0);
      const edgeCycles = chosen.map(unit => unit.cycle.map(type => types[type].edgeIds[cursors[type]++]));
      const edgeCycleColors = chosen.map(unit => unit.color);
      const components = groups.map(group => ({...group, edgeIds: []}));
      edgeCycles.forEach((cycle, i) => components[edgeCycleColors[i]].edgeIds.push(...cycle));
      const solution = {edgeCycles, edgeCycleColors, components};
      solutions.push(solution); solutionCounts.set(solution, colorCounts);
      if (solutions.length > limits.maxDecompositions) throw Error(`This pattern has more than ${limits.maxDecompositions} lifted color groupings. Narrow the input before listing all of them.`);
    };
    const fits = unit => unit.costs.every(([slot, cost]) => remainingSlots.get(slot) >= cost)
      && unit.cycle.every(type => remaining[type] > 0);
    const search = () => {
      spend();
      /* Prefer the tightest remaining constraint to prune failed lifts early. */
      let pivot = null, choices = [];
      for (const slot of slots) {
        if (remainingSlots.get(slot) === 0) continue;
        const available = candidates.get(slot).filter(index => {
          spend();
          return fits(units[index]);
        });
        if (!available.length) return;
        if (pivot === null || available.length < choices.length) { pivot = slot; choices = available; }
      }
      if (pivot === null) {
        if (remaining.every(count => count === 0)) materialize();
        return;
      }
      /* Fill one multiplicity constraint in sorted cycle order, so exchanging
         identical copies does not repeat the same search branch. */
      const fillPivot = minimum => {
        if (remainingSlots.get(pivot) === 0) { search(); return; }
        for (const index of choices) {
          if (index < minimum) continue;
          spend();
          const unit = units[index];
          if (!fits(unit)) continue;
          for (const [slot, cost] of unit.costs) remainingSlots.set(slot, remainingSlots.get(slot) - cost);
          for (const type of unit.cycle) remaining[type]--;
          chosen.push(unit); fillPivot(index); chosen.pop();
          for (const type of unit.cycle) remaining[type]++;
          for (const [slot, cost] of unit.costs) remainingSlots.set(slot, remainingSlots.get(slot) + cost);
        }
      };
      fillPivot(0);
    };
    search();
    return found;
  };

  for (const projectedSolution of projected.solutions) {
    /* Compare types in the common projected period, with their phases intact.
       Identical copies remain inseparable in every candidate grouping. */
    const grouped = new Map();
    for (const component of projectedSolution.components) {
      const signature = component.edgeIds.map(id => {
        const edge = projected.pattern.edges[id]; return [edge.phase, edge.duration];
      }).sort((a, b) => a[0] - b[0] || a[1] - b[1]).map(edge => edge.join(",")).join(";");
      if (!grouped.has(signature)) grouped.set(signature, {projectedEdgeIds: [],
        typeEdgeIds: component.edgeIds, copies: 0, objects: 0});
      const group = grouped.get(signature);
      group.projectedEdgeIds.push(...component.edgeIds); group.copies++; group.objects += component.objects;
    }
    const atoms = [...grouped.values()];
    const initial = atoms.map((_, i) => 1n << BigInt(i));
    const queue = [initial], visited = new Set([initial.join(",")]), finest = [];
    const canonical = parts => parts.sort((a, b) => a < b ? -1 : a > b ? 1 : 0);
    for (let cursor = 0; cursor < queue.length; cursor++) {
      spend();
      const parts = queue[cursor];
      /* Breadth first visits every strict refinement before its coarsenings.
         Retain all incomparable finest partitions, even with different sizes. */
      if (finest.some(finer => { spend(); return isRefinement(finer, parts); })) continue;
      const groups = parts.map(part => {
        const members = atoms.filter((_, i) => (part & (1n << BigInt(i))) !== 0n);
        return {types: members, projectedEdgeIds: members.flatMap(member => member.projectedEdgeIds),
          objects: members.reduce((sum, member) => sum + member.objects, 0)};
      });
      if (liftPartition(groups)) { finest.push(parts); continue; }
      for (let i = 0; i < parts.length; i++) for (let j = i + 1; j < parts.length; j++) {
        spend();
        const coarser = canonical([...parts.filter((_, k) => k !== i && k !== j), parts[i] | parts[j]]);
        const signature = coarser.join(",");
        if (!visited.has(signature)) { visited.add(signature); queue.push(coarser); }
      }
    }
    if (finest.some(parts => parts.length < atoms.length)) coarsenedDecompositions++;
  }
  /* Different projected decompositions can yield comparable restorations.
     Compare multiplicities of original edge types, not arbitrary copy IDs. */
  const refinesColors = (finer, coarser) => {
    if (finer.length <= coarser.length) return false;
    const remaining = coarser.map(counts => [...counts]);
    const parts = [...finer].sort((a, b) => b.reduce((s, n) => s + n, 0) - a.reduce((s, n) => s + n, 0));
    const assign = index => {
      spend();
      if (index === parts.length) return remaining.every(counts => counts.every(n => n === 0));
      const part = parts[index];
      for (const counts of remaining) {
        if (part.some((n, i) => n > counts[i])) continue;
        part.forEach((n, i) => { counts[i] -= n; });
        const found = assign(index + 1);
        part.forEach((n, i) => { counts[i] += n; });
        if (found) return true;
      }
      return false;
    };
    return assign(0);
  };
  const finestSolutions = solutions.filter(coarser => !solutions.some(finer =>
    refinesColors(solutionCounts.get(finer), solutionCounts.get(coarser))));
  if (!finestSolutions.length) throw Error("No balanced hand-merged grouping was found within the input period.");
  return {pattern, cycles, solutions: finestSolutions, projectedPattern: projected.pattern, projectedPeriod,
    projectedDecompositions: projected.solutions.length, coarsenedDecompositions,
    partitionsSearched, searchSteps: budget.steps};
}

globalThis.ColorDecomposition = {colorEdgeTypes, simpleColorCycles,
  formatColorComponent, enumerateColorDecompositions, collapseHands, enumerateHandMergedDecompositions};
"""
