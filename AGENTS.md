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

- Markdown inside `mo.md(r"""...""")` — prose, headings, tables
- site UI strings in `scripts/build-site.py`: navigation and control labels
  (`導覽`, `主題`, `亮色`, `深色`, `關閉`), the tagline, the meta description
- `aria-label` and other accessibility text, in any file
- loading and status messages in `scripts/site.js` and `styles/site.css`

A file is never wholly one or the other. A notebook under `content/` holds
rendered Chinese prose and English code comments side by side, and
`scripts/build-site.py` is English code that emits Chinese markup.

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
