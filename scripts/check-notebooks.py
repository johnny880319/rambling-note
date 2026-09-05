"""Catch markdown and KaTeX mistakes in the notebooks before they ship.

Every check here comes from a bug that actually reached a rendered page: a
stray backtick that swallowed a formula, a bold span left unpaired so the
asterisks showed up as text, LaTeX written outside ``$...$`` so the reader saw
``a_{4}``.  They are cheap to run and awkward to spot by eye in a long article.

Usage::

    uv run python scripts/check-notebooks.py [PATH ...]

Paths default to every ``content/**/*.py`` notebook.  Exits non-zero when
anything is reported.
"""

import ast
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_ROOT = REPO_ROOT / "content"

# Two CJK punctuation marks in a row is almost always an editing leftover.
DOUBLED_PUNCTUATION = re.compile(r"[。，、：；]{2,}")
# A LaTeX subscript or command that escaped its math delimiters.
BARE_LATEX = re.compile(r"[A-Za-z]_\{|\\[a-zA-Z]+")
# marimo hands KaTeX its input inside this element; everything else is prose.
# pymdownx's block syntax: an opener `/// admonition | Title`, its options
# indented four spaces, and a bare `///` to close.  Every way of getting it
# wrong degrades quietly instead of failing, so the checks below compare what
# the source asked for against what came out of the renderer.
BLOCK_OPEN = re.compile(r"^[ \t]*/{3}[ \t]+\S.*$", re.MULTILINE)
BLOCK_CLOSE = re.compile(r"^[ \t]*/{3}[ \t]*$", re.MULTILINE)
BLOCK_TYPE = re.compile(r"^[ \t]+type:[ \t]*(\S+)[ \t]*$", re.MULTILINE)
# One or two slashes is a typo for three; four or more is legal nesting.
BLOCK_TYPO = re.compile(r"^[ \t]*/{1,2}[ \t]*admonition\b", re.MULTILINE)
RENDERED_BLOCK = re.compile(r'<div class="admonition([^"]*)"')
MATH_ELEMENT = re.compile(r"<marimo-tex.*?</marimo-tex>", re.DOTALL)
HTML_TAG = re.compile(r"<[^>]+>")
CODE_SPAN_WITH_MATH = re.compile(r"<code>[^<]*\$")
INLINE_DOLLAR = re.compile(r"(?<!\$)\$(?!\$)")


class Finding(dict):
    """A problem to report, carrying enough to point at a line."""


def markdown_blocks(path: Path) -> list[tuple[int, str]]:
    """Return ``(line number, source)`` for every ``mo.md("...")`` literal."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    blocks: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        is_markdown_call = (
            isinstance(function, ast.Attribute) and function.attr == "md"
        )
        if not is_markdown_call or not node.args:
            continue
        argument = node.args[0]
        if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
            blocks.append((argument.lineno, argument.value))
    return blocks


def line_of(block_start: int, source: str, offset: int) -> int:
    return block_start + source.count("\n", 0, offset)


def check_block(path: Path, start: int, source: str, render) -> list[Finding]:
    findings: list[Finding] = []

    def report(line: int, message: str) -> None:
        findings.append(Finding(path=path, line=line, message=message))

    if source.count("$$") % 2:
        report(start, "odd number of $$ delimiters")
    if len(INLINE_DOLLAR.findall(source)) % 2:
        report(start, "odd number of inline $ delimiters")
    if source.count("**") % 2:
        report(start, "odd number of ** markers, so bold will not pair up")

    for match in DOUBLED_PUNCTUATION.finditer(source):
        report(
            line_of(start, source, match.start()),
            f"doubled punctuation {match.group(0)!r}",
        )

    html = render(source)
    if "**" in html:
        report(start, "literal ** survived rendering, so a bold span is broken")
    if CODE_SPAN_WITH_MATH.search(html):
        report(start, "a code span contains $, so the math will not render")

    prose = HTML_TAG.sub("", MATH_ELEMENT.sub("", html))
    for fragment in sorted(set(BARE_LATEX.findall(prose))):
        # An escaped backslash in the source means the author is naming the
        # command rather than trying to typeset it.
        if fragment.startswith("\\") and "\\" + fragment in source:
            continue
        report(start, f"LaTeX {fragment!r} outside math delimiters")

    for match in BLOCK_TYPO.finditer(source):
        report(
            line_of(start, source, match.start()),
            "a block opener needs three slashes",
        )

    opened = len(BLOCK_OPEN.findall(source))
    if opened != len(BLOCK_CLOSE.findall(source)):
        # An unclosed block runs to the end of the cell, swallowing whatever
        # follows it into the panel.
        report(start, f"{opened} /// block(s) opened, but the /// fences do not pair up")

    rendered = RENDERED_BLOCK.findall(html)
    if opened != len(rendered):
        report(start, f"{opened} /// block(s) opened but {len(rendered)} rendered")

    wanted = Counter(BLOCK_TYPE.findall(source))
    got = Counter(kind.strip() for kind in rendered if kind.strip())
    for kind, count in wanted.items():
        if got[kind] < count:
            # Almost always the option line lost its four-space indent, which
            # turns it into body text and drops the type from the class list.
            report(start, f"block type {kind!r} did not reach the rendered class list")

    return findings


def main(argv: list[str]) -> int:
    if argv:
        paths = [Path(argument).resolve() for argument in argv]
    else:
        paths = sorted(CONTENT_ROOT.rglob("*.py"))
    paths = [path for path in paths if "__marimo__" not in path.parts]

    # Imported late: it is slow, and a bad path should fail before that cost.
    import marimo

    def render(source: str) -> str:
        return marimo.md(source).text

    findings: list[Finding] = []
    for path in paths:
        for start, source in markdown_blocks(path):
            findings.extend(check_block(path, start, source, render))

    for finding in findings:
        path = finding["path"]
        location = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        print(f"{location}:{finding['line']}: {finding['message']}")

    blocks = sum(len(markdown_blocks(path)) for path in paths)
    print(
        f"checked {blocks} markdown block(s) in {len(paths)} notebook(s): "
        f"{len(findings)} problem(s)"
    )
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
