import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Introduction

    之前因為有做語音相關的專案，被指派要去理解信號處理的一些知識跟大家分享。
    於是去看了李琳山老師的
    [信號與系統](https://www.youtube.com/playlist?list=PLxMgz3qtpNvVL6lo9ESoeG5f-airyWtqt)
    線上課程。

    雖然最後我並沒有把傅立葉的理論應用到專案中，但他至少讓我知道甚麼樣的音檔丟給機器可能會有問題。
    而且我本來就喜歡看這種東西所以也不虧。

    李琳山老師針對傅立葉理論講得十分詳盡。
    可惜如果需要完全理解delta function及其性質，需要一些實分析的基礎。
    所以我想要從實分析的視角去嚴格定義一下傅立葉，並加些自己的詮釋。

    不過既然是以實分析的視角，這系列就不會是入門的介紹了。但這個主題對於數學本科生來說可能又過於簡單。
    所以這比較像是寫給我自己看的筆記。
    而且內容基本上以抽象理論為主，所以對於實際要做語音相關的專案的人來說也沒有可以拿來應用的地方。

    ---

    ## Other Fourier Resources

    - 簡單的介紹影片:
      - [3Blue1Brown](https://www.youtube.com/@3blue1brown): 三藍一棕剛好在推出新的一系列傅立葉的影片，等他出完我再補上來。

        - [But what is the Fourier Transform? A visual introduction.](https://www.youtube.com/watch?v=spUNpyF58BY)

        - [But what is a Fourier series? From heat flow to drawing with circles | DE4](https://www.youtube.com/watch?v=r6sGWTCMz2k&t=1332s)

      - [【漫士】所以，到底什么是傅里叶变换？](https://www.youtube.com/watch?v=nwMKuChwpMo)

    - 整套線上課程:
      - [信號與系統 Signals and Systems｜李琳山教授|臺大開放式課程](https://www.youtube.com/playlist?list=PLxMgz3qtpNvVL6lo9ESoeG5f-airyWtqt)
      - [Digital Signal Processing 專項課程|Coursera](https://www.coursera.org/specializations/digital-signal-processing)
        : 這個課程我只有看前幾堂，因為我覺得不嚴謹。但如果只是想用比較直覺的方式去理解傅立葉，我覺得可能會有幫助。

    - 比較數學的文章及書籍:
      - [273022 FOURIERSERIER 5|Kursernas Hemsidor|Matematiska Institutionen](https://web.abo.fi/fak/mnf/mate/kurser/fourieranalys//)
        : 神奇的lecture notes，跳過了不少證明但敘述是嚴謹的。適合有實分析底子的人快速複習傅立葉。
      - [Measure and Integral: An Introduction to Real Analysis|Richard Wheeden, Richard L. Wheeden, Antoni Zygmund](https://books.google.com.tw/books/about/Measure_and_Integral.html?id=YDkDmQ_hdmcC&redir_esc=y)
        : 我的實分析啟蒙書，後面的有稍微帶過傅立葉的基礎。

      - [Fourier Analysis on Groups|Walter Rudin](https://books.google.com.tw/books/about/Fourier_Analysis_on_Groups.html?id=DKizDgAAQBAJ&redir_esc=y)
        : 學生時期跟朋友開過這本書的讀書會，超級看不懂，到底誰會想在群上做傅立葉分析?
        不過如果有多餘的時間的話，我還蠻想再一次好好讀這本書的。
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
