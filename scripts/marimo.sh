#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPYCACHEPREFIX="$repo_root/.build/pycache"

args=("$@")
if [[ "${1:-}" == "edit" ]] && [[ ! " ${args[*]:1} " =~ [[:space:]]--headless[[:space:]] ]]; then
  args=("edit" "--headless" "${args[@]:1}")
fi

exec uv run marimo "${args[@]}"
