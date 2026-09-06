import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Juggling States
    """)
    return


@app.cell
def _(mo):
    get_beat, set_beat = mo.state(0)
    return get_beat, set_beat


@app.cell(hide_code=True)
def _(mo, set_beat):
    pattern_input = mo.ui.text(
        value=(
            "{(1,1),(2,2),(3,3)}|{(3,2)}|{} {(3,1)}|{}|{} "
            "{}|{(2,3)}|{(3,2),(3,3)} {}|{}|{(2,3)} "
            "{}|{}|{(1,2)} {}|{(1,1)}|{(1,1)}"
        ),
        label="pattern",
        full_width=True,
        on_change=lambda _: set_beat(0),
    )
    pattern_input
    return (pattern_input,)


@app.cell(hide_code=True)
def _(pattern_input, state_graph):
    try:
        pattern = state_graph.read_pattern(pattern_input.value.strip())
    except ValueError as _error:
        pattern, background, trouble = None, None, str(_error)
    else:
        background, trouble = state_graph.surrounding(pattern), ""
    return background, pattern, trouble


@app.cell(hide_code=True)
def _(mo, pattern, set_beat):
    previous_beat_button = mo.ui.button(
        label="← 上一拍",
        value=0,
        on_click=lambda clicks: clicks + 1,
        on_change=lambda _: set_beat(lambda beat: max(0, beat - 1)),
    )
    next_beat_button = mo.ui.button(
        label="下一拍 →",
        value=0,
        on_click=lambda clicks: clicks + 1,
        on_change=lambda _: set_beat(
            lambda beat: min(len(pattern) if pattern else 0, beat + 1)
        ),
    )
    (
        mo.hstack(
            [previous_beat_button, next_beat_button],
            widths=[0.5, 0.5],
            align="center",
            gap=1,
        )
        if pattern
        else mo.md("")
    )
    return


@app.cell(hide_code=True)
def _(get_beat, mo, pattern, set_beat):
    _last = len(pattern) if pattern else 1
    beat_slider = mo.ui.slider(
        start=0,
        stop=_last,
        step=1,
        value=min(get_beat(), _last),
        show_value=True,
        full_width=True,
        label="第幾拍",
        on_change=set_beat,
    )
    beat_slider if pattern else mo.md("")
    return


@app.cell
def _(get_beat, pattern):
    beat_index = min(get_beat(), len(pattern)) if pattern else 0
    return (beat_index,)


@app.cell(hide_code=True)
def _(background, beat_index, mo, pattern, state_graph, trouble):
    if pattern is None:
        _view = mo.md(f"*{trouble}*")
    else:
        _shape = (
            f"{pattern.objects} 個物件、{pattern.hands} 隻手、"
            f"最大滯空 {pattern.height}、一格最多 {pattern.capacity} 顆"
        )
        if background is None:
            _shape += "（狀態空間太大，只畫這個 pattern 走過的循環）"

        _here = state_graph.state_label(pattern.states[beat_index % len(pattern)])
        if beat_index == 0:
            _step = f"起點 `{_here}`，尚未投擲"
        else:
            # The figure lights the throws already made, so the caption names
            # the last of them rather than the one still to come.
            _throw = state_graph.throw_label(
                pattern.throws[beat_index - 1], pattern.hands
            )
            _from = state_graph.state_label(pattern.states[beat_index - 1])
            _step = f"第 {beat_index} 拍：從 `{_from}` 丟 `{_throw}` 到 `{_here}`"
            if beat_index == len(pattern):
                _step += "，走完一個週期"

        _view = mo.vstack(
            [
                mo.md(f"*{_shape}*"),
                mo.md(f"*{_step}*"),
                state_graph.make_figure(
                    pattern, traced=beat_index, background=background
                ),
            ]
        )
    _view
    return


@app.cell(hide_code=True)
def _(mo, state_graph):
    mo.md(
        "一個狀態是 $\\mathcal{M}(\\mathcal{F})$ 的元素，寫成它在每個格子上的值；"
        "一次投擲是 juggling matrix 的一欄，每隻手一個 multiset，手與手之間用 `|` 分隔。"
        "以下由 `state_graph` 的標籤函式直接產生：\n\n"
        "| | state | throw |\n| --- | --- | --- |\n"
        + "\n".join(
            f"| {name} | `{state}` | `{throw}` |"
            for name, state, throw in state_graph.notation_examples()
        )
    )
    return


@app.cell
def _():
    import marimo as mo
    import state_graph

    return mo, state_graph


if __name__ == "__main__":
    app.run()
