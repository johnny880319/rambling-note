import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Dual problem

    前一篇文章，我們透過 **simplex method** 來解線性規劃問題。但其實除了從頭開始解規劃問題以外，還有很多議題可以研究，比如:

    1. 限制式的常數項稍微變動時，對 optimal solution 的影響。 (敏感度分析)
    2. 在已經求得 optimal solution 的問題哩，加入新的變數or限制式，能否快速找到新的 optimal solution。

    Dual problem 剛好可以用來處理這些問題。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## General form

    雖然之後這篇筆記只會對比較 particular 形式的線性規劃問題去做分析。 但因為 general 版本的 duality 我覺得十分美麗，所以我這裡還是先用 general 版本的 **primal problem** 起頭

    $$
    \begin{aligned}
        \text{minimize } \quad &
            \left[ \begin{array}{ccc}
                c_P^T & c_N^T & c_R^T
            \end{array} \right]
            \left[ \begin{array}{c}
                x_P \\
                x_N \\
                x_R
            \end{array} \right]
            \\
        \text{subject to } \quad &
            \left[ \begin{array}{ccc}
                A_{P, P} & A_{P, N} & A_{P, R} \\
                A_{N, P} & A_{N, N} & A_{N, R} \\
                A_{R, P} & A_{R, N} & A_{R, R}
            \end{array} \right]
            \left[ \begin{array}{c}
                x_P \\
                x_N \\
                x_R
            \end{array} \right]
            \left\{ \begin{array}{c}
                \geq \\
                \leq \\
                =
            \end{array} \right\}
            \left[ \begin{array}{c}
                b_P \\
                b_N \\
                b_R
            \end{array} \right]
            \\
        \text{and } \quad &
        \left[ \begin{array}{c}
            x_P \\
            x_N \\
            x_R
        \end{array} \right]
        \left\{ \begin{array}{c}
            \geq \\
            \leq \\
            \in
        \end{array} \right\}
        \left[ \begin{array}{c}
            0 \\
            0 \\
            \mathbb{R}^{\dim{x_R}}
        \end{array} \right]
    \end{aligned}
    \tag{primal-general}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    則他對應的 **dual problem** 為

    $$
    \begin{aligned}
        \text{maximize } \quad &
            \left[ \begin{array}{ccc}
                b_P^T & b_N^T & b_R^T
            \end{array} \right]
            \left[ \begin{array}{c}
                y_P \\
                y_N \\
                y_R
            \end{array} \right]
            \\
        \text{subject to } \quad &
            \left[ \begin{array}{ccc}
                A_{P, P}^T & A_{N, P}^T & A_{R, P}^T \\
                A_{P, N}^T & A_{N, N}^T & A_{R, N}^T \\
                A_{P, R}^T & A_{N, R}^T & A_{R, R}^T
            \end{array} \right]
            \left[ \begin{array}{c}
                y_P \\
                y_N \\
                y_R
            \end{array} \right]
            \left\{ \begin{array}{c}
                \leq \\
                \geq \\
                =
            \end{array} \right\}
            \left[ \begin{array}{c}
                c_P \\
                c_N \\
                c_R
            \end{array} \right]
            \\
        \text{and } \quad &
        \left[ \begin{array}{c}
            y_P \\
            y_N \\
            y_R
        \end{array} \right]
        \left\{ \begin{array}{c}
            \geq \\
            \leq \\
            \in
        \end{array} \right\}
        \left[ \begin{array}{c}
            0 \\
            0 \\
            \mathbb{R}^{\dim{y_R}}
        \end{array} \right]
    \end{aligned}
    \tag{dual-general}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    當我們同時考慮這個 **primal-dual pairs** 時，可以發現對於所有滿足兩問題限制式的 $x, y$ ，以下關係式都能滿足

    $$
    \begin{aligned}
    &
    \left[ \begin{array}{ccc}
        c_P^T & c_N^T & c_R^T
    \end{array} \right]
    \left[ \begin{array}{c}
        x_P \\
        x_N \\
        x_R
    \end{array} \right]
    \\
    \geq &
    \left[ \begin{array}{ccc}
        y_P^T & y_N^T & y_R^T
    \end{array} \right]
    \left[ \begin{array}{ccc}
        A_{P, P} & A_{P, N} & A_{P, R} \\
        A_{N, P} & A_{N, N} & A_{N, R} \\
        A_{R, P} & A_{R, N} & A_{R, R}
    \end{array} \right]
    \left[ \begin{array}{c}
        x_P \\
        x_N \\
        x_R
    \end{array} \right]
    \\
    \geq &
    \left[ \begin{array}{ccc}
        y_P^T & y_N^T & y_R^T
    \end{array} \right]
    \left[ \begin{array}{c}
        b_P \\
        b_N \\
        b_R
    \end{array} \right]
    \end{aligned}
    $$

    其中第一個不等號式成立是因為 dual 的限制式及 $x$ 的值域。第二個不等號成立是因為 primal 的限制式及 $y$ 的值域。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    於是我們就有了 primal-dual 的 weak duality theorem:

    > **Theorem** For primal-dual pairs defined above, if $x, y$ are primal-dual feasible, then
    >
    > - $c^T x \geq b^T y$
    > - If $c^T x = b^T y$, then $x, y$ are primal-dual optimal.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Strong Duality and Complementary Slackness

    Weak duality 告訴我們說如果 primal-dual 的目標值如果相等，則它們都是 optimal solution。而 strong duality 則是說**若 primal 有有限最佳解，則 dual 也有最佳解，且兩者最佳值相等；反之亦然。**是比 weak duality 還強的性質。理論上 general form 是有 strong duality 的，但證起來應該會很麻煩，所以這邊就先只考慮簡單的 form ，這個 form 能直接讓上一篇文章的 canonical form 帶入，好處就是我們可以直接套用前一篇文章推導出來的性質。

    考慮以下 primal-dual problem

    $$
    \begin{aligned}
        \text{minimize } \quad &
            c^T x \\
        \text{subject to } \quad &
            A x = b \\
        \text{and } \quad &
            x \geq 0
    \end{aligned}
    \tag{primal}
    $$

    $$
    \begin{aligned}
        \text{maximize } \quad &
            b^T y \\
        \text{subject to } \quad &
            A^T y \leq c \\
        \text{and } \quad &
            y \in \mathbb{R}^{\dim{y}}
    \end{aligned}
    \tag{dual}
    $$

    假設 $\overline{x}$ 是 primal 的 basic optimal solution，並選取一個 optimal basis $B$，使其 reduced costs 滿足 $c_N^T - c_B^T A_B^{-1} A_N \geq 0$，或者也可以寫成 $A_N^T (A_B^T)^{-1} c_B \leq c_N$ ，此時如果我們令 $\overline{y} = (A_B^T)^{-1} c_B$，我們會發現他是dual feasible 的

    $$
    A^T \overline{y} =
    \left[ \begin{array}{c}
        A_B^T \\
        A_N^T
    \end{array} \right]
    (A_B^T)^{-1} c_B
    =
    \left[ \begin{array}{c}
        c_B \\
        A_N^T (A_B^T)^{-1} c_B
    \end{array} \right]
    \leq
    \left[ \begin{array}{c}
        c_B \\
        c_N
    \end{array} \right]
    = c
    $$

    並且因為 $x_N = 0$ ，所以可以得到以下等式

    $$
    b^T \overline{y} = \overline{x}^T A^T \overline{y}
    = \overline{x}^T
    \left[ \begin{array}{c}
        c_B \\
        A_N^T (A_B^T)^{-1} c_B
    \end{array} \right]
    =
    \left[ \begin{array}{cc}
        \overline{x_B}^T & \overline{x_N}^T
    \end{array} \right]
    \left[ \begin{array}{c}
        c_B \\
        A_N^T (A_B^T)^{-1} c_B
    \end{array} \right]
    = \overline{x_B}^T c_B = \overline{x}^T c
    $$

    by weak duality, 我們可以得到 $\overline{y} = (A_B^T)^{-1} c_B$ 是 dual optimal solution，並且 primal-dual optimal value 相等。於是我們就有了 primal-dual 的 strong duality theorem:

    > Theorem: For primal-dual pairs defined above, $\overline{x}, \overline{y}$ are primal-dual optimal if
    and only if $\overline{x}, \overline{y}$ are primal-dual feasible and $c^T \overline{x} = b^T \overline{y}$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    假如今天我們為 dual problem 加入 slack variable

    $$
    \begin{aligned}
        \text{maximize } \quad &
            b^T y \\
        \text{subject to } \quad &
            A^T y + s = c \\
        \text{and } \quad y \in \mathbb{R}^{\dim{y}}, s \geq 0
    \end{aligned}
    \tag{slack dual}
    $$

    則對於任意 feasible 的 $x, y, s$ ，我們有

    $$
    c^T x = y^T A x + s^T x =  y^T b + s^T x
    $$

    於是我們可以擴充 strong duality 的內容

    > **Theorem (complementary slackness):**For primal, slack dual pairs defined above and $x, (y, s)$ are feasible solution, then the following are equivalent
    >
    > - $x, (y, s)$ are primal-dual optimal
    > - $c^T x = b^T y$
    > - $s^T x = 0$

    > **Remark:** Duality 會交換限制式與變數的角色；在特定問題結構與求解方法下，解 dual 可能更有效率，但不能只從限制式數量判斷。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Shadow prices
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
