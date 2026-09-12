"""Check browser trajectories and parity with the state-graph input notation.

Run with `uv run python content/mathematic/juggling/check-juggling.py`.
Node.js is also required.
No browser or npm packages are needed for these mathematical checks.
"""

import importlib.util
import json
import random
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import marimo as mo

JUGGLING = Path(__file__).resolve().parent


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


parser = load_module(
    "pattern_parser", JUGGLING / "02-juggling_states/pattern_parser.py"
)
editor = load_module("juggling_editor", JUGGLING / "juggling_editor.py")
widget_adapter = load_module("pattern_editor", JUGGLING / "02-juggling_states/pattern_editor.py")
load_module("animation_parser", JUGGLING / "01-general_notation/animation_parser.py")
state_graph = load_module("state_graph", JUGGLING / "02-juggling_states/state_graph.py")
simulation = load_module(
    "juggling_simulation", JUGGLING / "01-general_notation/juggling_simulation.py"
)

# Both frontends must keep the same tab stops and initial canonical pattern.
for line in editor.DEFAULT_PATTERN.splitlines():
    assert [i for i, char in enumerate(line.expandtabs(4)) if char == "|"] == [16, 28]
assert widget_adapter.PatternEditor.class_traits()["value"].default_value == editor.DEFAULT_PATTERN
subprocess.run(
    ["node", "--input-type=module", "--check"],
    input=widget_adapter.PatternEditor._esm,
    text=True,
    check=True,
)


class IframeSource(HTMLParser):
    source = ""

    def handle_starttag(self, tag, attrs):
        if tag == "iframe":
            self.source = dict(attrs)["srcdoc"]


# Exercise the actual embedding path: marimo strips newlines from srcdoc.
iframe = IframeSource()
iframe.feed(mo.iframe(simulation.HTML).text)
scripts = re.findall(r"<script>(.*?)</script>", iframe.source, re.DOTALL)
engine = scripts[0]

examples = [
    editor.DEFAULT_PATTERN,
    "9 7 5 3 1",
    "[9] [7] [5] [3] [1]",
    "9 7 5 31",
    "[3,4]",
    "[34]",
    "[3_1,4_1]",
    "3_2|0 0|3_1",
    "[3_2]|[] []|[3_1]",
    "[3_2,3_2]|0 0|[3_1,3_1]",
    "0|0",
    "[]|[]",
    "0|0|1_3",
    "1_1|0|0",
    "a",
    "p_1",
    "25_1",
    "a_1",
    "10_1",
    "36_1",
    "64_1",
    "p_2|p_1",
    "25_2|25_1",
    "[a_2,10_2,p_2,25_2]|[10_1,a_1,25_1,p_1]",
    "p",
    "3 p 2",
    "[3,p,2]",
    "25",
    "[25]",
    "[25_1]",
    "[1_1,2_2,3_3]|2_3|0 1_3|0|0 0|3_2|[2_3,3_3] 0|0|3_2 0|0|2_1 0|1_1|1_1",
    "5 3 1",
    "4 4 1",
    "7 5 3 1",
    "0",
    "{}",
    "{0}",
    "{3,4}",
    "{4,3,3}",
    "{a}",
    "{A}",
    "{10}",
    "{1s}",
    "(invalid)",
    "{(2,3)}|{} {}|{(1,3)}",
    "{(2,3)} {}|{(1,3)}",
    "{(2,3),(2,3)}|{} {}|{(1,3),(1,3)}",
    "{(1,2)}|{(2,2)}",
    "{(2,2),(1,2)}|{(2,2),(1,2)}",
    "{(4,3)}|{}|{(2,3)}|{} {}|{(3,3)}|{}|{(1,3)}",
    "{(2,1)}|{1}",
    "{(1,0),(1,3)}",
    "5 3 2",
    "{(2,3)}|{}",
]
# Permuting a multiset of vertices produces balanced periodic graphs; adding
# whole periods to edges tests throws that cross several period boundaries.
rng = random.Random(87)
for _ in range(80):
    hands, period = rng.randint(1, 5), rng.randint(1, 6)
    vertices = [(t, h) for t in range(period) for h in range(hands)]
    beats = [[[] for _ in range(hands)] for _ in range(period)]
    for _ in range(rng.randint(1, 3)):
        targets = rng.sample(vertices, len(vertices))
        for (t, h), (landing, target) in zip(vertices, targets):
            duration = (landing - t) % period + period * rng.randint(1, 3)
            beats[t][h].append((target, duration))
    examples.append("\n".join(state_graph.throw_label(beat, hands) for beat in beats))

