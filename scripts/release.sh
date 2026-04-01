#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if command -v uv >/dev/null 2>&1; then
  UV_BIN="uv"
elif [[ -x ".venv/bin/uv" ]]; then
  UV_BIN=".venv/bin/uv"
else
  echo "uv is required. Install from https://github.com/astral-sh/uv" >&2
  exit 1
fi

BUMP="${1:-}"

if [[ -n "$BUMP" ]]; then
  case "$BUMP" in
    patch|minor|major)
      "$UV_BIN" version --bump "$BUMP"
      ;;
    *)
      echo "Invalid bump level: $BUMP (use: patch|minor|major)" >&2
      exit 1
      ;;
  esac
fi

"$UV_BIN" lock
"$UV_BIN" sync --all-extras --frozen
"$UV_BIN" run ruff check src tests
"$UV_BIN" run mypy src
"$UV_BIN" run pytest
rm -rf dist
"$UV_BIN" build
"$UV_BIN" run python -m twine check dist/*

echo "Release artifacts ready in dist/."
echo "To publish: uv publish --token \$PYPI_TOKEN"
