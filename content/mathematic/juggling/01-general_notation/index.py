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

    先考慮後者，對於每個物件，我們可以用兩個物理量來描述他落下時的行為: **落到哪隻手**跟**落入手的時間點**。手用正整數編號，我們可以用以下的集合來刻畫此性質

    $$
    \mathcal{S} := \mathbb{Z}_{>0} \times \mathbb{Z}
    $$

    其中 $(i,t) \in \mathcal{S}$ 表示物件在時間 $t$ 落在第 $i$ 隻手。

    接著我們考慮前者，同一隻手可能會有多顆但有限數量的物件被拋出，此時一個拋的動作可以用 $\mathcal{S}$ 的 finite multiset 表示

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
    & \mathcal{S}_p := \mathbb{Z}_{>0} \times \mathbb{Z}/p\mathbb{Z} \\
    & T_p: \mathcal{S}_p \to M(\mathcal{S}_p) \\
    & T_p(i, \overline{t})(j, \overline{u}) := \sum_{q \in \mathbb{Z}}T(i, t)(j, u + qp)
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    注意到對於任意 $t_1 = t_2 + q_t p, u_1 = u_2 + q_u p, \quad q_t, q_u \in \mathbb{Z}$ ，我們有

    $$
    \begin{align*}
    & T_p(i, \overline{t_1})(j, \overline{u_1}) \\
    = & \sum_{q \in \mathbb{Z}}T(i, t_1)(j, u_1 + qp) \\
    = & \sum_{q \in \mathbb{Z}}T(i, t_2 + q_t p)(j, u_2 + q_u p + qp) \\
    = & \sum_{q \in \mathbb{Z}}T(i, t_2)(j, u_2 + (q + q_u - q_t)p) \\
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
    = & \sum_{j \in \mathbb{Z}_{>0}} \sum_{u_0 = 0}^{p - 1} \sum_{q \in \mathbb{Z}} T(i, t)(j, u_0 + qp) \\
    = & \sum_{j \in \mathbb{Z}_{>0}} \sum_{u_0 = 0}^{p - 1} T_p(i, \overline{t})(j, \overline{u_0}) \\
    = & \sum_{(j, \overline{u}) \in \mathcal{S}_p} T_p(i, \overline{t})(j, \overline{u})
    \end{align*}
    $$

    For (2)

    $$
    \begin{align*}
    & \sum_{(j, u) \in \mathcal{S}} T(j, u)(i, t) \\
    = & \sum_{j \in \mathbb{Z}_{>0}} \sum_{u_0 = 0}^{p - 1} \sum_{q \in \mathbb{Z}} T(j, u_0 + qp)(i, t) \\
    = & \sum_{j \in \mathbb{Z}_{>0}} \sum_{u_0 = 0}^{p - 1} \sum_{q \in \mathbb{Z}} T(j, u_0)(i, t - qp) \\
    = & \sum_{j \in \mathbb{Z}_{>0}} \sum_{u_0 = 0}^{p - 1} T_p(j, \overline{u_0})(i, \overline{t}) \\
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
    \mathcal{F} := \mathbb{Z}_{>0} \times \mathbb{Z}_{>0}
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
    b(t) := \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l \leq t < r}} T(i, l)(j, r)
    $$

    當然我們總不能雜耍招做到一半，球的數量突然就變多或變少，事實上今天 $T$ 如果是一個 juggling pattern ，那 $b(t)$ 確實會是一個常數函數。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proposition

    Let $T$ be a juggling pattern. Then $b(t)$ is constant in $t$.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    Split $b(t - 1), b(t)$ into two parts

    $$
    \begin{align*}
    b(t - 1)
    & = \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l < t < r}} T(i, l)(j, r)
        \;+\; \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l < t,\; r = t}} T(i, l)(j, r) \\
    b(t)
    & = \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l < t < r}} T(i, l)(j, r)
        \;+\; \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l = t,\; t < r}} T(i, l)(j, r)
    \end{align*}
    $$

    All terms are non-negative, so the splittings hold in $\mathbb{Z}_{\geq 0} \cup \{\infty\}$; the first parts agree, and so do the second:

    $$
    \begin{align*}
    & \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l < t,\; r = t}} T(i, l)(j, r) \\
    =& \sum_{(i, l) \in \mathcal{S},\; j \in \mathbb{Z}_{>0}} T(i, l)(j, t) && \text{(by causality)} \\
    =& \sum_{(i, l) \in \mathcal{S},\; j \in \mathbb{Z}_{>0}} T(j, t)(i, l) && \text{(by balance)} \\
    =& \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l = t,\; t < r}} T(i, l)(j, r) && \text{(by causality and change of variables)} \\
    \end{align*}
    $$

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    既然球數是獨立於時間的常數函數，我們可以僅用 $b_J$ 來表示。而除了球數跟週期外，其實還有其他 juggling matrices 內蘊的性質，包括手數、滯空時間上界、 multiplex 上界等等。我們皆可以把它翻譯成 juggling matrices 的語言描述這些性質。

    /// admonition | Definition (Parameters of a Pattern)
        type: definition

    Let $J$ be a juggling matrix. Its parameters are

    $$
    \begin{align*}
    b_J &:= \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l \leq t < r}} J(i, l)(j, r - l), \quad \forall t \in \mathbb{Z} && \text{(objects)} \\
    h_J &:= \sup \{\, i : J(i, t)(x) > 0,\, t \in \mathbb{Z},\, x \in \mathcal{F} \,\} && \text{(hands)} \\
    k_J &:= \sup \{\, u : J(s)(j, u) > 0,\, s \in \mathcal{S},\, j \in \mathbb{Z}_{>0} \,\} && \text{(max height)} \\
    c_J &:= \sup \Bigl\{\, \sum_{x \in \mathcal{F}} J(s)(x) : s \in \mathcal{S} \,\Bigr\} && \text{(max multiplex)} \\
    p_J &:= \inf \{\, q \in \mathbb{Z}_{>0} : J(i, t + q) = J(i, t),\ \forall (i, t) \in \mathcal{S} \,\} && \text{(min period)}
    \end{align*}
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    另外從定義還可以看出，任何時間點拋出的物件總數都不會超過 $b_J$ 。

    /// admonition
        type: proposition


    $$
    \begin{align*}
    \sum_{\substack{i \in \mathbb{Z}_{>0},\, (j, u) \in \mathcal{S}}} T(i, t)(j, u) \leq b_J, \quad \forall t \in \mathbb{Z} \\
    \sum_{\substack{i \in \mathbb{Z}_{>0},\, (j, u) \in \mathcal{F}}} J(i, t)(j, u) \leq b_J, \quad \forall t \in \mathbb{Z}
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

    Let $T$ be a juggling pattern and $m, n \in \mathbb{Z}, m < n$. Let

    $$
    \lambda_{m, n}(\tau, u) := \bigl\lvert\, [\tau,\, \tau + u) \cap [m,\, n) \,\bigr\rvert = \bigl( \min(n,\, \tau + u) - \max(m,\, \tau) \bigr)^{+}
    $$

    be the number of beats that $[\tau, \, \tau + u)$ spends inside $[m, \, n)$. Then the number of objects satisfies

    $$
    b_J \;=\; \frac{1}{n - m} \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}}
    J(i, \tau)(j, u) \, \lambda_{m, n}(\tau, u).
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
    J(i, \tau)(j, u) \, \lambda_{m, n}(\tau, u) \\
    = & \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}} T(i, \tau)(j, \tau + u) \, \bigl\lvert\, [\tau,\, \tau + u) \cap [m,\, n) \,\bigr\rvert \\
    = & \sum_{\substack{(i, l) \in \mathcal{S} \\ (j, r) \in \mathcal{S}}} \, \bigl\lvert\, [l,\, r) \cap [m,\, n) \,\bigr\rvert \, T(i, l)(j, r) \\
    = & \sum_{(i, l),\, (j, r) \in \mathcal{S}}  \sum_{\substack{m \leq t < n\\ l \leq t < r}} T(i, l)(j, r) \\
    = & \sum_{m \leq t < n}  \sum_{\substack{(i, l),\, (j, r) \in \mathcal{S} \\ l \leq t < r}} T(i, l)(j, r) \\
    = & \sum_{m \leq t < n} b(t) \\
    = & (n - m) \cdot b_J
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
    b_J = \frac{1}{p} \sum_{\substack{(i, \tau) \in \mathcal{S}, \, (j, u) \in \mathcal{F} \\ 0 \leq \tau < p}} J(i, \tau)(j, u) \, u.
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    Apply the average theorem with $m = 0$ and $n = p$.

    $$
    \begin{align*}
    & b \\
    = & \frac{1}{p} \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}}
    J(i, \tau)(j, u) \, \lambda_{0, p}(\tau, u) \\
    = & \frac{1}{p} \sum_{\substack{i \in \mathbb{Z}_{>0} \\ (j, u) \in \mathcal{F}}} \sum_{\tau \in \mathbb{Z}} J(i, \tau)(j, u) \, \lambda_{0, p}(\tau, u) \\
    = &  \frac{1}{p} \sum_{\substack{i \in \mathbb{Z}_{>0} \\ (j, u) \in \mathcal{F}}} \sum_{\tau_0 = 0}^{p - 1} \sum_{q \in \mathbb{Z}} J(i, \tau_0 + qp)(j, u) \, \lambda_{0, p}(\tau_0 + qp, u) \\
    = &  \frac{1}{p} \sum_{\substack{i \in \mathbb{Z}_{>0} \\ (j, u) \in \mathcal{F}}} \sum_{\tau_0 = 0}^{p - 1} J(i, \tau_0)(j, u) \underbrace{\sum_{q \in \mathbb{Z}} \lambda_{0, p}(\tau_0 + qp, u)}_{(1)} && \text{(by periodic)}
    \end{align*}
    $$

    Compute (1)

    $$
    \begin{align*}
    & \sum_{q \in \mathbb{Z}} \lambda_{0, p}(\tau_0 + qp, u) \\
    = & \sum_{q \in \mathbb{Z}}  \bigl\lvert\, [\tau_0 + qp,\, \tau_0 + qp + u) \cap [0,\, p) \,\bigr\rvert \\
    = & \sum_{q \in \mathbb{Z}}  \bigl\lvert\, [0 ,\, u) \cap [- \tau_0 - qp,\, -\tau_0 - qp + p) \,\bigr\rvert \\
    = & \bigl\lvert\, [0 ,\, u) \cap (-\infty,\, \infty) \,\bigr\rvert \\
    = & u
    \end{align*}
    $$

    Hence

    $$
    \begin{align*}
    & b \\
    = &  \frac{1}{p} \sum_{\substack{i \in \mathbb{Z}_{>0} \\ (j, u) \in \mathcal{F}}} \sum_{\tau_0 = 0}^{p - 1} J(i, \tau_0)(j, u) \, u \\
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
    如果今天只有有限隻手，且道具的滯空時間有 upper bound ，那也可以透過取極限的方式去計算道具數量。

    /// admonition
        type: corollary

    Let $T$ be a juggling pattern with $h_J, k_J < \infty$. Then the number of juggling items satisfies

    $$
    b_J = \lim_{\substack{m \to -\infty \\ n \to \infty }} \frac{1}{n - m} \sum_{\substack{(i, \tau) \in \mathcal{S}, \, (j, u) \in \mathcal{F} \\ m \leq \tau < n}} J(i, \tau)(j, u) \, u
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
    A(m, n) := \sum_{\substack{(i, \tau) \in \mathcal{S},\, (j, u) \in \mathcal{F} \\ m \leq \tau < n}} J(i, \tau)(j, u) \, u,
    \qquad
    E(m, n) := \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, \lambda_{m, n}(\tau, u).
    $$

    Note that $E(m, n) = b_J \cdot (n - m)$ and

    $$
    \begin{align*}
    & E(m, n) \\
    = & \sum_{\substack{i \in \mathbb{Z}_{>0} \\ m - k_J < \tau < n}} \sum_{(j, u) \in \mathcal{F}} J(i, \tau)(j, u) \, \lambda_{m, n}(\tau, u) \\
    \leq & \sum_{\substack{i \in \mathbb{Z}_{>0} \\ m - k_J < \tau < n}} k_J \sum_{(j, u) \in \mathcal{F}} J(i, \tau)(j, u) \\
    < & \infty && \text{(by $h_J, k_J < \infty$ and definition of finite multiset)}
    \end{align*}
    $$

    We have both $E(m, n), \, b_J < \infty$. Now we can compute

    $$
    \begin{align*}
    &  A(m, n) - E(m, n) \\
    = & \sum_{\substack{(i, \tau) \in \mathcal{S},\, (j, u) \in \mathcal{F} \\ m \leq \tau < n}} J(i, \tau)(j, u) \, u - \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, \lambda_{m, n}(\tau, u) \\
    = & \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, (u I_{[m,n)}(\tau) - \lambda_{m, n}(\tau, u)) \\
    \end{align*}
    $$

    where $I_{[m, n)}$ is the indicator function of $[m, n)$. The summation above can be split into several parts, in particular, the following part equals $0$

    $$
    \begin{align*}
    & \tau \leq m - u & \implies & u \, I_{[m, n)} (\tau) = 0, \, \lambda_{m, n} (\tau, u) = 0 \\
    & m \leq \tau \leq n - u & \implies & u \, I_{[m, n)} (\tau) = u, \, \lambda_{m, n} (\tau, u) = u \\
    & n \leq \tau & \implies & u \, I_{[m, n)} (\tau) = 0, \, \lambda_{m, n} (\tau, u) = 0
    \end{align*}
    $$

    Hence we have

    $$
    \begin{align*}
    & \left\lvert\, A(m, n) - E(m, n) \,\right\rvert \\
    = & \left\lvert\, \sum_{\substack{(i, \tau) \in \mathcal{S} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, (u I_{[m,n)}(\tau) - \lambda_{m, n}(\tau, u))  \,\right\rvert \\
    \leq & \left\lvert\, \sum_{m - k_J < \tau < m} \sum_{\substack{i \in \mathbb{Z}_{>0} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, (u I_{[m,n)}(\tau) - \lambda_{m, n}(\tau, u))  \,\right\rvert +
    \left\lvert\, \sum_{n - k_J < \tau < n} \sum_{\substack{i \in \mathbb{Z}_{>0} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \, (u I_{[m,n)}(\tau) - \lambda_{m, n}(\tau, u))  \,\right\rvert \\
    \leq & \left\lvert\, \sum_{m - k_J < \tau < m} 2 k_J \sum_{\substack{i \in \mathbb{Z}_{>0} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u)  \,\right\rvert +
    \left\lvert\, \sum_{n - k_J < \tau < n} 2 k_J \sum_{\substack{i \in \mathbb{Z}_{>0} \\ (j, u) \in \mathcal{F}}} J(i, \tau)(j, u) \,\right\rvert \\
    \leq & \left\lvert\, \sum_{m - k_J < \tau < m} 2 k_J b_J \,\right\rvert +
    \left\lvert\, \sum_{n - k_J < \tau < n} 2 k_J b_J \,\right\rvert \\
    \leq & 4 k_J^2 b_J
    \end{align*}
    $$

    finally

    $$
    \left\lvert \frac{A(m, n)}{n - m} - b_J \right\rvert
    = \frac{\lvert A(m, n) - E(m, n) \rvert}{n - m}
    \leq \frac{4 k_J^2 b_J}{n - m}
    \xrightarrow[\; \substack{m \to -\infty \\ n \to \infty} \;]{} 0 .
    $$

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Juggling Simulation

    下面是我讓 AI vibe 出來的雜耍模擬。

    因為 Juggling matrices 只能描述拋接相隔幾拍跟拋接的手。而這些拍子在整個時間軸上怎麼分布，及拋接的手何時會在哪個位置的資訊並不會包含在其中。為了簡單起見，以下模擬都會先假設時間是被這些拍子均勻切割，且所有拋接使用相同、可調整的持球時長。而對於每步驟，我們都用滑鼠去拖曳指定拋接球的位置。

    /// admonition
        type: remark

    模擬將整數拍作為接球的時間點，持球 $d$ 拍後拋出，因此拋接時長 $u$ 包含持球時間，實際滯空時間為 $u-d$。關於持球的討論未來有機會可以跟 claude 的雜耍三大定理一起討論。
    ///

    重力加速度也可以調整，單位是 $y$ 座標單位／拍平方，而不是公尺／秒平方。
    拋接拍數固定時，較大的重力需要較高的初速度，因此球會拋得更高；速度滑桿只改變播放快慢。
    初始視野會等比例縮放以容納整段軌跡，並在播放時保持固定；可以用滑鼠滾輪或雙指縮放，
    拖曳動畫空白處移動視野，也可以拖曳動畫下方的把手調整視窗高度。拋接座標不隨視野移動或縮放改變；
    拖曳平台時會鎖住視野，放開後才重新取景。

    當然在模擬之中，我們不太可能直接輸入 juggling matrices 的函數形式，但用玩家間流行的符號，在某些情境又會容易造成混淆，所以以下會用這裡自創但足夠簡潔的符號去表示我們的 juggling matrices 。另外，因為我們也不可能輸入無限長的 juggling matrices ，所以以下我們都考慮 periodic 的 juggling matrices 以循環播放。統理 $b, h, k, c$ 也都會是有限的。

    我們用以下符號代表某個球的拋接時長跟落回的手

    $$
    u\_j \simeq (j, u) \in \mathcal{F}
    $$

    而 multiplex 就可以用中括號列出零個或多個元素來表示

    $$
    [x_1, x_2, \cdots, x_l] \simeq m \in M(\mathcal{F}), \quad m(x) = \#\{i \in [l] : x_i = x\}
    $$

    在同一個瞬間，對不同的拋出手，我們用 $|$ 來做為分隔符

    $$
    m_1 | m_2 | \cdots | m_h \simeq (m_1, m_2, \cdots, m_h) \in M(\mathcal{F})^{[h]}
    $$

    最後，我們只要用空白或換行隔開 juggling matrices 的不同時間點即可

    $$
    f_{\overline{0}} \quad f_{\overline{1}} \quad \cdots \quad f_{\overline{p - 1}} \simeq (f_{\overline{0}}, f_{\overline{1}}, \cdots, f_{\overline{p - 1}}) \in M(\mathcal{F})^{[h] \times \mathbb{Z}/p\mathbb{Z}}
    $$

    具體例子可以看以下模擬的預設範例。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    另外為了因應雜耍玩家的習慣，一些簡化的符號也可以用在這裡的模擬

    | 寫法 | 意義或使用條件 |
    | --- | --- |
    | `0` | 空 multiset，等同 `[]` |
    | `a`~`z` | 時長 10~35 |
    | `u` | 僅在單手時，可省略 `u_1` 的 `_1`；`u` 可為數字或單字母 |
    | `u_j` | 單顆球可省略中括號，等同 `[u_j]` |

    此外輸入中的連續數字一律視為一個十進位整數，所以不同拍的內容務必用空白或換行分開。不同手跟 multiplex 也要各自用 `|` 跟 `,` 隔開。
    """)
    return


@app.cell(hide_code=True)
def _(juggling_simulation, mo):
    mo.iframe(juggling_simulation.HTML, height="1050px")
    return


@app.cell
def _():
    import juggling_simulation
    import marimo as mo

    return juggling_simulation, mo


if __name__ == "__main__":
    app.run()
