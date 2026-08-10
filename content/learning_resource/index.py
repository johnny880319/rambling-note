import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 讚的學習資源


    如題，這邊就來蒐集一些我覺得超讚的學習資源。

    我暫時把他們分成四類，但其實很多資源是跨領域的，所以分類也不一定精確。

    ## 數學

    | 名稱 | 類型 | 備註 |
    | --- | --- | --- |
    | [3Blue1Brown](https://www.youtube.com/@3blue1brown) | YouTube頻道 | 生動的動畫介紹數學。 |
    | [Meditation Math](https://www.youtube.com/@manshi_math) | YouTube頻道 | 生動的動畫介紹數學，主題比3B1B大眾一些。 |
    | [Information Theory course by Prof. Raymond Yeung (CUHK)](https://www.youtube.com/playlist?list=PLZDU8a6AcnuixlMLNuqvQSS7PDUK8pZmO) | YouTube播放清單 | 資訊理論的課程，可以搭配他的課本觀看。 |
    | [孔令傑副教授](https://www.youtube.com/@lckung.lectures) | YouTube頻道 | 孔令傑老師的頻道，有許多課程，我第一份工作的第一個專案做最佳化時就是先看他的影片學的。基本上有高中數學基礎就能看懂了。 |

    ## 電腦科學

    | 名稱 | 類型 | 備註 |
    | --- | --- | --- |
    | [Hung-yi Lee](https://www.youtube.com/@HungyiLeeNTU) | YouTube頻道 | 李宏毅老師的頻道，每年都會出最新的機器學習課程。 |
    | [Hsuan-Tien Lin](https://www.youtube.com/@hsuantien/videos) | YouTube頻道 | 林軒田老師的頻道，有機器學習的課程，比李宏毅老師更偏重數學理論，是非常重要的基本功。 |
    | [李琳山](https://www.youtube.com/@linshanlee531) | YouTube頻道 | 李琳山老師的頻道，有信號與系統課程。沒學過實分析的話可能會覺得某些地方不嚴謹。 |
    | [【10920黃能富教授｜計算機網路】](https://www.youtube.com/playlist?list=PLS0SUwlYe8cxktXNovos9xleroaWyb-z5) | YouTube播放清單 | 我是看這個學計算機網路的。 |
    | [【11010周志遠教授｜作業系統 - 字幕版】](https://www.youtube.com/playlist?list=PLS0SUwlYe8cxj8FCPRoPHAehIiN9Vo6VZ) | YouTube播放清單 | 我是看這個學作業系統的，建議先看計算機結構。 |
    | [【11010黃婷婷教授｜計算機結構高畫質版=10002】](https://www.youtube.com/playlist?list=PLS0SUwlYe8czszh6M74JCU0mIUL_ymBbe) | YouTube播放清單 | 我是看這個學計算機結構的，建議先看邏輯設計。 |
    | [【10620王俊堯教授｜數位邏輯設計】](https://www.youtube.com/playlist?list=PLS0SUwlYe8czJbz5-sRtbuTleObQE9mOa) | YouTube播放清單 | 我是看這個學邏輯設計的。 |
    | [Redknot-乔红](https://www.youtube.com/@redknot-miaomiao) | YouTube | 介紹很多硬體原理，動畫十分生動。 |
    | [Understanding Quantum Information & Computation](https://www.youtube.com/playlist?list=PLOFEBzvs-VvqKKMXX4vbi4EB1uaErFMSO) | YouTube播放清單 | IBM的講師講解的量子計算課程。前半段講量子演算法，後半段講量子資訊理論。 |
    | [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/) | 網頁 | 作業系統的經典教材，github有實作練習的程式碼。 |

    ## 軟體工程

    | 名稱 | 類型 | 備註 |
    | --- | --- | --- |
    | [Peter Pang](https://www.youtube.com/@yuan_zi_neng) | YouTube | 講一些軟體工程概念，現在沒更新了，但我還是初階工程師時，很多想法深受他啟發。 |
    | [码农高天](https://www.youtube.com/@minkoder) | YouTube | 介紹很多Python原理。 |
    | [Crafting Interpreters](https://craftinginterpreters.com/) | 網頁 | 介紹如何從零開始造一個程式語言，前半段是直譯器，後半段是編譯器。 |
    | [Category Theory for Programmers](https://github.com/hmemcpy/milewski-ctfp-pdf) | GitHub | 為工程師寫的範疇論教材，裡面用Haskell作為範例來說明Functional Programming的概念。 |

    ## 其他

    | 名稱 | 類型 | 備註 |
    | --- | --- | --- |
    | [PAPAYA 電腦教室](https://www.youtube.com/@papayaclass) | YouTube | 介紹各種好用軟體。 |
    | [长河劫](https://www.youtube.com/@%E9%95%BF%E6%B2%B3%E5%8A%AB) | YouTube | 不知道算不算學習資源，科學史非常好看，bilibili上的進度比較新。 |
    | [李永乐老师](https://www.youtube.com/@%E6%9D%8E%E6%B0%B8%E4%B9%90%E8%80%81%E5%B8%88%E5%AE%98%E6%96%B9) | YouTube | 不知道算不算學習資源，介紹的知識很廣且淺顯易懂。 |
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
