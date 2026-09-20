import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Random Siteswap Generator

    這裡提供一個 siteswap 隨機生成器來讓玩家可以做為日常的遊戲或挑戰使用。在設定球數、最大高度與週期範圍之後，按 `New Pattern` 產生新的 pattern。另外因為0代表空拍，所以可以選擇是否要禁止0這個數字出現。

    生成的 pattern 出發並結束於基態，且過程不經過基態。也不會在狀態圖中走重複的 cycle ，但會允許經過重複的非基態的狀態。可以透過選擇 `Prime loops only` 來禁止經過重複的狀態。

    為了讓大部分玩家看懂， $10$ 以上的數字，在高度限制的地方允許輸入英文或十進位數字，產出的 siteswap 則會用英文字母顯示。此模擬的高度上限則設定在 $35$ ，對應到英文字母的 $z$ 。

    產出的 pattern 會是 simple juggling ，但動畫會用雙手交替的方式來呈現，以貼近人類世界的情境。另外模擬動畫會在前後各插入一段運球 qualify ，讓玩家能看清楚如何在運球跟 siteswap pattern 之間做切換。

    其他關於此模擬的功能還有:

    - 能調整速度、持球時間、重力、手的位置等設定。
    - 可以選擇是否顯示控制點、球的軌跡，以及是否模擬接球下沉。
    - 可以拖曳平移模擬畫面，也可以用滑鼠滾輪或手指縮放模擬畫面。
    """)
    return


@app.cell(hide_code=True)
def _(challenge_simulation, mo):
    mo.iframe(challenge_simulation.HTML, height="1120px")
    return


@app.cell
def _():
    import challenge_simulation
    import marimo as mo

    return challenge_simulation, mo


if __name__ == "__main__":
    app.run()
