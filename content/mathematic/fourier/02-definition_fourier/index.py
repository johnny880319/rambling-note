import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The Complete Definition of the Fourier Transform

    ---

    ## Completing the Definition

    前一篇文章我們介紹了dirac delta function的本質，並嘗試擴充了一下傅立葉變換的定義，將他理解成把分佈轉換成另一個分佈的變換。雖然我們當時的定義還是不完整的，但其實也已經幾乎要完成了。接下來我們會先用一些篇幅來把傅立葉變換的定義補完。

    在上一篇文章中，眼尖的讀者可能會發現，我們當時推廣的傅立葉變換是一個把作用在$L^2(\mathbb{R}; \mathbb{C}) \cap L^1(\mathbb{R}; \mathbb{C})$ 上的分佈，轉換成另一個作用在同樣函數空間上的分佈。令
    $\mathcal{X}=L^2(\mathbb{R};\mathbb{C})\cap L^1(\mathbb{R};\mathbb{C})$，則可將上篇文章的傅立葉定義稍微再推廣：
    """)
    return


@app.cell
def _(mo):
    mo.image(
        str(mo.notebook_location() / "fourier_on_X.svg"),
        caption="稍微推廣的傅立葉定義",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    但我們會發現上篇文章最後的$\mathcal{F}(T_{1})$只能作用於傅立葉變換前後皆為Lebesgue可積的函數:

    $$\mathcal{F}(T_{1}): L^1(\mathbb{R}, \mathbb{C}) \cap \mathcal{F}^{-1}(L^1(\mathbb{R}, \mathbb{C})) \to \mathbb{C}$$

    where $\mathcal{F}^{-1}(L^1(\mathbb{R}, \mathbb{C})) := \{ g: \mathcal{F}(g) \in L^{1}(\mathbb{R}, \mathbb{C}) \}$.

    但我們會發現，若嚴格要求變換前後皆為 Lebesgue 可積，這會排除掉很多我們想處理的函數。比如$g(x) = 1_{[-1, 1]}(x) \in L^1(\mathbb{R}, \mathbb{C})$，但他的傅立葉變換為

    $$\mathcal{F}(g)(\xi) = \int_{-1}^{1} e^{-i 2 \pi x \xi} dx = \frac{\sin(2 \pi \xi)}{\pi \xi}$$

    而這個函數就不是Lebesgue可積的函數，換言之$\mathcal{F}(T_{1})$無法作用在$1_{[-1, 1]}(x)$上。

    此時我們或許會有個疑問: 我們真的有必要作用在$1_{[-1, 1]}(x)$這種函數上嗎?我們只能處理作用在$L^1(\mathbb{R}, \mathbb{C}) \cap L^2(\mathbb{R}, \mathbb{C})$上面的分佈嗎?還是其實我們可以讓我們要處理的函數空間縮小一些，這樣就可以涵蓋更多分佈?

    事實上，我們可以讓我們要處理的函數空間縮小一些，也就是前述的diagram裡的 $\mathcal{X}$ 找一個更合適的函數空間，這個函數空間不能太大，至少我們可能希望排除$1_{[-1, 1]}(x)$這種我們難以處理的函數。但也不能太小，不然可能會導致擴展後的傅立葉變換的定義不well-defined。至少我們希望$f \mapsto T_{f} \in ?$要是injective的，這樣$T_{f}$才能充分做為$f$的代表。

    不過要繼續深就細節的話真的會一發不可收拾，所以就直接說結論。我們可以把 $\mathcal{X}$ 這個函數空間選成Schwartz space $\mathcal{S}(\mathbb{R}; \mathbb{C}) := \{ g \in C^{\infty}(\mathbb{R}; \mathbb{C}) | \sup_{x \in \mathbb{R}} |x^{m} g^{(n)}(x)| < \infty, \forall m, n \in \mathbb{N}_{0} \}$ (他的中文名稱超級中二，叫做速降函數空間)，也就是所有無限可微且及其導數都比任何多項式衰減還快的函數所組成的空間。

    而能夠作用在 Schwartz space 上的連續線性泛函（Continuous Linear Functionals）所構成的空間，我們稱之為 Tempered Distributions。或者在分析領域裡，我們可以稱其是Schwartz space的拓樸對偶空間（Topological Dual Space），記作 $\mathcal{S}'(\mathbb{R}; \mathbb{C})$。而數學家證明了，當我們把 $\mathcal{X}$ 選成Schwartz space時，不僅不需要處理像$1_{[-1, 1]}(x)$這種難以處理的函數，還能讓傅立葉變換的定義維持well-defined。

    Schwartz space裡的函數都十分好處理，不但可積，而且因其光滑且衰減快速的特性，做一些分佈積分之類的操作時也都很方便，也可輕鬆的將其套上傅立葉變換或逆變換。當我們處理tempered distribution的傅立葉變換時，依定義我們總是要把他轉換成對Schwartz space裡的函數做逆變換並做處理，此時Schwartz space的良好性質各方面來說都幫了大忙。

    有趣的是，Schwartz space裡面的函數的傅立葉變換還是Schwartz space裡面的函數，tempered distribution裡的分佈的傅立葉變換也還是tempered distribution裡的分佈。這樣的自對偶性讓傅立葉變換的理論變得非常漂亮。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.image(
        str(mo.notebook_location() / "fourier_on_tempered_distributions.svg"),
        caption="Tempered distributions 上傅立葉變換的定義。",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    以上就是傅立葉變換的完整定義了。

    ## Afterword

    ### On Bounded Linear Functionals

    首先有個的小細節是(如果你是數學系的可能才會在意)，其實$\mathcal{S}'(\mathbb{R}; \mathbb{C})$不能寫成$\mathcal{B}(\mathcal{S}(\mathbb{R}; \mathbb{C}); \mathbb{C})$，因為 Schwartz space 不是 Banach space，我們通常不用 Norm bounded 來描述，而是用 Semi-norm 來描述其連續性。

    ### On Injectivity

    像前面說的，我們必須確保Schwartz space不會小到讓distribution無法做為函數的代表。也就是我們需要:

    $$ T_{f} = T_{g} \implies f = g, \quad \forall f, g \in L^1(\mathbb{R}; \mathbb{C})$$

    因為$f \mapsto T_{f}$是線性的，所以其實只要證明$T_{f} = 0 \implies f = 0$就可以了。事實上:

    $$
    \begin{aligned}
    T_{f} = 0 &\implies T_{f}(g) = 0, \quad \forall g \in \mathcal{S}(\mathbb{R}; \mathbb{C}) \\
    &\implies \int_{-\infty}^{\infty} f(x) g(x) dx = 0, \quad \forall g \in \mathcal{S}(\mathbb{R}; \mathbb{C}) \\
    &\implies f(x) = 0, \text{ almost everywhere}
    \end{aligned}
    $$

    最後一步可以用分析常用的dense argument來證明，這裡不多做贅述。

    ### An Example of a Schwartz Function

    一個簡單的Schwartz function的例子是$g(x) = e^{-x^{2}}$，我們可以看到他的所有導數都是多項式乘上$e^{-x^{2}}$，而這個函數衰減的速度比任何多項式都快，所以他是Schwartz function。

    ### Closure of Schwartz Space Under the Fourier Transform

    待補充。
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
