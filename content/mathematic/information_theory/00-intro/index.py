import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Introduction

    機器學習的 loss function 相關的數學式中，常常出現像是 cross entropy, KL divergence 等數學式。但當時其實沒辦法想像他們的實際意義，所以就去找了 information theory 的課程來看。

    我看的課程是香港中文大學的 [Raymond W. Yeung 教授的線上課](https://www.coursera.org/learn/information-theory)， coursera 上可以找到課程影片及投影片。教授的上課內容應該是參考[教授本人寫的書](https://link.springer.com/book/10.1007/978-0-387-79234-7)，如果是在學的學生應該可以免費下載。

    因為 information theory 的內容龐大且數學證明的篇幅不少，所以這系列我應該會比較著重在這門學問的直覺及思路，就不會去做太多嚴謹證明，但定理敘述我還是會用嚴謹的語言描述。

    此外我最近剛看完 IBM 的 quantum computing 課程，未來如果我有把 quantum information theory 的部分也給看完的話，應該會再開新的系列紀錄量子計算相關的筆記。
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
