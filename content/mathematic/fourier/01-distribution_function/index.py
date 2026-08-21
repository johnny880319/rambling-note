import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # What Is the Dirac Delta Function


    ---

    ## Where the Fourier Integral Falls Short

    有碰過傅立葉的朋友們可能會知道，傅立葉變換根據作用的值域可以分為四種。
    分別是離散週期、離散非週期、連續週期、連續非週期的傅立葉變換。

    我會在之後的文章中說明，連續非週期的傅立葉變換是最根本的傅立葉變換，
    其他三種傅立葉變換都是他的特例。
    所以除非我們有特別標註，否則以下講的傅立葉變換都是指連續非週期的傅立葉變換。

    而為何我這個章節會說傅立葉變換有不足之處呢，原因其實在於其總是需要計算從負無限到正無限的積分。這就導致其實很多常見的函數的傅立葉變換都沒辦法用積分去計算。

    再繼續討論之前，讓我們複習一下傅立葉變換的定義:

    對於一個Lebesgue可積函數 $f(x): \mathbb{R} \to \mathbb{C}$ (或著說 $f \in L^1(\mathbb{R}; \mathbb{C})$ )，其傅立葉變換為

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
    這時你的工數或訊號處理課程的老師可能會跟你說，他的傅立葉變換就是dirac $\delta$ 函數，
    ，他是一個在 $\xi = 0$ 時無限大，其他地方都是零的函數。
    然後通常稍微介紹一下這個函數怎麼操作跟計算後，就不會繼續探究下去了。
    你可能會覺得數學家很隨便，怎麼加了一個看起來甚至不知道能不能稱為函數的東西進來就算了事。
    但事實上，這個dirac $\delta$ 函數背後有著非常嚴謹的數學理論基礎。


    > Remark:
    > 我這裡使用 $\mathcal{F}(f)$ 而不用 $\widehat{f}$ 是因為我發現不管是 `MathJax` 還是 `KateX` 都沒辦法渲染\\widecheck，好生氣。
    > 考慮到之後還要用到逆變換，我就先用這個符號吧。

    ## Extending the Definition of the Fourier Transform

    除了常數函數外，其實你會發現有一堆函數都是無法用積分去算傅立葉變換的。比如 $x, \sin x, \log x$ 等等。
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

    不過只是把當作他吃函數，吐函數的函數還是不太夠。
    就像前面看到的，他吃了常數函數或其他基本函數時，就沒辦法吐出一個有意義的函數出來了。
    所以我們也要把他吃的東西跟吐的東西也上升一個抽象的層次，
    但在做這件事之前，我們可以先觀查一個超讚的傅立葉變換的性質:


    對於任意的 $f, g \in L^2(\mathbb{R}; \mathbb{C}) \cap L^1(\mathbb{R}; \mathbb{C})$
    我們有:

    $$
    \int_{-\infty}^{\infty} \mathcal{F}(f)(\xi) \overline{g(\xi)} d\xi = \int_{-\infty}^{\infty} f(x) \overline{\mathcal{F}^{-1}(g)(x)} dx
    $$

    其中 $L^2$ 的假設保證了此積分收斂，且 $L^1$ 保證了傅立葉變換及逆變換存在。上述式子中 $\mathcal{F}^{-1}$ 是傅立葉的逆變換。其定義為:

    $$
    \mathcal{F}^{-1}(g)(x) := \int_{-\infty}^{\infty} g(\xi) e^{i 2\pi x \xi} d\xi
    $$

    如果我們用內積的表示法重寫上述性質的話，我們會得到一個漂亮的內積關係:

    $$
    \left\langle \mathcal{F}(f), g \right\rangle_{L^2(\mathbb{R};\mathbb{C})}
    =
    \left\langle f, \mathcal{F}^{-1}(g) \right\rangle_{L^2(\mathbb{R};\mathbb{C})}.
    $$

    這個內積關係給了我們一個很好的抽象化的方向，
    就像前面我們把傅立葉變換當作一個mapping一樣，我們也可以把函數當成一個mapping。
    只是通常我們都只會把函數看作一個從$\mathbb{R}$映射到$\mathbb{C}$的mapping。

    但如果從內積的視角看，我們就可以把函數 $f$ 當作一個從 $L^2(\mathbb{R}; \mathbb{C})$ 映射到 $\mathbb{C}$ 的mapping。
    或著更嚴謹的寫法，每個 $f \in L^2(\mathbb{R}; \mathbb{C})$
    都induce了一個bounded linear functional $T_f \in \mathcal{B}(L^2(\mathbb{R}; \mathbb{C}); \mathbb{C})$:

    $$
    \begin{aligned}
    T_{f}: L^2(\mathbb{R}; \mathbb{C}) \cap L^1(\mathbb{R}; \mathbb{C}) &\to \mathbb{C} \\
    g &\mapsto \left\langle f, \overline{g}\right\rangle_{L^2(\mathbb{R}; \mathbb{C})} \\
    \\
    T_{\mathcal{F}(f)}: L^2(\mathbb{R}; \mathbb{C}) \cap L^1(\mathbb{R}; \mathbb{C}) &\to \mathbb{C} \\
    g &\mapsto \left\langle\mathcal{F}(f), \overline{g}\right\rangle_{L^2(\mathbb{R}; \mathbb{C})}
    = \left\langle f, \mathcal{F}^{-1}(\overline{g})\right\rangle_{L^2(\mathbb{R}; \mathbb{C})}
    \end{aligned}
    $$

    這裡要特別注意的是，因為induced的mapping是linear的，但bra-ket右邊的參數是anti-linear的，
    所以我們寫成內積時要加個conjugate。

    因為 $L^2(\mathbb{R}; \mathbb{C})$ 是內積空間，所以 $f \mapsto T_f$ 是injective的。
    換句話說我們就能完全用這個mapping來代表函數 $f$ 本身。

    令 $\mathcal{X}=L^2(\mathbb{R};\mathbb{C})\cap L^1(\mathbb{R};\mathbb{C})$。則透過這種表示法，我們就能把傅立葉變換重新定義成一個從 $\mathcal{B}(\mathcal{X};\mathbb{C})$ 映射到 $\mathcal{B}(\mathcal{X};\mathbb{C})$ 的 mapping：
    """)
    return


@app.cell
def _(mo):
    mo.image(
        str(mo.notebook_location() / "fourier_on_X.svg"),
        caption="稍微廣義的傅立葉變換",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    用這種定義， $f$ 就不再被局限於可積函數了，只要 $f$ 能讓變換前後對應的內積都收斂就可以了。
    當然如果 $f \in L^2(\mathbb{R}; \mathbb{C}) \cap L^1(\mathbb{R}; \mathbb{C})$ ， 則 $\mathcal{F}(T_{f}) = T_{\mathcal{F}(f)}$。也就是說新的傅立葉變換定義跟舊的定義是兼容的。


    如果你是工程師，然後你覺得這個定義很抽象，那或許這樣的寫法可能會幫助你理解:


    ```python
    def fourier_transform(
        f: Callable[[Callable[[float], complex]], complex],
    ) -> Callable[[Callable[[float], complex]], complex]:
        ...
    ```

    順帶一提，這種把函數打到複數的mapping在泛函分析中被稱為 **"分佈"(distribution)**。大部分人對distribution的印象應該都是機率分佈(probability distribution)。而事實上機率分布確實是一個把函數打到複數的mapping，比如常態分佈可以把$f(x) = x$這個函數打到他的期望值。或是把$f(x) = x^2$這個函數打到他的variance:

    $$\mathbb{E}_{X \sim \mathcal{N}(0, 1)}[X] = \int_{-\infty}^{\infty} x \cdot \frac{1}{\sqrt{2 \pi}} e^{-\frac{x^2}{2}} dx = 0$$

    $$\mathbb{E}_{X \sim \mathcal{N}(0, 1)}[X^2] = \int_{-\infty}^{\infty} x^2 \cdot \frac{1}{\sqrt{2 \pi}} e^{-\frac{x^2}{2}} dx = 1$$

    如果用強調mapping的寫法:

    $$
    \begin{aligned}
    T_{\mathcal{N}(0,1)}:L^{\infty}(\mathbb{R};\mathbb{C})&\longrightarrow\mathbb{C}, \\
    f&\longmapsto \int_{-\infty}^{\infty} f(x)\,\frac{1}{\sqrt{2\pi}}e^{-x^2/2}\,dx.
    \end{aligned}
    $$

    從這個角度我們可以說，原本的傅立葉變換的定義是把函數轉換成另一個函數，
    而這個新的定義則是把**分佈轉換成另一個分佈**。

    ---

    ## Back to the Fourier Transform of a Constant


    雖然這離真正完成廣義版的傅立葉變換還差了一些，
    不過我們或許可以先來感受一下常數函數的傅立葉變換是甚麼樣的東西。
    假如今天有個函數 $g$ 滿足 $g, \mathcal{F}(g) \in L^1(\mathbb{R}, \mathbb{C})$，則我們有:

    $$
    \begin{aligned}
    \mathcal{F}(T_{1})(g) &= \left\langle 1, \mathcal{F}^{-1}(\overline{g})\right\rangle_{L^2(\mathbb{R}; \mathbb{C})} \\
    &= \int_{-\infty}^{\infty} 1 \cdot \overline{\mathcal{F}^{-1}(\overline{g})(x)} dx \\
    &= \int_{-\infty}^{\infty} \overline{\left( \int_{-\infty}^{\infty} \overline{g(\xi)} e^{i 2\pi x \xi} d\xi \right)} dx \\
    &= \int_{-\infty}^{\infty} \left( \int_{-\infty}^{\infty} g(\xi) e^{-i 2\pi x \xi} d\xi \right) dx \\
    &= \int_{-\infty}^{\infty} \mathcal{F}(g)(x) dx \\
    &= \int_{-\infty}^{\infty} \mathcal{F}(g)(x) e^{i 2\pi x 0} dx \\
    &= \mathcal{F}^{-1}(\mathcal{F}(g))(0) \\
    &= g(0)
    \end{aligned}
    $$

    也就是說，常數函數induce出來的mapping的傅立葉變換其實就是 $g \mapsto g(0)$ 這樣子的mapping。這正是dirac $\delta$ 函數 (或著更精確來說，我們應該叫他dirac $\delta$ 分佈) 的本質。這也是為甚麼大家會說 $\delta$ 是一個原點無窮大，其他地方是0的函數，因為他作用於其他函數時，確實完全不在意其他點，只在意被作用的函數的原點的值。


    到目前為止，雖然我們似乎已經成功擴展了傅立葉變換的定義，也確實回答了dirac $\delta$ 函數的本質是甚麼。
    但事實上上面的計算中，我們假設了 $g, \mathcal{F}(g) \in L^1(\mathbb{R}, \mathbb{C})$，
    而不是貫穿全文脈絡的 $g \in L^2(\mathbb{R}, \mathbb{C}) \cap L^1(\mathbb{R}, \mathbb{C})$。

    這代表其實我們離真正完成廣義版的傅立葉變換定義還有一些細節需要處理。
    不過我認為如果只是要認識dirac $\delta$ 函數的本質、為何我們想要擴充傅立葉變換的定義、如何想像廣義的傅立葉變換，這篇文章的思路已十分充足，繼續介紹下去cp值好像就會變低了。

    或許我之後會寫一篇文章來完成廣義的傅立葉變換定義(也就是引入tempered distribution跟Schwartz space)，
    但也可能就直接跳過這些細節，來講解如何統一四種傅立葉變換的定義(引入Poisson summation formula之類的)。
    也可能就放著這系列不管了。
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
