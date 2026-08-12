import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 線性規劃


    還記得高中學線性規劃的時候，覺得線性規劃是一個不嚴謹，很依賴作圖的東西，而且做圖法基本上超過三個變數就無法使用了。而後來讀數學系時也沒有碰到線性規劃，所以就漸漸地淡忘掉他。

    結果畢業後的第一份工作的第一個專案，就是整數線性規劃的專案。當時還為了那個專案去看[孔令傑老師的課程](https://www.youtube.com/@lckung.lectures)，才知道做圖法以外的方法。雖然老師教的東西不難，但這類應用數學的方法我超極容易忘記，所以決定用自己的理解來寫幾篇筆記，方便自己之後回顧。
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
