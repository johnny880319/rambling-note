"""Vanilla siteswap challenges using the shared multi-hand animation."""

from juggling_simulation import make_html
from siteswap_generator import JAVASCRIPT

CONTROLS = r"""
<style>
#challengeForm { display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: end; }
#challengeForm label { display: flex; flex-direction: column; align-items: start; gap: 3px; }
#challengeForm input { width: 92px; }
#challengeForm .option { flex-direction: row; align-items: center; padding-bottom: 6px; }
#challengeForm .option input { width: auto; }
#sequence { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0; padding: 0; list-style: none; }
#sequence li { font: 600 21px/1.5 ui-monospace, monospace; padding: 2px 9px; border: 1px solid var(--line); border-radius: 6px; }
#sequence li[aria-current=true] { color: var(--panel); background: var(--accent); border-color: var(--accent); }
#challengeStats { display: block; color: var(--accent); margin-top: 12px; }
#routinePhases { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
#routinePhases span { border: 1px solid var(--line); border-radius: 6px; padding: 4px 8px; }
#routinePhases span[aria-current=true] { border-color: var(--accent); color: var(--accent); font-weight: 600; }
#beatHint { min-height: 24px; }
</style>
<form id="challengeForm">
  <label>球數<input id="balls" type="number" min="1" max="16" step="1" value="3" required></label>
  <label>最大高度<input id="height" type="text" inputmode="text" value="7" maxlength="2" aria-describedby="heightHint" required></label>
  <label>最小週期<input id="minimum" type="number" min="1" max="64" step="1" value="2" required></label>
  <label>最大週期<input id="maximum" type="number" min="1" max="64" step="1" value="6" required></label>
  <label class="option"><input id="allowZero" type="checkbox" checked>允許空拍（0）</label>
  <button id="generate" type="submit" class="primary">下一題</button>
</form>
<p id="heightHint" class="hint">最大高度可輸入十進位整數，或以 a–z 代表 10–35。</p>
<output id="challengeStats" aria-live="polite"></output>
<div id="routinePhases" role="group" aria-label="循環播放流程">
  <span id="leadIn"></span><span id="challengePhase">挑戰</span><span id="leadOut"></span>
</div>
<ol id="sequence" aria-label="本題的 siteswap，各數字依序代表一拍"></ol>
<p id="beatHint"></p>
<span id="stats" class="hint"></span>
"""

STARTUP = (
    JAVASCRIPT
    + r"""
let challenge = null, routine = null, shownBeat = -1;
$("stage").before($("sequence"));
$("timelineLabel").before($("beatHint"));
onFrame = currentTime => {
  if (!routine) return;
  $("clock").textContent = `t = ${currentTime.toFixed(2)}`;
  const t = Math.floor(currentTime), beat = mod(t, routine.values.length);
  if (shownBeat === t) return;
  shownBeat = t;
  const inChallenge = beat >= routine.challengeStart && beat < routine.challengeEnd;
  const stage = beat < routine.challengeStart ? "leadIn" : inChallenge ? "challengePhase" : "leadOut";
  for (const id of ["leadIn", "challengePhase", "leadOut"]) $(id).setAttribute("aria-current", String(id === stage));
  [...$("sequence").children].forEach((item, i) => item.setAttribute("aria-current", String(inChallenge && i === beat - routine.challengeStart)));
  const side = t % 2 === 0 ? "左手" : "右手", value = routine.values[beat];
  const progress = inChallenge ? `挑戰 · 第 ${beat - routine.challengeStart + 1} / ${challenge.length} 拍`
    : `${stage === "leadIn" ? "起始運球" : "回穩運球"} · ${routine.basicName} · 第 ${stage === "leadIn" ? beat + 1 : beat - routine.challengeEnd + 1} / ${routine.qualifyBeats} 拍`;
  $("beatHint").textContent = `${progress} · ${side} · ` + (value === 0 ? "空拍" : value === 2 ? "持球" : `${formatSiteswapValue(value)} 拍後由${(t + value) % 2 === 0 ? "左手" : "右手"}接住`);
};
async function nextChallenge() {
  if ($("generate").disabled) return;
  $("generate").disabled = true;
  try {
    const settings = Object.fromEntries(["balls", "minimum", "maximum"].map(id => [id, $(id).value === "" ? NaN : Number($(id).value)]));
    settings.height = parseSiteswapValue($("height").value);
    settings.allowZero = $("allowZero").checked;
    message("正在尋找從基態出發、途中不回到基態的題目…");
    const search = searchSiteswap(settings);
    let step;
    do {
      step = search.next();
      if (!step.done) await new Promise(resolve => setTimeout(resolve, 0));
    } while (!step.done);
    const candidate = step.value;
    const nextRoutine = qualifyRoutine(candidate, settings.balls);
    const beats = alternatingHands(nextRoutine.values);
    /* Validate before replacing the displayed challenge or animation. */
    buildPattern(beats);
    challenge = candidate; routine = nextRoutine; shownBeat = -1;
    $("leadIn").textContent = `起始 ${routine.basicName} · ${routine.qualifyBeats} 拍`;
    $("challengePhase").textContent = `挑戰 · ${candidate.length} 拍`;
    $("leadOut").textContent = `回穩 ${routine.basicName} · ${routine.qualifyBeats} 拍`;
    $("sequence").replaceChildren(...candidate.map(value => { const item = document.createElement("li"); item.textContent = formatSiteswapValue(value); item.title = `${value} 拍`; return item; }));
    load(candidate.join(" "), beats, {holdTwos: true, handLabels: ["左手", "右手"], horizontalScale: 0.35});
    $("challengeStats").textContent = `${settings.balls} 顆球 · 最短週期 ${candidate.length} 拍 · 本題最高 ${formatSiteswapValue(Math.max(...candidate))}`;
    $("stats").textContent = `每輪 ${routine.values.length} 拍 · 雙手動作循環 ${beats.length} 拍 · 持續循環播放`;
    message("前後各接一個 qualify；完成題目後還要穩定回運，才算挑戰成功。");
    running = !matchMedia("(prefers-reduced-motion: reduce)").matches;
    schedule();
  } catch (error) { message(error.message, true); }
  finally { $("generate").disabled = false; }
}
$("challengeForm").onsubmit = event => { event.preventDefault(); nextChallenge(); };
$("challengeForm").oninput = () => { message("設定已修改；按「下一題」套用。"); };
$("guides").checked = false;
nextChallenge();
"""
)

HTML = make_html(controls=CONTROLS, startup=STARTUP)
