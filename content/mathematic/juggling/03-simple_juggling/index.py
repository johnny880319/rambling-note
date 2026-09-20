import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Simple Juggling

    前面文章在一個很 general 的框架下介紹雜耍中的數學。但其實有些有趣的理論，比如 reverse average theorem ，並沒有辦法推廣到多手跟 multiplex 的情況，所以這個章節將會專注於 $h, c = 1$ 的情境來做討論。
    """)
    return


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
