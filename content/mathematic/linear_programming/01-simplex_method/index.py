# /// script
# dependencies = ["marimo", "numpy", "plotly"]
# requires-python = ">=3.12"
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Simplex Method

    單純形法（Simplex Method）是線性規劃（Linear Programming）中一個非常常見的求解方法。雖然它時間複雜度最糟的情況下是指數級的，但因為其常數項很小，而且實務上也不太會遇到這麼糟的狀況，所以現在很多線性規劃的套件都還是用單純形法搭配內點法去求解。

    ## 核心思想

    Simplex Method的核心思想是，線性規劃的限制式圍成了一個凸多面體；當問題可行而且最佳值有限時，至少會有一個頂點是最佳解 (高中數學課本裡用的圖形法也是利用了此性質)。因此如果我們能先找到一個頂點，然後沿著邊走到另一個能讓目標式變得更好的頂點，就有機會逐步抵達最佳頂點。

    關於為何一定存在一個頂點使得目標式達到最佳解，這裡暫不做嚴謹證明。不過直覺的想法其實跟圖形法一樣，因目標式是一個線性函數，它的梯度是固定的，所以我們在凸多面體裡朝著這個方向走時，碰壁時就還是沿著牆壁朝著這個梯度走；若最佳值有限，最終要嘛會碰到一個最佳頂點，要嘛會碰到一個與梯度垂直的面，這時這個面上的頂點也會是最佳解。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 標準形式 (standard form)

    首先，我們總能把$n$個變數，$m$個限制式的線性規劃寫成**標準形式 (standard form)**:

    $$
    \begin{aligned}
    \text{maximize } \quad & z = c^T x \\
    \text{subject to } \quad & Ax \leq b \\
    \text{and } \quad & x \geq 0
    \end{aligned}
    $$

    其中
    - $z \in \mathbf{R}$ 是目標式的值，我們想知道他最大值是多少。
    - $x \in \mathbf{R}^n$ 是變數們
    - $c \in \mathbf{R}^n$ 是目標式的係數
    - $A \in \mathbf{R}^{m \times n}$ 是限制式的係數
    - $b \in \mathbf{R}^m$ 是限制式的常數項
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **關於為何限制式可以寫成小於等於的不等式 ：**
    >
    > - 若有等式限制式 $A_{i, \cdot} x = b_i$，可以把它拆成兩個不等式 $A_{i, \cdot} x \leq b_i$ 和 $A_{i, \cdot} x \geq b_i$。
    > - 若有大於等於的不等式限制式 $A_{i, \cdot} x \geq b_i$，可以把係數取負號變成 $-A_{i, \cdot} x \leq -b_i$。

    > **關於為何變數可以寫成非負形式：**
    >
    > 若 $x_i$ 沒有非負限制，可令
    > $x_i = x_i^+ - x_i^-$，其中 $x_i^+, x_i^- \geq 0$。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    不過在弄成標準形式後，我們還要加個鬆弛變數 (slack variable)，讓限制式變成等式，這樣才能方便做 row operation。

    $$
    \begin{aligned}
        \text{maximize } \quad & z = c^T x \\
        \text{subject to } \quad & s + Ax = b \\
        \text{and } \quad & s, x \geq 0
    \end{aligned}
    \tag{slack form}
    $$


    > 這邊其實我蠻好奇的是為何要先變成小於等於的形式再化成等於的形式，而不直接化成等於的形式，感覺白白增加了一些沒必要的slack variable。後來發現其實大部分solver確實是直接化成等於的形式的。至於小於等於的形式的優點我猜是比較好做演算法的視覺化。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    可以發現我們可以把目標式也寫進矩陣裡，此線性規劃就化簡成了一個求變數 $z$ 的最大值的問題。

    $$
    \begin{aligned}
        \text{maximize } \quad & z \\
        \text{subject to } \quad &
            \begin{bmatrix}
                1 & 0 & -c^T \\
                0 & I_m & A
            \end{bmatrix}
            \begin{bmatrix}
                z \\
                s \\
                x
            \end{bmatrix}
            =
            \begin{bmatrix}
                0 \\
                b
            \end{bmatrix} \\
        \text{and } \quad & s, x \geq 0
    \end{aligned}
    \tag{initial form}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    此時如果 $b \geq 0$，那 initial form 就會是下列 canonical form 的特例。一般情況還需要其他方法來把問題化約成 canonical form ，這之後有機會再討論；為了方便起見，本文**從現在開始只考慮 $b \geq 0$ 的情況**。

    $$
    \begin{aligned}
        \text{maximize } \quad & z \\
        \text{subject to } \quad &
            \begin{bmatrix}
                1 & 0 & -c_D^T \\
                0 & I_m & D
            \end{bmatrix}
            \begin{bmatrix}
                z \\
                x_B \\
                x_D
            \end{bmatrix}
            =
            \begin{bmatrix}
                z_0 \\
                b_B
            \end{bmatrix} \\
        \text{and } \quad & x_D, x_B, b_B \geq 0 \\
        \text{where } \quad &
            \begin{bmatrix}
                x_B \\
                x_D
            \end{bmatrix}
            \text{ is a permutation of }
            \begin{bmatrix}
                s \\
                x
            \end{bmatrix}
            , z_0, b_B \text{ are constant.}
    \end{aligned}
    \tag{canonical form}
    $$

    那simplex method的核心思想，就是不斷的將 canonical form 轉換成另一個 canonical form，看看能否能讓 $c_D \leq 0$ 。假如此情境真的發生了，則令 $(x_B, x_D) = (b_B, 0)$ 就能讓 $z$ attain 最大值 $z_0$。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **Remark:** initial form 跟 canonical form 是我在這篇文章為了方便先暫時取的名稱。不同教材對 standard form 的 convention 也不完全相同；本文固定用 $Ax\leq b,\ x\geq0$ 的最大化形式。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 基變數 (basic variables), 非基變數 (non-basic variables) 與轉軸操作 (pivot operation)

    在上述討論之中，可以觀察到假如我們今天的規劃問題可以整理成canonical form的形式，則 $(x_B, x_D) = (b_B, 0)$ 就一定會是一組可行解 (不一定能讓 $z$ attain 最大值)。基於這個觀察，我們可以把

    - $x_i \in x_B$ 稱為 `基變數 (basic variables)`
    - $x_i \in x_D$ 稱為 `非基變數 (non-basic variables)`。

    Simplex method 的思想基本上就是持續的將基變數跟非基變數互換，並且互換的過程都保持 canonical form，直到換到 $c_D \leq 0$ 為止。這樣的操作被稱為轉軸操作 (pivot operation)

    實際操作大概長這樣，不失一般性假設 $c_D$ 的第一個元素 $c_{D, 1} > 0$。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.center(
        mo.image(
            str(mo.notebook_location() / "pivot_operation_step-1.svg"),
            caption="Pivot operation step 1.",
            width=600,
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    為了消除 $c_{D, 1}$，我們需要選擇一個 row 讓他對目標式還有其他 row 做高斯消去法，並且還要維持 $b_B >= 0$。 這個 row 要怎麼挑我們等等再討論，WLOG 我們可以先假設 1-th row 就是那個合適的 row ，則消去後會長這樣
    """)
    return


@app.cell
def _(mo):
    mo.center(
        mo.image(
            str(mo.notebook_location() / "pivot_operation_step-2.svg"),
            caption="Pivot operation step 2.",
            width=800,
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    最後再把 $x_{B, 1}$ 跟 $x_{D, 1}$ 位置互換， $x_{B, 1}$ 從 basic variable 變成 non-basic variable， $x_{D, 1}$ 從 non-basic variable 變成 basic variable。這樣就完成了一次 pivot operation。
    """)
    return


@app.cell
def _(mo):
    mo.center(
        mo.image(
            str(mo.notebook_location() / "pivot_operation_step-3.svg"),
            caption="Pivot operation step 3.",
            width=800,
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    當然，我們做完pivot operation之後，整個矩陣的表達式依舊要滿足canonical form，我們等式右邊的向量的 entries 必須都非負。觀察一下上式就可以發現當

    $$
    D_{1, 1} > 0 \quad \text{ and } \quad \frac{b_{B, 1}}{D_{1, 1}} = \min_{\substack{1 \leq i \leq m \\ D_{i, 1} > 0}} \frac{b_{B, i}}{D_{i, 1}}.
    $$

    就可以了。

    > **Remark:** 這裡有個小細節是，今天選好 $c_{D, 1}$ 並準備開始 pivot operation 時，如果 $D_{1, 1}, D_{2, 1} \cdots D_{m, 1}$ 皆小於等於 0 的話，似乎就沒辦法正常執行上述計算了。
    >
    > 但這種情況其實代表，令 $x_{D, \geq 2} = 0$ 後，對任意 $x_{D,1} \geq 0$ 都可取
    > $x_B = b_B - D_{\cdot, 1} x_{D, 1}$ ，所以仍是可行解。讓 $x_{D,1}$ 趨近無窮大時，$z$ 也會趨近無窮大；此時問題無界，也就不用再做 pivot operation 了。

    > **Remark:** 其實理論上還需要一些手段才能保證 simplex method 經過有限次 pivot operation 就能終止，這或許以後有機會再來談。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Simplex method 的視覺化模擬

    總之我讓 AI 幫我生成了一下 simplex method 的視覺化模擬

    下面可以自行輸入三維線性規劃的目標式跟限制式。

    - 限制式的格式為: `a_1, a_2, a_3 <= b` ，程式會把他轉成 $a_1 x_1 + a_2 x_2 + a_3 x_3 \leq b$
    - 目標式的格式為: `c_1, c_2, c_3` ，程式會把他轉成 maximize $c_1 x_1 + c_2 x_2 + c_3 x_3$

    同時程式也會自動加入 $x_1,x_2,x_3\geq0$ 的條件。

    為了能直接用 slack variables 作為初始 basis，目前要求每個 $b\geq0$，且可行域必須是有體積、封閉的三維多面體。
    """)
    return


@app.cell(hide_code=True)
def _(mo, set_simulation_step, simplex_simulation):
    simulation_input_form = mo.ui.batch(
        mo.md("""
        **目標係數 $c=(c_1,c_2,c_3)$**

        {objective}

        **限制式（每行：`a1, a2, a3 <= b`）**

        {constraints}
        """),
        elements={
            "objective": mo.ui.text(
                value=simplex_simulation.DEFAULT_OBJECTIVE,
                full_width=True,
            ),
            "constraints": mo.ui.text_area(
                value=simplex_simulation.DEFAULT_CONSTRAINTS,
                rows=6,
                full_width=True,
            ),
        },
    ).form(
        submit_button_label="套用並重新計算",
        on_change=lambda _: set_simulation_step(0),
    )
    simulation_input_form
    return (simulation_input_form,)


@app.cell(hide_code=True)
def _(mo, simplex_simulation, simulation_input_form):
    _submitted = simulation_input_form.value
    _objective_text = (
        _submitted["objective"]
        if _submitted is not None
        else simplex_simulation.DEFAULT_OBJECTIVE
    )
    _constraints_text = (
        _submitted["constraints"]
        if _submitted is not None
        else simplex_simulation.DEFAULT_CONSTRAINTS
    )
    try:
        _program = simplex_simulation.parse_linear_program(
            _objective_text,
            _constraints_text,
        )
        simulation_result = simplex_simulation.build_simulation(_program)
        _notice = mo.md("")
    except ValueError as _error:
        simulation_result = simplex_simulation.DEFAULT_SIMULATION
        _notice = mo.callout(
            mo.md(f"**輸入無法套用：** {_error} 目前仍顯示預設範例。"),
            kind="warn",
        )

    mo.vstack(
        [
            _notice,
            mo.md(simplex_simulation.program_markdown(simulation_result)),
            mo.md(
                "拖曳滑桿，或按上一步／下一步。橘色是已走路徑；"
                "綠色箭頭是目標函數梯度。右側 tableau 和幾何頂點使用同一個 basis。"
            ),
        ]
    )
    return (simulation_result,)


@app.cell
def _(mo):
    get_simulation_step, set_simulation_step = mo.state(0)
    return get_simulation_step, set_simulation_step


@app.cell(hide_code=True)
def _(mo, set_simulation_step, simulation_result):
    previous_step_button = mo.ui.button(
        label="← 上一步",
        value=0,
        on_click=lambda click_count: click_count + 1,
        on_change=lambda _: set_simulation_step(lambda value: max(0, value - 1)),
    )
    next_step_button = mo.ui.button(
        label="下一步 →",
        value=0,
        on_click=lambda click_count: click_count + 1,
        on_change=lambda _: set_simulation_step(
            lambda value: min(
                len(simulation_result.steps) - 1,
                value + 1,
            )
        ),
    )
    mo.hstack(
        [previous_step_button, next_step_button],
        widths=[0.5, 0.5],
        align="center",
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _(get_simulation_step, mo, set_simulation_step, simulation_result):
    _last_step = len(simulation_result.steps) - 1
    simulation_step_slider = mo.ui.slider(
        start=0,
        stop=_last_step,
        step=1,
        value=min(get_simulation_step(), _last_step),
        show_value=True,
        full_width=True,
        label="步驟",
        on_change=set_simulation_step,
    )
    simulation_step_slider
    return


@app.cell
def _(get_simulation_step, simulation_result):
    simulation_step_index = min(
        get_simulation_step(),
        len(simulation_result.steps) - 1,
    )
    return (simulation_step_index,)


@app.cell(hide_code=True)
def _(mo, simplex_simulation, simulation_result, simulation_step_index):
    _figure = simplex_simulation.make_figure(
        simulation_result,
        simulation_step_index,
    )
    _explanation = mo.md(
        simplex_simulation.step_markdown(
            simulation_result,
            simulation_step_index,
        )
    )
    mo.hstack(
        [mo.ui.plotly(_figure), _explanation],
        widths=[0.48, 0.52],
        align="start",
        gap=1.5,
        wrap=True,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    從模擬跟限制式可以觀察到，當 $A_{i,\cdot}\neq0$ 時，slack variable 除以限制式法向量的 norm，就會是**現在的點**跟**對應限制式的平面**之間的距離，也就是

    $$\frac{s_i}{\lVert A_{i, \cdot} \rVert} = \frac{b_i - A_{i, \cdot} x}{\lVert A_{i, \cdot} \rVert} = \text{distance between the current point and the constraint plane}.$$

    當 $s_i$ 變成 0 時，代表現在的點正好在對應的限制平面上。$x_i$ 也是同理，只是它對應的邊界平面是 $x_i=0$。
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import simplex_simulation

    return (simplex_simulation,)


if __name__ == "__main__":
    app.run()
