# Rambling Notes

An article-first collection of mathematics notes. Every note is a
[Marimo](https://marimo.io/) Python notebook that can be opened, executed and
interacted with on its own; the source for plots, simulations and LaTeX diagrams
lives in the same directory as the article.

## Opening a note

For first-time setup, install the environment and the task runner:

```bash
uv sync
uv tool install rust-just
```

Every common command lives in the `Justfile`. Running `just` on its own lists
them all:

```bash
just         # list all available recipes
just edit    # open the Marimo notebook browser
```

`just edit` does not open a browser tab automatically; the URL is printed to the
terminal. To open it inside VS Code, use `Ctrl+Shift+P` → `Simple Browser: Show`
and paste that URL.

## Writing notes

One topic is one directory, holding the article, its interactive components and
its assets together:

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

Write ordinary math directly inside `mo.md(r"""...""")` using KaTeX-compatible
LaTeX. For more involved commutative diagrams, put the `.tex` and its generated
`.svg` in the same folder and load the SVG with `mo.image(...)` from the note;
this does not rely on Marimo's `/public` static file route. Open Marimo through
`just edit` so Python bytecode is collected under `.build/pycache/`.

## Updating LaTeX diagrams

After changing any `.tex` diagram, run this from the repository root:

```bash
just diagrams
```

The script uses LuaLaTeX by default and writes each diagram to a `.svg` of the
same name. If LuaLaTeX is not fully installed on your system, you can fall back
to:

```bash
LATEX_COMPILER=pdflatex just diagrams
```

For a complete LuaLaTeX setup on Ubuntu/Debian:

```bash
sudo apt install texlive-luatex texlive-latex-extra texlive-lang-chinese dvisvgm
```

## Building the site

The build discovers every `content/**/index.py` automatically, so there is no
article list to maintain in the script. Each note is emitted into the same
directory structure as `content/`, and the home page generates the index.

To build everything locally:

```bash
just build
```

Output lands in `_site/`. Because WebAssembly pages must be served over HTTP,
preview them this way rather than opening the HTML directly:

```bash
just serve          # port 8000 by default; use `just serve 9000` to override
just preview        # build, then start the server
```

Then open <http://localhost:8000>.

To check the site structure quickly without executing every notebook first:

```bash
just build-fast
```

`.github/workflows/deploy-pages.yml` builds and deploys to GitHub Pages on every
push to `main`. Before the first publish, go to the repository's
**Settings → Pages → Build and deployment** and set Source to **GitHub Actions**.
