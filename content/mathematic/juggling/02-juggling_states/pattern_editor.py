# /// script
# dependencies = ["anywidget>=0.11.0", "traitlets>=5.16.1"]
# ///
"""Connect the shared juggling editor to marimo's reactive widget state."""

import json

import anywidget
import traitlets
from juggling_editor import CSS, DEFAULT_PATTERN, JAVASCRIPT


class PatternEditor(anywidget.AnyWidget):
    value = traitlets.Unicode(DEFAULT_PATTERN).tag(sync=True)
    traditional = traitlets.Bool(False).tag(sync=True)

    _esm = JAVASCRIPT + r"""
export default {
  render({model, el}) {
    const shadow = el.shadowRoot || el.attachShadow({mode: "open"});
    const style = document.createElement("style");
    style.textContent = __EDITOR_CSS__ + `
      .actions { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
      button { font: inherit; cursor: pointer; padding: 5px 9px; border-radius: 7px;
        color: var(--editor-ink); background: var(--editor-bg); border: 1px solid var(--editor-line); }
      button:focus-visible { outline: 2px solid var(--editor-accent); outline-offset: 2px; }
      .primary { background: var(--editor-accent); color: var(--editor-bg); border-color: var(--editor-accent); }
    `;
    const wrapper = document.createElement("div");
    wrapper.className = "juggling-editor";
    const root = document.createElement("div");
    const editor = createPatternEditor(root, {value: model.get("value"), traditional: model.get("traditional"), hint: "Select Apply after editing."});
    const actions = document.createElement("div");
    actions.className = "actions";
    const apply = document.createElement("button"), restore = document.createElement("button");
    apply.textContent = "Apply"; apply.className = "primary";
    restore.textContent = "Restore Current Pattern";
    const events = new AbortController();
    apply.addEventListener("click", () => {
      /* Model setters emit synchronously, so capture both edits before sync. */
      const value = editor.input.value, traditional = editor.notation.checked;
      model.set("value", value);
      model.set("traditional", traditional);
      model.save_changes();
    }, {signal: events.signal});
    const sync = () => { editor.input.value = model.get("value"); editor.notation.checked = model.get("traditional"); };
    restore.addEventListener("click", sync, {signal: events.signal});
    model.on("change:value", sync);
    model.on("change:traditional", sync);
    actions.append(apply, restore);
    wrapper.append(root, actions);
    shadow.append(style, wrapper);
    return () => { model.off("change:value", sync); model.off("change:traditional", sync); events.abort(); editor.destroy(); shadow.replaceChildren(); };
  }
};
""".replace("__EDITOR_CSS__", json.dumps(CSS))
