# List all available recipes
_default:
    @just --list

# Install and sync the Python environment
setup:
    uv sync

# Open the Marimo notebook browser (does not auto-launch a browser tab)
edit *ARGS:
    ./scripts/marimo.sh edit {{ARGS}}

# Regenerate SVGs for all .tex diagrams
diagrams:
    ./scripts/render-diagrams.sh

# Build the full site into _site/ (executes every notebook)
build:
    uv run python scripts/build-site.py

# Build quickly to check site structure, without executing notebooks
build-fast:
    uv run python scripts/build-site.py --no-execute

# Serve the built site locally
serve port="8000":
    uv run python -m http.server --directory _site {{port}}

# Build, then serve immediately
preview port="8000": build (serve port)

# Lint
lint:
    uv run ruff check .

# Format
fmt:
    uv run ruff format .

# Remove build artifacts
clean:
    rm -rf _site .build
