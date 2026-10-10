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

function verify(text, expected = null, traditional = false) {
  const beats=parseThrows(text, traditional), result=enumerateColorDecompositions(beats), base=buildPattern(beats);
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
verify('97531',1,true);
verify('(6x,4)*',1,true);
verify('(4,2)(2x,[44x])',null,true);
verify('[33]',1,true);
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


let liftChecked=0, unliftableChecked=0, liftLimitChecked=false;
const groupingSignature=(pattern,groups)=>groups.map(ids=>formatColorComponent(pattern,ids)).sort().join('\n---\n');
function verifyLift(beats, expectedObjects=null) {
  const result=enumerateHandMergedDecompositions(beats), base=buildPattern(beats);
  assert.equal(result.pattern.hands,base.hands);
  assert.equal(result.pattern.period,base.period);
  assert.equal(result.projectedPattern.hands,1);
  assert.equal(result.projectedPattern.objects,base.objects);
  const seenGroupings=new Set();
  for(const solution of result.solutions) {
    const seen=new Set(), groups=solution.components.map(c=>c.edgeIds);
    const typeSignatures=new Set();
    assert.equal(solution.edgeCycleColors.length,solution.edgeCycles.length);
    if(expectedObjects!==null) assert.deepEqual(solution.components.map(c=>c.objects).sort((a,b)=>a-b),[...expectedObjects].sort((a,b)=>a-b));
    solution.edgeCycles.forEach((cycle,index)=>{
      const color=solution.edgeCycleColors[index];
      assert.ok(Number.isInteger(color) && color>=0 && color<solution.components.length);
      for(let i=0;i<cycle.length;i++) {
        const id=cycle[i],edge=base.edges[id],next=base.edges[cycle[(i+1)%cycle.length]];
        assert.ok(!seen.has(id));seen.add(id);
        assert.equal(edge.destination,next.source);
        assert.equal((edge.phase+edge.duration)%base.period,next.phase);
        assert.ok(solution.components[color].edgeIds.includes(id));
      }
    });
    assert.equal(seen.size,base.edges.length);
    solution.components.forEach(component=>{
      const typeSignature=formatColorComponent(result.projectedPattern,component.typeEdgeIds);
      assert.ok(!typeSignatures.has(typeSignature),'Identical projected types must share one color');
      typeSignatures.add(typeSignature);
      assert.ok(Number.isSafeInteger(component.copies) && component.copies>0);
      assert.equal(component.projectedEdgeIds.length,component.typeEdgeIds.length*component.copies);
      const typePattern=buildPattern(parseThrows(typeSignature));
      assert.equal(typePattern.objects*component.copies,component.objects);
      assert.equal(enumerateColorDecompositions(parseThrows(typeSignature)).solutions[0].components.length,1);
      const restored=buildPattern(parseThrows(formatColorComponent(base,component.edgeIds)));
      assert.equal(restored.objects,component.objects);
      assert.equal(component.edgeIds.reduce((sum,id)=>sum+base.edges[id].duration,0)/base.period,component.objects);
      const projectedRows=Array.from({length:result.projectedPeriod},()=>[]);
      for(const id of component.projectedEdgeIds) {
        const edge=result.projectedPattern.edges[id];projectedRows[edge.phase].push(edge.duration);
      }
      for(let t=0;t<result.projectedPeriod;t++) {
        const typeDurations=component.typeEdgeIds.filter(id=>result.projectedPattern.edges[id].phase===t).map(id=>result.projectedPattern.edges[id].duration);
        assert.deepEqual(projectedRows[t].sort((a,b)=>a-b),Array.from({length:component.copies},()=>typeDurations).flat().sort((a,b)=>a-b));
      }
      for(let t=0;t<base.period;t++) {
        const durations=component.edgeIds.filter(id=>base.edges[id].phase===t).map(id=>base.edges[id].duration).sort((a,b)=>a-b);
        assert.deepEqual(durations,projectedRows[t%result.projectedPeriod].sort((a,b)=>a-b));
      }
    });
    const signature=groupingSignature(base,groups);
    assert.ok(!seenGroupings.has(signature),'Color permutations or equal copies must not duplicate a grouping');seenGroupings.add(signature);
    const animated=buildPattern(beats,{edgeCycles:solution.edgeCycles,edgeCycleColors:solution.edgeCycleColors});
    assert.equal(animated.balls.length,base.objects);
    solution.components.forEach((component,color)=>assert.equal(animated.balls.filter(ball=>ball.colorId===color).length,component.objects));
    const geometry=defaultGeometry(animated);
    for(const ball of animated.balls) for(const segment of ball.segments) for(const boundary of [0,0.35]) {
      const t=ball.origin+segment.start+boundary;
      const a=ballPosition(animated,geometry,ball,t-1e-7,0.35,true),b=ballPosition(animated,geometry,ball,t+1e-7,0.35,true);
      assert.ok(Math.hypot(a.x-b.x,a.y-b.y)<0.001);
      assert.equal(a.edge.colorId,ball.colorId);assert.equal(b.edge.colorId,ball.colorId);
    }
    liftChecked++;
  }
  return result;
}
const five=verifyLift(parseThrows('97531',true),[2,2,1]);
assert.equal(five.projectedPeriod,5);
assert.equal(five.pattern.period,10);
assert.deepEqual(five.solutions[0].components.map(c=>c.projectedEdgeIds.map(id=>five.projectedPattern.edges[id].duration).sort((a,b)=>a-b)),[[1,9],[3,7],[5]]);
const sync=verifyLift(parseThrows('(6x,4)*',true),[2,3]);
assert.equal(sync.projectedPeriod,2);
assert.equal(sync.pattern.period,4);
assert.deepEqual(sync.solutions[0].components.map(c=>c.projectedEdgeIds.map(id=>sync.projectedPattern.edges[id].duration)),[[4],[6]]);
assert.throws(()=>enumerateHandMergedDecompositions(parseThrows('(6x,4)',true)),/Balance fails/);
assert.deepEqual(collapseHands(parseThrows('[1,1] [1]')),[[[[0,1],[0,1]]],[[[0,1]]]]);
assert.deepEqual(collapseHands(parseThrows('4_1|6_2 []|[] 6_1|4_2 []|[]')),[[[[0,4],[0,6]]],[[]]]);
verifyLift(parseThrows('9 7 5 3 1'),[2,2,1]);
verifyLift(parseThrows('0|0'),[]);
verifyLift(parseThrows('[1_1,1_1]|[1_2,1_2]'),[4]);
const identicalTypes=verifyLift(parseThrows('2_1|2_2 2_1|2_2'),[4]);
assert.equal(identicalTypes.solutions.length,1);
const partial=verifyLift(parseThrows('5_2|1_1 3_2|1_1'),[2,3]);
assert.equal(partial.projectedDecompositions,2);
assert.equal(partial.unliftableDecompositions,1);
assert.equal(partial.solutions.length,1);
assert.throws(()=>enumerateHandMergedDecompositions(parseThrows('1_2|2_1')),/within the input period/);
assert.throws(()=>enumerateHandMergedDecompositions(parseThrows('3',true),{maxSearch:0}),/combinatorial/);
assert.throws(()=>buildPattern(parseThrows('3',true),{edgeCycles:[[0,1]],edgeCycleColors:[]}),/valid color index/);
assert.throws(()=>buildPattern(parseThrows('3',true),{edgeCycles:[[0,1]],edgeCycleColors:[-1]}),/valid color index/);

// An independent oracle assigns colors to individual edges and checks balance;
// it does not use the lifted-cycle exact-cover search.
function referenceLifts(beats) {
  const base=buildPattern(beats), projected=enumerateColorDecompositions(collapseHands(beats)), signatures=new Set();
  for(const solution of projected.solutions) {
    const types=new Map();
    for(const component of solution.components) {
      const key=formatColorComponent(projected.pattern,component.edgeIds);
      if(!types.has(key)) types.set(key,new Map());
      const quotas=types.get(key);
      for(const id of component.edgeIds) {
        const edge=projected.pattern.edges[id],slot=`${edge.phase},${edge.duration}`;
        quotas.set(slot,(quotas.get(slot) ?? 0)+1);
      }
    }
    const remaining=[...types.values()].map(quotas=>{
      const counts=new Map();
      for(let t=0;t<base.period;t++) for(const [slot,copies] of quotas) {
        const [phase,duration]=slot.split(',').map(Number);
        if(t%projected.pattern.period===phase) counts.set(`${t},${duration}`,copies);
      }
      return counts;
    });
    const groups=remaining.map(()=>[]);
    function assign(index) {
      if(index===base.edges.length) {
        if(remaining.some(counts=>[...counts.values()].some(n=>n!==0))) return;
        for(const ids of groups) {
          const balance=Array(base.period*base.hands).fill(0);
          for(const id of ids) {
            const edge=base.edges[id];balance[edge.phase*base.hands+edge.source]++;
            balance[((edge.phase+edge.duration)%base.period)*base.hands+edge.destination]--;
          }
          if(balance.some(n=>n!==0)) return;
        }
        signatures.add(groupingSignature(base,groups));return;
      }
      const edge=base.edges[index],key=`${edge.phase},${edge.duration}`;
      remaining.forEach((counts,color)=>{
        const count=counts.get(key) ?? 0;
        if(!count) return;
        counts.set(key,count-1);groups[color].push(edge.id);assign(index+1);
        groups[color].pop();counts.set(key,count);
      });
    }
    assign(0);
  }
  return signatures;
}
function compareLifts(beats) {
  try {buildPattern(beats);} catch(error){assert.match(error.message,/Balance fails/);return;}
  const expected=referenceLifts(beats);
  if(!expected.size) {
    assert.throws(()=>enumerateHandMergedDecompositions(beats),/cannot be restored|can be restored/);unliftableChecked++;
  } else {
    const result=verifyLift(beats);
    const actual=new Set(result.solutions.map(s=>groupingSignature(result.pattern,s.components.map(c=>c.edgeIds))));
    assert.deepEqual(actual,expected);
    if(!liftLimitChecked && result.projectedDecompositions===1 && result.solutions.length>1) {
      assert.throws(()=>enumerateHandMergedDecompositions(beats,{maxDecompositions:1}),/more than 1 lifted/);
      liftLimitChecked=true;
    }
  }
}
const handOptions=[[]];
for(let target=0;target<2;target++) for(let duration=1;duration<=3;duration++) handOptions.push([[target,duration]]);
for(let period=1;period<=2;period++) for(let code=0;code<handOptions.length**(2*period);code++) {
  let n=code;
  const beats=Array.from({length:period},()=>Array.from({length:2},()=>{const hand=handOptions[n%handOptions.length];n=Math.floor(n/handOptions.length);return hand.map(slot=>[...slot]);}));
  compareLifts(beats);
}
const multiplexOptions=[...handOptions];
for(let a=1;a<handOptions.length;a++) for(let b=a;b<handOptions.length;b++) multiplexOptions.push([...handOptions[a],...handOptions[b]]);
for(const left of multiplexOptions) for(const right of multiplexOptions) compareLifts([[left,right]]);
// Generate branching multiplex paths with shared projected edges, so distinct
// types can have more than one balanced assignment to the original hands.
const destinations=[];
for(let a=0;a<2;a++) for(let b=a;b<2;b++) destinations.push([a,b]);
for(const left of destinations) for(const right of destinations) for(let mask=0;mask<16;mask++) {
  const beats=[
    [left.map(target=>[target,1]),right.map(target=>[target,1])],
    Array.from({length:2},(_,hand)=>Array.from({length:2},(_,rank)=>[(mask>>(hand*2+rank))&1,rank*2+1]))
  ];
  compareLifts(beats);
}
assert.ok(liftLimitChecked,'Generated patterns must exercise the lifted-grouping limit');
console.log(`Passed ${liftChecked} type color groupings against independent edge-color enumeration and ${unliftableChecked} unliftable patterns; identical-copy merging, shortest projected periods, multiplex counts, trajectories, and input limits passed.`);
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