first_beat = "[1_1,2_2,3_3]|2_3|0"
explicit_beat = "[1_1,2_2,3_3]|[2_3]|[]"
expected_beat = ((((0, 1), (1, 2), (2, 3)), ((2, 2),), ()),)
for duration in range(1, 65):
    text = f"{duration}_1"
    assert parser.parse_throws(text) == ((((0, duration),),),)
    examples.append(text)
    for spelling in (str(duration), f"[{duration}]", f"{{{duration}}}", f"{{(1,{duration})}}"):
        assert parser.parse_throws(spelling) == parser.parse_throws(text)
        examples.append(spelling)
    if duration < 36:
        symbol = "0123456789abcdefghijklmnopqrstuvwxyz"[duration]
        assert parser.parse_throws(f"{symbol}_1") == parser.parse_throws(text)
        examples.append(f"{symbol}_1")
assert parser.parse_throws("[a_2,10_2,p_2,25_2]") == (
    (((1, 10), (1, 10), (1, 25), (1, 25)), ()),
)
assert parser.parse_throws("25") == ((((0, 25),),),)
assert parser.parse_throws("[25]") == ((((0, 25),),),)
assert parser.parse_throws("2 5") == ((((0, 2),),), (((0, 5),),))
assert parser.parse_throws("[2,5]") == ((((0, 2), (0, 5)),),)
assert parser.parse_throws("[34]") == ((((0, 34),),),)
assert parser.parse_throws("[3,4]") == ((((0, 3), (0, 4)),),)
assert parser.parse_throws("[25_1]") == ((((0, 25),),),)
assert state_graph.throw_label((((0, 36),),), 1) == "36"
assert parser.parse_throws(first_beat) == expected_beat
assert parser.parse_throws(explicit_beat) == expected_beat
assert parser.parse_throws("9 7 5 3 1") == tuple(
    (((0, value),),) for value in (9, 7, 5, 3, 1)
)
assert parser.parse_throws("9 7 5 31") == tuple(
    (((0, value),),) for value in (9, 7, 5, 31)
)
assert parser.parse_throws("a\tb\np") == tuple(
    (((0, value),),) for value in (10, 11, 25)
)
examples.extend([first_beat, explicit_beat, "2 5", "[2,5]", "a\tb\np", "[a,b]", "[3_2] \t | []\n[] | [3_1]"])
invalid_inputs = [
    "97531",
    "[97531]",
    "65",
    "[65]",
    "ab",
    "[ab]",
    "1s",
    "[1s]",
    "{1s}",
    "{(1,1s)}",
    "[9][7][5][3][1]",
    "3[4]",
    "[3]4",
    "[3]|[4][5]",
    "",
    "[",
    "[3,]",
    "[3,,4]",
    "3_0",
    "3_17",
    "[3_2",
    "3_2|",
    "[3_2]|3",
    "-3",
    "[3_2] junk!",
    "[3_2]]",
    "1s_1",
    "[1s_1]",
    "ap_2",
    "[a_2_1]",
    "65_1",
    "3p2",
    "pp2",
    "25p2",
    "ap2",
    "[3p2]",
    "[pp2]",
    "[25p2,3_1]",
    "{3p2}",
    "3p2|0 0|3p1",
    "3_",
    "_2",
    "3__2",
    "3_2_1",
]
examples.extend(invalid_inputs)
canonical_fixtures = []
for text in examples:
    try:
        throws = parser.parse_throws(text)
    except ValueError:
        canonical_fixtures.append({"text": text, "invalid": True})
        continue
    canonical_fixtures.append({"text": text, "throws": throws})
    formatted = "\n".join(
        state_graph.throw_label(beat, len(throws[0])) for beat in throws
    )
    assert parser.parse_throws(formatted) == throws, (text, formatted)
for text in invalid_inputs:
    try:
        parser.parse_throws(text)
    except ValueError:
        pass
    else:
        raise AssertionError(f"Accepted malformed input: {text}")

fixtures = []
for text in examples:
    try:
        pattern = state_graph.read_pattern(text)
    except ValueError:
        fixtures.append({"text": text, "invalid": True})
        continue
    fixtures.append(
        {
            "text": text,
            "hands": pattern.hands,
            "period": len(pattern),
            "objects": pattern.objects,
            "throws": pattern.throws,
        }
    )

