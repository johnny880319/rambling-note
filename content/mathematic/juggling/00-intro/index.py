import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Introduction

    除了數學研究所畢業生及軟體工程師這兩個身分之外，我還有另一個身分是雜耍愛好者，其中又特別喜歡扯鈴跟拋接球。我覺得拋接球有個很大的魅力是，它有許多技巧是可以用數學的語言描述的，事實上我有時會用這套理論去發明新的雜耍招。

    雖然如果只是要將理論應用到實際的雜耍招裡，其實只要熟悉名為 **siteswap** 的記號就好，但它也可以衍生出很多有趣的數學問題，所以決定來為這個主題寫一系列筆記。另外扯鈴因為也有拋接的元素在，所以經過適當的調整後，也可以融入 siteswap 的框架之中。

    關於雜耍數學的研究，最經典的著作是 [The Mathematics of Juggling](https://books.google.com.tw/books/about/The_Mathematics_of_Juggling.html?id=YCARBwAAQBAJ&redir_esc=y)，裡面講解了許多 siteswap 會用到的記號跟理論，此外這本書的作者也有寫一篇簡短的[文章](https://www.qedcat.com/articles/juggling_survey.pdf)，算是濃縮了這本書的精華。

    不過這系列的筆記，考慮到嚴謹性與數學操作上的方便性，我會使用我發明的記號，但它基本上等價於書裡所講的 Multi-hand notation 。此外這系列筆記，我將使用 finite multiset 去描述 multiplex 的操作，但這個 notation 無法區分 multiplex 的不同球，所以基本上沒辦法用我現在用的記號去研究 color code 的理論。但考量到 color code 我目前並沒有知道太多理論，再加上考慮這件事情會讓記號跟規則變得過於複雜，所以這邊暫時會先放棄這一塊的討論。等我文章的框架成熟之後，再考慮要不要研究這方面的東西跟改變 notation 。

    除了 The Mathematics of Juggling 外，還有一些不錯的相關資源

    - [Juggle Wiki](https://juggle.fandom.com/wiki/Juggle_Wiki) 裡面收錄了很多有趣的雜耍知識。
    - [Modern Club Passing](https://modernpassing.com/) 有系統性的多人拋接理論章節。
    - [Passing Zone](https://passing.zone/) 收錄了大量 pattern 的影片與記號。
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
