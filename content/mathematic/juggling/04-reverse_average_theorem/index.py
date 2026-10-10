import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Reverse Average Theorem

    這篇還在寫，敬請期待。
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Simulation

    以下是我讓 AI vibe 出來的模擬，照著上面的證明走：輸入一串平均為整數的數字，從 $0\,0\,\cdots\,0$ 出發，每一次 substitution 把目標裡下一個還沒對上的數字換進來、下一個位置吸收餘數；每一次 substitution 裡面，auxiliary array 顯示兩個空的 beat $e_0, e_1$ 、右側懸著待放的 $v_0, v_1$ 與空的落點 $\ell_0, \ell_1$ ，每一輪不是放進去就是換掉 beat $x = \ell_0 - v_0$ 上的數字。全部換完之後，下方的動畫會用雙手輪流的方式把結果丟出來。
    """)
    return


@app.cell(hide_code=True)
def _(mo, rearrange_simulation):
    mo.iframe(rearrange_simulation.HTML, height="1400px")
    return


@app.cell
def _():
    import marimo as mo
    import rearrange_simulation

    return mo, rearrange_simulation


if __name__ == "__main__":
    app.run()