CHECKS = r"""
const assert = require('node:assert/strict');
const parsePattern = text => buildPattern(parseThrows(text));
for (const fixture of CANONICAL_FIXTURES) {
  if (fixture.invalid) assert.throws(() => parseThrows(fixture.text), fixture.text);
  else assert.deepEqual(parseThrows(fixture.text), fixture.throws, fixture.text);
}
SCRIPTS.forEach(script => new (require('node:vm').Script)(script));
const close = (a, b) => assert.ok(Math.hypot(a.x - b.x, a.y - b.y) < 0.001,
  `Discontinuous trajectory: (${a.x}, ${a.y}) -> (${b.x}, ${b.y})`);
let samples = 0;
for (const fixture of FIXTURES) {
  if (fixture.invalid) { assert.throws(() => parsePattern(fixture.text)); continue; }
  const p = parsePattern(fixture.text);
  assert.equal(p.hands, fixture.hands, fixture.text);
  assert.equal(p.period, fixture.period, fixture.text);
  assert.equal(p.objects, fixture.objects, fixture.text);
  assert.equal(p.balls.length, p.objects);
  assert.deepEqual(p.outgoing.map(row => row.map(edges => edges.map(e => [e.destination, e.duration]))), fixture.throws);
  const g = defaultGeometry(p);
  g.forEach((hand, h) => hand.forEach((points, t) => {
    points.catch = {x: 10 + (h * 13 + t * 7) % 70, y: 40 + (h * 17 + t * 3) % 40};
    points.throw = {x: 15 + (h * 17 + t * 9) % 70, y: 40 + (h * 11 + t * 7) % 40};
  }));
  for (const dwell of [0.1, 0.35, 0.8]) {
    for (const time of [-8.7, 0, 0.09, 0.35, 0.9, 1, 3.001, 23.4, 10000.3]) {
      const counts = Array(p.edges.length).fill(0);
      for (const ball of p.balls) {
        const point = ballPosition(p, g, ball, time, dwell, true);
        assert.ok(Number.isFinite(point.x) && Number.isFinite(point.y));
        counts[point.edge.id]++;
        close(point, ballPosition(p, g, ball, time + ball.length, dwell, true));
        samples++;
      }
      for (const edge of p.edges) {
        const expected = Math.floor((time - edge.phase) / p.period)
          - Math.floor((time - edge.phase - edge.duration) / p.period);
        assert.equal(counts[edge.id], expected, `Wrong occupancy: ${fixture.text}, t=${time}`);
      }
    }
    for (const ball of p.balls) for (const segment of ball.segments) {
      const event = ball.origin + segment.start;
      for (const time of [event, event + dwell]) {
        close(ballPosition(p, g, ball, time - 1e-7, dwell, true),
          ballPosition(p, g, ball, time + 1e-7, dwell, true));
      }
    }
    for (let h = 0; h < p.hands; h++) for (const phase of p.active[h]) {
      for (const time of [phase, phase + dwell]) {
        close(handPosition(p, g, h, time - 1e-7, dwell, true),
          handPosition(p, g, h, time + 1e-7, dwell, true));
      }
    }
  }
}
for (const text of ['', '{', '{(0,3)}', '{(1,-1)}', '{(1,1t)}', '{3,}', '{3}|', '{(17,1)}', Array(129).fill('{z}').join(' '), '{z,z,z,z,z,z,z,z}']) {
  assert.throws(() => parsePattern(text), text);
}
// Equal multiplex copies remain distinct in space, even with equal endpoints.
const multiplex = parsePattern('{3,3}'), geometry = defaultGeometry(multiplex);
for (const time of [0, 0.1, 0.35, 0.9]) {
  const points = multiplex.balls.map(ball => ballPosition(multiplex, geometry, ball, time, 0.35, true));
  const copies = points.filter(point => point.edge.phase === 0 && point.held);
  if (copies.length) assert.equal(new Set(copies.map(point => point.x)).size, copies.length);
}
console.log(`Passed ${FIXTURES.length} notation fixtures and ${samples} ball samples; event continuity and input limits passed.`);
"""
subprocess.run(
    ["node"],
    input=engine
    + "\nconst FIXTURES = "
    + json.dumps(fixtures)
    + ";\nconst CANONICAL_FIXTURES = "
    + json.dumps(canonical_fixtures)
    + ";\nconst SCRIPTS = "
    + json.dumps(scripts)
    + ";\n"
    + CHECKS,
    text=True,
    check=True,
)
