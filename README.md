# Rambling Notes

以文章為本的數學筆記庫。每一篇筆記都是可獨立開啟、執行與互動的 [Marimo](https://marimo.io/) Python notebook；圖表、模擬與 LaTeX 圖的原始碼都和文章放在同一個目錄。

## 開啟筆記

第一次使用時安裝環境：

```bash
uv sync
```

從專案根目錄開啟 Marimo 的 notebook 瀏覽器：

```bash
./scripts/marimo.sh edit
```

## 撰寫方式

一個主題是一個目錄，文章、互動元件和資產放在一起：

```text
content/mathematic/
  fourier/
    00_intro/
      index.py
    02-definition_fourier/
      index.py
      fourier_on_tempered_distributions.tex
      fourier_on_tempered_distributions.svg
  linear_programming/
    simplex_method/
      simplex_method.py
```

一般數學式直接寫在 `mo.md(r"""...""")` 中，使用 KaTeX 相容的 LaTeX。需要較複雜的交換圖時，將 `.tex` 與產生的 `.svg` 放在同一資料夾，並在筆記中用 `mo.image(...)` 讀取 SVG；這不依賴 Marimo 的 `/public` 靜態檔案路由。請透過 `scripts/marimo.sh` 開啟 Marimo，Python bytecode 就會集中在 `.build/pycache/`。

## 更新 LaTeX 圖

修改任何 `.tex` 圖後，在根目錄執行：

```bash
./scripts/render-diagrams.sh
```

腳本預設使用 LuaLaTeX，並將每個圖輸出為同名 `.svg`。若系統的 LuaLaTeX 尚未裝完整，可暫時使用：

```bash
LATEX_COMPILER=pdflatex ./scripts/render-diagrams.sh
```

在 Ubuntu/Debian 上要完整使用 LuaLaTeX：

```bash
sudo apt install texlive-luatex texlive-latex-extra texlive-lang-chinese dvisvgm
```

## 建置網站

網站會自動尋找所有 `content/**/index.py`，不需要在腳本中維護文章清單。每篇筆記會輸出到與 `content/` 相同的目錄結構，並由首頁產生目錄。

在本機完整建置：

```bash
uv run python scripts/build-site.py
```

輸出位於 `_site/`。因為 WebAssembly 頁面必須透過 HTTP 開啟，請用下列方式預覽，不能直接雙擊 HTML：

```bash
uv run python -m http.server --directory _site 8000
```

然後開啟 <http://localhost:8000>。

若只想快速檢查網站結構，不預先執行每篇 notebook：

```bash
uv run python scripts/build-site.py --no-execute
```

`.github/workflows/deploy-pages.yml` 會在每次 push 到 `main` 時自動建置並部署 GitHub Pages。第一次發布前，需要到 GitHub repository 的 **Settings → Pages → Build and deployment**，把 Source 設為 **GitHub Actions**。
