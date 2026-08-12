#!/usr/bin/env bash
set -euo pipefail

# Render every LaTeX diagram to SVGs beside its source file. For example:
#
#   mathematic/fourier/diagrams/example.tex
#   mathematic/fourier/diagrams/example.svg
#
# A one-page PDF produces `example.svg`. A multi-page PDF (for example, a
# `standalone` document using the `math` option) produces `example-1.svg`,
# `example-2.svg`, and so on.

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

if ! command -v pdfinfo >/dev/null 2>&1; then
  echo "pdfinfo is required to determine how many SVG pages to render." >&2
  echo "Install the Poppler utilities package (for example: poppler-utils)." >&2
  exit 1
fi

theme_svg() {
  local output_file="$1"
  local themed_output="$2"

  # SVGs displayed as images don't inherit Marimo's CSS. Give each generated
  # diagram its own light/dark palette instead. The white stroke is emitted by
  # tikz-cd for an equals arrow's inner gap, so it must follow the background.
  local svg_style
  svg_style="<style type='text/css'><![CDATA[:root{color:#1f2937;--diagram-background:#ffffff}@media (prefers-color-scheme: dark){:root{color:#e5e7eb;--diagram-background:#18181b}}]]></style>"
  awk -v style="$svg_style" '/^<defs>/ { print style } { print }' "$output_file" > "$themed_output"
  sed "s|stroke='#fff'|stroke='var(--diagram-background)'|g" "$themed_output" > "$output_file"
}

remove_stale_outputs() {
  local output_stem="$1"
  local page_count="$2"
  local candidate
  local suffix

  if (( page_count == 1 )); then
    # A source that changed from multi-page to one page no longer owns any
    # numeric page variants.
    rm -f -- "$output_stem"-[0-9]*.svg
    return
  fi

  # A multi-page source owns only numeric page variants, so its old single-page
  # output would otherwise be an ambiguous, stale diagram.
  rm -f -- "$output_stem.svg"

  shopt -s nullglob
  for candidate in "$output_stem"-[0-9]*.svg; do
    suffix="${candidate#"$output_stem"-}"
    suffix="${suffix%.svg}"
    if [[ "$suffix" =~ ^[1-9][0-9]*$ ]] && (( suffix > page_count )); then
      rm -f -- "$candidate"
    fi
  done
  shopt -u nullglob
}

rendered_files=0
rendered_pages=0
while IFS= read -r -d '' tex_file; do
  relative_path="${tex_file#"$notes_root/"}"
  output_stem="${tex_file%.tex}"
  job_name="$(printf '%s' "${relative_path%.tex}" | tr '/' '_')"
  pdf_file="$build_root/$job_name.pdf"

  mkdir -p "$(dirname "$output_stem")"
  echo "Rendering: $relative_path"

  "$compiler" \
    -interaction=nonstopmode \
    -halt-on-error \
    -jobname "$job_name" \
    -output-directory "$build_root" \
    "$tex_file" >/dev/null

  page_count="$(pdfinfo "$pdf_file" | awk '$1 == "Pages:" { print $2; exit }')"
  if ! [[ "$page_count" =~ ^[1-9][0-9]*$ ]]; then
    echo "Could not determine the number of pages in: $relative_path" >&2
    exit 1
  fi

  remove_stale_outputs "$output_stem" "$page_count"

  for ((page_number = 1; page_number <= page_count; page_number++)); do
    if (( page_count == 1 )); then
      output_file="$output_stem.svg"
    else
      output_file="$output_stem-$page_number.svg"
    fi

    # Embed glyphs as paths: this avoids broken Unicode mappings for some
    # Computer Modern symbols (notably extensible delimiters and \mapsto).
    # `currentColor` lets the SVG change foreground colour without recompiling.
    dvisvgm --pdf --page="$page_number" --no-fonts --currentcolor "$pdf_file" --output="$output_file" >/dev/null
    theme_svg "$output_file" "$build_root/$job_name-$page_number.themed.svg"

    rendered_pages=$((rendered_pages + 1))
  done

  rendered_files=$((rendered_files + 1))
done < <(
  find "$notes_root" \
    \( -path "$notes_root/.git" -o -path "$notes_root/.venv" -o -path "$notes_root/.build" \) -prune -o \
    -type f -name '*.tex' -print0
)

if (( rendered_files == 0 )); then
  echo "No LaTeX diagrams found under $notes_root."
else
  echo "Rendered $rendered_pages SVG page(s) from $rendered_files LaTeX file(s)."
fi
