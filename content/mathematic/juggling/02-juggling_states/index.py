import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Juggling States

    在前一個章節，我們關心如何將一串雜耍的 pattern 轉為符號的形式。每個時間點，玩家都會進行不同的拋接動作，來讓雜耍持續下去。 Juggling State 則是記錄了每個時間點的狀態，這個狀態告訴我們接下來玩家可以進行何種拋接動作。這個狀態是無記憶性的，也就是不管你是透過何種途徑來到這個狀態，都不會影響你後續可以選擇的拋接動作。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Notation

    回顧上一個章節， $M(\mathcal{F})$ 用來刻劃著某個瞬間拋出的物件們的性質。包括**滯空時長**和**落入哪隻手**。但其實他不只可以刻畫拋出的物件的性質，他可以刻畫空中所有物件的性質。

    每一個瞬間 $t$，我們可以將狀態表述為 $\sigma(t) \in M(\mathcal{F})$ ，其代表在 $u$ 單位時間過後，會有 $\sigma(t)(j, u)$ 個物件落回第 $j$ 隻手中。

    juggling matrix 其實就是做一次狀態轉移。他將 $1$ 單位時間後落回手中的物件，再重新拋回空中，整個過程消耗了 $1$ 單位時間，我們可以將此狀態轉移表示成此形式

    $$
    \sigma(t + 1) = \sigma(t)^{\downarrow} + \sum_{i \in \mathcal{H}} J(i, t), \quad \text{ where } f^{\downarrow}(j, u) := f(j, u + 1) \quad \text{ for } f \in M(\mathcal{F})
    $$

    並且下一拍要落回手中的物件數量，跟接下來要丟出的物件的數量要一致

    $$
    \sum_{x \in \mathcal{F}} J(i, t)(x) = \sigma(t)(i, 1), \qquad \forall i \in \mathcal{H} \qquad \text{(balance)}
    $$

    有了上述狀態跟 juggling matrix 的關係式，我們會發現當我們從一個狀態出發，經過各個後回到原來的位置。拋出的**落點手 $\times$ 滯空時長**的重數的合，只取決於經過的狀態，不取決於經過的順序。這就是著名的 **States Determine Throws**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Theorem (States Determine Throws)
        type: theorem

    Let $J$ be a $p$-periodic juggling matrix, and the corresponding state is $\sigma$, write

    $$
    \Sigma := \sum_{t = 0}^{p - 1} \sigma(t) \;\in\; M(\mathcal{F})
    $$

    then

    $$
    \sum_{t = 0}^{p - 1} \sum_{i \in \mathcal{H}} J(i, t) \;=\; \Sigma - \Sigma^{\downarrow}.
    $$

    *[Polster, *The Mathematics of Juggling*](https://books.google.com.tw/books/about/The_Mathematics_of_Juggling.html?id=YCARBwAAQBAJ&redir_esc=y) states this for one hand in §2.8.3 and for several in §4.3;
    the closed form on the right, and the proof below, are worked out here.*
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    $$
    \begin{align*}
    & \sum_{t = 0}^{p - 1} \sum_{i \in \mathcal{H}} J(i, t) \\
    = & \sum_{t = 0}^{p - 1} \bigl( \sigma(t + 1) - \sigma(t)^{\downarrow} \bigr) \\
    = & \sum_{t = 0}^{p - 1} \sigma(t + 1) \;-\; \sum_{t = 0}^{p - 1} \sigma(t)^{\downarrow}
        && \text{(each sum is finite)} \\
    = & \sum_{t = 0}^{p - 1} \sigma(t) \;-\; \Bigl( \sum_{t = 0}^{p - 1} \sigma(t) \Bigr)^{\downarrow}
        && \text{(periodic; } \downarrow \text{ is linear)} \\
    = & \; \Sigma - \Sigma^{\downarrow}
    \end{align*}
    $$

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: remark

    注意到 State Determine Throws 只決定了落回哪隻手跟滯空時長，並無法推出這些物件是何時從哪隻手拋出。
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Simulation

    以下是我讓 AI vibe 出來的 juggling state 模擬。符號的部分可以參考第一篇雜耍文章。
    """)
    return


@app.cell
def _(mo):
    get_beat, set_beat = mo.state(0)
    return get_beat, set_beat


@app.cell(hide_code=True)
def _(PatternEditor, mo):
    pattern_input = mo.ui.anywidget(PatternEditor())
    pattern_input
    return (pattern_input,)


@app.cell(hide_code=True)
def _(pattern_input, set_beat, state_graph):
    set_beat(0)
    try:
        pattern = state_graph.read_pattern(pattern_input.value["value"].strip())
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
    from pattern_editor import PatternEditor

    return PatternEditor, mo, state_graph


if __name__ == "__main__":
    app.run()
