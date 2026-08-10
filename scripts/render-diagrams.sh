#!/usr/bin/env bash
set -euo pipefail

# Render every LaTeX diagram to an SVG beside its source file. For example:
#
#   mathematic/fourier/diagrams/example.tex
#   mathematic/fourier/diagrams/example.svg

notes_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compiler="${LATEX_COMPILER:-lualatex}"
build_root="$(mktemp -d)"

cleanup() {
  rm -rf "$build_root"
}
trap cleanup EXIT

if ! command -v "$compiler" >/dev/null 2>&1; then
  echo "LaTeX compiler not found: $compiler" >&2
  exit 1
fi

if [[ "$compiler" == "lualatex" ]] && ! kpsewhich luaotfload-main.lua >/dev/null; then
  echo "LuaLaTeX is incomplete. Install its TeX Live components first:" >&2
  echo "  sudo apt install texlive-luatex texlive-latex-extra texlive-lang-chinese" >&2
  echo "To use a different compiler temporarily: LATEX_COMPILER=pdflatex $0" >&2
  exit 1
fi

if ! command -v dvisvgm >/dev/null 2>&1; then
  echo "dvisvgm is required to convert PDFs to SVGs." >&2
  exit 1
fi

rendered=0
while IFS= read -r -d '' tex_file; do
  relative_path="${tex_file#"$notes_root/"}"
  output_file="${tex_file%.tex}.svg"
  job_name="$(printf '%s' "${relative_path%.tex}" | tr '/' '_')"
  pdf_file="$build_root/$job_name.pdf"

  mkdir -p "$(dirname "$output_file")"
  echo "Rendering: $relative_path"

  "$compiler" \
    -interaction=nonstopmode \
    -halt-on-error \
    -jobname "$job_name" \
    -output-directory "$build_root" \
    "$tex_file" >/dev/null
  # Embed glyphs as paths: this avoids broken Unicode mappings for some
  # Computer Modern symbols (notably extensible delimiters and \mapsto).
  # `currentColor` lets the SVG change foreground colour without recompiling.
  dvisvgm --pdf --no-fonts --currentcolor "$pdf_file" --output="$output_file" >/dev/null

  # SVGs displayed as images don't inherit Marimo's CSS. Give each generated
  # diagram its own light/dark palette instead. The white stroke is emitted by
  # tikz-cd for an equals arrow's inner gap, so it must follow the background.
  svg_style="<style type='text/css'><![CDATA[:root{color:#1f2937;--diagram-background:#ffffff}@media (prefers-color-scheme: dark){:root{color:#e5e7eb;--diagram-background:#18181b}}]]></style>"
  themed_output="$build_root/$(basename "$output_file").themed.svg"
  awk -v style="$svg_style" '/^<defs>/ { print style } { print }' "$output_file" > "$themed_output"
  sed "s|stroke='#fff'|stroke='var(--diagram-background)'|g" "$themed_output" > "$output_file"

  rendered=$((rendered + 1))
done < <(
  find "$notes_root" \
    \( -path "$notes_root/.git" -o -path "$notes_root/.venv" -o -path "$notes_root/.build" \) -prune -o \
    -type f -name '*.tex' -print0
)

if (( rendered == 0 )); then
  echo "No LaTeX diagrams found under $notes_root."
else
  echo "Rendered $rendered diagram(s)."
fi
