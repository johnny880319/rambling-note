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

    Simplex Method的核心思想是，當線性規劃的限制式圍成的凸多面體至少有一個頂點、問題可行且最佳值有限時，至少會有一個頂點是最佳解 (高中數學課本裡用的圖形法也是利用了此性質)。因此如果我們能先找到一個頂點，然後沿著邊走到另一個能讓目標式變得更好的頂點，就有機會逐步抵達最佳頂點。

    > **Remark: **關於為何一定存在一個頂點使得目標式達到最佳解，這裡暫不做嚴謹的證明。不過直覺的想法其實跟圖形法一樣，因目標式是一個線性函數，它的梯度是固定的，所以我們在凸多面體裡朝著這個方向走時，碰壁時就還是沿著牆壁朝著這個梯度走；若最佳值有限，最終要嘛會碰到一個最佳頂點，要嘛會碰到一個與梯度垂直的面，這時這個面上的頂點也會是最佳解。
    >
    > **Remark: **後面我們會把所有變數都轉成非負，那時可行域就一定會有頂點。

    現在大部分線性規劃求解器，都會使用 `two-phase-implementation` 的方法來求解，第一階段先找出滿足限制式的**可行解 (feasible solution) **，第二階段再找出滿足限制式且讓目標式attain最大值的**最佳解 (optimal solution) **。而兩個階段的演算法其實幾乎是一樣的，都是先想辦法把規畫問題 formulate 成某種 canonical form，然後利用能夠 preserve canonical form 的**轉軸操作 (pivot operation) **來達成目標。

    之前看[孔令傑老師的課程](https://www.youtube.com/@lckung.lectures)的時候，覺得老師跳過了許多做 `two-phase-implementation` 時需要注意的細節。這篇筆記會盡量把這些細節給補齊。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Canonical form 與轉軸操作 (pivot operation)

    在具體說明如何拆成兩階段之前，先來看一下如何做**轉軸操作 (pivot operation) **。考慮以下的 `canonical form`

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
        \text{where } \quad & z, x_B, x_D \text{ are variables.}
    \end{aligned}
    \tag{canonical form}
    $$

    如果將 $z$ 用 $x_B, x_D$ 來表示，那他就是一個** $n$ 變數 $m$ 限制式**的特別的線性規劃問題，其中

    - $z \in \mathbf{R}$ 是目標式的值，我們想知道他最大值是多少。
    - $x_B \in \mathbf{R}^m$ 是**基變數 (basic variables)**
    - $x_D \in \mathbf{R}^{n - m}$ 是**非基變數 (non-basic variables)**
    - $c_D \in \mathbf{R}^{n - m}$ 是非基變數在目標式中的係數
    - $D \in \mathbf{R}^{m \times (n - m)}$ 是非基變數在限制式中的係數
    - $b_B \in \mathbf{R}_{\geq 0}^m$ 是限制式的常數項
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    可以發現在這種形式之中， $(x_B, x_D) = (b_B, 0)$ 一定會是一組可行解，我們稱這種解叫**基本可行解 (basic feasible solution) **。特別的，假如今天  $c_D \leq 0$ ，此時 basic feasible solution 就會是讓 $z$ attain 最大值 $z_0$ 的**最佳解 (optimal solution) **。那我們就解開了這個 canonical form 的最佳化問題。

    > **Remark: **`canonical form` 是我在這篇文章為了方便先暫時取的名稱。學術圈似乎對此形式沒有一個統一的名稱。
    >
    > **Remark: **一般來說，如果不考慮 $b_B \geq 0$ 這個條件， $(x_B, x_D) = (b_B, 0)$ 都叫**基本解 (basic solution) **；而 canonical form 中因為要求 $b_B \geq 0$，所以這裡的基本解一定是基本可行解。

    而 pivot operation 就是一個可以將 canonical form 轉換成另一個 canonical form，並將 $c_D$ 慢慢轉換成非正向量的一個步驟。具體操作大概遵循下列流程

    不失一般性假設 $c_D$ 的第一個元素 $c_{D, 1} > 0$。
    """)
    return


@app.cell
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
    當然，我們做完pivot operation之後，整個矩陣的表達式依舊要滿足canonical form，我們等式右邊的向量的 entries 必須都非負。所以回到前面說的，用來高斯消去別人的 row 不能亂選，不過觀察一下上面的矩陣就可以發現被選擇的 row 只要滿足下面其中一點即可

    1. $b_{B, 1} = 0$, $D_{1, 1} \neq 0$
    2. $b_{B, 1} > 0$, $D_{1, 1} > 0$ 且

    $$
    \frac{b_{B, 1}}{D_{1, 1}} = \min_{\substack{1 \leq i \leq m \\ D_{i, 1} > 0}} \frac{b_{B, i}}{D_{i, 1}}.
    $$

    這個條件叫 `minimum ratio test` 。

    > **Remark:** 這裡有個小細節是，今天選好 $c_{D, 1}$ 並準備開始 pivot operation 時，如果 $b_{B, 1} > 0$ 且 $D_{1, 1}, D_{2, 1} \cdots D_{m, 1}$ 皆小於等於 0 的話，似乎就沒辦法做 minimum ratio test 了。
    >
    > 但這種情況其實代表，令 $x_{D, \geq 2} = 0$ 後，對任意 $x_{D,1} \geq 0$ 都可取
    > $x_B = b_B - D_{\cdot, 1} x_{D, 1}$ ，所以仍是可行解。讓 $x_{D,1}$ 趨近無窮大時，$z$ 也會趨近無窮大；此時問題無界，也就不用再做 pivot operation 了。

    > **Remark:** 通常我們會優先選擇 $b_{B, i} > 0$ 的 row 來進行 pivot operation，這樣我們目標式所對應的常數才會持續上升，讓我們盡快達到 optimal solution 。不過可能還是會遇到所有可行的 row 的 $b_{B, i}$ 皆為 0 的狀況。此時就需要一些其他手法來保證演算法可以在有限步 pivot operation 內停止。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Two-phase implementation

    從上述討論來看，我們接下來只要煩惱如何把任意的最佳化問題都轉成 canonical form 就好了。考慮以下 general 版本的線性規劃問題

    $$
    \begin{aligned}
    \text{maximize } \quad & z = c^T x \\
    \text{subject to } \quad & A_1 x \leq b_1 \\
    \text{and } \quad & A_2 x = b_2 \\
    \text{and } \quad & A_3 x \geq b_3
    \end{aligned}
    $$

    > **Remark: **$x, b_i, c$ 皆為向量， $A_i$ 皆為矩陣，只有 $z$ 是一維變數。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    首先，針對各個變數 $x$ ，我們總是能透過平移、乘負號或是將值域為實數的變數拆成兩個非負實數相減，讓變數的值域變成 $\mathbb{R}_{\geq 0}$ 。

    針對每個限制式的常數項，我們也能透過乘負號的方式讓他們都變為非負常數。只是第一類的限制式會變成第三類，反之同理。

    所以不失一般性，我們可以將變數跟常數加上非負的條件。

    $$
    \begin{aligned}
    \text{maximize } \quad & z = c^T x \\
    \text{subject to } \quad & A_1 x \leq b_1 \\
    \text{and } \quad & A_2 x = b_2 \\
    \text{and } \quad & A_3 x \geq b_3 \\
    \text{and } \quad & b_1, b_2, b_3, x \geq 0
    \end{aligned}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    接著加入鬆弛變數，目的是要製造人工的**基變數 (basic variables) **。

    $$
    \begin{aligned}
    \text{maximize } \quad & z = c^T x \\
    \text{subject to } \quad & A_1 x + s_1 = b_1 \\
    \text{and } \quad & A_2 x + s_2 = b_2 \\
    \text{and } \quad & A_3 x - s_3^- + s_3 = b_3 \\
    \text{and } \quad & b_1, b_2, b_3 \geq 0 \\
    \text{and } \quad & x, s_1, s_3^- \geq 0 \\
    \text{and } \quad & s_2, s_3 = 0
    \end{aligned}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    或是寫成矩陣的形式

    $$
    \begin{aligned}
        \text{maximize } \quad & z \\
        \text{subject to } \quad &
            \left[ \begin{array}{c|ccc|cc}
                1 & 0 & 0 & 0 & 0 & -c^T \\
                \hline
                0 & I & 0 & 0 & 0 & A_1  \\
                0 & 0 & I & 0 & 0 & A_2  \\
                0 & 0 & 0 & I & -I & A_3  \\
            \end{array} \right]
            \left[ \begin{array}{c}
                z \\
                \hline
                s_1 \\
                s_2 \\
                s_3 \\
                \hline
                s_3^- \\
                x
            \end{array} \right]
            =
            \left[ \begin{array}{c}
                0 \\
                \hline
                b_1 \\
                b_2 \\
                b_3
            \end{array} \right] \\
        \text{and } \quad & b_1, b_2, b_3 \geq 0 \\
        \text{and } \quad & s_1, s_2, s_3, s_3^-, x \geq 0 \\
        \text{and } \quad & s_2, s_3 = 0
    \end{aligned}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    可以發現這幾乎已經是 canonical form 的樣子了，只是此時的 basic feasible solution 並不一定滿足 $s_2, s_3 = 0$ ，為了找到可行解，我們可以先捨棄 $s_2, s_3 = 0$ 的條件，把目標式改成最大化 $- s_2 - s_3$ 的值並做 pivot operation。當算法停止時，如果此規劃問題的目標式

    - **最大值 < 0 **，代表在滿足限制式的情況下，根本就沒有 $s_2, s_3 = 0$ 的可行解。原規劃問題無解。
    - **最大值 = 0 **，此時的 basic feasible solution 對於原規劃問題是 feasible solution 。我們可以從這個點開始對原目標式做 pivot operation 來嘗試得到 optimal solution 。
    - **最大值 > 0 **，這個狀況代表 $- s_2 - s_3 > 0$，會跟 $s_2, s_3 \geq 0$ 的條件矛盾，所以不會發生。

    也就是說 `phase one` 其實就是先解以下規劃問題，把我們的點嘗試**從不可行解移動成可行解**。

    $$
    \begin{aligned}
        \text{maximize } \quad & z \\
        \text{subject to } \quad &
            \left[ \begin{array}{c|ccc|cc}
                1 & 0 & 1^T & 1^T & 0 & 0 \\
                \hline
                0 & I & 0 & 0 & 0 & A_1  \\
                0 & 0 & I & 0 & 0 & A_2  \\
                0 & 0 & 0 & I & -I & A_3  \\
            \end{array} \right]
            \left[ \begin{array}{c}
                z \\
                \hline
                s_1 \\
                s_2 \\
                s_3 \\
                \hline
                s_3^- \\
                x
            \end{array} \right]
            =
            \left[ \begin{array}{c}
                0 \\
                \hline
                b_1 \\
                b_2 \\
                b_3
            \end{array} \right] \\
        \text{and } \quad & b_1, b_2, b_3 \geq 0 \\
        \text{and } \quad & s_1, s_2, s_3, s_3^-, x \geq 0
    \end{aligned}
    $$

    只要對第一個row做高斯消去就能得到 canonical form ，也就能開始執行一系列的 pivot operation 。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    假設我們的最佳化問題有可行解，那麼 `phase one` 的最佳化結果就會是 0 。此時的 basic feasible solution 裡， $s_2, s_3$ 的部分都會是 0 (但他們不一定全是non basic variables) 。其形式大概會是這樣

    $$
    \begin{aligned}
        \text{maximize } \quad & z \\
        \text{subject to } \quad &
            \left[ \begin{array}{c|cc|c}
                1 & 0 & 0 & -c_{\widetilde{D}}^T \\
                \hline
                0 & I & 0 & D_1 \\
                0 & 0 & I & D_2
            \end{array} \right]
            \left[ \begin{array}{c}
                z \\
                \hline
                x_{\widetilde{B}} \\
                x_S \\
                \hline
                x_{\widetilde{D}}
            \end{array} \right]
            =
            \left[ \begin{array}{c}
                0 \\
                \hline
                b_{\widetilde{B}} \\
                0
            \end{array} \right] \\
        \text{and } \quad & b_{\widetilde{B}} \geq 0 \\
        \text{and } \quad & x_{\widetilde{B}}, x_S, x_{\widetilde{D}} \geq 0 \\
        \text{where } \quad & x_S \subseteq s_2 \cup s_3 \subseteq x_S \cup x_{\widetilde{D}}.
    \end{aligned}
    $$

    雖然我們已經得到 basic feasible solution 了，但我們會希望接下來要固定 $s_2, s_3 = 0$ 的條件，所以我們會希望他們能夠都變成 non-basic variables 。

    因為有點懶得再打一個大矩陣，所以就大概口頭描述解法就好。假如今天某個 $x_{S, i} \in x_S$ 想從 basic variable 降級為 non-basic variable 。需要先找出對應的會讓 $x_{S, i}$ 係數為 1 的 row ，然後尋找在那個 row 之中係數 $\neq 0$ 且不是 $s_2, s_3$ 裡的成員的 non-basic variable。那麼就對那個 non-basic variable 以此 row 為基準去做 pivot operation 。因為這個 row 原本是對應到 $x_{S, i}$ 的，所以他會被降級為 non-basic variable。

    至於為何一定能以此 row 做 pivot operation，是因為這個 row 對應的常數項是 0 ，所以之前在 minimum ratio test 時討論的第一項條件一定會成立。

    上面的過程中，選擇不是 $s_2, s_3$ 裡的成員的 non-basic variable 是因為，這樣才能保證做最多 $|s_2| + |s_3|$ 次 pivot operation 就能完成上述過程。不過萬一此 row 的所有非 $s_2, s_3$ 的成員的 non-basic variable 對應到的係數都是 0 。那就沒辦法進行 pivot operation 了。但此時這個限制式將可以完全被 $s_2, s_3 = 0$ 給替代，而 $x_{S, i}$ 也不會在其他限制式出現。所以它們其實就是多餘的條件了，直接把 $x_{S, i}$ 連同這個限制式刪除就好。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    完成了上述的過程之後，我們的限制式會變成以下這種形式


    $$
    \begin{aligned}
        \text{maximize } \quad & z \\
        \text{subject to } \quad &
            \left[ \begin{array}{c|c|cc}
                1 & 0 & -\widetilde{c}_D^T & -\widetilde{c}_{\widetilde{s}}^T \\
                \hline
                0 & I & D & A_{\widetilde{s}}
            \end{array} \right]
            \left[ \begin{array}{c}
                z \\
                \hline
                x_B \\
                \hline
                x_D \\
                \widetilde{s}
            \end{array} \right]
            =
            \left[ \begin{array}{c}
                0 \\
                \hline
                b_B
            \end{array} \right] \\
        \text{and } \quad & b_B \geq 0 \\
        \text{and } \quad & x_B, x_D, \widetilde{s} \geq 0 \\
        \text{and } \quad &
        \begin{bmatrix}
            x_B \\
            x_D
        \end{bmatrix}
        \text{ is permutation of }
        \begin{bmatrix}
            s_1 \\
            s_3^- \\
            x
        \end{bmatrix},
        \widetilde{s} \subseteq s_2 \cup s_3
    \end{aligned}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    此時我們就可以把 $s_2, s_3 = 0$ (也就是 $\widetilde{s} = 0$ ) 的條件加回來了，或是更精簡的作法是，因為他們從現在開始永遠都只會是 0 了，所以就可以把他們從式子裡刪掉，同時也把目標式改回我們原本的目標式，要注意的是因為有做過一些 column permutation 了，所以矩陣裡目標式的係數要跟著對齊。

    $$
    \begin{aligned}
        \text{maximize } \quad & z \\
        \text{subject to } \quad &
            \left[ \begin{array}{c|c|c}
                1 & -c_B^T & -c_D^T \\
                \hline
                0 & I & D
            \end{array} \right]
            \left[ \begin{array}{c}
                z \\
                \hline
                x_B \\
                \hline
                x_D
            \end{array} \right]
            =
            \left[ \begin{array}{c}
                0 \\
                \hline
                b_B
            \end{array} \right] \\
        \text{and } \quad & b_B \geq 0 \\
        \text{and } \quad & x_B, x_D \geq 0 \\
        \text{and } \quad &
        \begin{bmatrix}
            x_B \\
            x_D
        \end{bmatrix}
        \text{ is permutation of }
        \begin{bmatrix}
            s_1 \\
            s_3^- \\
            x
        \end{bmatrix}
    \end{aligned}
    $$

    此時就可以進入 `phase two` 的階段了，只要用基變數對目標式的 row 做高斯消去，就可以得到一個完美的 canonical form 。接著只要持續做 pivot operation 。嘗試**從可行解移動到最佳解** simplex method 就圓滿成功了。
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
