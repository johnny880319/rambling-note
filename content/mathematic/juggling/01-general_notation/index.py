import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # General Notation

    在拋接雜耍之中，我們時常會透過把不同的雜耍物件拋至不同高度來呈現不同的視覺效果。透過萬有引力定律我們知道，拋接的高度跟物件離開手上的時間呈正相關。但物件數量可能會遠超我們手的數量，此時就會需要把拋接不同物件的時間點給錯開。 `siteswap` 就是用來記錄拋接的時機以及離手時間的記號，一般來說學習這類記號可能會從單手且一個時間點只能拋接一個物件的記號開始。但這系列文章我打算一開始就用最 general 的記號來描述雜耍。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Juggling Pattern

    當我們描述拋接雜耍時，可以把物件的行為拆成**如何被拋出**與**如何落入手中**。

    先考慮後者，對於每個物件，我們可以用兩個物理量來描述他落下時的行為: **落到哪隻手**跟**落入手的時間點**。我們用以下的集合來刻畫此性質

    $$
    \mathcal{S} := \mathcal{H} \times \mathbb{Z}, \quad \mathcal{H} := \{1, 2, \cdots, h\}
    $$

    其中 $(i,t) \in \mathcal{S}$ 表示物件在時間 $t$ 落在第 $i$ 隻手。

    接著我們考慮前者，同一隻手可能會有多顆但有限數量的物件被拋出，此時一個拋的動作可以用 $\mathcal{S}$ 的有限 multiset 表示

    $$
    M(\mathcal{S}) := \left\{ m : \mathcal{S} \to \mathbb{Z}_{\geq 0} \;\middle|\; \sum_{s \in \mathcal{S}} m(s) < \infty \right\}
    $$

    當然每隻手在不同的時間點都可能會有不同的拋的動作，將所有這些動作蒐集起來，就可以用一個函數來描述雜耍的 pattern 。

    $$
    T: \mathcal{S} \to M(\mathcal{S})
    $$

    在這系列文章，我們會將 domain 跟 co-domain 在這兩個地方的 mapping 稱為 **juggling function** 。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    最後，並不是所有的 $T$ 都能被實際拋接出來。事實上一個 juggling function 要能被拋接若且唯若

    $$
    \begin{align*}
    & T(i,t)(j,u) > 0 \implies u > t, && \text{(causality)} \\
    & \sum_{x \in \mathcal{S}} T(s)(x) \;=\; \sum_{x \in \mathcal{S}} T(x)(s), \quad \forall s \in \mathcal{S}. && \text{(balance)}
    \end{align*}
    $$

    `causality` 是因為時光無法倒流，我們拋出去的物件只能在更後面的時間點接到。而 `balance` 則保證了我們接到的物件數量等於接下來要拋出去的球的數量，讓物件不會憑空消失。

    滿足以上兩個性質的 juggling function ，在這系列文章中，我們就稱他為 **juggling pattern** 。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Permutation Test

    通常雜耍玩家關心的會是有周期的pattern，也就是存在 $p \in \mathbb{Z}_{>0}$ 使得以下性質成立的 mapping

    $$
    T(i, t)(j, u) = T(i, t + p)(j, u + p), \quad \forall (i, t), (j, u) \in \mathcal{S}, \quad \text{(periodic)}
    $$

    在有周期的情況下，我們能想像我們只要蒐集一個周期的拋球的資訊就可以判斷一個 juggling function 是不是合法的 pattern 。我們甚至能將接球的資訊也壓縮在一個周期之內，而這壓縮後的資訊就是下面定義的 $T_p$

    $$
    \begin{align*}
    & \mathcal{S}_p := \mathcal{H} \times \mathbb{Z}/p\mathbb{Z} \\
    & T_p: \mathcal{S}_p \to M(\mathcal{S}_p) \\
    & T_p(i, \overline{t})(j, \overline{u}) := \sum_{k \in \mathbb{Z}}T(i, t)(j, u + kp)
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    注意到對於任意 $t_1 = t_2 + k_t p, u_1 = u_2 + k_u p, \quad k_t, k_u \in \mathbb{Z}$ ，我們有

    $$
    \begin{align*}
    & T_p(i, \overline{t_1})(j, \overline{u_1}) \\
    = & \sum_{k \in \mathbb{Z}}T(i, t_1)(j, u_1 + kp) \\
    = & \sum_{k \in \mathbb{Z}}T(i, t_2 + k_t p)(j, u_2 + k_u p + kp) \\
    = & \sum_{k \in \mathbb{Z}}T(i, t_2)(j, u_2 + (k + k_u - k_t)p) \\
    = &  T_p(i, \overline{t_2})(j, \overline{u_2})
    \end{align*}
    $$

    也就是說 $T_p$ 是 well-defined 的。

    而大名鼎鼎的 **permutation test** 告訴我們，只用 $T_p$ 就能判斷一個 causal periodic 的 juggling function 是否合法。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Theorem (Permutation Test)
        type: theorem

    Let $T$ be a causal, $p$-periodic juggling function. Then $T$ is a juggling
    pattern if and only if

    $$
    \sum_{\overline{x} \in \mathcal{S}_p} T_p(\overline{s})(\overline{x}) \;=\; \sum_{\overline{x} \in \mathcal{S}_p} T_p(\overline{x})(\overline{s}),
    \qquad \forall\, \overline{s} \in \mathcal{S}_p,
    $$

    that is, the throws of a single period permute the slots of $\mathcal{S}_p$
    among themselves, counted with multiplicity.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    It suffices to prove the following

    $$
    \begin{align*}
    \sum_{x \in \mathcal{S}} T(s)(x) \;=\; \sum_{\overline{x} \in \mathcal{S}_p} T_p(\overline{s})(\overline{x}), \quad \forall s \in \mathcal{S}. && \text{(1)} \\
    \sum_{x \in \mathcal{S}} T(x)(s) \;=\; \sum_{\overline{x} \in \mathcal{S}_p} T_p(\overline{x})(\overline{s}), \quad \forall s \in \mathcal{S}. && \text{(2)}
    \end{align*}
    $$

    where if $s = (i, t), \overline{s} := (i, \overline{t})$

     For (1)

    $$
    \begin{align*}
    & \sum_{(j, u) \in \mathcal{S}} T(i, t)(j, u) \\
    = & \sum_{j \in \mathcal{H}} \sum_{u_0 = 0}^{p - 1} \sum_{k \in \mathbb{Z}} T(i, t)(j, u_0 + kp) \\
    = & \sum_{j \in \mathcal{H}} \sum_{u_0 = 0}^{p - 1} T_p(i, \overline{t})(j, \overline{u_0}) \\
    = & \sum_{(j, \overline{u}) \in \mathcal{S}_p} T_p(i, \overline{t})(j, \overline{u})
    \end{align*}
    $$

    For (2)

    $$
    \begin{align*}
    & \sum_{(j, u) \in \mathcal{S}} T(j, u)(i, t) \\
    = & \sum_{j \in \mathcal{H}} \sum_{u_0 = 0}^{p - 1} \sum_{k \in \mathbb{Z}} T(j, u_0 + kp)(i, t) \\
    = & \sum_{j \in \mathcal{H}} \sum_{u_0 = 0}^{p - 1} \sum_{k \in \mathbb{Z}} T(j, u_0)(i, t - kp) \\
    = & \sum_{j \in \mathcal{H}} \sum_{u_0 = 0}^{p - 1} T_p(j, \overline{u_0})(i, \overline{t}) \\
    = & \sum_{(j, \overline{u}) \in \mathcal{S}_p} T_p(j, \overline{u})(i, \overline{t})
    \end{align*}
    $$

    Note that the terms are all non-negative, so the sums may be regrouped and reordered freely.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: remark

    當 $h = 1$ 且每個時間點恰好丟出一顆球時，等式左邊恆為 1 ，於是條件變成「每個時間點恰好落進一顆球」。換句話說，拋接形成了 $\mathbb{Z}/p\mathbb{Z}$ 上的permutation。
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Juggling Matrices

    在實際場景中，雜耍玩家們比起描述球落下的時間點，描述拋出後球滯空的時間會更直覺。所以實務場景裡，我們會用經過 affine transformation 後的記號來描述雜耍 pattern

    $$
    \mathcal{F} := \mathcal{H} \times \mathbb{Z}_{>0}
    $$

    $$
    J : \mathcal{S} \to M(\mathcal{F}), \qquad J(i,t)(j,u) := T(i,t)(j,\, t+u)
    $$

    /// admonition
        type: remark

    對於任意一個 juggling pattern $T$ ，因為我們有 causality 的條件，所以當 $u \leq 0$ 時， $T(i,t)(j,\, t+u)$ 都會是 $0$ ，因此我們只要關注 $u > 0$ 的狀況即可。

    反之今天如果我們做反變換，並將沒有定義的點設為 $0$，juggling matrices 的 co-domain 能保證 induce 出來的 juggling pattern 滿足 causality 的條件。
    ///

    此時 $u$ 的意義就會變成物件的滯空時間了，而 juggling matrices 就可以記為以下形式。

    $$
    J =
    \left[ \begin{array}{ccc}
        J(1, 1) & J(1, 2) & \cdots \\
        J(2, 1) & J(2, 2) & \cdots   \\
        \vdots & \vdots & \cdots  \\
        J(h, 1) & J(h, 2) & \cdots  \\
    \end{array} \right]
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    當我們要驗證一個 matrix 是否是 juggling matrix 時，只要把 juggling pattern 的條件翻譯過來即可。而前面提及過，causality 的條件因 co-domain 的性質會自動滿足，所以只要翻譯 balance 的條件即可。

    $$
    \sum_{x \in \mathcal{F}} J(i, t)(x)
    \;=\;
    \sum_{\substack{(j, u) \in \mathcal{S} \\ u < t}} J(j, u)(i, t - u),
    \qquad \forall (i, t) \in \mathcal{S} \qquad \text{(balance)}
    $$

    另外 periodic 的性質也可以翻譯成 juggling matrices 的語言，可以看出其意義就是每隔一個週期，就會拋出拋接時長、拋出手跟接入手一模一樣的物件

    $$
    J(i, t)(j, u) = J(i, t + p)(j, u), \quad \forall (i, t), (j, u) \in \mathcal{F}, \qquad \text{(periodic)}
    $$

    上述兩性質的翻譯因過於顯然，所以就讀者自證吧。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Average Theorem

    在日常雜耍中，玩家們遇到一個沒看過的 siteswap 時，第一件做的事情幾乎都是先算算看他的平均值，以確認這個是幾個物件的雜耍招。這就是所謂的 **average theorem** 。

    不過我們要先定義甚麼是一個雜耍招的物件數量，我們可以將某一時刻 $t$ 的雜耍物件數量定成**在 $t$ 或比 $t$ 早拋出去，並比 $t$ 晚落下的物件數量**，寫成數學式會長這樣

    $$
    N(t) := \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l \leq t < r}} T(i, l)(j, r)
    $$

    當然我們總不能雜耍招做到一半，球的數量突然就變多或變少，事實上今天 $T$ 如果是一個 juggling pattern ，那 $N(t)$ 確實會是一個常數函數。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proposition

    Let $T$ be a juggling pattern. Then $N(t)$ is a constant function.
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
    & N(t - 1) \\
    = & \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l \leq t - 1 < r}} T(i, l)(j, r) \\
    = & \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l \leq t < r}} T(i, l)(j, r) + \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l < t = r}} T(i, l)(j, r) - \underbrace{\sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l = t < r}} T(i, l)(j, r)}_{(1)}\\
    = & N(t) + \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l < t = r}} T(i, l)(j, r) - \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l = t < r}} T(i, l)(j, r) \\
    = & N(t) + \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ r = t}} T(i, l)(j, r) - \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l = t}} T(i, l)(j, r) && \text{(by causality)} \\
    = & N(t) + \sum_{k \in \mathcal{H},\, x \in \mathcal{S}} T(x)(k, t)  - \sum_{k \in \mathcal{H},\, x \in \mathcal{S}} T(k, t)(x)\\
    = & N(t) && \text{(by balance)} \\
    \end{align*}
    $$

    Note that (1) is finite since $| \mathcal{H} | < \infty$ and co-domain of juggling function is finite multiset.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    由上述性質可知，當我們考慮的是一個 juggling pattern 時，我們可以省略變數 $t$ ，直接將球數記為 $N$ 。

    另外從定義還可以看出，任何時間點拋出的物件總數都不會超過 $N$ 。

    /// admonition
        type: proposition


    $$
    \begin{align*}
    \sum_{\substack{i \in \mathcal{H},\, (j, u) \in \mathcal{S}}} T(i, t)(j, u) \leq N, \quad \forall t \in \mathbb{Z} \\
    \sum_{\substack{i \in \mathcal{H},\, (j, u) \in \mathcal{F}}} J(i, t)(j, u) \leq N, \quad \forall t \in \mathbb{Z}
    \end{align*}
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    接下來我們就可以討論 average theorem 了，它用 juggling matrices 的語言描述會比較直覺，也比較符合雜耍人日常計算道具數量的模式，以下是定理敘述

    /// admonition | Theorem (Average Theorem)
        type: theorem

    Let $T$ be a juggling pattern and $a, b \in \mathbb{Z}, a < b$. Let

    $$
    \lambda_{a, b}(\tau, u) := \bigl\lvert\, [\tau,\, \tau + u) \cap [a,\, b) \,\bigr\rvert = \bigl( \min(b,\, \tau + u) - \max(a,\, \tau) \bigr)^{+}
    $$

    be the number of beats that $[\tau, \, \tau + u)$ spends inside $[a, \, b)$. Then the number of objects satisfies

    $$
    N \;=\; \frac{1}{b - a} \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}}
    J(i, \tau)(j, u) \, \lambda_{a, b}(\tau, u).
    $$
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
    & \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}}
    J(i, \tau)(j, u) \, \lambda_{a, b}(\tau, u) \\
    = & \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}} T(i, \tau)(j, \tau + u) \, \bigl\lvert\, [\tau,\, \tau + u) \cap [a,\, b) \,\bigr\rvert \\
    = & \sum_{\substack{(i, l) \in \mathcal{S} \\ (j, r) \in \mathcal{S}}} \, \bigl\lvert\, [l,\, r) \cap [a,\, b) \,\bigr\rvert \, T(i, l)(j, r) \\
    = & \sum_{(i, l),\, (j, r) \in \mathcal{S}}  \sum_{\substack{a \leq t < b\\ l \leq t < r}} T(i, l)(j, r) \\
    = & \sum_{a \leq t < b}  \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l \leq t < r}} T(i, l)(j, r) \\
    = & \sum_{a \leq t < b} N(t) \\
    = & (b - a) \cdot N
    \end{align*}
    $$

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    當然，通常雜耍玩家只會去算週期性的 pattern 需要多少道具

    /// admonition
        type: corollary

    Let $T$ be a juggling pattern with period $p$. Then the number of juggling items satisfies

    $$
    N = \frac{1}{p} \sum_{\substack{(i, \tau) \in \mathcal{S}, \, (j, u) \in \mathcal{F} \\ 0 \leq \tau < p}} J(i, \tau)(j, u) \, u.
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    Apply the average theorem with $a = 0$ and $b = p$.

    $$
    \begin{align*}
    & N \\
    = & \frac{1}{p} \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}}
    J(i, \tau)(j, u) \, \lambda_{0, p}(\tau, u) \\
    = & \frac{1}{p} \sum_{\substack{i \in \mathcal{H} \\ (j, u) \in \mathcal{F}}} \sum_{\tau \in \mathbb{Z}} J(i, \tau)(j, u) \, \lambda_{0, p}(\tau, u) \\
    = &  \frac{1}{p} \sum_{\substack{i \in \mathcal{H} \\ (j, u) \in \mathcal{F}}} \sum_{\tau_0 = 0}^{p - 1} \sum_{k \in \mathbb{Z}} J(i, \tau_0 + kp)(j, u) \, \lambda_{0, p}(\tau_0 + kp, u) \\
    = &  \frac{1}{p} \sum_{\substack{i \in \mathcal{H} \\ (j, u) \in \mathcal{F}}} \sum_{\tau_0 = 0}^{p - 1} J(i, \tau_0)(j, u) \underbrace{\sum_{k \in \mathbb{Z}} \lambda_{0, p}(\tau_0 + kp, u)}_{(1)} && \text{(by periodic)}
    \end{align*}
    $$

    Compute (1)

    $$
    \begin{align*}
    & \sum_{k \in \mathbb{Z}} \lambda_{0, p}(\tau_0 + kp, u) \\
    = & \sum_{k \in \mathbb{Z}}  \bigl\lvert\, [\tau_0 + kp,\, \tau_0 + kp + u) \cap [0,\, p) \,\bigr\rvert \\
    = & \sum_{k \in \mathbb{Z}}  \bigl\lvert\, [0 ,\, u) \cap [- \tau_0 - kp,\, -\tau_0 - kp + p) \,\bigr\rvert \\
    = & \bigl\lvert\, [0 ,\, u) \cap (-\infty,\, \infty) \,\bigr\rvert \\
    = & u
    \end{align*}
    $$

    Hence

    $$
    \begin{align*}
    & N \\
    = &  \frac{1}{p} \sum_{\substack{i \in \mathcal{H} \\ (j, u) \in \mathcal{F}}} \sum_{\tau_0 = 0}^{p - 1} J(i, \tau_0)(j, u) \, u \\
    = & \frac{1}{p} \sum_{\substack{(i, \tau) \in \mathcal{S}, \, (j, u) \in \mathcal{F} \\ 0 \leq \tau < p}} J(i, \tau)(j, u) \, u
    \end{align*}
    $$

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    如果道具的滯空時間有 upper bound ，那也可以透過取極限的方式去計算道具數量

    /// admonition
        type: corollary

    Let $T$ be a juggling pattern. Suppose there exists $U \in \mathbb{Z}_{>0}$ such that $J(i, t)(j, u) = 0$ for all $u > U$. Then the number of juggling items satisfies

    $$
    N = \lim_{\substack{a \to -\infty \\ b \to \infty }} \frac{1}{b - a} \sum_{\substack{(i, \tau) \in \mathcal{S}, \, (j, u) \in \mathcal{F} \\ a \leq \tau < b}} J(i, \tau)(j, u) \, u
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    Write

    $$
    A(a, b) := \sum_{\substack{(i, \tau) \in \mathcal{S},\, (j, u) \in \mathcal{F} \\ a \leq \tau < b}} J(i, \tau)(j, u) \, u,
    \qquad
    E(a, b) := \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, \lambda_{a, b}(\tau, u).
    $$

    Note that $E(a, b) = N \cdot (b - a)$ and

    $$
    \begin{align*}
    & E(a, b) \\
    = & \sum_{\substack{i \in \mathcal{H} \\ a - U < \tau < b}} \sum_{(j, u) \in \mathcal{F}} J(i, \tau)(j, u) \, \lambda_{a, b}(\tau, u) \\
    \leq & \sum_{\substack{i \in \mathcal{H} \\ a - U < \tau < b}} U \sum_{(j, u) \in \mathcal{F}} J(i, \tau)(j, u) \\
    < & \infty
    \end{align*}
    $$

    We have both $E(a, b), \, N < \infty$. Now we can compute

    $$
    \begin{align*}
    &  A(a, b) - E(a, b) \\
    = & \sum_{\substack{(i, \tau) \in \mathcal{S},\, (j, u) \in \mathcal{F} \\ a \leq \tau < b}} J(i, \tau)(j, u) \, u - \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, \lambda_{a, b}(\tau, u) \\
    = & \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, (u I_{[a,b)}(\tau) - \lambda_{a, b}(\tau, u)) \\
    \end{align*}
    $$

    where $I_{[a, b)}$ is the indicator function of $[a, b)$. The summation above can be split into several parts, in particular, the following part equals $0$

    $$
    \begin{align*}
    & \tau \leq a - u & \implies & u \, I_{[a, b)} (\tau) = 0, \, \lambda_{a, b} (\tau, u) = 0 \\
    & a \leq \tau \leq b - u & \implies & u \, I_{[a, b)} (\tau) = u, \, \lambda_{a, b} (\tau, u) = u \\
    & b \leq \tau & \implies & u \, I_{[a, b)} (\tau) = 0, \, \lambda_{a, b} (\tau, u) = 0
    \end{align*}
    $$

    Hence we have

    $$
    \begin{align*}
    & \left\lvert\, A(a, b) - E(a, b) \,\right\rvert \\
    = & \left\lvert\, \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, (u I_{[a,b)}(\tau) - \lambda_{a, b}(\tau, u))  \,\right\rvert \\
    \leq & \left\lvert\, \sum_{a - U < \tau < a} \sum_{\substack{i \in \mathcal{H} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, (u I_{[a,b)}(\tau) - \lambda_{a, b}(\tau, u))  \,\right\rvert +
    \left\lvert\, \sum_{b - U < \tau < b} \sum_{\substack{i \in \mathcal{H} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, (u I_{[a,b)}(\tau) - \lambda_{a, b}(\tau, u))  \,\right\rvert \\
    \leq & \left\lvert\, \sum_{a - U < \tau < a} 2U \sum_{\substack{i \in \mathcal{H} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u)  \,\right\rvert +
    \left\lvert\, \sum_{b - U < \tau < b} 2U \sum_{\substack{i \in \mathcal{H} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \,\right\rvert \\
    \leq & \left\lvert\, \sum_{a - U < \tau < a} 2UN \,\right\rvert +
    \left\lvert\, \sum_{b - U < \tau < b} 2UN \,\right\rvert \\
    \leq & 4U^2N
    \end{align*}
    $$

    finally

    $$
    \left\lvert \frac{A(a, b)}{b - a} - N \right\rvert
    = \frac{\lvert A(a, b) - E(a, b) \rvert}{b - a}
    \leq \frac{4U^2N}{b - a}
    \xrightarrow[\; \substack{a \to -\infty \\ b \to \infty} \;]{} 0 .
    $$

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
