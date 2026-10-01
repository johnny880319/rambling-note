"""Interactive minimized color decompositions using the shared animation."""

from color_decomposition import JAVASCRIPT
from juggling_editor import DEFAULT_PATTERN_JSON
from juggling_simulation import make_html

CONTROLS = r"""
<style>
#decompositionControls { margin-top: 12px; }
#decomposition { min-width: min(100%, 320px); }
#decompositionStats { color: var(--accent); }
#colorLegend { display: grid; gap: 8px; margin: 12px 0; }
.color-component { border: 1px solid var(--line); border-left: 7px solid var(--color); border-radius: 7px; padding: 7px 9px; background: var(--panel); }
.color-component strong { color: var(--color); }
.color-component pre { margin: 5px 0 0; overflow: auto; font: 13px/1.5 ui-monospace, monospace; }
</style>
<div id="patternEditor"></div>
<div class="row">
  <button id="apply" class="primary">Decompose and Play</button>
  <button id="restore">Restore Current Pattern</button>
  <span id="stats"></span>
</div>
<div id="decompositionControls" hidden>
  <div class="row">
    <label>Minimized decomposition <select id="decomposition" aria-label="Minimized color decomposition"></select></label>
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
let colorResult = null, colorBeats = null, colorSource = "", colorChoice = 0;

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
  load(colorSource, colorBeats, {edgeCycles: solution.edgeCycles});
  $("decompositionStats").textContent = `${colorResult.solutions.length} minimized ${colorResult.solutions.length === 1 ? "decomposition" : "decompositions"} found · showing ${colorChoice + 1} of ${colorResult.solutions.length}`;
  $("colorLegend").replaceChildren(...solution.components.map((component, colorId) => {
    const card = document.createElement("div"), title = document.createElement("strong"), matrix = document.createElement("pre");
    card.className = "color-component"; card.style.setProperty("--color", ballColor(colorId));
    title.textContent = `Color ${colorId + 1} · ${count(component.objects, "object")}`;
    matrix.textContent = formatColorComponent(colorResult.pattern, component.edgeIds);
    card.append(title, matrix); return card;
  }));
  message("Every displayed color is an indecomposable periodic subpattern. Select another decomposition to compare all possibilities.");
  running = !matchMedia("(prefers-reduced-motion: reduce)").matches; schedule();
}

function decomposeAndPlay(text) {
  const beats = parseThrows(text), result = enumerateColorDecompositions(beats);
  colorResult = result; colorBeats = beats; colorSource = text; colorChoice = 0;
  $("decomposition").replaceChildren(...result.solutions.map(decompositionOption));
  $("decompositionControls").hidden = false;
  showColorDecomposition(0);
}

$("apply").onclick = () => {
  try { decomposeAndPlay($("editor").value); }
  catch (error) { message(error.message, true); }
};
$("restore").onclick = () => { $("editor").value = colorSource; message("Restored the pattern currently being played."); };
$("decomposition").onchange = () => showColorDecomposition(Number($("decomposition").value));
$("previousDecomposition").onclick = () => showColorDecomposition(colorChoice - 1);
$("nextDecomposition").onclick = () => showColorDecomposition(colorChoice + 1);
$("editor").value = colorCodeDefault;
decomposeAndPlay(colorCodeDefault);
"""
)

HTML = make_html(controls=CONTROLS, startup=STARTUP)
