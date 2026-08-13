#!/usr/bin/env python3
"""Build every content/**/index.py notebook into a GitHub Pages site.

The script deliberately discovers notebooks from the content tree instead of
keeping a hand-written list. Each notebook is exported to its matching URL,
for example:

    content/mathematic/fourier/00_intro/index.py
      -> _site/mathematic/fourier/00_intro/index.html

Run it through the project environment:

    uv run python scripts/build-site.py
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = REPO_ROOT / "content"
DEFAULT_OUTPUT = REPO_ROOT / "_site"
SITE_CSS = REPO_ROOT / "styles" / "site.css"
SITE_JS = REPO_ROOT / "scripts" / "site.js"

PUBLISHABLE_ASSET_SUFFIXES = {
    ".avif",
    ".csv",
    ".gif",
    ".html",
    ".ico",
    ".jpeg",
    ".jpg",
    ".json",
    ".mp3",
    ".mp4",
    ".parquet",
    ".pdf",
    ".png",
    ".svg",
    ".txt",
    ".wav",
    ".webm",
    ".webp",
}


@dataclass(frozen=True)
class Note:
    source: Path
    relative_directory: Path
    title: str

    @property
    def output_directory(self) -> Path:
        return self.relative_directory

    @property
    def url(self) -> str:
        return self.relative_directory.as_posix().rstrip("/") + "/"


@dataclass
class TopicNode:
    name: str
    children: dict[str, TopicNode] = field(default_factory=dict)
    notes: list[Note] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output directory (default: _site)",
    )
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="Do not embed pre-executed notebook outputs",
    )
    return parser.parse_args()


def extract_title(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    match = re.search(r"^\s{4}#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    if match:
        return match.group(1)
    return humanize(source.parent.name)


def discover_notes() -> list[Note]:
    notes = [
        Note(
            source=source,
            relative_directory=source.parent.relative_to(CONTENT_ROOT),
            title=extract_title(source),
        )
        for source in CONTENT_ROOT.rglob("index.py")
        if not any(part.startswith((".", "__")) for part in source.parts)
    ]
    if not notes:
        raise RuntimeError(f"No index.py notebooks found under {CONTENT_ROOT}")
    return sorted(notes, key=lambda note: note.relative_directory.parts)


def humanize(name: str) -> str:
    name = re.sub(r"^\d+[-_]", "", name)
    words = name.replace("-", " ").replace("_", " ")
    if words.lower() == "mathematic":
        return "Mathematics"
    return words.title()


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def export_note(note: Note, output_root: Path, *, execute: bool) -> None:
    output_directory = output_root / note.output_directory
    output_directory.mkdir(parents=True, exist_ok=True)

    run(
        [
            sys.executable,
            "-m",
            "marimo",
            "check",
            str(note.source),
            "--select",
            "MW",
        ]
    )

    command = [
        sys.executable,
        "-m",
        "marimo",
        "export",
        "html-wasm",
        str(note.source),
        "--output",
        str(output_directory),
        "--mode",
        "run",
        "--no-show-code",
        "--force",
        "--no-sandbox",
    ]
    command.append("--execute" if execute else "--no-execute")
    run(command)

    html_path = output_directory / "index.html"
    rewrite_exported_html(html_path, note, output_root)
    copy_note_assets(note, output_directory)


def rewrite_exported_html(html_path: Path, note: Note, output_root: Path) -> None:
    text = html_path.read_text(encoding="utf-8")

    # The editor theme is a personal preference, so it is deliberately absent
    # from pyproject.toml. Only the published site's default is set here.
    text, replacements = re.subn(
        r'("display":\s*\{[^{}]*"theme":\s*)"(?:light|dark|system)"',
        r'\1"system"',
        text,
        count=1,
    )
    if replacements != 1:
        raise RuntimeError(f"Could not set the exported theme in {html_path}")

    title = html.escape(note.title)
    text = re.sub(
        r"<title>.*?</title>", f"<title>{title} · Rambling Notes</title>", text, count=1
    )
    text = text.replace(
        '<meta name="description" content="a marimo app" />',
        f'<meta name="description" content="{title} — Rambling Notes" />',
        1,
    )

    relative_home = os.path.relpath(output_root, html_path.parent).replace(os.sep, "/")
    if relative_home == ".":
        relative_home = "./"
    else:
        relative_home += "/"
    site_css = relative_home + "site.css"
    site_js = relative_home + "site.js"
    text = text.replace(
        "</head>",
        f'  <link rel="stylesheet" href="{site_css}" />\n</head>',
        1,
    )
    text = text.replace(
        '<body>\n    <div id="root"></div>',
        (
            "<body>\n"
            '    <button class="note-sidebar-toggle" type="button" '
            'aria-label="開啟文章目錄" aria-expanded="false" '
            "data-note-sidebar-toggle>目錄</button>\n"
            '    <nav class="note-theme-switch" aria-label="主題">\n'
            "      <span>主題</span>\n"
            '      <a href="?theme=light" data-note-theme="light">亮色</a>\n'
            '      <a href="?theme=dark" data-note-theme="dark">深色</a>\n'
            "    </nav>\n"
            '    <aside class="note-sidebar" data-note-sidebar>\n'
            f'      <a class="note-site-link" href="{relative_home}" target="_top">'
            "← Rambling Notes</a>\n"
            f'      <p class="note-sidebar-title">{title}</p>\n'
            '      <nav class="note-toc" aria-label="文章目錄" data-note-toc></nav>\n'
            "    </aside>\n"
            '    <div id="root"></div>'
            f'\n    <script src="{site_js}" defer></script>'
        ),
        1,
    )
    html_path.write_text(text, encoding="utf-8")


def copy_note_assets(note: Note, output_directory: Path) -> None:
    for source in note.source.parent.rglob("*"):
        if (
            not source.is_file()
            or source.suffix.lower() not in PUBLISHABLE_ASSET_SUFFIXES
        ):
            continue
        relative = source.relative_to(note.source.parent)
        if any(part.startswith((".", "__")) for part in relative.parts):
            continue
        if relative == Path("index.html"):
            continue
        target = output_directory / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def build_topic_tree(notes: list[Note]) -> TopicNode:
    root = TopicNode("")
    for note in notes:
        node = root
        # The final directory identifies the article; its parents are topics.
        for topic in note.relative_directory.parts[:-1]:
            node = node.children.setdefault(topic, TopicNode(topic))
        node.notes.append(note)
    return root


def render_topic(node: TopicNode) -> str:
    parts: list[str] = []
    for child in node.children.values():
        parts.append(
            f'<details class="topic" open><summary>{html.escape(humanize(child.name))}</summary>'
            f'<div class="topic-children">{render_topic(child)}</div></details>'
        )
    if node.notes:
        links = []
        for index, note in enumerate(node.notes, start=1):
            links.append(
                '<li><a class="note-link" href="'
                + html.escape(note.url)
                + '"><span class="note-index">'
                + f"{index:02d}"
                + '</span><span class="note-title">'
                + html.escape(note.title)
                + '</span><span class="note-arrow">↗</span></a></li>'
            )
        parts.append('<ol class="note-list">' + "".join(links) + "</ol>")
    return "".join(parts)


def write_homepage(notes: list[Note], output_root: Path) -> None:
    tree = render_topic(build_topic_tree(notes))
    page = f"""<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="color-scheme" content="light dark" />
    <meta name="description" content="數學、程式模擬與視覺化筆記" />
    <title>Rambling Notes</title>
    <link rel="stylesheet" href="site.css" />
  </head>
  <body>
    <nav class="note-theme-switch" aria-label="主題">
      <span>主題</span>
      <a href="?theme=light" data-note-theme="light">亮色</a>
      <a href="?theme=dark" data-note-theme="dark">深色</a>
    </nav>
    <main class="site-shell">
      <header class="site-header">
        <div>
          <p class="site-kicker">Mathematics · Simulation · Notes</p>
          <h1>Rambling<br />Notes</h1>
        </div>
        <p class="site-intro">偷偷來放些筆記。</p>
      </header>
      <nav class="notes-tree" aria-label="筆記目錄">{tree}</nav>
      <footer class="site-footer">
        <span>{len(notes)} notes</span>
        <span>Built from <code>content/**/index.py</code> with marimo</span>
      </footer>
    </main>
    <script src="site.js"></script>
  </body>
