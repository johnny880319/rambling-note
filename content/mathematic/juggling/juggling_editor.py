"""Shared textarea, keyboard behavior, and initial pattern for both notebooks."""

import json

DEFAULT_PATTERN = (
    "[1_1, 2_2, 3_3]\t|\t[2_3]\t|\t[]\n"
    "[1_3]\t\t\t|\t[]\t\t|\t[]\n"
    "[]\t\t\t\t|\t[3_2]\t|\t[2_3, 3_3]\n"
    "[]\t\t\t\t|\t[]\t\t|\t[3_2]\n"
    "[]\t\t\t\t|\t[]\t\t|\t[2_1]\n"
    "[]\t\t\t\t|\t[1_1]\t|\t[1_1]"
)

CSS = """
.juggling-editor {
  color-scheme: light dark;
  --editor-bg: #fff; --editor-ink: #23344a; --editor-muted: #596a81;
  --editor-line: #d7e0eb; --editor-accent: #2768ba;
  width: 100%; min-width: 0; color: var(--editor-ink);
  font: 14px/1.6 system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  .juggling-editor {
    --editor-bg: #1c293c; --editor-ink: #e0e9f5; --editor-muted: #a2b3cb;
    --editor-line: #3b4d65; --editor-accent: #8fbeff;
  }
}
.juggling-editor label { display: block; }
.juggling-editor .editor-hint { margin: 7px 0 12px; font-size: 13px; color: var(--editor-muted); }
.juggling-editor textarea {
  display: block; box-sizing: border-box; width: 100%; min-height: 112px;
  resize: vertical; padding: 5px 9px; border: 1px solid var(--editor-line);
  border-radius: 7px; background: var(--editor-bg); color: var(--editor-ink);
  font: 14px/1.6 ui-monospace, monospace; white-space: pre; tab-size: 4;
}
.juggling-editor textarea:focus-visible {
  outline: 2px solid var(--editor-accent); outline-offset: 2px;
}
"""

JAVASCRIPT = r"""
function createPatternEditor(root, {value, hint = "", describedBy = ""}) {
  root.classList.add("juggling-editor");
  root.innerHTML = `<label for="editor">一個週期的拋接資料</label>
    <p id="editorHint" class="editor-hint"></p>
    <textarea id="editor" rows="6" wrap="off" spellcheck="false"></textarea>`;
  const input = root.querySelector("textarea");
  root.querySelector(".editor-hint").textContent = "Tab 可對齊欄位；先按 Esc 再按 Tab 可離開輸入框。" + hint;
  input.setAttribute("aria-describedby", ["editorHint", describedBy].filter(Boolean).join(" "));
  input.value = value;
  let allowTabExit = false;
  const events = new AbortController();
  input.addEventListener("keydown", event => {
    if (event.key === "Escape") { allowTabExit = true; return; }
    if (event.key !== "Tab") { allowTabExit = false; return; }
    if (allowTabExit || event.shiftKey || event.ctrlKey || event.altKey || event.metaKey || event.isComposing) {
      allowTabExit = false;
      return;
    }
    event.preventDefault();
    /* Native insertion preserves undo history; setRangeText is the fallback. */
    if (typeof document.execCommand !== "function" || !document.execCommand("insertText", false, "\t")) {
      input.setRangeText("\t", input.selectionStart, input.selectionEnd, "end");
      input.dispatchEvent(new InputEvent("input", {bubbles: true, inputType: "insertText", data: "\t"}));
    }
  }, {signal: events.signal});
  input.addEventListener("blur", () => { allowTabExit = false; }, {signal: events.signal});
  return {input, destroy: () => { events.abort(); root.replaceChildren(); }};
}
"""

DEFAULT_PATTERN_JSON = json.dumps(DEFAULT_PATTERN, ensure_ascii=False)
