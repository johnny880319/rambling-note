import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Juggling States

    在前一個章節，我們關心如何將一串雜耍的 pattern 轉為符號的形式。每個時間點，玩家都會進行不同的拋接動作，來讓雜耍持續下去。 **State Sequence** 則是記錄了每個時間點的狀態 (**Juggling State**)，這個狀態告訴我們接下來玩家可以進行何種拋接動作。這個狀態是無記憶性的，也就是不管你是透過何種途徑來到這個狀態，都不會影響你後續可以選擇的拋接動作。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## State Sequence

    在某個瞬間，對於每個物件，他的狀態能簡要用**將落入哪隻手**和**還有多久會落入手中**這兩個性質概括，可以發現此剛好我們能用上一章定義的 $\mathcal{F}$ 來描述。此外，我們會有多個物件，所以我們一樣可以用 multiset 來描述有多少物件屬於哪些狀態。只是跟 juggling function 的值域不同的是，我們有可能允許物件有無限多個 (但要注意我們每隻手每個瞬間能拋接的物件的數量有限)。綜上所述，我們可以用以下集合來描述各種可能的狀態，我們稱之為 **juggling state**

    $$
    \sigma \in M_{\infty}(\mathcal{F}) := \left\{ m : \mathcal{F} \to \mathbb{Z}_{\geq 0} \right\}, \qquad M(\mathcal{F}) \subset M_{\infty}(\mathcal{F}).
    $$

    這樣的 juggling state 代表著，若從此刻起不再做任何拋接，則再經過 $u$ 單位時間，會有 $\sigma(j, u)$ 個物件落回第 $j$ 隻手中。特別地，第 $u = 1$ 描述的就是下一瞬間各個手會拋接多少物件。

    當我們今天處於某個狀態時，我們會需要執行一個雜耍動作，來轉移到另一個狀態。在此過程中，我們會將下一瞬間落入手中的物件接住並再次拋出

    $$
    \sum_{x \in \mathcal{F}} \theta_i(x) = \sigma(i, 1) \qquad \forall i \in \mathbb{Z}_{>0}, \qquad \text{(balance)}
    $$

    其中 $\theta_i \in M(\mathcal{F})$ 代表著第 $i$ 隻手拋出的物件們的落點。在拋出物件的同時，空中其他的物件離落地又近了一拍，於是轉移到了新的狀態，其表達式為

    $$
    \sigma' = \sigma^{\downarrow} + \sum_{i \in \mathbb{Z}_{>0}} \theta_i, \qquad \text{where } \sigma^{\downarrow}(j, u) := \sigma(j, u + 1). \qquad \text{(transition)}
    $$

    當我們將各種狀態蒐集起來，雜耍動作當作我們的邊，我們就可以建構出一個 directed multigraph $\mathcal{G}$，我們稱其為 **state graph**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Definition (State Graph)
        type: definition

    The state graph $\mathcal{G}$ is the directed multigraph with vertex set

    $$
    V(\mathcal{G}) = M_{\infty}(\mathcal{F})
    $$

    and edge set

    $$
    E(\mathcal{G}) = \{\, (\sigma, \theta, \sigma') : \sigma, \sigma' \in M_{\infty}(\mathcal{F}),\ \theta \in M(\mathcal{F})^{\mathbb{Z}_{>0}},\ \text{balance and transition hold} \,\}
    $$
    ///

    /// admonition
        type: remark

    這是一個多重圖，因為今天如果有多隻手同時拋出物件時，如果將落點互換，其拋出前後的狀態會一致，但其代表的邊並不相同。
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    當我們遵循一個 juggling matrix 執行雜耍時，其實就相當於在各個 juggling state 之間轉換。每一拍都在 $\mathcal{G}$ 上行走。事實上，給定一個 juggling matrix ，則存在且唯一一個 $\mathcal{G}$ 上面的 walk ，其 vertex sequence 為 $\gamma \in V(\mathcal{G})^{\mathbb{Z}}$ ，使得它滿足

    $$
    \begin{align*}
    & \gamma(t)(i, 1) = \sum_{x \in \mathcal{F}} J(i, t)(x), && \forall (i, t) \in \mathcal{S} \quad \text{(balance)} \\
    & \gamma(t + 1) = \gamma(t)^{\downarrow} + \sum_{i \in \mathbb{Z}_{>0}} J(i, t), && \forall t \in \mathbb{Z} \quad \text{(transition)}
    \end{align*}
    $$

    也就是說當時間從 $t$ 推進到 $t + 1$ 時，點會從 $\gamma(t) \in V(\mathcal{G})$ 移動到 $\gamma(t + 1) \in V(\mathcal{G})$ ，而對應的邊則是

    $$
    (\gamma(t), J(\cdot, t), \gamma(t + 1)) \in E(\mathcal{G})
    $$

    我們稱這樣的 vertex sequence 為 **state sequence** 。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    在證明給定 $J$ 時， walk 的存在唯一性之前，我們先看一個簡單但實用的性質。雖然總球數可能是無限的，但我們每隻手每一瞬間能拋的物件數量都是有限的。而依據 balance 條件，我們可以得知對於每個落下的手，他每個瞬間準備接到的球也都會是有限的，而這些球正是以前各拍拋出、恰好在這一瞬間落下的球的總和。用精確一點的語言表達如下

    /// admonition
        type: proposition

    $$
    \sum_{\tau < t} \sum_{i \in \mathbb{Z}_{>0}} J(i, \tau)(j, t - \tau) < \infty, \qquad \forall (j, t) \in \mathcal{S}
    $$

    In particular,

    $$
    \sum_{i \in \mathbb{Z}_{>0}} J(i, t)(j, u) < \infty, \qquad \forall t \in \mathbb{Z},\, (j, u) \in \mathcal{F}
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
    \sum_{\tau < t} \sum_{i \in \mathbb{Z}_{>0}} J(i, \tau)(j, t - \tau)
    &= \sum_{x \in \mathcal{F}} J(j, t)(x) && \text{(by balance)} \\
    &< \infty && \text{(by definition of finite multiset)}
    \end{align*}
    $$

    For the second result

    $$
    \begin{align*}
    \sum_{i \in \mathbb{Z}_{>0}} J(i, t)(j, u) &\leq \sum_{\tau < t + 1} \sum_{i \in \mathbb{Z}_{>0}} J(i, \tau)(j, u + t - \tau) \\
    &< \infty
    \end{align*}
    $$

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    有了上述性質，我們就能解答存在唯一的問題，事實上只要證明 vertex sequence 存在唯一即可，其經過的邊會直接由 juggling matrices 給出。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Proposition (Throws Determine Sequence)
        type: proposition

    Let $T$ be a juggling pattern and $J$ its juggling matrix.  Then exactly
    one state sequence $\gamma : \mathbb{Z} \to M_{\infty}(\mathcal{F})$ satisfies the
    transition and balance equations for $J$, namely

    $$
    \gamma(t)(j, u) \;=\; \sum_{i \in \mathbb{Z}_{>0}} \sum_{\tau < t} J(i, \tau)(j, \; t + u - 1 - \tau).
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    **$\gamma \in M_{\infty}(\mathcal{F})^{\mathbb{Z}}$.**

    $$
    \begin{align*}
    \gamma(t)(j, u) &= \sum_{i \in \mathbb{Z}_{>0}} \sum_{\tau < t} J(i, \tau)(j, \; t + u - 1 - \tau) \\
    &\leq \sum_{i \in \mathbb{Z}_{>0}} \sum_{\tau < t + u - 1} J(i, \tau)(j, \; t + u - 1 - \tau) \\
    &< \infty && \text{(by proposition above)}
    \end{align*}
    $$

    **Uniqueness.**

    Let $\gamma, \gamma'$ both satisfy the two equations for $J$ and write

    $$\delta := \gamma - \gamma'$$

    Then by transition equation

    $$
    \begin{align*}
    & \delta(t + 1) \\
    &= \gamma(t + 1) - \gamma'(t + 1) \\
    &= \gamma(t)^{\downarrow} + \sum_{i \in \mathbb{Z}_{>0}} J(i, t) - \gamma'(t)^{\downarrow} - \sum_{i \in \mathbb{Z}_{>0}} J(i, t) \\
    &= \delta(t)^{\downarrow} && \text{(by the second part of proposition above)}
    \end{align*}
    $$

    Hence,

    $$
    \begin{align*}
    \delta(t)(j, u)
    &= \delta(t + 1)(j, u - 1) \\
    & \quad \vdots \\
    &= \delta(t + u - 1)(j, 1) \\
    &= \gamma(t + u - 1)(j, 1) - \gamma'(t + u - 1)(j, 1) \\
    &= 0 && \text{(by balance)}
    \end{align*}
    $$

    **Existence.**

    It suffices to check both equations for the displayed $\gamma$.

    *Balance.*

    $$
    \begin{align*}
    \gamma(t)(i, 1) &= \sum_{\substack{(i', \tau) \in \mathcal{S} \\ \tau < t}} J(i', \tau)(i, \; t - \tau) \\
    &= \sum_{x \in \mathcal{F}} J(i, t)(x) && \text{(by balance of $J$)}
    \end{align*}
    $$

    *Transition.*

    $$
    \begin{align*}
    \gamma(t + 1)(j, u)
    &= \sum_{i \in \mathbb{Z}_{>0}} \sum_{\tau < t + 1} J(i, \tau)(j, \; t + u - \tau) \\
    &= \sum_{i \in \mathbb{Z}_{>0}} \sum_{\tau < t} J(i, \tau)(j, \; t + u - \tau) + \sum_{i \in \mathbb{Z}_{>0}} J(i, t)(j, u) \\
    &= \gamma(t)^{\downarrow}(j, u) + \sum_{i \in \mathbb{Z}_{>0}} J(i, t)(j, u) \\
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

    一個 juggling matrix 決定唯一一條 $\mathcal{G}$ 上的 walk 。反之給定一條 walk ，對應的 juggling matrix 若存在則必唯一，其對應到的是 walk 的邊裡的 $\theta \in M(\mathcal{F})^{\mathbb{Z}_{>0}}$ 。

    但也有不存在的情況，比如

    $$
    \gamma(t)(j, u) = 1_{\{t \geq 0,\, j = 1,\, u = 1\}} + 1_{\{t < 0,\, j = 1,\, u = 1 - t\}},
    $$

    它描述的是一顆從未被拋出，卻一直在空中往下掉的球。在時間點 $0$ 落回第 $1$ 隻手，之後每拍被丟成 $1$ 。會有此現象的根本原因是因為 walk 只要確定每一步的狀態轉換是否合法，但 juggling matrix 要去溯源每一顆球如何被拋出。
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Juggling matrix 可以決定 walk ，所以可以進而決定 state sequence，但反之則不全然。因為當我們同時拋出多個物件時，把各手拋出物件的落點互換，也會得出一樣的 state 。

    不過弱化版的性質是成立的，一個 periodic 的 juggling matrix 在 $\mathcal{G}$ 裡對應到一條 closed walk，沿著它拋出的**落點手 $\times$ 滯空時長**的重數的和，只取決於經過了哪些頂點，不取決於經過的順序跟經過的邊，這就是著名的 **States Determine Throws**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Theorem (States Determine Throws)
        type: theorem

    Let $J$ be a $p$-periodic juggling matrix, and $\gamma$ its state sequence. Write

    $$
    \Sigma := \sum_{t = 0}^{p - 1} \gamma(t) \;\in\; M_{\infty}(\mathcal{F})
    $$

    then

    $$
    \sum_{t = 0}^{p - 1} \sum_{i \in \mathbb{Z}_{>0}} J(i, t) \;=\; \Sigma - \Sigma^{\downarrow}.
    $$

    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    Since $J$ is $p$-periodic, so is $\gamma$ by uniqueness. Then

    $$
    \begin{align*}
    & \sum_{t = 0}^{p - 1} \sum_{i \in \mathbb{Z}_{>0}} J(i, t) \\
    &= \sum_{t = 0}^{p - 1} \bigl( \gamma(t + 1) - \gamma(t)^{\downarrow} \bigr) \\
    &= \sum_{t = 0}^{p - 1} \gamma(t + 1) \;-\; \sum_{t = 0}^{p - 1} \gamma(t)^{\downarrow}
        && \text{(entrywise finite)} \\
    &= \sum_{t = 0}^{p - 1} \gamma(t) \;-\; \Bigl( \sum_{t = 0}^{p - 1} \gamma(t) \Bigr)^{\downarrow}
        && \text{(periodic; } \downarrow \text{ is linear)} \\
    &= \; \Sigma - \Sigma^{\downarrow}
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

    注意到 States Determine Throws 只決定了落回哪隻手跟滯空時長，並無法推出這些物件是何時從哪隻手拋出。
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    最後， juggling state 之所以可以被稱為**狀態**，是因為某個時間點是否能執行某個拋的動作，只取決於現在的狀態，我們不需要知道 juggling matrices 過去的所有行為。

    /// admonition | Theorem (Splicing)
        type: theorem

    Let $J, J'$ be juggling matrices with state sequences $\gamma, \gamma'$, and
    $t \in \mathbb{Z}$. The splice

    $$
    J''(\cdot, \tau) := \begin{cases} J(\cdot, \tau) & \tau < t \\ J'(\cdot, \tau) & \tau \geq t \end{cases}
    $$

    is a juggling matrix if and only if $\gamma(t) = \gamma'(t)$.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    $J''$ is causal, so it is a juggling matrix if and only if it is balanced, that
    is, for every $(i, \tau) \in \mathcal{S}$

    $$
    \sum_{\substack{(j, l) \in \mathcal{S} \\ l < \tau}} J''(j, l)(i, \tau - l) - \sum_{x \in \mathcal{F}} J''(i, \tau)(x) = 0,
    $$

    the second sum being finite as $J''(i, \tau) \in M(\mathcal{F})$. For $\tau < t$,

    $$
    \begin{align*}
    & \sum_{\substack{(j, l) \in \mathcal{S} \\ l < \tau}} J''(j, l)(i, \tau - l) - \sum_{x \in \mathcal{F}} J''(i, \tau)(x) \\
    &= \sum_{\substack{(j, l) \in \mathcal{S} \\ l < \tau}} J(j, l)(i, \tau - l) - \sum_{x \in \mathcal{F}} J(i, \tau)(x) \\
    &= 0 && \text{(by balance of $J$)}
    \end{align*}
    $$

    It remains to see that the difference vanishes for all $\tau \geq t$ if and only
    if $\gamma(t) = \gamma'(t)$. For $\tau \geq t$,

    $$
    \begin{align*}
    & \sum_{\substack{(j, l) \in \mathcal{S} \\ l < \tau}} J''(j, l)(i, \tau - l) - \sum_{x \in \mathcal{F}} J''(i, \tau)(x) \\
    &= \sum_{\substack{(j, l) \in \mathcal{S} \\ l < t}} J(j, l)(i, \tau - l) + \sum_{\substack{(j, l) \in \mathcal{S} \\ t \leq l < \tau}} J'(j, l)(i, \tau - l) - \sum_{x \in \mathcal{F}} J'(i, \tau)(x) \\
    &= \sum_{\substack{(j, l) \in \mathcal{S} \\ l < t}} J(j, l)(i, \tau - l) + \sum_{\substack{(j, l) \in \mathcal{S} \\ t \leq l < \tau}} J'(j, l)(i, \tau - l) - \sum_{\substack{(j, l) \in \mathcal{S} \\ l < \tau}} J'(j, l)(i, \tau - l) && \text{(by balance of $J'$)} \\
    &= \sum_{\substack{(j, l) \in \mathcal{S} \\ l < t}} J(j, l)(i, \tau - l) - \sum_{\substack{(j, l) \in \mathcal{S} \\ l < t}} J'(j, l)(i, \tau - l) \\
    &= \gamma(t)(i, \tau - t + 1) - \gamma'(t)(i, \tau - t + 1) && \text{(by Throws Determine Sequence)}
    \end{align*}
    $$

    With $v = \tau - t + 1$, this vanishes for all $(i, \tau)$ with $\tau \geq t$ if
    and only if $\gamma(t)(i, v) = \gamma'(t)(i, v)$ for all $(i, v) \in \mathcal{F}$.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Constraint on Juggling State

    實際雜耍的時候總是會有一些物理限制。比如不可能有無限隻手無限個物件，或是人的力量與地球的重力加速度，幾乎不太可能讓拋出去的物件的滯空時長達到 40 以上，除非你是玩彈力球之類的。同理，以人手掌的大小， multiplex 同時拋出 5 個物件應該也算蠻多的了。

    而這些限制對應到的就是上一篇文提到的 $b_J, h_J, k_J, c_J, p_J$ 這些參數，它們是 juggling matrices 內蘊的性質，而這些性質也會顯化在 juggling state 上面。我們可以先定義 juggling state 對應到的各項參數。

    /// admonition
        type: definition

    For $\sigma \in M_{\infty}(\mathcal{F})$, define the following parameters for $\sigma$

    $$
    \begin{align*}
    b_{\sigma} &:= \sum_{x \in \mathcal{F}} \sigma(x) && \text{(objects)} \\
    h_{\sigma} &:= \sup \{\, i : \sigma(i, u) > 0,\, u \in \mathbb{Z}_{>0} \,\} && \text{(hands)} \\
    k_{\sigma} &:= \sup \{\, u : \sigma(j, u) > 0,\, j \in \mathbb{Z}_{>0} \,\} && \text{(max height)} \\
    c_{\sigma} &:= \sup \{\, \sigma(x) : x \in \mathcal{F} \,\} && \text{(max multiplex)}
    \end{align*}
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: remark

    可以注意到相連的兩個狀態 $\sigma, \sigma'$ 的球數會一樣，假如 $(\sigma, \theta, \sigma') \in E(\mathcal{G})$

    $$
    \begin{align*}
    b_{\sigma'} &= \sum_{(i, u) \in \mathcal{F}} \sigma'(i, u) \\
    &= \sum_{(i, u) \in \mathcal{F}} \sigma^{\downarrow}(i, u) + \sum_{j \in \mathbb{Z}_{>0}} \sum_{(i, u) \in \mathcal{F}} \theta_j(i, u) \\
    &= \sum_{(i, u) \in \mathcal{F}} \sigma(i, u + 1) + \sum_{j \in \mathbb{Z}_{>0}} \sigma(j, 1) \\
    &= \sum_{(i, u) \in \mathcal{F}} \sigma(i, u) \\
    &= b_{\sigma}
    \end{align*}
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    這樣除了 period 以外的狀態序列的參數就可以用其經過的 juggling state 訂出來，而且會跟 juggling matrices 導出的參數是一樣的，不過這邊證明我先偷懶用 AI 證，之後有空我再用我的語言重寫。

    /// admonition | Proposition (Parameters from the State)
        type: proposition

    Let $\gamma$ be the state sequence of a juggling matrix $J$. Then

    $$
    \begin{align*}
    b_J &= \sup \{\, b_{\gamma(t)} : t \in \mathbb{Z} \,\} && \text{(objects)} \\
    h_J &= \sup \{\, h_{\gamma(t)} : t \in \mathbb{Z} \,\} && \text{(hands)} \\
    k_J &= \sup \{\, k_{\gamma(t)} : t \in \mathbb{Z} \,\} && \text{(max height)} \\
    c_J &= \sup \{\, c_{\gamma(t)} : t \in \mathbb{Z} \,\} && \text{(max multiplex)} \\
    p_{\gamma} &:= \inf \{\, q \in \mathbb{Z}_{>0} : \gamma(t + q) = \gamma(t),\ \forall t \in \mathbb{Z} \,\}, \qquad p_{\gamma} \mid p_J \text{ for } p_J < \infty && \text{(period)}
    \end{align*}
    $$

    In fact $b_{\gamma(t)}$ does not depend on $t$, so

    $$
    b_J = b_{\gamma(t)} \quad \forall t \in \mathbb{Z} \qquad \text{(objects)}
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Proof (by AI)
        type: proof

    *Objects.*

    $$
    \begin{align*}
    b_{\gamma(t)}
    &= \sum_{(j, u) \in \mathcal{F}} \sum_{i \in \mathbb{Z}_{>0}} \sum_{\tau < t} J(i, \tau)(j, \; t + u - 1 - \tau) \\
    &= \sum_{\substack{(i, \tau),\, (j, r) \in \mathcal{S} \\ \tau \leq t - 1 < r}} J(i, \tau)(j, r - \tau) && (r = t + u - 1) \\
    &= b(t - 1) = b_J
    \end{align*}
    $$

    *Hands.* If $\gamma(t)(i, u) > 0$ then hand $i$ catches at beat $t + u - 1$, so $J(i, \; t + u - 1) \neq 0$ by balance and $i \leq h_J$; hence $h_{\gamma(t)} \leq h_J$. Conversely $J(i, t)(x) > 0$ gives $\gamma(t)(i, 1) > 0$ by balance, so $h_J \leq \sup_t h_{\gamma(t)}$.

    *Height.* If $\gamma(t)(j, u) > 0$ then $J(i, \tau)(j, \; t + u - 1 - \tau) > 0$ for some $i$ and $\tau < t$, with $t + u - 1 - \tau \geq u$; hence $k_{\gamma(t)} \leq k_J$. Conversely $J(i, t)(j, u) > 0$ gives $\gamma(t + 1)(j, u) > 0$ by transition, so $k_J \leq \sup_t k_{\gamma(t)}$.

    *Multiplex.* By transition and balance,

    $$
    \gamma(t)(j, u) \leq \gamma(t + 1)(j, u - 1) \leq \cdots \leq \gamma(t + u - 1)(j, 1) = \sum_{x \in \mathcal{F}} J(j, \; t + u - 1)(x) \leq c_J,
    $$

    hence $c_{\gamma(t)} \leq c_J$; the case $u = 1$ is an equality, so $c_J \leq \sup_t c_{\gamma(t)}$.

    *Period.* For $p_J < \infty$, $\gamma(\cdot + p_J)$ satisfies both equations for $J$, so it equals $\gamma$ by uniqueness; thus $p_J$ is a period of $\gamma$, and every period of $\gamma$ is a multiple of the least one.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: remark

    跟 states determine throws 一樣，因為物件落點互換時 state 不會改變，所以我們無法從 state sequence 的週期去推算出 juggling matrices 的週期。但至少我們能知道後者週期是前者週期的倍數。
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    當我們沒加上任何限制時，因為我們可以拋到任意高度，或是擁有無限隻手無限個物件等等，可以輕易看出 $\mathcal{G}$ 有無限多個頂點。

    但我們可以加上手跟球有限、高度跟 multiplex 數量有有限上界的條件，用圖論的語言說，就是取 $\mathcal{G}$ 的一個誘導子圖：

    /// admonition | Definition (Bounded State Graph)
        type: definition

    For $b, h, k, c \in \mathbb{Z}_{>0} \cup \{\infty\}$, the bounded state graph
    $\mathcal{G}(b, h, k, c)$ is the subgraph of $\mathcal{G}$ induced by

    $$
    V(b, h, k, c) := \{\, \sigma \in M_{\infty}(\mathcal{F}) : b_{\sigma} = b,\ h_{\sigma} \leq h,\ k_{\sigma} \leq k,\ c_{\sigma} \leq c \,\}.
    $$
    ///

    球數取等號而其餘參數取上界，是因為相連的狀態球數會一樣。而這樣的誘導子圖，其狀態就會是有限的。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Proposition (Number of States)
        type: proposition

    For $b, h, k, c \in \mathbb{Z}_{>0}$,

    $$
    \lvert V(b, h, k, c) \rvert
    = \sum_{\ell \geq 0} (-1)^{\ell} \binom{hk}{\ell} \binom{b - \ell(c + 1) + hk - 1}{hk - 1}.
    $$

    In particular

    - For $c = 1$, the number is $\binom{hk}{b}$
    - For $c \geq b$, the number is $\binom{b + hk - 1}{b}$

    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    The conditions $h_{\sigma} \leq h$ and $k_{\sigma} \leq k$ confine $\sigma$ to
    the $hk$ slots $(j, u)$ with $j \leq h$ and $u \leq k$, and $c_{\sigma} \leq c$
    lets each of them take the values $0, 1, \cdots, c$; so the count is the
    coefficient of $z^{b}$ in

    $$
    \begin{align*}
    \left( 1 + z + \cdots + z^{c} \right)^{hk}
    & = \left( \frac{1 - z^{c + 1}}{1 - z} \right)^{hk} \\
    & = \left( \sum_{\ell \geq 0} (-1)^{\ell} \binom{hk}{\ell} z^{\ell(c + 1)} \right)
        \left( \sum_{n \geq 0} (-1)^{n} \binom{-hk}{n} z^{n} \right) \\
    & = \left( \sum_{\ell \geq 0} (-1)^{\ell} \binom{hk}{\ell} z^{\ell(c + 1)} \right)
        \left( \sum_{n \geq 0} \binom{n + hk - 1}{hk - 1} z^{n} \right)
    \end{align*}
    $$

    Taking $n = b - \ell(c + 1)$ from the second factor gives the sum.

    In particular,

    - At $c = 1$, the left side is $(1 + z)^{hk}$, the coefficient of $z^{b}$ is $\binom{hk}{b}$
    - At $c \geq b$, only the $\ell = 0$ term reaches $z^{b}$, giving $\binom{b + hk - 1}{b}$.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    雜耍玩家有時可能會想嘗試各種各樣的招式，而每個招是所要切換到的狀態可能都不太一樣。以下定理說明只要目前的 juggling state 的高度是有限的，就能在有限步驟內切換到想要的狀態。用圖的語言說就是，在 $\mathcal{G}$ 裡，從任何高度有限的頂點出發，都有 walk 通到每一個球數相同的頂點，而且走的步數跟路徑可以被嚴格控制。

    /// admonition | Theorem (Forgetting the Past)
        type: theorem

    Let $\sigma, \sigma' \in V(b, h, k, c)$ with $k < \infty$. Then
    $\mathcal{G}(b, h, k, c)$ contains a walk of length $k_\sigma$ from $\sigma$ to
    $\sigma'$.

    In particular, $\mathcal{G}(b, h, k, c)$ is strongly connected, with diameter at most $k$.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Proof (by AI)
        type: proof

    Start at time $0$; every object of $\sigma$ lands within $k_{\sigma}$ beats.
    Write $D(u) := \sum_{j} \sum_{v \geq u} \sigma'(j, v)$ for the number of objects
    of $\sigma'$ at height at least $u$. A throw at beat $s$ landing in slot
    $(j, u)$ of the state at time $k_{\sigma}$ has flight $k_{\sigma} + u - 1 - s$,
    which is at most $k$ exactly when $s \geq s_u := \max(0,\; u - 1 - (k - k_{\sigma}))$;
    so the $D(u)$ objects of $\sigma'$ at height $\geq u$ must be thrown at beats in
    $[s_u, k_{\sigma} - 1]$, an interval of $\min(k - u + 1, k_{\sigma})$ beats. Note
    $D(u) \leq hc (k - u + 1)$ and $D(u) \leq b \leq hc \, k_{\sigma}$.

    *Bounces.* An object may be thrown once more before its final throw: at the
    beat $s$ it lands, to some hand $\leq h$ at a beat $\tau \leq k_{\sigma} - 1$,
    with flight $\tau - s \leq k$. Process $u = k, k - 1, \cdots, 2$, and let $m(u)$
    be the number of objects whose last landing beat is $\geq s_u$. If
    $m(u) < D(u)$, bounce the $D(u) - m(u)$ earliest-landing objects not yet
    bounced into slots $(j, \tau)$ with $\tau \geq s_u$ that hold fewer than $c$
    objects. Such objects exist, since $D(u) \leq b$, and they land before beat
    $s_u$, so all earlier bounces also came from before beat $s_u$; hence the room
    in the beats $\geq s_u$ is $hc \min(k - u + 1, k_{\sigma}) - m(u) \geq D(u) - m(u)$.
    Afterwards $m(u) \geq D(u)$ for every $u$.

    *Targets.* Process $u = k, \cdots, 1$ again: assign the objects of $\sigma'$ at
    height $u$ to $D(u) - D(u + 1)$ unassigned objects whose last landing beat $s$
    is $\geq s_u$, of which there are $m(u) - D(u + 1)$, and throw each from that
    beat with flight $k_{\sigma} + u - 1 - s \leq k$.

    Every object is thrown when it lands, so each beat is an edge of
    $\mathcal{G}$; every flight is at most $k$ and lands in a hand $\leq h$; every
    slot holds at most $c$ objects, those landing before beat $k_{\sigma}$ by
    construction and the later ones because they form $\sigma'$; and at time
    $k_{\sigma}$ exactly the objects of $\sigma'$ are in the air.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    剩下幾個也是關於 juggling state 的性質，但因為篇幅跟時間因素，就不證明他們了。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    以下兩個定理是研究 $\mathcal{G}(b, h, k, \infty)$ 的 cycle (在 [Polster, *The Mathematics of Juggling*](https://books.google.com.tw/books/about/The_Mathematics_of_Juggling.html?id=YCARBwAAQBAJ&redir_esc=y) 裡稱作 **prime loop** ) 最長可以到多長。

    /// admonition | Theorem
        type: theorem

    For $b, h, k \geq 2$, no cycle of $\mathcal{G}(b, h, k, \infty)$ visits every vertex.

    *[Polster, *The Mathematics of Juggling*](https://books.google.com.tw/books/about/The_Mathematics_of_Juggling.html?id=YCARBwAAQBAJ&redir_esc=y) §4.3, where a sketch of the proof is given.*

    ///

    /// admonition | Theorem (Maximal Prime Loops)
        type: theorem

    Let $\mathrm{MMP}(b, h, k)$ be the length of a longest cycle of
    $\mathcal{G}(b, h, k, \infty)$.  For $b, h, k \geq 2$,

    $$
    \binom{b + h - 1}{b} k \;\leq\; \mathrm{MMP}(b, h, k) \;\leq\; \binom{b + hk - 1}{b} - 1 .
    $$

    The upper bound is the theorem above; the lower bound comes from a cycle
    through the states whose objects all sit at the same height.

    *[Polster, *The Mathematics of Juggling*](https://books.google.com.tw/books/about/The_Mathematics_of_Juggling.html?id=YCARBwAAQBAJ&redir_esc=y) §4.3.*

    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    最後，當我們只有一隻手且不做 multiplex 時，週期為 p 的 juggling matrices 的可能性可以被精確算出來。

    /// admonition | Theorem (Buhler–Eisenbud–Graham–Wright)
        type: theorem

    The number of closed walks of length $p$ in $\mathcal{G}(b, 1, \infty, 1)$ is $(b + 1)^{p} - b^{p}$.

    *[Buhler, Eisenbud, Graham & Wright, *Juggling Drops and Descents*, Amer. Math. Monthly **101** (1994) 507–519](https://doi.org/10.1080/00029890.1994.11996984).*
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Work in Progress

    從這裡以下的內容是我讓 AI 先幫我整理有哪些定理跟簡短的證明，之後會把它們都整理好，或是把過於細節的內容捨棄。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    接著是有界狀態圖的一個對稱性。

    /// admonition | Theorem (Complement Duality)
        type: theorem

    For $h, k, c < \infty$, reversing each hand's slots and then replacing every
    count $x$ by $c - x$ is a bijection $V(b, h, k, c) \to V(hkc - b, h, k, c)$
    that carries every edge of $\mathcal{G}(b, h, k, c)$ to an edge of
    $\mathcal{G}(hkc - b, h, k, c)$ in the reverse direction.  The two graphs are
    therefore anti-isomorphic, and have the same number of closed walks of each
    length.

    *[Polster, *The Mathematics of Juggling*](https://books.google.com.tw/books/about/The_Mathematics_of_Juggling.html?id=YCARBwAAQBAJ&redir_esc=y) §2.8.5 treats the one-hand case without multiplex; the form above, for any $h$ and $c$, is proved below.*

    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    Write $\varphi(\sigma)(j, u) := c - \sigma(j, k + 1 - u)$.  Each entry stays
    in $\{0, \cdots, c\}$, the total becomes $hkc - b$, and $\varphi$ is an
    involution, so it is a bijection between the two vertex sets.

    Let $\sigma \to \sigma'$ be an edge and write
    $\theta := \sum_{i \in \mathbb{Z}_{>0}} J(i, t)$ for where its objects land, so
    that $\sigma'(j, u) = \sigma(j, u + 1) + \theta(j, u)$ throughout, reading
    $\sigma(j, k + 1) = 0$.  Put

    $$
    \tilde{\theta}(j, u) := \begin{cases}
    \theta(j, k - u) & 1 \leq u \leq k - 1 \\
    c - \sigma(j, 1) & u = k
    \end{cases}
    $$

    Then for $u \leq k - 1$

    $$
    \begin{align*}
    \varphi(\sigma')(j, u + 1) + \tilde{\theta}(j, u)
    & = c - \sigma'(j, k - u) + \theta(j, k - u) \\
    & = c - \sigma(j, k + 1 - u) - \theta(j, k - u) + \theta(j, k - u) \\
    & = \varphi(\sigma)(j, u)
    \end{align*}
    $$

    and at $u = k$ the left side is $0 + c - \sigma(j, 1)$, which is
    $\varphi(\sigma)(j, k)$ as well.  So $\tilde{\theta}$ carries
    $\varphi(\sigma')$ to $\varphi(\sigma)$, one step in the reversed direction.
    It throws the right number of objects:

    $$
    \begin{align*}
    \sum_{j, u} \tilde{\theta}(j, u)
    & = \sum_{j \in \mathbb{Z}_{>0}} \sum_{v = 1}^{k - 1} \theta(j, v)
        \;+\; hc - \sum_{j \in \mathbb{Z}_{>0}} \sigma(j, 1) \\
    & = hc - \sum_{j \in \mathbb{Z}_{>0}} \theta(j, k)
        && \text{(balance for } \sigma \text{)} \\
    & = \sum_{j \in \mathbb{Z}_{>0}} \bigl( c - \sigma'(j, k) \bigr)
        \;=\; \sum_{j \in \mathbb{Z}_{>0}} \varphi(\sigma')(j, 1)
    \end{align*}
    $$

    and a total may be split among the throwing hands exactly as their individual
    balances require, because a throw constrains only where objects land, never
    which hand released them.  Applying the construction to the new edge returns
    the old one, so $\varphi$ is a bijection on edges as well.

    <span class="qed">$\square$</span>
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
