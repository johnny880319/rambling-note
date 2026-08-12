# Commit conventions

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