</html>
"""
    (output_root / "index.html").write_text(page, encoding="utf-8")


def copy_site_files(output_root: Path) -> None:
    shutil.copy2(SITE_CSS, output_root / "site.css")
    shutil.copy2(SITE_JS, output_root / "site.js")
    (output_root / ".nojekyll").touch()


def verify_site(notes: list[Note], output_root: Path) -> None:
    missing = [
        output_root / note.output_directory / "index.html"
        for note in notes
        if not (output_root / note.output_directory / "index.html").is_file()
    ]
    if missing:
        raise RuntimeError("Missing exported pages: " + ", ".join(map(str, missing)))
    if not (output_root / "index.html").is_file():
        raise RuntimeError("Missing site index.html")


def main() -> None:
    args = parse_args()
    output_root = args.output.resolve()
    if output_root.parent != REPO_ROOT or not output_root.name.startswith("_site"):
        raise RuntimeError(
            "Output must be a direct child of the repository whose name starts "
            f"with '_site': {output_root}"
        )

    notes = discover_notes()
    print(f"Discovered {len(notes)} notebooks", flush=True)
    shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True)

    for note in notes:
        print(f"\nBuilding {note.relative_directory} — {note.title}", flush=True)
        export_note(note, output_root, execute=not args.no_execute)

    write_homepage(notes, output_root)
    copy_site_files(output_root)
    verify_site(notes, output_root)
    print(f"\nBuilt {len(notes)} notes in {output_root}", flush=True)


if __name__ == "__main__":
    main()
