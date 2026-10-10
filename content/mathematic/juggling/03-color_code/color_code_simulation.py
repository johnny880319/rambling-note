"""Interactive minimized color decompositions using the shared animation."""

from color_decomposition import JAVASCRIPT
from juggling_editor import DEFAULT_PATTERN_JSON
from juggling_simulation import make_html

CONTROLS = r"""
<style>
#decompositionControls { margin-top: 12px; }
#decompositionControls .row > label { flex-wrap: wrap; min-width: 0; max-width: 100%; }
#decompositionLabel { white-space: nowrap; }
#decomposition { min-width: min(100%, 320px); max-width: 100%; }
#decompositionStats { color: var(--accent); }
#colorLegend { display: grid; gap: 8px; margin: 12px 0; }
.color-component { border: 1px solid var(--line); border-left: 7px solid var(--color); border-radius: 7px; padding: 7px 9px; background: var(--panel); }
.color-component strong { color: var(--color); }
.color-component pre { margin: 5px 0 0; overflow: auto; font: 13px/1.5 ui-monospace, monospace; }
</style>
<div id="patternEditor"></div>
<div class="row">
  <label><input id="mergeHands" type="checkbox">Ignore Hands and Group Identical Components</label>
</div>
<div class="row">
  <button id="apply" class="primary">Decompose and Play</button>
  <button id="restore">Restore Current Pattern</button>
  <span id="stats"></span>
</div>
<div id="decompositionControls" hidden>
  <div class="row">
    <label><span id="decompositionLabel">Minimized decomposition</span> <select id="decomposition" aria-label="Color decomposition or finest restored grouping"></select></label>
    <button id="previousDecomposition" type="button">Previous</button>
    <button id="nextDecomposition" type="button">Next</button>
  </div>
  <output id="decompositionStats" aria-live="polite"></output>
  <div id="colorLegend" aria-label="Color components"></div>
</div>
"""

STARTUP = (
    JAVASCRIPT
    + "\nconst colorCodeDefault = "
    + DEFAULT_PATTERN_JSON
    + r""";
let colorResult = null, colorBeats = null, colorSource = "", colorTraditional = false, colorMergeHands = false, colorChoice = 0;

function decompositionOption(solution, index) {
  const option = document.createElement("option");
  option.value = index;
  option.textContent = `${index + 1} — ${count(solution.components.length, "color")} · b = ${solution.components.map(component => component.objects).join(" + ") || "0"}`;
  return option;
}

function showColorDecomposition(index) {
  colorChoice = mod(index, colorResult.solutions.length);
  const solution = colorResult.solutions[colorChoice];
  $("decomposition").value = colorChoice;
  load(colorSource, colorBeats, {edgeCycles: solution.edgeCycles, edgeCycleColors: solution.edgeCycleColors, traditional: colorTraditional, holdTwos: colorTraditional, handLabels: colorTraditional ? ["L", "R"] : undefined});
  $("mergeHands").checked = colorMergeHands;
  $("decompositionLabel").textContent = colorMergeHands ? "Finest restored grouping" : "Minimized decomposition";
  $("decompositionStats").textContent = colorMergeHands
    ? `Hand-merged period ${count(colorResult.projectedPeriod, "beat")} · original hand cycle ${count(colorResult.pattern.period, "beat")} · ${count(colorResult.solutions.length, "finest grouping")} · showing ${colorChoice + 1} of ${colorResult.solutions.length}${colorResult.coarsenedDecompositions ? ` · ${count(colorResult.coarsenedDecompositions, "projected decomposition")} required type merging` : ""}`
    : `${colorResult.solutions.length} minimized ${colorResult.solutions.length === 1 ? "decomposition" : "decompositions"} found · showing ${colorChoice + 1} of ${colorResult.solutions.length}`;
  $("colorLegend").replaceChildren(...solution.components.map((component, colorId) => {
    const card = document.createElement("div"), title = document.createElement("strong");
    card.className = "color-component"; card.style.setProperty("--color", ballColor(colorId));
    title.textContent = `Color ${colorId + 1} · ${count(component.objects, "object")}`;
    card.append(title);
    if (colorMergeHands) {
      if (component.types.length > 1) title.textContent += ` · ${count(component.types.length, "type")}`;
      else if (component.types[0].copies > 1) title.textContent += ` · ${component.types[0].copies} copies`;
      component.types.forEach((type, index) => {
        if (component.types.length > 1) {
          const label = document.createElement("p");
          label.textContent = `Type ${index + 1} · ${type.copies} ${type.copies === 1 ? "copy" : "copies"}`;
          card.append(label);
        }
        const matrix = document.createElement("pre");
        matrix.textContent = formatColorComponent(colorResult.projectedPattern, type.typeEdgeIds);
        card.append(matrix);
      });
    } else {
      const matrix = document.createElement("pre");
      matrix.textContent = formatColorComponent(colorResult.pattern, component.edgeIds);
      card.append(matrix);
    }
    return card;
  }));
  if (colorMergeHands) {
    [...$("colorLegend").children].forEach((card, colorId) => {
      const details = document.createElement("details"), summary = document.createElement("summary"), matrix = document.createElement("pre");
      summary.textContent = "Original Hand Paths";
      matrix.textContent = formatColorComponent(colorResult.pattern, solution.components[colorId].edgeIds);
      details.append(summary, matrix); card.append(details);
    });
  }
  message(colorMergeHands
    ? "Identical hand-merged types share a color; different types merge when needed to balance the original hands. All finest restorations are listed."
    : "Every displayed color is an indecomposable periodic subpattern. Select another decomposition to compare all possibilities.");
  running = !matchMedia("(prefers-reduced-motion: reduce)").matches; schedule();
}

function decomposeAndPlay(text, traditional = false, mergeHands = false) {
  const beats = parseThrows(text, traditional);
  const result = mergeHands ? enumerateHandMergedDecompositions(beats) : enumerateColorDecompositions(beats);
  colorResult = result; colorBeats = beats; colorSource = text; colorTraditional = traditional; colorMergeHands = mergeHands; colorChoice = 0;
  $("decomposition").replaceChildren(...result.solutions.map(decompositionOption));
  $("decompositionControls").hidden = false;
  showColorDecomposition(0);
}

$("apply").onclick = () => {
  try { decomposeAndPlay($("editor").value, $("traditionalNotation").checked, $("mergeHands").checked); }
  catch (error) { message(error.message, true); }
};
$("restore").onclick = () => {
  $("editor").value = colorSource; $("traditionalNotation").checked = colorTraditional;
  $("mergeHands").checked = colorMergeHands;
  message("Restored the pattern currently being played.");
};
$("decomposition").onchange = () => showColorDecomposition(Number($("decomposition").value));
$("previousDecomposition").onclick = () => showColorDecomposition(colorChoice - 1);
$("nextDecomposition").onclick = () => showColorDecomposition(colorChoice + 1);
$("editor").value = colorCodeDefault;
decomposeAndPlay(colorCodeDefault);
"""
)

HTML = make_html(controls=CONTROLS, startup=STARTUP)
