import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Generalizing the Fourier Transform

    ---

    ## Where the Fourier Integral Falls Short

    有碰過傅立葉的朋友們可能會知道，傅立葉變換根據定義域可以分為四種。
    分別是離散週期、離散非週期、連續週期、連續非週期的傅立葉變換。

    我會在之後的文章中說明，連續非週期的傅立葉變換是最根本的傅立葉變換，
    其他三種傅立葉變換都是他的特例。
    所以除非我們有特別標註，否則以下講的傅立葉變換都是指連續非週期的傅立葉變換。

    而為何我這個章節會說傅立葉變換有不足之處呢，原因其實在於其總是需要計算從負無限到正無限的積分。這就導致其實很多常見的函數的傅立葉變換都沒辦法用積分去計算。

    在繼續討論之前，讓我們複習一下傅立葉變換的定義:

    對於一個Lebesgue可積函數 $f(x) \colon \mathbb{R} \to \mathbb{C}$ (或者說 $f \in L^1(\mathbb{R}; \mathbb{C})$ )，其傅立葉變換為

    $$
    \mathcal{F}(f)(\xi) := \int_{-\infty}^{\infty} f(x) e^{-i 2\pi x \xi} dx
    $$

    可以注意到，只有Lebesgue可積的函數才可以用上面的定義去計算傅立葉變換。
    但許多我們在數學或物理中會遇到的函數都不是Lebesgue可積的，比如常數函數 $f(x) = 1$。
    讓我們試著計算他的傅立葉變換:

    $$
    \mathcal{F}(1)(\xi) = \int_{-\infty}^{\infty} 1 \cdot e^{-i 2\pi x \xi} dx = \int_{-\infty}^{\infty} e^{-i 2\pi x \xi} dx
    $$

    這個積分不管是在黎曼還是勒貝格的意義下都是不可積的。
    這時你的工數或訊號處理課程的老師可能會跟你說，他的傅立葉變換就是 Dirac $\delta$ 函數，他是一個在 $\xi = 0$ 時無限大，其他地方都是零的函數。
    然後通常稍微介紹一下這個函數怎麼操作跟計算後，就不會繼續探究下去了。
    你可能會覺得數學家很隨便，怎麼加了一個看起來甚至不知道能不能稱為函數的東西進來就算了事。
    但事實上，這個 Dirac $\delta$ 函數背後有著非常嚴謹的數學理論基礎。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## From Functions to Functionals

    除了常數函數外，其實你會發現有一堆函數都是無法用積分去算傅立葉變換的。比如 $x, \sin x, \log \lvert x \rvert$ 等等。
    明明這些都是常見的函數，卻都沒辦法算，這或許在暗示我們需要一個更廣義的傅立葉變換定義。

    事實上，積分確實是有其侷限性的，所以如果想要擴充傅立葉變換的定義，我們就需要上升到更抽象的層次去思考這個問題。

    先從這個角度去想:傅立葉變換前是一個函數，傅立葉變換後還是一個函數，
    所以傅立葉變換本質上是一個(函數空間打到函數空間的)mapping。

    如果你是一個工程師，下面這個寫法可能能幫助你理解:


    ```python

    def fourier_transform(
        f: Callable[[float], complex]
    ) -> Callable[[float], complex]:
        ...

    ```

    不過只是把他當作吃函數，吐函數的函數還是不太夠。
    就像前面看到的，他吃了常數函數或其他基本函數時，就沒辦法吐出一個有意義的函數出來了。
    所以我們也要把他吃的東西跟吐的東西也上升一個抽象的層次，
    但在做這件事之前，我們可以先觀察一個超讚的傅立葉變換的性質:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Proposition (Multiplication Formula)
        type: proposition

    For $f, g \in L^1(\mathbb{R}; \mathbb{C})$,

    $$
    \int_{-\infty}^{\infty} \mathcal{F}(f)(\xi)\, g(\xi)\, d\xi
    = \int_{-\infty}^{\infty} f(x)\, \mathcal{F}(g)(x)\, dx
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// details
        type: proof

    For $f, g \in L^1(\mathbb{R}; \mathbb{C})$, note that

    $$
    \int_{-\infty}^{\infty} \int_{-\infty}^{\infty} \left\lvert  f(x) \, g(\xi) \, e^{-i 2\pi x \xi} \right\rvert \, dx \, d\xi = \lVert f \rVert_{1} \, \lVert g \rVert_{1} < \infty
    $$

    hence Fubini gives

    $$
    \begin{align*}
    \int_{-\infty}^{\infty} \mathcal{F}(f)(\xi)\, g(\xi)\, d\xi
    &= \int_{-\infty}^{\infty} \int_{-\infty}^{\infty} f(x) \, e^{-i 2\pi x \xi} \, dx \, g(\xi) \, d\xi \\
    &= \int_{-\infty}^{\infty} f(x) \int_{-\infty}^{\infty} g(\xi) \, e^{-i 2\pi x \xi} \, d\xi \, dx \\
    &= \int_{-\infty}^{\infty} f(x)\, \mathcal{F}(g)(x)\, dx
    \end{align*}
    $$

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    接著為了讓積分合法，考慮較小的定義域 $\mathcal{X} \subset L^1(\mathbb{R};\mathbb{C})$ ，則對於適當的 $f \in L^1(\mathbb{R};\mathbb{C})$，我們可以定義

    $$
    T_f \colon \mathcal{X} \longrightarrow \mathbb{C},\quad g \longmapsto \int_{-\infty}^{\infty} f(x)\, g(x)\, dx \,=:\, T_f(g),
    $$

    multiplication formula 告訴我們

    $$
    T_{\mathcal{F}(f)} \colon \mathcal{X} \longrightarrow \mathbb{C}, \quad
    g \longmapsto \int_{-\infty}^{\infty} f(x)\, \mathcal{F}(g)(x)\, dx \,=\, (T_f \circ \mathcal{F}) (g),
    $$

    此時如果將 $T_{\mathcal{F}(f)}$ 看成 $\mathcal{F}(T_f)$ ，我們就可以將傅立葉變換從作用在 function 上的變換推廣成作用在 functional 上的變換
    """)
    return


@app.cell
def _(mo):
    mo.center(
        mo.image(
            str(mo.notebook_location() / "general_fourier.svg"),
            caption="稍微廣義的傅立葉變換",
            width=600,
        )
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    此時傅立葉變換就變成了類似這種東西

    ```python

    def fourier_transform(
        T: Callable[[Callable[[float], complex]], complex]
    ) -> Callable[[Callable[[float], complex]], complex]:
        ...

    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Choosing the Test Functions

    不過上述 functional 的作用域 $\mathcal{X}$ 不能亂選，如果要讓上述的廣義傅立葉變換 well-defined ，則對於任意 $g \in \mathcal{X}$ ，其傅立葉變換需要合法

    $$
    \mathcal{X} \subset L^1(\mathbb{R}; \mathbb{C})
    $$

    且 $\mathcal{F}(g)$ 要落在 functional 的 domain 裡

    $$\mathcal{F}(\mathcal{X}) \subset \mathcal{X}$$

    我們還希望 $\mathcal{X}$ 對於乘上 $x$ 是封閉的，因為我們希望 $T_{x^m}$ 這類由多項式成長的函數 induce 出來的 functional 有定義。

    $$
    x \mathcal{X} \subset \mathcal{X}
    $$

    最後，因為傅立葉變換會將乘上 $x$ 轉換成微分，反之亦然，所以上述兩個條件也隱含了 $\mathcal{X}$ 裡面的函數需要光滑的條件。此性質的精確描述如下
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Proposition (Smoothness and Decay)
        type: proposition

    Let $f \in L^1(\mathbb{R}; \mathbb{C})$.

    (i) If $f$ is locally absolutely continuous and $f' \in L^1(\mathbb{R}; \mathbb{C})$, then

    $$
    \mathcal{F}(f')(\xi) = i 2\pi \xi \, \mathcal{F}(f)(\xi).
    $$

    (ii) If $x f \in L^1(\mathbb{R}; \mathbb{C})$, then $\mathcal{F}(f) \in C^1(\mathbb{R}; \mathbb{C})$ and

    $$
    \mathcal{F}(x f)(\xi) = \frac{i}{2\pi} \frac{d}{d\xi} \mathcal{F}(f)(\xi).
    $$
    ///

    /// details
        type: proof

    (i) By local absolute continuity, write

    $$
    f(x) = f(0) + \int_{0}^{x} f'(t) \, dt,
    $$

    note that

    $$
    \lim_{x \to \pm\infty} f(x) = 0,
    $$

    the limits exist since $f' \in L^1$ and vanish since $f \in L^1$. Hence

    $$
    \begin{align*}
    \mathcal{F}(f')(\xi)
    &= \lim_{R \to \infty} \int_{-R}^{R} f'(x) \, e^{-i 2\pi x \xi} \, dx
    && \text{(DCT by $f'$)} \\
    &= \lim_{R \to \infty} \left( \left[ f(x) \, e^{-i 2\pi x \xi} \right]_{-R}^{R} + i 2\pi \xi \int_{-R}^{R} f(x) \, e^{-i 2\pi x \xi} \, dx \right)
    && \text{(integration by parts)} \\
    &= i 2\pi \xi \, \mathcal{F}(f)(\xi)
    && \text{($f(\pm R) \to 0$ and DCT by $f$)}
    \end{align*}
    $$

    (ii) For $(\xi', h) \to (\xi, 0)$ with $h \neq 0$,

    $$
    \begin{align*}
    \frac{\mathcal{F}(f)(\xi' + h) - \mathcal{F}(f)(\xi')}{h}
    &= \int_{-\infty}^{\infty} f(x) \, e^{-i 2\pi x \xi'} \, \frac{e^{-i 2\pi x h} - 1}{h} \, dx \\
    &\longrightarrow \int_{-\infty}^{\infty} f(x) \, e^{-i 2\pi x \xi} \, (-i 2\pi x) \, dx
    && \text{(DCT by $2\pi \lvert x f \rvert$, as $\lvert e^{i\theta} - 1 \rvert \leq \lvert \theta \rvert$)} \\
    &= -i 2\pi \, \mathcal{F}(x f)(\xi).
    \end{align*}
    $$

    Fixing $\xi' = \xi$, $\mathcal{F}(f)$ is differentiable everywhere with
    $\frac{d}{d\xi} \mathcal{F}(f) = -i 2\pi \, \mathcal{F}(x f)$.
    Since the joint limit exists and so does the inner limit in $h$,

    $$
    \lim_{\xi' \to \xi} \frac{d}{d\xi} \mathcal{F}(f)(\xi')
    = \lim_{\xi' \to \xi} \lim_{h \to 0} \frac{\mathcal{F}(f)(\xi' + h) - \mathcal{F}(f)(\xi')}{h}
    = \frac{d}{d\xi} \mathcal{F}(f)(\xi),
    $$

    so $\mathcal{F}(f) \in C^1(\mathbb{R}; \mathbb{C})$.

    <span class="qed">$\square$</span>
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    此特性可以被詮釋成，傅立葉變換會將不夠光滑的函數轉換成衰減很慢的函數，反之亦然。直觀的想法是今天震盪得很快的波，他高頻的地方的成分就會很多。

    考慮到前述的幾個條件， **Schwartz space** 就成了 $\mathcal{X}$ 的一個自然而然的候選人，而傅立葉變換就可以推廣到作用於 Schwartz space 的 continuous linear functional ，也就是 **tempered distribution** 。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition | Definition (Schwartz Space and Tempered Distributions)
        type: definition

    For $g \in C^{\infty}(\mathbb{R}; \mathbb{C})$ and $m, n \in \mathbb{Z}_{\geq 0}$, let

    $$
    p_{m,n}(g) := \sup_{x \in \mathbb{R}} \lvert x^{m} g^{(n)}(x) \rvert.
    $$

    The Schwartz space is

    $$
    \mathcal{S}(\mathbb{R}; \mathbb{C}) := \left\{ g \in C^{\infty}(\mathbb{R}; \mathbb{C}) : p_{m,n}(g) < \infty \quad \forall m, n \in \mathbb{Z}_{\geq 0} \right\},
    $$

    with the topology induced by the semi-norms $\{ p_{m,n} \}_{m, n \geq 0}$. The space of tempered distributions is

    $$
    \mathcal{S}'(\mathbb{R}; \mathbb{C}) := \left\{ T \in \mathbb{C}^{\mathcal{S}(\mathbb{R}; \mathbb{C})} : T \text{ linear and continuous} \right\}.
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    就像前面提到的， Schwartz space 能夠滿足我們的需求。

    /// admonition | Proposition
        type: proposition

    The Schwartz space $\mathcal{S}(\mathbb{R}; \mathbb{C})$ satisfies

    - $\mathcal{S}(\mathbb{R}; \mathbb{C}) \subset L^1(\mathbb{R}; \mathbb{C})$,
    - $\mathcal{F}(g) \in \mathcal{S}(\mathbb{R}; \mathbb{C})$ for every $g \in \mathcal{S}(\mathbb{R}; \mathbb{C})$,
    - $x g \in \mathcal{S}(\mathbb{R}; \mathbb{C})$ for every $g \in \mathcal{S}(\mathbb{R}; \mathbb{C})$.

    *[Stein & Shakarchi, *Fourier Analysis: An Introduction*](https://press.princeton.edu/books/hardcover/9780691113845/fourier-analysis) Ch. 5, §1.3 and Theorem 1.3.*
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    為了讓推廣後的傅立葉變換把 tempered distribution 送回 tempered distribution，我們需要以下性質。

    /// admonition | Proposition (Fourier Transform on Tempered Distributions)
        type: proposition

    For $T \in \mathcal{S}'(\mathbb{R}; \mathbb{C})$,

    $$
    T \circ \mathcal{F} \in \mathcal{S}'(\mathbb{R}; \mathbb{C})
    $$

    *[Bishop, *Folland's Real Analysis: Chapter 9*, MAT 533 lecture notes, Stony Brook University](https://www.math.stonybrook.edu/~bishop/classes/math533.S21/Notes/chap9notes.pdf) §9.2.*
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    此時我們終於能精確定義廣義版本的傅立葉變換了

    /// admonition | Definition (Fourier Transform)
        type: definition

    The Fourier transform of $T \in \mathcal{S}'(\mathbb{R}; \mathbb{C})$ is

    $$
    \mathcal{F}(T) := T \circ \mathcal{F} \in \mathcal{S}'(\mathbb{R}; \mathbb{C})
    $$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    /// admonition
        type: remark

    機率論裡的 **分佈 (distribution)** 本質上也是連續線性泛函。比如常態分佈可以把$f(x) = x$這個函數打到他的期望值。或是把$f(x) = x^2$這個函數打到他的二階動差:

    $$\mathbb{E}_{X \sim \mathcal{N}(0, 1)}[X] = \int_{-\infty}^{\infty} x \cdot \frac{1}{\sqrt{2 \pi}} e^{-\frac{x^2}{2}} dx = 0$$

    $$\mathbb{E}_{X \sim \mathcal{N}(0, 1)}[X^2] = \int_{-\infty}^{\infty} x^2 \cdot \frac{1}{\sqrt{2 \pi}} e^{-\frac{x^2}{2}} dx = 1$$
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Examples

    上述討論都著重於抽象的說明，現在我們可以來看一些例子。

    /// admonition
        type: example

    For any polynomial $p$,

    $$
    p(x) \, e^{-x^{2}}, \; p(x) \, \Psi(x) \in \mathcal{S}(\mathbb{R}; \mathbb{C}),
    $$

    where $\Psi$ is the bump function

    $$
    \Psi(x) :=
    \begin{cases}
    \exp \left(\frac{-1}{1 - x^2} \right), & \lvert x \rvert < 1, \\
    0, & \lvert x \rvert \geq 1.
    \end{cases}
    $$

    *[Stein & Shakarchi, *Fourier Analysis: An Introduction*](https://press.princeton.edu/books/hardcover/9780691113845/fourier-analysis) Ch. 5, §1.3 and Exercise 4.*
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    而甚麼樣的函數可以用 tempered distribution 刻劃，則由以下定理給出

    /// admonition | Proposition (Tempered Functions)
        type: proposition

    Let $f \in L^1_{\mathrm{loc}}(\mathbb{R}; \mathbb{C})$ satisfy

    $$
    \int_{-\infty}^{\infty} \left( 1 + \lvert x \rvert \right)^{-N} \lvert f(x) \rvert \, dx < \infty
    $$

    for some $N \in \mathbb{Z}_{\geq 0}$. Then $T_f \in \mathcal{S}'(\mathbb{R}; \mathbb{C})$, where $T_f(g) := \int_{-\infty}^{\infty} f(x) \, g(x) \, dx$.

    *[Bishop, *Folland's Real Analysis: Chapter 9*, MAT 533 lecture notes, Stony Brook University](https://www.math.stonybrook.edu/~bishop/classes/math533.S21/Notes/chap9notes.pdf) §9.2.*
    ///

    常數、多項式、$\sin$、$\cos$、$\log \lvert x \rvert$ 以及所有 $L^1$ 函數都滿足這個條件。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    注意到因為對於任意 $f \in L^1(\mathbb{R}; \mathbb{C}),\, g \in \mathcal{S}(\mathbb{R}; \mathbb{C}) \subset L^1(\mathbb{R}; \mathbb{C})$ ，總是有

    $$
    \begin{align*}
    \mathcal{F}(T_f)(g) &= T_f(\mathcal{F}(g)) \\
    &= \int_{-\infty}^{\infty} f(x)\, \mathcal{F}(g)(x)\, dx \\
    &= \int_{-\infty}^{\infty} \mathcal{F}(f)(x)\, g(x)\, dx && \text{(multiplication formula)} \\
    &= T_{\mathcal{F}(f)}(g)
    \end{align*}
    $$

    也就是推廣後的傅立葉變換跟原本積分的定義是相容的。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    此外，對這類函數來說 $f \mapsto T_f$ 是 injective 的，因為 $C_c^{\infty}(\mathbb{R}; \mathbb{C}) \subset \mathcal{S}(\mathbb{R}; \mathbb{C})$，只要 $T_{f_1} = T_{f_2}$，下面的 proposition 就告訴我們 $f_1 = f_2$ almost everywhere。也就是說，我們可以完全用 tempered distribution 來代表這些函數本身。

    /// admonition | Proposition (Injectivity)
        type: proposition

    Let $f \in L^1_{\mathrm{loc}}(\mathbb{R}; \mathbb{C})$. If

    $$
    \int_{-\infty}^{\infty} f(x) \, g(x) \, dx = 0
    \qquad \forall g \in C_c^{\infty}(\mathbb{R}; \mathbb{C}),
    $$

    then $f = 0$ almost everywhere.

    *[Folland, *Real Analysis: Modern Techniques and Their Applications*](https://books.google.com.tw/books?id=wI4fAwAAQBAJ) §9.1, preceding Proposition 9.2.*
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What Is the Dirac Delta Function

    現在我們能回到常數函數的例子了，不過在計算常數函數的傅立葉變換之前，我們需要逆變換作為我們計算的工具

    /// admonition | Theorem (Fourier Inversion)
        type: theorem

    For $h \in \mathcal{S}(\mathbb{R}; \mathbb{C})$ and $T \in \mathcal{S}'(\mathbb{R}; \mathbb{C})$, let

    $$
    \mathcal{F}^{-1}(h)(x) := \int_{-\infty}^{\infty} h(\xi) \, e^{i 2\pi x \xi} \, d\xi,
    \qquad
    \mathcal{F}^{-1}(T) := T \circ \mathcal{F}^{-1}.
    $$

    Then $\mathcal{F}$ is a bijection of $\mathcal{S}(\mathbb{R}; \mathbb{C})$ onto itself and of $\mathcal{S}'(\mathbb{R}; \mathbb{C})$ onto itself, with inverse $\mathcal{F}^{-1}$ in both cases.

    *[Stein & Shakarchi, *Fourier Analysis: An Introduction*](https://press.princeton.edu/books/hardcover/9780691113845/fourier-analysis) Ch. 5, Theorem 1.9 and Corollary 1.10; [Bishop, *Folland's Real Analysis: Chapter 9*, MAT 533 lecture notes, Stony Brook University](https://www.math.stonybrook.edu/~bishop/classes/math533.S21/Notes/chap9notes.pdf) §9.2.*
    ///
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    有了這個工具後，我們可以發現，對於所有 $g \in \mathcal{S}(\mathbb{R}; \mathbb{C})$

    $$
    \begin{align*}
    \mathcal{F}(T_{1})(g)
    &= T_{1}\left( \mathcal{F}(g) \right) \\
    &= \int_{-\infty}^{\infty} \mathcal{F}(g)(x) \, dx \\
    &= \int_{-\infty}^{\infty} \mathcal{F}(g)(x) \, e^{i 2\pi x \cdot 0} \, dx \\
    &= \mathcal{F}^{-1}\left( \mathcal{F}(g) \right)(0) \\
    &= g(0)
    && \text{(Fourier inversion)}
    \end{align*}
    $$

    也就是說，常數函數 induce 出來的 mapping 的傅立葉變換其實就是 $g \mapsto g(0)$ 這樣子的 mapping。這正是 Dirac $\delta$ 函數（或者更精確來說，我們應該叫他 Dirac $\delta$ 分佈）的本質。這也是為甚麼大家會說 $\delta$ 是一個原點無窮大，其他地方是 0 的函數，因為他作用於其他函數時，確實完全不在意其他點，只在意被作用的函數的原點的值。至此我們終於解答了 Dirac $\delta$ 函數的本質，也推廣並嚴謹地描述了甚麼是傅立葉變換。
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
