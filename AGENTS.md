# Language

The test is whether the text is rendered — whether a reader of the published
site can see it.

## Anything not rendered is English

This covers `README.md`, `AGENTS.md`, `Justfile`, `pyproject.toml`, workflow
files, shell scripts, commit messages, and **all code comments** — including
comments inside the notebooks under `content/`.

## Rendered text follows the article

Text that reaches the reader is content, and stays in Chinese to match the
articles:

- Markdown inside `mo.md(r"""...""")` — prose and tables
- site UI strings in `scripts/build-site.py`: navigation and control labels
  (`導覽`, `主題`, `亮色`, `深色`, `關閉`), the tagline, the meta description
- `aria-label` and other accessibility text, in any file
- loading and status messages in `scripts/site.js` and `styles/site.css`

A file is never wholly one or the other. A notebook under `content/` holds
rendered Chinese prose and English code comments side by side, and
`scripts/build-site.py` is English code that emits Chinese markup.

## Headings are English, in Title Case

Headings are the exception to the rule above. The site's navigation is already
English — it is built from the directory names — so a reader reaches a note
through `Mathematics > Linear Programming > Simplex Method`, and a `#` or `##`
just continues that same spine. They are structural labels, closer to the
navigation than to the prose beneath them.

So write `## Canonical Form and Pivot Operation`, not
`## Canonical form 與轉軸操作`. The same applies to a series' opening note: it
is titled `# Introduction`, because the navigation already says which series it
opens.

## Blockquotes are English, except remarks

A `>` block sets a statement apart from the prose: a definition, theorem,
proposition, lemma, corollary. All of them are written in English, the way the
sources a note draws on state them. Such a block is a portable object — a
reader checking it against Polster or a paper compares the two sentences
directly, and a reader quoting it carries the English along.

```markdown
> **Theorem (Permutation Test):** Let $T$ be a causal, $p$-periodic juggling
> function. Then $T$ is a juggling pattern if and only if, over a single
> period, the multiset of landing slots and the multiset of throwing slots
> coincide in $\mathcal{H} \times \mathbb{Z}/p$, counted with multiplicity.
```

`Remark` is the exception. It comments on the prose around it rather than
standing on its own, so it follows the article and stays Chinese.

The boundary is the block, not the subject matter. A definition folded into
running prose is prose, and stays Chinese; the same definition set off in a
`>` block is English.

# Maths in conversation

Chat replies reach the reader through a terminal that renders markdown but has
no KaTeX, so inline `$\bar{c}_N^T = c_N^T - c_B^TA_B^{-1}A_N$` arrives as that
literal string, backslashes and all.

When discussing the maths, put expressions in code spans or fenced code blocks
and write them in readable ASCII: `c_N - A_N^T (A_B^T)^-1 c_B` rather than the
LaTeX source. Keep subscripts as `x_B`, superscripts as `A^-1`, and use `>=`
and `<=` where a symbol would otherwise need escaping. Multi-line derivations
belong in a fenced block.

This applies to conversation only. Files under `content/` are rendered through
KaTeX, so they keep real LaTeX.

# Maths in the notebooks

Displayed alignment uses `align*`. It never numbers, and it accepts a `\tag` on
every row when rows need labels. The alternatives each have a trap: `aligned`
allows only one `\tag` per display and fails with `Multiple \tag` on the
second, and the unstarred `align` silently numbers every row through a CSS
counter, so the numbers appear in the browser but not in the rendered text.

Use `aligned` only where the block nests inside other maths, such as
`\left\{ ... \right.` or a matrix cell. KaTeX accepts `align*` there too, but
real LaTeX does not, and keeping those few places portable costs nothing.

Delimiters default to `\left` and `\right`, which size themselves to their
contents.  Reach for the `\bigl` family only where delimiters nest and the
contents are not tall.  `\left` measures height, not nesting depth, so
`\left( \min(b, \tau + u) - \max(a, \tau) \right)` sets its outer parentheses at
exactly the size of the inner ones and the levels stop being legible.  Both
exceptions in this section are the same shape: the general tool gives way to
the manual one where the maths nests.

A proof ends with `<span class="qed">$\square$</span>` on its own line, after
the closing `$$`. The marker has to sit outside the maths: a `\tag` is centred
against the whole display rather than dropped to the last line. `styles/marimo.css`
right-aligns it. Use a `<span>`, not a `<p>` — marimo wraps each paragraph in a
`<span class="paragraph">`, and a block element nested there breaks the markup.

`scripts/check-notebooks.py` does not run KaTeX, so none of these mistakes are
caught by `just check`. Render the notebook to see them.

# Article authorization

Do not edit anything under `content/` unless the user explicitly asks for the
edit. Reviewing an article, answering a question about its mathematics, or being
asked what something should be named is not permission to change the file.
Report the finding or give the suggestion, and let the user apply it.

# Commit conventions

## Commit authorization

Do not create a commit unless the user explicitly asks you to commit the current changes. A request to edit, fix, build, test, or review files does not imply permission to commit them.

## Commit message format

All commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

Use this format:

```text
<type>[optional scope]: <description>
```

Common types include `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore`, `perf`, and `revert`.

- Keep the description concise and write it in the imperative mood.
- Use a scope when it makes the affected area clearer.
- Add `!` before `:` or a `BREAKING CHANGE:` footer when a commit introduces a breaking change.

Examples:

```text
docs(simplex): clarify the minimum ratio test
feat(simulation): add an objective-gradient arrow
fix(diagrams): preserve SVG text colors in dark mode
```
