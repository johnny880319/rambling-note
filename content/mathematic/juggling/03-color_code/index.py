import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Color Code

    通常雜耍玩家在做招時，常常會使用不同顏色的雜耍道具，並讓這些道具經過不同的軌跡或高度，營造多個球路有規律的合成在一起的效果。這就是所謂的 color code juggling 。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Color Decomposition

    用嚴謹的語言來說，今天我們有一個 juggling matrix $J$ 跟週期 $p$ ，我們會想將它分解成數個週期同樣為 $p$ 的子 pattern 。

    /// admonition | Definition (Color Decomposition)
        type: definition

    Let $J$ be a juggling matrix and $p \in \mathbb{Z}_{>0} \cup \{\infty\}$. A color decomposition of $J$ with period $p$ is a family of juggling matrices $(J_{\alpha})_{\alpha \in \mathcal{A}}$ with

    $$
    J = \sum_{\alpha \in \mathcal{A}} J_{\alpha}, \qquad p_{J_{\alpha}} \mid p \quad \forall \alpha \in \mathcal{A} .
    $$

    A decomposition with $\lvert \mathcal{A} \rvert = 1$ is called trivial.
    ///

    在 color decomposition 之中， $\mathcal{A}$ 就是顏色的集合。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    而對於任意的 color decomposition ， $J$ 的 state sequence 會等於 $(J_{\alpha})_{\alpha \in \mathcal{A}}$ 的 state sequence 的加總。

    /// admonition
        type: proposition

    Let $(J_{\alpha})_{\alpha \in \mathcal{A}}$ be a color decomposition of $J$, and $\gamma$, $\gamma_{\alpha}$ the state sequences of $J$, $J_{\alpha}$. Then

    $$
    \gamma = \sum_{\alpha \in \mathcal{A}} \gamma_{\alpha}
    $$
    ///

    /// details
        type: proof

    $$
    \begin{align*}
    \gamma(t)(j, u) &= \sum_{i \in \mathbb{Z}_{>0}} \sum_{\tau < t} J(i, \tau)(j, \; t + u - 1 - \tau) \\
    &= \sum_{i \in \mathbb{Z}_{>0}} \sum_{\tau < t} \sum_{\alpha \in \mathcal{A}} J_{\alpha}(i, \tau)(j, \; t + u - 1 - \tau) \\
    &= \sum_{\alpha \in \mathcal{A}} \sum_{i \in \mathbb{Z}_{>0}} \sum_{\tau < t} J_{\alpha}(i, \tau)(j, \; t + u - 1 - \tau) && \text{(non-negative terms)} \\
    &= \sum_{\alpha \in \mathcal{A}} \gamma_{\alpha}(t)(j, u)
    \end{align*}
    $$

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    而 $J$ 的各種參數也會跟 $(J_{\alpha})_{\alpha \in \mathcal{A}}$ 的各種參數相關。下列定理的證明只需要從定義出發去做簡單的計算，所以證明就只把核心想法寫出來。

    /// admonition
        type: proposition

    Let $(J_\alpha)_{\alpha \in \mathcal{A}}$ be a color decomposition of $J$. Then

    $$
    \begin{align*}
    b_J &= \sum_{\alpha \in \mathcal{A}} b_{J_\alpha} \\
    h_J &= \sup_{\alpha \in \mathcal{A}} h_{J_\alpha} \\
    k_J &= \sup_{\alpha \in \mathcal{A}} k_{J_\alpha} \\
    c_J &\geq \sup_{\alpha \in \mathcal{A}} c_{J_\alpha} \\
    p_J &\mid \operatorname*{lcm}_{\alpha \in \mathcal{A}} p_{J_\alpha}
    \end{align*}
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// details
        type: proof

    Unfold the definitions:

    - For $b_J, c_J$: every term is non-negative, so the sums may be reordered,
      and dropping terms only lowers them.
    - For $h_J, k_J$: $J(s)(x) > 0$ if and only if $J_{\alpha}(s)(x) > 0$ for
      some $\alpha \in \mathcal{A}$.
    - For $p_J$: every period of $J$ is a multiple of $p_J$.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    前面定義 color decomposition 的時候，我們並沒有對 $p_J$ 設下條件。但從前述命題，其實可以推出 color decomposition 存在的充要條件。

    /// admonition | Corollary
        type: corollary

    $J$ has a color decomposition with period $p$ if and only if $p_J \mid p$.
    ///

    /// details
        type: proof

    $(\Rightarrow)$ $p_J \mid \operatorname{lcm}_{\alpha \in \mathcal{A}} p_{J_\alpha} \mid p$, by the proposition and the definition of color decomposition.

    $(\Leftarrow)$ The trivial decomposition has period $p$.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Minimized color decomposition

    對於任意 juggling matrix $J$ 跟 $p$ 滿足 $p_J \mid p$ 時，雖然前面的定理告訴我們總是有 trivial 的 color decomposition 。但這種case很無聊，事實上為了讓雜耍的 pattern 可以看起來更有結構性。我們往往會希望把他 decompose 成越多顏色越好，於是就可以引入 minimal color decomposition 的概念

    /// admonition | Definition (Minimal Color Decomposition)
        type: definition

    A color decomposition $(J_{\alpha})_{\alpha \in \mathcal{A}}$ of $J$ with period $p$ is minimal if every color decomposition of every $J_{\alpha}$ with period $p$ is trivial.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    基本上每提出一個新概念時，我們總是需要先證明他的存在性，才有討論下去的價值。事實上只要 color decomposition 存在，那 minimal color decomposition 就會存在。

    /// admonition | Theorem (Existence of Minimal Decompositions)
        type: theorem

    If $p_J \mid p$, then $J$ has a minimal color decomposition with period $p$.
    ///

    /// details | Proof (by AI)
        type: proof

    Write $\mathcal{S}_{\infty} := \mathcal{S}$, and let $G$ be the multigraph on $\mathcal{S}_p$ with one edge from $(i, \overline{t})$ to $(j, \overline{t + u})$ for each object thrown by $J$ at $(i, t)$ with flight $u$, for $t$ in one period. A $p$-periodic $K \leq J$ is determined by its set of edges, and it is a juggling matrix if and only if that set is non-empty and every vertex has as many of its edges in as out. So the color decompositions of $J$ with period $p$ are the partitions of the edges of $G$ into non-empty balanced sets. Call a simple directed cycle or a simple two-way infinite directed path a *strand*.

    *A strand has only the trivial decomposition.* Every vertex of a strand has one edge in and one out, so a balanced set containing one edge of a strand contains its neighbours, hence the whole strand.

    *Every edge lies on a strand.* Let $F$ be a balanced set of edges, $e \in F$ an edge from $u$ to $v$, and $R$ the set of vertices reachable from $v$ in $F$. If $u \in R$, a shortest path from $v$ to $u$ closes with $e$ into a simple cycle. Otherwise no edge of $F$ leaves $R$ while $e$ enters it, so if $R$ were finite,

    $$
    \sum_{s \in R} \lvert \mathrm{in}_F(s) \rvert > \sum_{s \in R} \lvert \mathrm{out}_F(s) \rvert ,
    $$

    against balance. Hence $R$ is infinite, and since every vertex has finitely many edges, König's lemma gives a simple ray starting at $v$. Likewise a simple ray ends at $u$; the two are disjoint as $u \notin R$, and with $e$ they form a strand.

    *Exhaustion.* The edges of $G$ are countable; list them as $e_1, e_2, \cdots$. Put $F_0 := G$, and $F_n := F_{n - 1} \setminus C_n$ for a strand $C_n \subseteq F_{n - 1}$ through $e_n$ if $e_n \in F_{n - 1}$, else $F_n := F_{n - 1}$. Each $F_n$ is balanced, every edge lies in some $C_n$, so the $C_n$ partition the edges of $G$ into strands, a minimal color decomposition with period $p$.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    當 $p = \infty$ 時，他的 minimal color decomposition 裡的每個子 pattern 物件數都是 1 。換言之當我們考慮無週期的分解時，美一顆球都能當成一個獨立的 pattern 看待。

    /// admonition | Theorem (Orbit Decomposition)
        type: theorem

    A color decomposition $(J_{\alpha})_{\alpha \in \mathcal{A}}$ of $J$ with period $\infty$ is minimal if and only if

    $$
    b_{J_{\alpha}} = 1 \qquad \forall \alpha \in \mathcal{A} .
    $$

    In particular $J$ has such a decomposition, and every such decomposition has $\lvert \mathcal{A} \rvert = b_J$.
    ///

    /// details | Proof (by AI)
        type: proof

    $(\Leftarrow)$ Every part of a color decomposition of $J_{\alpha}$ has $b \geq 1$, and these sum to $b_{J_{\alpha}} = 1$ by additivity, so there is a single part.

    $(\Rightarrow)$ Let $K := J_{\alpha}$, which has only the trivial decomposition, and pick a throw of $K$ from $(i_0, t_0)$ to $(i_1, t_1)$. By balance $K$ throws wherever it catches and catches wherever it throws, so this throw extends to a chain of throws of $K$

    $$
    \cdots \longrightarrow (i_{-1}, t_{-1}) \longrightarrow (i_0, t_0) \longrightarrow (i_1, t_1) \longrightarrow \cdots
    $$

    one from each $(i_k, t_k)$ to $(i_{k + 1}, t_{k + 1})$. Let $L$ consist of these throws. By causality $t_k < t_{k + 1}$, so the positions are distinct and $t_k \to \pm\infty$; hence $L \leq K$, $L$ catches and throws exactly once at each $(i_k, t_k)$, so $L$ is a juggling matrix and $K - L$ is balanced, and for every $t \in \mathbb{Z}$

    $$
    b_L = \lvert \{\, k \in \mathbb{Z} : t_k \leq t < t_{k + 1} \,\} \rvert = 1 .
    $$

    If $K - L \neq 0$, then $(L, K - L)$ would be a non-trivial decomposition of $K$; so $K = L$ and $b_K = 1$.

    The existence of such a decomposition is the existence of minimal decompositions, and $\lvert \mathcal{A} \rvert = \sum_{\alpha \in \mathcal{A}} b_{J_{\alpha}} = b_J$ by additivity.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    還有一個蠻直覺的事實是，當我們今天沒有 multiplex 時，每顆物件的軌跡其實都固定了，所以只會有唯一的 minimal color decomposition 。

    /// admonition | Theorem (Uniqueness without Multiplex)
        type: theorem

    If $c_J = 1$ and $p_J \mid p$, then $J$ has exactly one minimal color decomposition with period $p$, up to reindexing.
    ///

    /// details | Proof (by AI)
        type: proof

    Let $P := \{\, s \in \mathcal{S} : J(s) \neq 0 \,\}$. As $c_J = 1$, each $s = (i, t) \in P$ has $J(s) = \{(j, u)\}$ for a single $(j, u)$; put $\mathrm{next}(s) := (j, t + u)$. By balance $J$ catches exactly once where it throws and nowhere else, so

    $$
    \mathrm{next} \colon P \longrightarrow P \text{ is a bijection.}
    $$

    Let $\sim$ be the equivalence relation on $P$ generated by

    $$
    s \sim \mathrm{next}(s), \qquad (i, t) \sim (i, t + p) \quad (\text{if } p < \infty),
    $$

    and for each class $C \in P / \sim$ let $J_C$ agree with $J$ on $C$ and vanish elsewhere.

    *Parts are unions of classes.* Let $K \leq J$ be a juggling matrix with $p_K \mid p$, and $s \in P$ with $K(s) \neq 0$, so $K(s) = J(s)$. Then $K$ catches at $\mathrm{next}(s)$, hence throws there; $K$ throws at $s$, hence catches there, and the only throw of $J$ landing at $s$ comes from $\mathrm{next}^{-1}(s)$; and $K(i, t \pm p) = K(i, t)$. So $\{\, s : K(s) \neq 0 \,\}$ is closed under $\mathrm{next}^{\pm 1}$ and the shifts by $\pm p$, hence a union of classes.

    *Classes are parts.* Each class is closed under $\mathrm{next}^{\pm 1}$, so $J_C$ catches exactly where it throws; and under the shifts by $\pm p$, so $p_{J_C} \mid p$. Thus $J_C$ is a juggling matrix.

    Hence the color decompositions of $J$ with period $p$ are the groupings of the classes, a part has only the trivial decomposition exactly when it is a single class, and $(J_C)_{C \in P / \sim}$ is the only minimal one.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Corollary (One-Hand Colors)
        type: corollary

    Let $h_J = c_J = 1$ and $p_J \mid p < \infty$, and write $J(1, t) = \{(1, a_t)\}$ where $J$ throws at beat $t$, with $a_t := 0$ elsewhere. Then the minimal color decomposition of $J$ with period $p$ has one part $J_Z$ for each cycle $Z$ of

    $$
    \pi \colon \mathbb{Z}/p\mathbb{Z} \longrightarrow \mathbb{Z}/p\mathbb{Z}, \qquad \overline{t} \longmapsto \overline{t + a_t}
    $$

    on which $a$ is non-zero. The part $J_Z$ throws $a_t$ at the beats $t$ with $\overline{t} \in Z$, and

    $$
    b_{J_Z} = \frac{1}{p} \sum_{\overline{t} \in Z} a_t .
    $$
    ///

    /// details | Proof (by AI)
        type: proof

    In the uniqueness theorem $P$ is the set of beats with $a_t > 0$ and $\mathrm{next}(t) = t + a_t$, so $\overline{\mathrm{next}(t)} = \pi(\overline{t})$. A beat with $a_t = 0$ is a fixed point of $\pi$, so each cycle lies either in $\overline{P}$ or outside it. If $\overline{t'} = \pi^{k}(\overline{t})$ then $t' = \mathrm{next}^{k}(t) + m p$ for some $m$, so $t \sim t'$; conversely $\sim$ preserves the $\pi$-orbit of $\overline{t}$. Hence the classes of $\sim$ are the preimages of the cycles in $\overline{P}$, and the count of objects is the average theorem applied to $J_Z$.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Color Decomposition Simulator

    以下為用 AI vibe 出來的 color decomposition 的模擬，輸入任意 siteswap 他會窮舉出所有 minimized color decomposition 的可能性。但如果可能性太多而窮舉不完時，程式會要求降遞週期數或 multiplex 數量。
    """)
    return


@app.cell(hide_code=True)
def _(color_code_simulation, mo):
    mo.iframe(color_code_simulation.HTML, height="1280px")
    return


@app.cell
def _():
    import color_code_simulation
    import marimo as mo

    return color_code_simulation, mo


if __name__ == "__main__":
    app.run()
