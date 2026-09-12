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
    const editor = createPatternEditor(root, {value: model.get("value"), hint: "修改後按「套用」。"});
    const actions = document.createElement("div");
    actions.className = "actions";
    const apply = document.createElement("button"), restore = document.createElement("button");
    apply.textContent = "套用"; apply.className = "primary";
    restore.textContent = "還原目前資料";
    const events = new AbortController();
    apply.addEventListener("click", () => {
      model.set("value", editor.input.value);
      model.save_changes();
    }, {signal: events.signal});
    restore.addEventListener("click", () => { editor.input.value = model.get("value"); }, {signal: events.signal});
    const sync = () => { editor.input.value = model.get("value"); };
    model.on("change:value", sync);
    actions.append(apply, restore);
    wrapper.append(root, actions);
    shadow.append(style, wrapper);
    return () => { model.off("change:value", sync); events.abort(); editor.destroy(); shadow.replaceChildren(); };
  }
};
""".replace("__EDITOR_CSS__", json.dumps(CSS))
