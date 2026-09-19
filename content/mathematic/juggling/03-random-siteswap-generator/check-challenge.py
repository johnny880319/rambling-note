"""Check first returns to ground, fundamental periods, and two-hand animation.

Run with `uv run python content/mathematic/juggling/03-random-siteswap-generator/check-challenge.py`.
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
sys.path[:0] = [str(SERIES), str(SERIES / "01-general_notation")]

import challenge_simulation
from siteswap_generator import JAVASCRIPT


class IframeSource(HTMLParser):
    source = ""

    def handle_starttag(self, tag, attrs):
        if tag == "iframe":
            self.source = dict(attrs)["srcdoc"]


iframe = IframeSource()
iframe.feed(mo.iframe(challenge_simulation.HTML).text)
scripts = re.findall(r"<script>(.*?)</script>", iframe.source, re.DOTALL)

CHECKS = r"""
const assert = require('node:assert/strict');
SCRIPTS.forEach(script => new (require('node:vm').Script)(script));
let seed = 7619, checked = 0, revisiting = 0;
const random = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 2**32; };
function firstReturn(values, balls) {
  const ground = (1n << BigInt(balls)) - 1n;
  let state = ground;
  for (let i=0;i<values.length;i++) {
    const h=values[i], catching=Boolean(state&1n);
    state >>= 1n;
    if (catching !== (h>0)) return false;
    if (h) {
      const slot=1n<<BigInt(h-1);
      if (state&slot) return false;
      state |= slot;
    }
    if (state===ground && i<values.length-1) return false;
  }
  return state===ground;
}
function traceStates(values, balls) {
  let state=(1n<<BigInt(balls))-1n;
  const states=[state];
  for(const h of values) {
    state >>= 1n;
    if(h) state |= 1n<<BigInt(h-1);
    states.push(state);
  }
  return states;
}
function repeatedLoop(values, balls) {
  const states=traceStates(values,balls);
  for(let start=0;start<values.length;start++) {
    for(let width=1;start+2*width<=values.length;width++) {
      if(states[start]!==states[start+width] || states[start]!==states[start+2*width]) continue;
      if(values.slice(start,start+width).every((h,i)=>h===values[start+width+i])) return true;
    }
  }
  return false;
}
const redundant=Array.from('5515045045045041',Number);
assert.ok(firstReturn(redundant,3));
assert.ok(repeatedLoop(redundant,3));
const trace=traceStates(redundant,3);
assert.equal(endsWithRepeatedLoop(redundant.slice(0,2),trace.slice(0,3)),false);
assert.equal(endsWithRepeatedLoop(redundant.slice(0,9),trace.slice(0,10)),true);
assert.equal(repeatedLoop(Array.from('5515041',Number),3),false);
function referenceExists({balls,height,minimum,maximum,allowZero=true}) {
  const ground=Array.from({length:balls},(_,i)=>i);
  function visit(landings,path) {
    const catching=landings.includes(0);
    const shifted=landings.filter(t=>t>0).map(t=>t-1);
    for(let h=allowZero ? 0 : 1;h<=height;h++) {
      if(catching!==(h>0) || (h>0 && shifted.includes(h-1))) continue;
      const next=(h ? [...shifted,h-1] : shifted).sort((a,b)=>a-b);
      const values=[...path,h];
      if(repeatedLoop(values,balls)) continue;
      if(next.every((t,i)=>t===ground[i])) {
        if(values.length>=minimum) return true;
      } else if(values.length<maximum && visit(next,values)) return true;
    }
    return false;
  }
  return visit(ground,[]);
}
function verify(settings, rng = random) {
  const values = generateSiteswap(settings, rng), p = values.length;
  assert.ok(p >= settings.minimum && p <= settings.maximum);
  assert.ok(values.every(h => Number.isInteger(h) && h >= 0 && h <= settings.height));
  if(settings.allowZero===false) assert.ok(values.every(h=>h>0));
  assert.equal(values.reduce((a,b) => a+b, 0), settings.balls * p);
  assert.equal(new Set(values.map((h,t) => (t+h)%p)).size, p);
  assert.equal(primitivePeriod(values), p);
  assert.ok(firstReturn(values,settings.balls),values.join(' '));
  assert.equal(repeatedLoop(values,settings.balls),false,values.join(' '));
  if(new Set(traceStates(values,settings.balls).slice(0,-1)).size<p) revisiting++;
  const beats = alternatingHands(values), pattern = buildPattern(beats);
  assert.equal(pattern.hands, 2);
  assert.equal(pattern.objects, settings.balls);
  assert.equal(pattern.balls.length, settings.balls);
  assert.equal(beats.length, p % 2 ? 2*p : p);
  beats.forEach((columns,t) => {
    assert.deepEqual(columns[1-t%2], []);
    assert.ok(columns[t%2].length <= 1);
    if (values[t%p]) assert.deepEqual(columns[t%2], [[(t+values[t%p])%2,values[t%p]]]);
    else assert.deepEqual(columns[t%2], []);
  });
  const original=[...values], routine=qualifyRoutine(values,settings.balls);
  const q=2*settings.balls, length=2*q+p;
  assert.deepEqual(values,original);
  assert.equal(routine.qualifyBeats,q);
  assert.equal(routine.challengeStart,q);
  assert.equal(routine.challengeEnd,q+p);
  assert.equal(routine.values.length,length);
  assert.deepEqual(routine.values.slice(q,q+p),values);
  assert.ok([...routine.values.slice(0,q),...routine.values.slice(q+p)].every(h=>h===settings.balls));
  const ground=(1n<<BigInt(settings.balls))-1n;
  const states=traceStates(routine.values,settings.balls);
  for(const t of [0,q,q+p,length]) assert.equal(states[t],ground);
  const wrapped=buildPattern(alternatingHands(routine.values));
  assert.equal(wrapped.objects,settings.balls);
  assert.equal(wrapped.balls.length,settings.balls);
  assert.equal(wrapped.period,length%2 ? 2*length : length);
  checked++;
  return values;
}
for (let balls=1; balls<=6; balls++) for (let height=balls; height<=12; height++) {
  for (let period=1; period<=12; period++) {
    const settings={balls,height,minimum:period,maximum:period};
    if ((balls===height && period>1) || ((balls===1 || height===balls+1) && period>height)) assert.throws(()=>generateSiteswap(settings));
    else for(let repeat=0;repeat<3;repeat++) {
      try { verify(settings); }
      catch(error) {
        assert.match(error.message,/找不到符合設定/);
        assert.equal(referenceExists(settings),false,JSON.stringify(settings));
        break;
      }
    }
  }
}
for(const period of [1,2,31,32,63,64]) {
  verify({balls:16,height:64,minimum:period,maximum:period});
  verify({balls:1,height:64,minimum:period,maximum:period},()=>0);
}
const periods = new Set();
for (let i=0;i<100;i++) periods.add(verify({balls:3,height:7,minimum:2,maximum:6}).length);
assert.deepEqual([...periods].sort(),[2,3,4,5,6]);
assert.ok(revisiting>0,'The generator must still allow non-prime loops.');
assert.deepEqual(generateSiteswap({balls:1,height:3,minimum:1,maximum:1,allowZero:false}),[1]);
assert.throws(()=>generateSiteswap({balls:1,height:3,minimum:2,maximum:3,allowZero:false}),/沒有空拍/);
for(let i=0;i<40;i++) verify({balls:3,height:7,minimum:2,maximum:6,allowZero:false});
for(const [value,label] of [[0,'0'],[9,'9'],[10,'a'],[25,'p'],[35,'z'],[36,'36'],[64,'64']]) {
  assert.equal(formatSiteswapValue(value),label);
}
for(const [source,value] of [['0',0],['09',9],['10',10],['64',64],['a',10],['A',10],['p',25],['z',35]]) {
  assert.equal(parseSiteswapValue(source),value);
}
for(const source of ['', 'a0', '-1', '3.5', '_']) assert.ok(Number.isNaN(parseSiteswapValue(source)));
// Independently enumerate small spaces to check the feasibility decisions.
for(let height=1;height<=4;height++) for(let p=1;p<=4;p++) {
  const possible=new Set();
  for(let code=0;code<(height+1)**p;code++) {
    let n=code; const a=Array.from({length:p},()=>{const h=n%(height+1);n=Math.floor(n/(height+1));return h;});
    const balls=a.reduce((x,y)=>x+y,0)/p;
    if(Number.isInteger(balls) && balls>0 && firstReturn(a,balls) && !repeatedLoop(a,balls)) possible.add(balls);
  }
  for(let balls=1;balls<=4;balls++) {
    const settings={balls,height,minimum:p,maximum:p};
    if(possible.has(balls)) verify(settings); else assert.throws(()=>generateSiteswap(settings));
  }
}
for (const settings of [
  {balls:0,height:5,minimum:1,maximum:3}, {balls:17,height:20,minimum:1,maximum:3},
  {balls:3,height:2,minimum:1,maximum:3}, {balls:3,height:65,minimum:1,maximum:3},
  {balls:3,height:7,minimum:4,maximum:3}, {balls:3,height:7,minimum:0,maximum:3},
  {balls:3,height:7,minimum:1,maximum:65}, {balls:3.5,height:7,minimum:1,maximum:3},
  {balls:NaN,height:7,minimum:1,maximum:3}, {balls:3,height:Infinity,minimum:1,maximum:3}
]) assert.throws(()=>generateSiteswap(settings));
const close=(a,b)=>assert.ok(Math.hypot(a.x-b.x,a.y-b.y)<0.001);
for(const [balls,values] of [[1,[3,0,0]],[2,[3,1]],[3,[5,3,1]],[3,[4,2]],[4,[5,3]],[4,[6,4,2]]]) {
  const routine=qualifyRoutine(values,balls);
  const pattern=buildPattern(alternatingHands(routine.values)),g=defaultGeometry(pattern);
  pattern.holdTwos=true;
  for(const dwell of [0.1,0.35,0.8]) for(const ball of pattern.balls) {
    for(const boundary of [routine.challengeStart,routine.challengeEnd,routine.values.length,pattern.period,2*pattern.period]) {
      close(ballPosition(pattern,g,ball,boundary-1e-7,dwell,true),ballPosition(pattern,g,ball,boundary+1e-7,dwell,true));
    }
  }
}
for(const values of [[2],[2,0],[5,2,2],[5,3,1],[4,4,1],[3,0,0]]) {
  const pattern=buildPattern(alternatingHands(values)), g=defaultGeometry(pattern);
  pattern.holdTwos=true;
  for(const dwell of [0.1,0.35,0.8]) for(const ball of pattern.balls) {
    for(const segment of ball.segments) {
      const event=ball.origin+segment.start;
      for(const t of [event,event+dwell]) close(ballPosition(pattern,g,ball,t-1e-7,dwell,true),ballPosition(pattern,g,ball,t+1e-7,dwell,true));
      if(segment.edge.duration===2) {
        const time=event+1;
        const point=ballPosition(pattern,g,ball,time,dwell,true);
        const hand=handPosition(pattern,g,segment.edge.source,time,dwell,true);
        assert.equal(point.held,true); close(point,{x:hand.x,y:hand.y-1.8});
      }
    }
  }
}
console.log(`Passed ${checked} challenges and qualify routines, exhaustive small-space feasibility, two-hand balance, and continuity across challenge and playback boundaries.`);
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
