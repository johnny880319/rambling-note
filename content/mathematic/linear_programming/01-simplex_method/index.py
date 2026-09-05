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

    > **Remark: **關於為何一定存在一個頂點使得目標式達到最佳解，這裡暫不做嚴謹的證明。不過直覺的想法其實跟圖形法一樣，因目標式是一個線性函數，它的梯度是固定的，所以我們在凸多面體裡朝著梯度的反方向（也就是讓目標值下降的方向）走時，碰壁後就沿著牆壁繼續朝那個方向走；若最佳值有限，最終要嘛會碰到一個最佳頂點，要嘛會碰到一個與梯度垂直的面，這時這個面上的頂點也會是最佳解。
    >
    > **Remark: **後面我們會把所有變數都轉成非負，那時可行域就一定會有頂點。

    現在大部分線性規劃求解器，都會使用 `two-phase-implementation` 的方法來求解，第一階段先找出滿足限制式的**可行解 (feasible solution) **，第二階段再找出滿足限制式且讓目標式attain最小值的**最佳解 (optimal solution) **。而兩個階段的演算法其實幾乎是一樣的，都是先想辦法把規畫問題 formulate 成某種 canonical form，然後利用能夠 preserve canonical form 的**轉軸操作 (pivot operation) **來達成目標。

    之前看[孔令傑老師的課程](https://www.youtube.com/@lckung.lectures)的時候，覺得老師跳過了許多做 `two-phase-implementation` 時需要注意的細節。這篇筆記會盡量把這些細節給補齊。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Canonical Form and Pivot Operation

    在具體說明如何拆成兩階段之前，先來看一下如何做**轉軸操作 (pivot operation) **。

    > **Definition (Canonical Form):** A linear program is in **canonical form** when it is written as
    >
    > $$
    > \begin{aligned}
    >     \text{minimize } \quad & z \\
    >     \text{subject to } \quad &
    >         \begin{bmatrix}
    >             1 & 0 & -\bar{c}_N^T \\
    >             0 & I_m & D
    >         \end{bmatrix}
    >         \begin{bmatrix}
    >             z \\
    >             x_B \\
    >             x_N
    >         \end{bmatrix}
    >         =
    >         \begin{bmatrix}
    >             z_0 \\
    >             b_B
    >         \end{bmatrix} \\
    >     \text{and } \quad & x_N, x_B, b_B \geq 0 \\
    >     \text{where } \quad & z, x_B, x_N \text{ are variables.}
    > \end{aligned}
    > $$

    如果將 $z$ 用 $x_B, x_N$ 來表示，那他就是一個** $n$ 變數 $m$ 限制式**的特別的線性規劃問題，其中

    - $z \in \mathbf{R}$ 是目標式的值，我們想知道他最小值是多少。
    - $x_B \in \mathbf{R}^m$ 是**基變數 (basic variables)**
    - $x_N \in \mathbf{R}^{n - m}$ 是**非基變數 (non-basic variables)**
    - $\bar{c}_N \in \mathbf{R}^{n - m}$ 是非基變數在目標式中的係數
    - $D \in \mathbf{R}^{m \times (n - m)}$ 是非基變數在限制式中的係數
    - $b_B \in \mathbf{R}_{\geq 0}^m$ 是限制式的常數項

    > **Remark: **$\bar{c}_N$ 上面那一橫是要強調它是**把基變數消掉之後**才剩下的係數
    > （也就是所謂的 **reduced cost**），跟原本目標式裡的係數不是同一回事。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    可以發現在這種形式之中， $(x_B, x_N) = (b_B, 0)$ 一定會是一組可行解，我們稱這種解叫**基本可行解 (basic feasible solution) **。特別的，假如今天  $\bar{c}_N \geq 0$ ，此時 basic feasible solution 就會是讓 $z$ attain 最小值 $z_0$ 的**最佳解 (optimal solution) **。那我們就解開了這個 canonical form 的最佳化問題。

    > **Remark: **`canonical form` 是我在這篇文章為了方便先暫時取的名稱。學術圈似乎對此形式沒有一個統一的名稱。
    >
    > **Remark: **一般來說，如果不考慮 $b_B \geq 0$ 這個條件， $(x_B, x_N) = (b_B, 0)$ 都叫**基本解 (basic solution) **；而 canonical form 中因為要求 $b_B \geq 0$，所以這裡的基本解一定是基本可行解。

    而 pivot operation 就是一個可以將 canonical form 轉換成另一個 canonical form，並將 $\bar{c}_N$ 慢慢轉換成非負向量的一個步驟。具體操作大概遵循下列流程

    不失一般性假設 $\bar{c}_N$ 的第一個元素 $\bar{c}_{N, 1} < 0$。
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
    為了消除 $\bar{c}_{N, 1}$，我們需要選擇一個 row 讓他對目標式還有其他 row 做高斯消去法，並且還要維持 $b_B >= 0$。 這個 row 要怎麼挑我們等等再討論，WLOG 我們可以先假設 1-th row 就是那個合適的 row ，則消去後會長這樣
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
    最後再把 $x_{B, 1}$ 跟 $x_{N, 1}$ 位置互換， $x_{B, 1}$ 從 basic variable 變成 non-basic variable， $x_{N, 1}$ 從 non-basic variable 變成 basic variable。這樣就完成了一次 pivot operation。
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

    這個條件叫 `minimum ratio test` 。此時我們可以說在這次 pivot operation 之中， $x_{N, 1}$ **進基 (Entering variable) **，而 $x_{B, 1}$ **離基 (Leaving variable) **。

    > **Remark:** 這裡有個小細節是，今天選好 $\bar{c}_{N, 1}$ 並準備開始 pivot operation 時，如果 $b_{B, 1} > 0$ 且 $D_{1, 1}, D_{2, 1} \cdots D_{m, 1}$ 皆小於等於 0 的話，似乎就沒辦法做 minimum ratio test 了。
    >
    > 但這種情況其實代表，令 $x_{N, \geq 2} = 0$ 後，對任意 $x_{N,1} \geq 0$ 都可取
    > $x_B = b_B - D_{\cdot, 1} x_{N, 1}$ ，所以仍是可行解。讓 $x_{N,1}$ 趨近無窮大時，$z$ 會趨近負無窮大；此時問題向下無界，也就不用再做 pivot operation 了。

    > **Remark:** 通常我們會優先選擇 $b_{B, i} > 0$ 的 row 來進行 pivot operation，這樣我們目標式所對應的常數才會持續下降，讓我們盡快達到 optimal solution 。不過可能還是會遇到所有可行的 row 的 $b_{B, i}$ 皆為 0 的狀況。此時就需要一些其他手法來保證演算法可以在有限步 pivot operation 內停止。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Two-Phase Implementation

    從上述討論來看，我們接下來只要煩惱如何把任意的最佳化問題都轉成 canonical form 就好了。考慮以下 general 版本的線性規劃問題

    $$
    \begin{aligned}
    \text{minimize } \quad & z = c^T x \\
    \text{subject to } \quad & A_L x \leq b_L \\
    \text{and } \quad & A_E x = b_E \\
    \text{and } \quad & A_G x \geq b_G
    \end{aligned}
    $$

    > **Remark: **下標 $L, E, G$ 分別代表 less、equal、greater，用來區分三類限制式。
    > $x, b_L, b_E, b_G, c$ 皆為向量， $A_L, A_E, A_G$ 皆為矩陣，只有 $z$ 是一維變數。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    首先，針對各個變數 $x$ ，我們總是能透過平移、乘負號或是將值域為實數的變數拆成兩個非負實數相減，讓變數的值域變成 $\mathbb{R}_{\geq 0}$ 。

    針對每個限制式的常數項，我們也能透過乘負號的方式讓他們都變為非負常數。只是乘負號會讓不等號反向，所以 $\leq$ 的限制式會跑到 $\geq$ 那一類去，反之同理。

    所以不失一般性，我們可以將變數跟常數加上非負的條件。

    $$
    \begin{aligned}
    \text{minimize } \quad & z = c^T x \\
    \text{subject to } \quad & A_L x \leq b_L \\
    \text{and } \quad & A_E x = b_E \\
    \text{and } \quad & A_G x \geq b_G \\
    \text{and } \quad & b_L, b_E, b_G, x \geq 0
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
    \text{minimize } \quad & z = c^T x \\
    \text{subject to } \quad & A_L x + s_L = b_L \\
    \text{and } \quad & A_E x + a_E = b_E \\
    \text{and } \quad & A_G x - s_G + a_G = b_G \\
    \text{and } \quad & b_L, b_E, b_G \geq 0 \\
    \text{and } \quad & x, s_L, s_G \geq 0 \\
    \text{and } \quad & a_E, a_G = 0
    \end{aligned}
    $$

    > **Remark: **這裡用兩組字母分辨兩種角色：$s$ 是真正的鬆弛量（$s_L$ 是 slack、$s_G$ 是 surplus），
    > $a$ 則是為了湊出基底而硬加的**人工變數 (artificial variables)**。
    > 人工變數不屬於原問題，所以要額外要求 $a_E, a_G = 0$。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    或是寫成矩陣的形式

    $$
    \begin{aligned}
        \text{minimize } \quad & z \\
        \text{subject to } \quad &
            \left[ \begin{array}{c|ccc|cc}
                1 & 0 & 0 & 0 & 0 & -c^T \\
                \hline
                0 & I & 0 & 0 & 0 & A_L  \\
                0 & 0 & I & 0 & 0 & A_E  \\
                0 & 0 & 0 & I & -I & A_G  \\
            \end{array} \right]
            \left[ \begin{array}{c}
                z \\
                \hline
                s_L \\
                a_E \\
                a_G \\
                \hline
                s_G \\
                x
            \end{array} \right]
            =
            \left[ \begin{array}{c}
                0 \\
                \hline
                b_L \\
                b_E \\
                b_G
            \end{array} \right] \\
        \text{and } \quad & b_L, b_E, b_G \geq 0 \\
        \text{and } \quad & s_L, s_G, a_E, a_G, x \geq 0 \\
        \text{and } \quad & a_E, a_G = 0
    \end{aligned}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    可以發現這幾乎已經是 canonical form 的樣子了，只是此時的 basic feasible solution 並不一定滿足 $a_E, a_G = 0$ ，為了找到可行解，我們可以先捨棄 $a_E, a_G = 0$ 的條件，把目標式改成最小化 $a_E + a_G$ 的值並做 pivot operation。當算法停止時，如果此規劃問題的目標式

    - **最小值 > 0 **，代表在滿足限制式的情況下，根本就沒有 $a_E, a_G = 0$ 的可行解。原規劃問題無解。
    - **最小值 = 0 **，此時的 basic feasible solution 對於原規劃問題是 feasible solution 。我們可以從這個點開始對原目標式做 pivot operation 來嘗試得到 optimal solution 。
    - **最小值 < 0 **，這個狀況代表 $a_E + a_G < 0$，會跟 $a_E, a_G \geq 0$ 的條件矛盾，所以不會發生。

    也就是說 `phase one` 其實就是先解以下規劃問題，把我們的點嘗試**從不可行解移動成可行解**。

    $$
    \begin{aligned}
        \text{minimize } \quad & z \\
        \text{subject to } \quad &
            \left[ \begin{array}{c|ccc|cc}
                1 & 0 & -1^T & -1^T & 0 & 0 \\
                \hline
                0 & I & 0 & 0 & 0 & A_L  \\
                0 & 0 & I & 0 & 0 & A_E  \\
                0 & 0 & 0 & I & -I & A_G  \\
            \end{array} \right]
            \left[ \begin{array}{c}
                z \\
                \hline
                s_L \\
                a_E \\
                a_G \\
                \hline
                s_G \\
                x
            \end{array} \right]
            =
            \left[ \begin{array}{c}
                0 \\
                \hline
                b_L \\
                b_E \\
                b_G
            \end{array} \right] \\
        \text{and } \quad & b_L, b_E, b_G \geq 0 \\
        \text{and } \quad & s_L, s_G, a_E, a_G, x \geq 0
    \end{aligned}
    $$

    只要對第一個row做高斯消去就能得到 canonical form ，也就能開始執行一系列的 pivot operation 。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    假設我們的最佳化問題有可行解，那麼 `phase one` 的最佳化結果就會是 0 。此時的 basic feasible solution 裡， $a_E, a_G$ 的部分都會是 0 (但他們不一定全是non basic variables) 。其形式大概會是這樣

    $$
    \begin{aligned}
        \text{minimize } \quad & z \\
        \text{subject to } \quad &
            \left[ \begin{array}{c|cc|c}
                1 & 0 & 0 & -\bar{c}_{\widetilde{N}}^T \\
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
                x_{\widetilde{N}}
            \end{array} \right]
            =
            \left[ \begin{array}{c}
                0 \\
                \hline
                b_{\widetilde{B}} \\
                0
            \end{array} \right] \\
        \text{and } \quad & b_{\widetilde{B}} \geq 0 \\
        \text{and } \quad & x_{\widetilde{B}}, x_S, x_{\widetilde{N}} \geq 0 \\
        \text{where } \quad & x_S \subseteq a_E \cup a_G \subseteq x_S \cup x_{\widetilde{N}}.
    \end{aligned}
    $$

    雖然我們已經得到 basic feasible solution 了，但我們會希望接下來要固定 $a_E, a_G = 0$ 的條件，所以我們會希望他們能夠都變成 non-basic variables 。

    因為有點懶得再打一個大矩陣，所以就大概口頭描述解法就好。假如今天某個 $x_{S, i} \in x_S$ 想從 basic variable 降級為 non-basic variable 。需要先找出對應的會讓 $x_{S, i}$ 係數為 1 的 row ，然後尋找在那個 row 之中係數 $\neq 0$ 且不是人工變數的 non-basic variable。那麼就對那個 non-basic variable 以此 row 為基準去做 pivot operation 。因為這個 row 原本是對應到 $x_{S, i}$ 的，所以他會被降級為 non-basic variable。

    至於為何一定能以此 row 做 pivot operation，是因為這個 row 對應的常數項是 0 ，所以之前在 minimum ratio test 時討論的第一項條件一定會成立。

    上面的過程中，選擇不是人工變數的 non-basic variable 是因為，這樣才能保證做最多 $|a_E| + |a_G|$ 次 pivot operation 就能完成上述過程。不過萬一此 row 的所有非人工變數的 non-basic variable 對應到的係數都是 0 。那就沒辦法進行 pivot operation 了。但此時這個限制式將可以完全被 $a_E, a_G = 0$ 給替代，而 $x_{S, i}$ 也不會在其他限制式出現。所以它們其實就是多餘的條件了，直接把 $x_{S, i}$ 連同這個限制式刪除就好。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    完成了上述的過程之後，我們的限制式會變成以下這種形式


    $$
    \begin{aligned}
        \text{minimize } \quad & z \\
        \text{subject to } \quad &
            \left[ \begin{array}{c|c|cc}
                1 & 0 & -\widetilde{\bar{c}}_N^T & -\widetilde{c}_{\widetilde{a}}^T \\
                \hline
                0 & I & D & A_{\widetilde{a}}
            \end{array} \right]
            \left[ \begin{array}{c}
                z \\
                \hline
                x_B \\
                \hline
                x_N \\
                \widetilde{a}
            \end{array} \right]
            =
            \left[ \begin{array}{c}
                0 \\
                \hline
                b_B
            \end{array} \right] \\
        \text{and } \quad & b_B \geq 0 \\
        \text{and } \quad & x_B, x_N, \widetilde{a} \geq 0 \\
        \text{and } \quad &
        \begin{bmatrix}
            x_B \\
            x_N
        \end{bmatrix}
        \text{ is permutation of }
        \begin{bmatrix}
            s_L \\
            s_G \\
            x
        \end{bmatrix},
        \widetilde{a} \subseteq a_E \cup a_G
    \end{aligned}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    此時我們就可以把 $a_E, a_G = 0$ (也就是 $\widetilde{a} = 0$ ) 的條件加回來了，或是更精簡的作法是，因為他們從現在開始永遠都只會是 0 了，所以就可以把他們從式子裡刪掉，同時也把目標式改回我們原本的目標式，要注意的是因為有做過一些 column permutation 了，所以矩陣裡目標式的係數要跟著對齊。

    $$
    \begin{aligned}
        \text{minimize } \quad & z \\
        \text{subject to } \quad &
            \left[ \begin{array}{c|c|c}
                1 & -c_B^T & -\bar{c}_N^T \\
                \hline
                0 & I & D
            \end{array} \right]
            \left[ \begin{array}{c}
                z \\
                \hline
                x_B \\
                \hline
                x_N
            \end{array} \right]
            =
            \left[ \begin{array}{c}
                0 \\
                \hline
                b_B
            \end{array} \right] \\
        \text{and } \quad & b_B \geq 0 \\
        \text{and } \quad & x_B, x_N \geq 0 \\
        \text{and } \quad &
        \begin{bmatrix}
            x_B \\
            x_N
        \end{bmatrix}
        \text{ is permutation of }
        \begin{bmatrix}
            s_L \\
            s_G \\
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
    ## A More Compact Formulation

    前面整套流程都是用 row operation 跟 column operation 進行描述的。透過這樣一步步操作我們才能知道現在的 basic variables, non-basic variables, 以及矩陣裡的各個係數為何。

    但其實我們只要知道 basic variables, non-basic variables 分別有哪些成員，我們就能直接算出矩陣裡的內容。

    方便起見我們就先假設我們的線性規劃問題已經轉成了以下形式

    $$
    \begin{aligned}
    \text{minimize } \quad & z = c^T x \\
    \text{subject to } \quad & A x = b \\
    \text{and } \quad & x \geq 0.
    \end{aligned}
    $$

    假設現在把 $x$ 切成 basic variables $x_B$ 跟 non-basic variables $x_N$ ，並將 $A, c$ 都做相應的拆分，可以得到


    $$
    \begin{aligned}
    \text{minimize } \quad & z = c_B^T x_B + c_N^T x_N \\
    \text{subject to } \quad & A_B x_B + A_N x_N = b \\
    \text{and } \quad & x_B, x_N \geq 0.
    \end{aligned}
    $$

    注意到我們在進基過程中，就是不停地做 row operation 及 column 互換。這代表 $A_B$ 可以透過一系列 row operation 變回單位矩陣（每次 pivot 都要求 $D_{1,1} \neq 0$，所以那些列運算都是可逆的），也就是說他可逆，於是我們可以得到關係式

    $$
    x_B = A_B^{-1} (b - A_N x_N)
    $$

    帶回上述式子就得到

    $$
    \begin{aligned}
    \text{minimize } \quad & z = (c_N - A_N^T (A_B^T)^{-1} c_B)^T x_N + c_B^T A_B^{-1} b \\
    \text{subject to } \quad & x_B + A_B^{-1} A_N x_N = A_B^{-1} b \\
    \text{and } \quad & x_B, x_N \geq 0.
    \end{aligned}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    或者寫成 block matrix 的形式，就會發現他是一個令人熟悉的形式

    $$
    \begin{aligned}
        \text{minimize } \quad & z \\
        \text{subject to } \quad &
            \left[ \begin{array}{c|c|c}
                1 & 0 & - (c_N - A_N^T (A_B^T)^{-1} c_B)^T \\
                \hline
                0 & I & A_B^{-1} A_N
            \end{array} \right]
            \left[ \begin{array}{c}
                z \\
                \hline
                x_B \\
                \hline
                x_N
            \end{array} \right]
            =
            \left[ \begin{array}{c}
                c_B^T A_B^{-1} b \\
                \hline
                A_B^{-1} b
            \end{array} \right] \\
        \text{and } \quad & x_B, x_N \geq 0
    \end{aligned}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    也就是前幾段說的 $\bar{c}_N$ 其實就是 $c_N - A_N^T (A_B^T)^{-1} c_B$ 。我們稱他為 **reduced cost** 。

    > **Remark: **reduced cost 的符號有兩種慣例，對照別的教材時要小心。
    >
    > 本文跟隨凸最佳化的慣例（目標式取 $\min$），所以
    > $\bar{c}_N = c_N - A_N^T (A_B^T)^{-1} c_B$，最佳性條件是 $\bar{c}_N \geq 0$。
    > 但有些教材用 $\max$，並把 $A_N^T (A_B^T)^{-1} c_B - c_N$ 稱為 reduced cost ，跟本文差一個負號。

    這個表達式告訴我們，** canonical form 裡的矩陣形式完全由基底決定**，跟你經過哪一連串列運算走到這裡完全無關。
    於是整個 simplex method 可以重新表述成

    > 在所有「選 $m$ 個線性獨立欄位」的基底之間搜尋，
    > 直到找到一組同時滿足 $A_B^{-1}b \geq 0$（原始可行）
    > 與 $c_N - A_N^T (A_B^T)^{-1} c_B \geq 0$（最佳性）的基底。

    之後我們探討 dual simplex 等主題時，這個表達式會很好用。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Visualizing the Simplex Method

    這個章節我讓 AI 完全照著我前面寫的內容生成 simplex method 的視覺化模擬。目前效果感覺還不錯，不過之後的一些細節跟用詞我可能還會再親自修。

    下面可以自行輸入三維線性規劃的目標式跟限制式。

    - 限制式一行一條，格式為 `A1, A2, A3 <= b`，第 $i$ 行會被轉成
      $A_{i,1}x_1 + A_{i,2}x_2 + A_{i,3}x_3 \leq b_i$，也就是 $A_{i,\cdot}\,x \leq b_i$。
      `>=` 與 `=` 也支援；$b_i$ 是負的會自動整條乘上 $-1$（不等號跟著反向）
    - 目標式的格式為 `c1, c2, c3`，會被轉成 minimize $c^T x$

    同時程式也會自動加入 $x_1,x_2,x_3\geq0$ 的條件。

    ### Mapping Back to the Earlier Sections

    模擬會依輸入自動選擇路徑，每一步的標籤會標示目前在哪個階段：

    | 標籤 | 對應的段落 |
    | --- | --- |
    | `Phase two` | 全部都是 $\leq$ 時，slack variables 直接就是可行基底，跳過 phase one |
    | `Phase one` | 有 $\geq$ 或 $=$ 時，替它們加上人工變數 $a_i$，最小化 $\sum_i a_i$ |
    | `逐出人工變數` | phase one 結束後仍留在基底裡的 $a_i$；整列在非人工欄位全為 0 時則刪除該冗餘限制式 |
    | `換回原目標式` | 刪掉 $a_i$ 的欄位、放回 $z=c^Tx$，再消去一次得到 canonical form |

    模擬沿用前面的字母：$A$ 是限制式係數、$b$ 是常數項、$c$ 是目標式係數、
    $s$ 是真正的鬆弛量、$a$ 是人工變數（在 tableau 裡會標成紫色）。

    > **Remark: **不過下標的意義換了。前面按限制式的「類別」分組，所以只有
    > $A_L, A_E, A_G$、$b_L, b_E, b_G$、$s_L, s_G$、$a_E, a_G$ 這些向量與矩陣；
    > 模擬則一律按限制式的「編號」逐條給，於是會看到 $s_1, s_2, \dots$ 和 $a_5, a_6$ 這種。
    >
    > 換句話說，模擬裡的 $s_i$ 是 $s_L$ 或 $s_G$ 的其中一個分量（看第 $i$ 條是
    > $\leq$ 還是 $\geq$），$a_i$ 則是 $a_E$ 或 $a_G$ 的其中一個分量，
    > $A_{i,\cdot}$ 與 $b_i$ 也是同理。
    > 所以看到 tableau 裡的 $s_2$ 時，它指的是**第 2 條限制式**的鬆弛變數，
    > 不是前面那個按類別分組的向量。

    下面的「範例」下拉選單準備了四組輸入，分別對應四條不同的路徑，其中第二組會演出
    **人工變數逐出**與**刪除冗餘限制式**這兩個步驟。

    > **Remark: **想看逐出的話得付出一點代價：可行域會是扁平的。
    >
    > 原因是這樣 —— 人工變數之所以能卡在基底裡，必須是限制式把某個方向**釘死**了。
    > 但每條*不等式*都會帶自己的 slack 或 surplus 欄，這讓它的列跟其他列線性獨立，
    > 於是總能用非人工的欄位把 $a_i$ 換出去；真正會出事的是*等式*（或被 $\geq$ 與 $\leq$
    > 夾出來的等式），而那剛好也把三維可行域壓成一個平面。
    >
    > 我讓 AI 隨機掃了兩萬多組例子，**立體可行域的 9143 組裡沒有任何一組發生逐出事件**，
    > 扁平的 12080 組裡則有 8.12% 會。所以「立體」與「看得到逐出」大概是不能兼得的。
    >
    > 可行域被壓成平面時，模擬會省略那層半透明的實體、只保留邊框與路徑。
    > 另外可行域必須有界，否則沒有封閉的圖形可以畫。

    ### Path Colors

    Phase one 期間的點通常還在**可行域外面**，這時會畫成紅色叉叉與紅色虛線；
    等到人工變數全部歸零、進入 phase two 之後才會變回橘色。
    如果 phase one 的最佳值小於 0，模擬會直接停在那裡並說明原問題無可行解。

    ### Constraint Planes

    每條限制式（連同 $x_i=0$）對應的**整個平面**都會用很淡的灰色畫出來，不只是可行域的那一面。
    其中通過目前這個點的平面會標成**黃色**。

    這樣就看得出來每一步的點是「哪幾個平面的交點」，以及 pivot operation 換基變數時
    是沿著哪條交線在滑動 —— 因為某個變數變成非基變數（值為 0），
    幾何上就等於「這個點貼到了它對應的平面上」。
    phase one 之所以能在可行域外面移動，正是因為它走的是這些平面的交線，
    只是還沒走到全部限制式都滿足的那一塊。

    ### The Arrow Changes Meaning in Phase One

    Phase two 的綠色箭頭指向 $-\nabla f = -c$，也就是讓 $z$ 下降最快的方向。
    但 phase one 根本不在乎 $z$，所以那時候畫 $c$ 是沒有意義的。

    Phase one 表面上是在最小化 $\sum_i a_i$，而如果把輔助變數消掉，它其實是在最小化**總違反量**

    $$
    V(x)=\sum_{i \in \geq}\max(0,\; b_i - A_{i,\cdot}x)\;+\sum_{i \in =}\lvert b_i - A_{i,\cdot}x \rvert.
    $$

    （對一條 $\geq$ 的限制式，固定 $x$ 之後能取到的最小 $a_i$ 就是 $\max(0, b_i - A_{i,\cdot}x)$；
    等式那項在 phase one 可達的範圍內恆有 $A_{i,\cdot}x \leq b_i$，所以絕對值可以直接拆開）

    所以 $-V$ 的次梯度就是**目前還被違反的那些限制式的法向量之和**

    $$
    \nabla(-V)(x)=\sum_{i\,:\,a_i>0}A_{i,\cdot},
    $$

    這正是讓違反量下降最快的方向。因此在 phase one 期間箭頭會改成**紅色**並指向這個方向，
    也就是字面意義上的「往可行域走」；等到人工變數全部歸零，箭頭才切回綠色的 $-\nabla f$。
    """)
    return


@app.cell(hide_code=True)
def _(mo, set_simulation_step, simplex_simulation):
    preset_picker = mo.ui.dropdown(
        options=list(simplex_simulation.PRESETS),
        value=next(iter(simplex_simulation.PRESETS)),
        label="範例",
        on_change=lambda _: set_simulation_step(0),
    )
    preset_picker
    return (preset_picker,)


@app.cell(hide_code=True)
def _(mo, preset_picker, set_simulation_step, simplex_simulation):
    preset_objective, preset_constraints = simplex_simulation.PRESETS[
        preset_picker.value
    ]
    simulation_input_form = mo.ui.batch(
        mo.md("""
        **目標係數 $c=(c_1,c_2,c_3)$**

        {objective}

        **限制式（每行：`A1, A2, A3 <= b`，也支援 `>=` 與 `=`）**

        {constraints}
        """),
        elements={
            "objective": mo.ui.text(value=preset_objective, full_width=True),
            "constraints": mo.ui.text_area(
                value=preset_constraints,
                rows=6,
                full_width=True,
            ),
        },
    ).form(
        submit_button_label="套用並重新計算",
        on_change=lambda _: set_simulation_step(0),
    )
    simulation_input_form
    return preset_constraints, preset_objective, simulation_input_form


@app.cell(hide_code=True)
def _(
    mo,
    preset_constraints,
    preset_objective,
    simplex_simulation,
    simulation_input_form,
):
    _submitted = simulation_input_form.value
    _objective_text = (
        _submitted["objective"] if _submitted is not None else preset_objective
    )
    _constraints_text = (
        _submitted["constraints"] if _submitted is not None else preset_constraints
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
                "綠色箭頭是目標函數的負梯度。右側 tableau 和幾何頂點使用同一個 basis。"
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
    從模擬跟限制式可以觀察到，當 $A_{i,\cdot}\neq0$ 時，$s_i$ 除以限制式法向量的 norm，就會是**現在的點**跟**對應限制式的平面**之間的距離，也就是

    $$\frac{s_i}{\lVert A_{i, \cdot} \rVert} = \frac{\lvert b_i - A_{i, \cdot} x \rvert}{\lVert A_{i, \cdot} \rVert} = \text{distance between the current point and the constraint plane}.$$

    這對 slack 和 surplus 都成立 —— $\leq$ 的限制式給出 $s_i = b_i - A_{i,\cdot}x$，$\geq$ 的則是 $s_i = A_{i,\cdot}x - b_i$，兩者都非負，差別只在點落在平面的哪一側。

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
