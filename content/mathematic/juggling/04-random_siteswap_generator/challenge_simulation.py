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
  <label>Balls<input id="balls" type="number" min="1" max="16" step="1" value="3" required></label>
  <label>Max Throw<input id="height" type="text" inputmode="text" value="7" maxlength="2" aria-describedby="heightHint" required></label>
  <label>Min Period<input id="minimum" type="number" min="1" max="64" step="1" value="2" required></label>
  <label>Max Period<input id="maximum" type="number" min="1" max="64" step="1" value="6" required></label>
  <label class="option"><input id="allowZero" type="checkbox" checked>Allow 0</label>
  <label class="option"><input id="primeOnly" type="checkbox">Prime loops only</label>
  <button id="generate" type="submit" class="primary">New Pattern</button>
</form>
<p id="heightHint" class="hint">Enter the maximum throw as a decimal integer, or use a–z for 10–35 and α–ω for 36–59.</p>
<output id="challengeStats" aria-live="polite"></output>
<div id="routinePhases" role="group" aria-label="Playback phases">
  <span id="leadIn"></span><span id="challengePhase">Challenge</span><span id="leadOut"></span>
</div>
<ol id="sequence" aria-label="Challenge siteswap, with one value per beat"></ol>
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
  const side = t % 2 === 0 ? "Left Hand" : "Right Hand", value = routine.values[beat];
  const progress = inChallenge ? `Challenge · Beat ${beat - routine.challengeStart + 1} / ${challenge.length}`
    : `${stage === "leadIn" ? "Lead-in" : "Recovery"} · ${routine.basicName} · Beat ${stage === "leadIn" ? beat + 1 : beat - routine.challengeEnd + 1} / ${routine.qualifyBeats}`;
  $("beatHint").textContent = `${progress} · ${side} · ` + (value === 0 ? "Empty beat" : value === 2 ? "Hold" : `${formatSiteswapValue(value)}-beat throw to the ${(t + value) % 2 === 0 ? "left" : "right"} hand`);
};
async function nextChallenge() {
  if ($("generate").disabled) return;
  $("generate").disabled = true;
  try {
    const settings = Object.fromEntries(["balls", "minimum", "maximum"].map(id => [id, $(id).value === "" ? NaN : Number($(id).value)]));
    settings.height = parseSiteswapValue($("height").value);
    settings.allowZero = $("allowZero").checked;
    settings.primeOnly = $("primeOnly").checked;
    message("Searching for a pattern that first returns to the ground state at the end…");
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
    $("leadIn").textContent = `Lead-in ${routine.basicName} · ${count(routine.qualifyBeats, "beat")}`;
    $("challengePhase").textContent = `Challenge · ${count(candidate.length, "beat")}`;
    $("leadOut").textContent = `Recovery ${routine.basicName} · ${count(routine.qualifyBeats, "beat")}`;
    $("sequence").replaceChildren(...candidate.map(value => { const item = document.createElement("li"); item.textContent = formatSiteswapValue(value); item.title = `${value} beats`; return item; }));
    load(candidate.join(" "), beats, {holdTwos: true, handLabels: ["L", "R"], horizontalScale: 0.35});
    $("challengeStats").textContent = `${count(settings.balls, "ball")} · shortest period ${count(candidate.length, "beat")} · highest throw ${formatSiteswapValue(Math.max(...candidate))}${settings.primeOnly ? " · prime loop" : ""}`;
    $("stats").textContent = `${count(routine.values.length, "beat")} per round · ${beats.length}-beat two-hand cycle · loops continuously`;
    message("A qualify comes before the challenge and another follows it. Recover into a stable basic pattern to complete the challenge.");
    running = !matchMedia("(prefers-reduced-motion: reduce)").matches;
    schedule();
  } catch (error) { message(error.message, true); }
  finally { $("generate").disabled = false; }
}
$("challengeForm").onsubmit = event => { event.preventDefault(); nextChallenge(); };
$("challengeForm").oninput = () => { message("Settings changed. Select New Pattern to apply them."); };
$("guides").checked = false;
nextChallenge();
"""
)

HTML = make_html(controls=CONTROLS, startup=STARTUP)
