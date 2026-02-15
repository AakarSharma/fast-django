# Releasing

fast-django uses `uv` as the release workflow source of truth.

## One-command Release Validation

Run:

```bash
./scripts/release.sh
```

This performs:

- `uv lock`
- `uv sync --all-extras --frozen`
- `uv run ruff check src tests`
- `uv run mypy src`
- `uv run pytest`
- `uv build`
- `uv run python -m twine check dist/*`

## Version Bump + Validation

Use one of:

```bash
./scripts/release.sh patch
./scripts/release.sh minor
./scripts/release.sh major
```

These call `uv version --bump <level>` before running the full validation/build workflow.

## Publish

After successful validation:

```bash
uv publish --token $PYPI_TOKEN
```
