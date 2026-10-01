"""Check exhaustive minimized periodic color decompositions.

Run with `uv run python content/mathematic/juggling/03-color_code/check-color-code.py`.
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
sys.path[:0] = [
    str(Path(__file__).resolve().parent),
    str(SERIES),
    str(SERIES / "01-general_notation"),
]

import color_code_simulation
from color_decomposition import JAVASCRIPT
from juggling_editor import DEFAULT_PATTERN


class IframeSource(HTMLParser):
    source = ""

    def handle_starttag(self, tag, attrs):
        if tag == "iframe":
            self.source = dict(attrs)["srcdoc"]


iframe = IframeSource()
iframe.feed(mo.iframe(color_code_simulation.HTML).text)
scripts = re.findall(r"<script>(.*?)</script>", iframe.source, re.DOTALL)

CHECKS = r"""
const assert = require('node:assert/strict');
SCRIPTS.forEach(script => new (require('node:vm').Script)(script));
let checked = 0;

function verify(text, expected = null) {
  const beats=parseThrows(text), result=enumerateColorDecompositions(beats), base=buildPattern(beats);
  if(expected!==null) assert.equal(result.solutions.length,expected,text);
  const decompositions=new Set();
  for(const solution of result.solutions) {
    const seen=new Set(), matrices=[];
    assert.equal(solution.edgeCycles.length,solution.components.length);
    solution.edgeCycles.forEach((cycle,colorId) => {
      assert.ok(cycle.length>0);
      const vertices=cycle.map(id => {
        assert.ok(!seen.has(id)); seen.add(id);
        const edge=base.edges[id]; return edge.phase*base.hands+edge.source;
      });
      assert.equal(new Set(vertices).size,vertices.length,'Every minimized component is a simple directed cycle.');
      cycle.forEach((id,index) => {
        const edge=base.edges[id], next=base.edges[cycle[(index+1)%cycle.length]];
        assert.equal((edge.phase+edge.duration)%base.period,next.phase);
        assert.equal(edge.destination,next.source);
      });
      const component=solution.components[colorId];
      assert.equal(cycle.reduce((sum,id)=>sum+base.edges[id].duration,0),component.objects*base.period);
      const matrix=formatColorComponent(base,component.edgeIds);
      const rendered=buildPattern(parseThrows(matrix));
      assert.equal(rendered.objects,component.objects);
      matrices.push(matrix);
    });
    assert.equal(seen.size,base.edges.length);
    const animated=buildPattern(beats,{edgeCycles:solution.edgeCycles});
    assert.equal(animated.objects,base.objects);
    for(let colorId=0;colorId<solution.components.length;colorId++) {
      assert.equal(animated.balls.filter(ball=>ball.colorId===colorId).length,solution.components[colorId].objects);
    }
    const signature=matrices.sort().join('\n---\n');
    assert.ok(!decompositions.has(signature),'Color names must not create duplicate decompositions.');
    decompositions.add(signature);
    checked++;
  }
  return result;
}

const shared=verify(SHARED_DEFAULT,4);
assert.deepEqual(shared.solutions.map(solution=>solution.components.map(component=>component.objects).sort((a,b)=>a-b)),
  [[1,1,1,2,3],[1,1,1,1,4],[1,1,3,3],[1,1,2,4]]);
const example=verify(`[1, 2]
[1, 2]
[1, 2]`,2);
assert.deepEqual(example.solutions.map(solution=>solution.components.map(component=>component.objects)),[[1,2],[1,1,1]]);
verify('3',1);
const identical=verify('[1, 1]',1);
assert.equal(identical.solutions[0].components.length,2);
verify('[1_2] | [1_1]',1);
verify('[1_2, 1_3] | [1_1, 1_3] | [1_1, 1_2]',2);
assert.throws(()=>enumerateColorDecompositions(parseThrows(`[1, 2]
[1, 2]
[1, 2]`),{maxDecompositions:1}),/more than 1/);
assert.throws(()=>buildPattern(parseThrows('1 2')),/Balance fails/);
assert.throws(()=>buildPattern(parseThrows('3'),{edgeCycles:[]}),/does not cover every throw/);
assert.throws(()=>enumerateColorDecompositions(parseThrows(`[${Array(97).fill('1').join(', ')}]`)),/at most 96 throws/);

for(let period=1;period<=5;period++) {
  const total=5**period;
  for(let code=0;code<total;code++) {
    let value=code;
    const throws=Array.from({length:period},()=>{const height=value%5+1;value=Math.floor(value/5);return height;});
    const text=throws.join(' ');
    try { buildPattern(parseThrows(text)); }
    catch(error) { assert.match(error.message,/Balance fails/); continue; }
    verify(text,1);
  }
}

const pairs=[];
for(let a=1;a<=3;a++) for(let b=a;b<=3;b++) pairs.push(`[${a}, ${b}]`);
for(let first=0;first<pairs.length;first++) for(let second=0;second<pairs.length;second++) for(let third=0;third<pairs.length;third++) {
  const text=[pairs[first],pairs[second],pairs[third]].join('\n');
  try { buildPattern(parseThrows(text)); }
  catch(error) { assert.match(error.message,/Balance fails/); continue; }
  verify(text);
}

console.log(`Passed ${checked} minimized decompositions, including every valid one-hand capacity-1 pattern through period 5 and small capacity-2 patterns.`);
"""

subprocess.run(
    ["node"],
    input=scripts[0]
    + JAVASCRIPT
    + "\nconst SCRIPTS="
    + json.dumps(scripts)
    + ";\n"
    + "const SHARED_DEFAULT="
    + json.dumps(DEFAULT_PATTERN)
    + ";\n"
    + CHECKS,
    text=True,
    check=True,
)
