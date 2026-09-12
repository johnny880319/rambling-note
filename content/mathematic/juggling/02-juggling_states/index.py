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
    \begin{align*}
    & \sigma(t + 1) = \sigma(t)^{\downarrow} + \sum_{i \in [h]} J(i, t), & \qquad \text{(transition)} \\
    \text{ where } \quad & f^{\downarrow}(j, u) := f(j, u + 1) \quad \text{ for } f \in M(\mathcal{F})
    \end{align*}
    $$

    並且下一拍要落回手中的物件數量，跟接下來要丟出的物件的數量要一致

    $$
    \sum_{x \in \mathcal{F}} J(i, t)(x) = \sigma(t)(i, 1), \qquad \forall i \in [h] \qquad \text{(balance)}
    $$

    當然，滿足上述條件的 juggling state 是否存在唯一沒有到很顯然，敘述及證明如下
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Proposition (Throws Determine States)
        type: proposition

    Let $T$ be a juggling pattern with $b < \infty$, and $J$ its juggling matrix.
    Then exactly one $\sigma : \mathbb{Z} \to M(\mathcal{F})$ satisfies the
    transition and balance equations for $J$, namely

    $$
    \sigma(t)(j, u) \;=\; \sum_{i \in [h]} \sum_{\tau < t} J(i, \tau)(j, \; t + u - 1 - \tau) ,
    $$

    and $\sum_{x \in \mathcal{F}} \sigma(t)(x) = b$ for every $t$.
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    *Uniqueness.*  Let $\sigma, \sigma'$ both satisfy the two equations for $J$ and
    write $\delta := \sigma - \sigma'$.  The transition equation is affine in
    $\sigma$ with the same $\sum_i J(i, t)$ on both sides, so $\delta$ satisfies
    $\delta(t + 1) = \delta(t)^{\downarrow}$, that is
    $\delta(t)(j, u) = \delta(t + 1)(j, u - 1)$, and iterating,

    $$
    \delta(t)(j, u) = \delta(t + u - 1)(j, 1) \qquad \text{for every } u \geq 1 .
    $$

    Balance reads $\sigma(\tau)(j, 1) = \sum_x J(j, \tau)(x) = \sigma'(\tau)(j, 1)$,
    so the right side vanishes and $\delta = 0$.

    *Existence.*  The displayed $\sigma(t)$ is non-negative, and its total is $b(t - 1) = b < \infty$.  Splitting its sum at $\tau = t$,

    $$
    \begin{align*}
    \sigma(t + 1)(j, u)
    & = \sum_{i \in [h]} \sum_{\tau < t} J(i, \tau)(j, \; t + u - \tau)
        \;+\; \sum_{i \in [h]} J(i, t)(j, u) \\
    & = \sigma(t)(j, u + 1) + \sum_{i \in [h]} J(i, t)(j, u)
    \end{align*}
    $$

    which is the transition equation.  For balance, $\sigma(t)(i, 1)$ counts every
    object landing in hand $i$ at beat $t$, which is
    $\sum_{x \in \mathcal{S}} T(x)(i, t)$; by the balance of $T$ this equals
    $\sum_{x \in \mathcal{S}} T(i, t)(x) = \sum_{x \in \mathcal{F}} J(i, t)(x)$.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
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
    \sum_{t = 0}^{p - 1} \sum_{i \in [h]} J(i, t) \;=\; \Sigma - \Sigma^{\downarrow}.
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
    & \sum_{t = 0}^{p - 1} \sum_{i \in [h]} J(i, t) \\
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
    關於 juggling state ，還有幾個性質可以探討。以下先把有界化的設定寫清楚，接著給出幾個能當場證完的結果，最後再把我還沒能給出夠短證明的敘述連同來源一起列出來。

    到目前為止 $\mathcal{F} = [h] \times \mathbb{Z}_{>0}$ 沒有上界，狀態有無窮多個。以下固定兩個上限：滯空不超過 $k$，且一隻手在一拍最多接住 $c$ 個物件。記

    $$
    \mathcal{F}_k := [h] \times [k]
    $$

    則 **$b$ 物件 $h$ 手高度 $k$ 容量 $c$ 的狀態圖**，其頂點是滿足 $\sum \sigma = b$ 且每格不超過 $c$ 的 $\sigma \in M(\mathcal{F}_k)$，每個合法的投擲給出一條邊。

    $c = 1$ 就是不允許 multiplex 的情形，而 $c \geq b$ 則是完全不設限；以下的敘述會標明各自需要哪些條件。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    先數點。

    /// admonition | Proposition (Number of States)
        type: proposition

    The state graph has

    $$
    \sum_{\ell \geq 0} (-1)^{\ell} \binom{hk}{\ell} \binom{b - \ell(c + 1) + hk - 1}{hk - 1}
    $$

    states.  At $c = 1$ this is $\binom{hk}{b}$, and at $c \geq b$ only the first
    term survives and it is $\binom{b + hk - 1}{b}$.

    *The $c \geq b$ case is stated in [Polster, *The Mathematics of Juggling*](https://books.google.com.tw/books/about/The_Mathematics_of_Juggling.html?id=YCARBwAAQBAJ&redir_esc=y) §4.3; the bounded form is the standard inclusion–exclusion count.*

    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    A state is a choice of $\sigma(x) \in \{0, 1, \cdots, c\}$ for each of the
    $hk$ slots $x \in \mathcal{F}_k$ subject to $\sum_x \sigma(x) = b$, so the
    number of states is the coefficient of $z^{b}$ in

    $$
    \begin{align*}
    \left( 1 + z + \cdots + z^{c} \right)^{hk}
    & = \left( \frac{1 - z^{c + 1}}{1 - z} \right)^{hk} \\
    & = \left( \sum_{\ell \geq 0} (-1)^{\ell} \binom{hk}{\ell} z^{\ell(c + 1)} \right)
        \left( \sum_{n \geq 0} \binom{n + hk - 1}{hk - 1} z^{n} \right)
    \end{align*}
    $$

    Taking $n = b - \ell(c + 1)$ from the second factor gives the sum.  At $c = 1$
    the left side is $(1 + z)^{hk}$; at $c \geq b$ no term with $\ell \geq 1$ can
    reach $z^{b}$.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    再數邊。這一條需要 $c = 1$，而且 balance 條件在證明裡真的做了事。

    /// admonition | Proposition (Out-degree)
        type: proposition

    Suppose $c = 1$.  Let $m := \sum_{i \in [h]} \sigma(i, 1)$ be the
    number of objects $\sigma$ must throw and $f := hk - (b - m)$ the number of
    slots left empty by $\sigma^{\downarrow}$.  Then $\sigma$ has exactly

    $$
    f (f - 1) \cdots (f - m + 1)
    $$

    outgoing edges; in particular the out-degree depends on $\sigma$ only through
    how many objects each hand catches.  With one hand this is $k - b + 1$ when
    the hand catches and $1$ when it does not.

    *[Polster, *The Mathematics of Juggling*](https://books.google.com.tw/books/about/The_Mathematics_of_Juggling.html?id=YCARBwAAQBAJ&redir_esc=y) §2.8.3 treats the one-hand case; the falling factorial, for any $h$, is proved below.*

    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    Since $c = 1$ every hand holds at most one object, so the $m$ objects to be
    thrown lie in $m$ distinct hands $i_1, \cdots, i_m$.  For the same reason
    $\sigma^{\downarrow}$ has each entry at most $1$, so its $b - m$ objects
    occupy $b - m$ of the $hk$ slots of $\mathcal{F}_k$ and leave
    $f = hk - (b - m)$ of them empty.

    An outgoing edge is a choice of $J(i, t)$ for every $i \in [h]$.
    Balance makes $J(i_r, t)$ a single slot and $J(i, t)$ empty for every other
    hand, and the successor $\sigma^{\downarrow} + \sum_i J(i, t)$ is a state
    only if each of its entries is at most $1$, which forces those $m$ slots to
    be distinct and empty in $\sigma^{\downarrow}$.  An edge is therefore exactly
    an injection from $\{ i_1, \cdots, i_m \}$ into the $f$ empty slots, and
    there are $f (f - 1) \cdots (f - m + 1)$ of those.

    With one hand $m = \sigma(1, 1)$ is $1$ or $0$, giving $f = k - b + 1$ or the
    empty product $1$.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: remark

    $c \geq 2$ 時這條不成立 —— 出邊數不再只由「每隻手接幾顆」決定。
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    接著是狀態圖的一個對稱性。

    /// admonition | Theorem (Complement Duality)
        type: theorem

    Reversing each hand's slots and then replacing every count $x$ by $c - x$
    carries the $b$-object state graph to the $(hkc - b)$-object state graph of
    the same $h$, $k$ and $c$, reversing every edge.  The two are therefore
    anti-isomorphic, and since transposing leaves a trace unchanged, they hold
    the same number of patterns of each period.

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
    $\theta := \sum_{i \in [h]} J(i, t)$ for where its objects land, so
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
    & = \sum_{j \in [h]} \sum_{v = 1}^{k - 1} \theta(j, v)
        \;+\; hc - \sum_{j \in [h]} \sigma(j, 1) \\
    & = hc - \sum_{j \in [h]} \theta(j, k)
        && \text{(balance for } \sigma \text{)} \\
    & = \sum_{j \in [h]} \bigl( c - \sigma'(j, k) \bigr)
        \;=\; \sum_{j \in [h]} \varphi(\sigma')(j, 1)
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
    最後一個可證的，是說任何狀態都收得回 ground state 。

    /// admonition | Lemma (Return to Ground)
        type: lemma

    Give the slot $(j, u)$ the rank $r(j, u) := (u - 1) h + j$, so that $\mathcal{F}_k$ is
    ranked $1, \cdots, hk$ and the ground state $\gamma$ is the one filling the
    ranks $1, 2, 3, \cdots$ to capacity until the objects run out.  Then from any
    state, repeatedly throwing every caught object into the lowest-ranked slot
    that still has room reaches $\gamma$.

    *Worked out here; it is one half of the theorem below.*

    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: proof

    Write $C_{\sigma}(\rho) := \sum_{r(x) \leq \rho} \sigma(x)$ for how many
    objects sit at rank $\rho$ or below, reading $C_{\sigma}(\rho) = b$ for
    $\rho \geq hk$.  Two bounds hold for every state: $C_{\sigma}(\rho) \leq b$,
    and $C_{\sigma}(\rho) \leq \rho c$ because $\rho$ slots hold at most $\rho c$
    objects.  Let $\sigma'$ be the state one greedy beat later.

    Shifting sends the slot of rank $\rho$ to rank $\rho - h$ and empties the
    ranks $1, \cdots, h$, whose $m := C_{\sigma}(h)$ objects are the ones in
    hand, so $C_{\sigma^{\downarrow}}(\rho) = C_{\sigma}(\rho + h) - m$.  Greedy
    fills the lowest free capacity, which places all $m$ objects at rank $\rho$
    or below unless the ranks up to $\rho$ are already full.  Hence

    $$
    C_{\sigma'}(\rho) = \min \bigl( \rho c, \; C_{\sigma}(\rho + h) \bigr)
    \;\geq\; C_{\sigma}(\rho)
    \qquad \text{for every } \rho
    $$

    the inequality because $C_{\sigma}$ obeys both bounds on the right.  Now

    $$
    \sum_{x \in \mathcal{F}_k} r(x) \, \sigma(x)
    \;=\; \sum_{\rho = 0}^{hk - 1} \bigl( b - C_{\sigma}(\rho) \bigr)
    $$

    since an object of rank $\rho_0$ is counted by exactly the $\rho_0$ terms
    with $\rho < \rho_0$.  So this rank sum never increases along the greedy
    walk, and being a non-negative integer it is eventually constant; once it is,
    the displayed inequality is an equality at every $\rho$, so $\sigma' = \sigma$.

    It remains to see that a greedy walk can only rest at $\gamma$.  Let
    $\rho^{*}$ be the highest occupied rank of $\sigma$ and read
    $C_{\sigma'} = C_{\sigma}$ at $\rho = \rho^{*} - 1$.  Either
    $C_{\sigma}(\rho^{*} - 1) = (\rho^{*} - 1) c$, so every rank below
    $\rho^{*}$ is full and the remaining objects all sit at $\rho^{*}$, which is
    $\gamma$; or $C_{\sigma}(\rho^{*} - 1) = C_{\sigma}(\rho^{*} - 1 + h)$, so
    $\sigma$ has nothing at the ranks $\rho^{*}, \cdots, \rho^{*} - 1 + h$,
    against the choice of $\rho^{*}$.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: remark

    實際跑起來收斂得比證明保證的快得多：試過的每組 $b, h, k, c$ 裡，任何狀態都在 $k$ 拍之內回到 ground state 。上面的論證只說明了「終究會到」，沒有給出這個界。

    另外貪婪必須允許跨手。只丟回自己那隻手的話球換不了手，狀態會卡在原地回不去。
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    剩下的幾個我還沒能給出夠短的證明，把敘述跟來源記在這裡。

    /// admonition | Theorem (Strong Connectivity)
        type: theorem

    The state graph is strongly connected: from any state some sequence of throws
    reaches any other.  In particular any two patterns with the same number of
    objects are joined by a transition.

    *No source located; checked numerically here for one, two and three hands, with and without multiplex.*

    ///

    /// admonition
        type: remark

    上面的 lemma 已經給了一半：任何狀態都能走到 ground state 。缺的是另一半 —— 從 ground state 出發能走到任何狀態。$b \leq hc$ 時這是一行，因為 ground state 就是「所有物件都在手上」，一拍就能丟成任何狀態；$b > hc$ 時就得自己造一條鏈了。
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    以下兩個關於 prime loop 的結果需要 $b, h, k \geq 2$。

    /// admonition | Theorem
        type: theorem

    For $b, h, k \geq 2$, no prime loop visits every state.

    *[Polster, *The Mathematics of Juggling*](https://books.google.com.tw/books/about/The_Mathematics_of_Juggling.html?id=YCARBwAAQBAJ&redir_esc=y) §4.3, where a sketch of the proof is given.*

    ///

    /// admonition | Theorem (Maximal Prime Loops)
        type: theorem

    Let $\mathrm{MMP}(b, h, k)$ be the length of a longest prime loop when the
    capacity is unbounded.  For $b, h, k \geq 2$,

    $$
    \binom{b + h - 1}{b} k \;\leq\; \mathrm{MMP}(b, h, k) \;\leq\; \binom{b + hk - 1}{b} - 1 .
    $$

    The upper bound is the theorem above; the lower bound comes from a loop built
    out of the states whose objects all sit in one column.

    *[Polster, *The Mathematics of Juggling*](https://books.google.com.tw/books/about/The_Mathematics_of_Juggling.html?id=YCARBwAAQBAJ&redir_esc=y) §4.3.*

    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    最後一個需要更強的條件，而且有反例說明條件不能拿掉。

    /// admonition | Theorem (Buhler-Eisenbud-Graham-Wright)
        type: theorem

    Suppose $h = 1$ and $c = 1$.  Then the number of $p$-periodic juggling
    sequences with $b$ objects is $(b + 1)^{p} - b^{p}$.

    *[Buhler, Eisenbud, Graham & Wright, *Juggling Drops and Descents*, Amer. Math. Monthly **101** (1994) 507–519](https://doi.org/10.1080/00029890.1994.11996984).*

    ///

    /// admonition
        type: remark

    這條只對單手成立。兩手時同樣的計數會給出完全不同的數字 —— 例如 $2$ 物件 $2$ 手高度 $5$，週期 $1, 2, 3$ 分別是 $4, 40, 310$，而公式給 $1, 5, 19$ —— 因為原本的證明吃的是「每一拍恰好丟一顆」。
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: remark

    $k = 1$ 是個退化的情形：此時 $\sigma^{\downarrow} = 0$，下一個狀態完全由這一拍的投擲決定，而每個物件都必須被重新拋出，所以任何狀態都能到任何狀態 —— 圖是完全的，含自環。
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
