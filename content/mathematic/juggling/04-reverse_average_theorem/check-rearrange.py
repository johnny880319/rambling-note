"""Check Polster's rearrangement on every small integer-mean multiset.

Run with `uv run python content/mathematic/juggling/04-reverse_average_theorem/check-rearrange.py`.
Node.js is required; no browser packages are needed.
"""

import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import marimo as mo

SERIES = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(Path(__file__).resolve().parent), str(SERIES), str(SERIES / "01-general_notation")]

import rearrange_simulation
from rearrange_simulation import JAVASCRIPT


class IframeSource(HTMLParser):
    source = ""

    def handle_starttag(self, tag, attrs):
        if tag == "iframe":
            self.source = dict(attrs)["srcdoc"]


iframe = IframeSource()
iframe.feed(mo.iframe(rearrange_simulation.HTML).text)
scripts = re.findall(r"<script>(.*?)</script>", iframe.source, re.DOTALL)

CHECKS = r"""
const assert = require('node:assert/strict');
SCRIPTS.forEach(script => new (require('node:vm').Script)(script));
const sorted = values => [...values].sort((a, b) => a - b);
function* multisets(p, largest, start = 0, prefix = []) {
  if (prefix.length === p) { yield prefix; return; }
  for (let v = start; v <= largest; v++) yield* multisets(p, largest, v, [...prefix, v]);
}
// The lemma on the book's example: 53052630 with columns 2 and 4 replaced by 1, 1.
const book = substitute([5, 3, 0, 5, 2, 6, 3, 0], 2, 4, 1, 1);
assert.deepEqual(book.values, [0, 1, 5, 3, 1, 6, 3, 5]);
assert.equal(book.rounds, 4);
// The outer walk on the book's example 023355 visits the substitutions it lists.
const walk = createRearrangement([0, 2, 3, 3, 5, 5]), seen = [];
while (!walk.done) { const event = walk.step(); if (event.kind === 'substitute') seen.push([event.b0, event.b1]); }
assert.deepEqual(seen, [[2, 4], [3, 1], [3, 4], [5, 5]]);
assert.ok(isSiteswap(walk.values));
let checked = 0, exchanges = 0, longest = 0;
for (let p = 1; p <= 7; p++) {
  for (const values of multisets(p, p + 2)) {
    if (values.reduce((s, v) => s + v, 0) % p !== 0) continue;
    for (const order of [values, [...values].reverse()]) {
      const machine = createRearrangement(order);
      let rounds = 0;
      while (!machine.done) { const event = machine.step(); if (event.kind === 'exchange') { exchanges++; rounds++; longest = Math.max(longest, rounds); } if (event.kind !== 'exchange') rounds = 0; }
      assert.deepEqual(sorted(machine.values), sorted(order), `${order}: not a rearrangement`);
      assert.ok(isSiteswap(machine.values), `${order}: ${machine.values} fails the permutation test`);
      assert.ok(machine.values.every(v => v !== null));
      checked++;
    }
  }
}
assert.ok(longest <= 5, 'the lemma ends within p - 2 exchanges');
assert.deepEqual(rearrange([7]), [7]);
assert.deepEqual(sorted(rearrange([2, 5, 5, 2, 4, 6])), [2, 2, 4, 5, 5, 6]);
assert.deepEqual(parseSequence(' 2, 5 5  b α 1 '), [2, 5, 5, 11, 36, 1]);
assert.throws(() => parseSequence('4 3'), /not an integer/);
assert.throws(() => parseSequence('x1'), /Cannot read/);
assert.throws(() => parseSequence(''), /at least one/);
for (const [value, label] of [[9, '9'], [10, 'a'], [35, 'z'], [36, 'α'], [59, 'ω'], [60, '60']]) assert.equal(formatValue(value), label);
assert.equal(alternatingHands([3]).length, 2);
assert.equal(alternatingHands([6, 4, 2, 5, 5, 2]).length, 6);
console.log(`Passed ${checked} integer-mean sequences up to period 7 (${exchanges} exchanges, longest run ${longest}), the book's examples, parsing, formatting and layout checks.`);
"""

subprocess.run(
    ["node"],
    input=scripts[0]
    + JAVASCRIPT
    + "\nconst SCRIPTS="
    + json.dumps(scripts)
    + ";\n"
    + CHECKS,
    text=True,
    check=True,
)
