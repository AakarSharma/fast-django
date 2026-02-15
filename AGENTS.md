# Fast Django Agent Playbook

## Purpose
This repository evolves Django-like DX on top of FastAPI, with `manage.py` workflows, app-local migrations, ORM signals, and admin hooks.

## Core Technical Standards
- Preserve Django-like ergonomics (`startproject`, `startapp`, `makemigrations`, `migrate`, `runserver`, etc.).
- Keep migrations app-local. Migration artifacts must live under each app instead of one global project migration directory.
- Do not use broad or silent exception handling (`except Exception`, suppressed failures) unless there is a documented and explicit reason.
- Prefer explicit failures and observability-friendly behavior so monitoring systems can capture issues.
- Keep code readable and composable; apply simple, maintainable design patterns over cleverness.
- Add only necessary comments; avoid redundant comments.
- Keep docstrings accurate and update docs whenever behavior changes.
- Add/maintain unit tests for every behavior change.
- Work as a senior tech lead: prioritize long-term maintainability and explicit tradeoffs.
- Prefer explicit exception types and failure paths; do not silently ignore runtime errors.
- Avoid generic `try/except` blocks that hide failures from error monitoring systems.

## Dependency and Packaging Standards
- Project dependency source of truth is `pyproject.toml`.
- Use `uv` workflows for locking and sync.
- Keep `uv.lock` committed and updated with dependency changes.
- Avoid adding `requirements.txt`-based workflows.

## Migration and ORM Expectations
- Use Tortoise ORM + Aerich with `pyproject`-driven config.
- `startapp` should create Django-like app scaffolding including a `migrations` package.
- `makemigrations` should operate per app and keep migration state app-scoped.

## Signals and Admin Expectations
- Signal dispatch should not silently swallow receiver exceptions.
- Admin hook failures should propagate unless the module itself is truly absent.
- Optional admin dependencies may use a deterministic fallback app, but only for missing dependency cases.

## Development Workflow
- Run tests for modified behavior before committing.
- Update docs for any CLI/configuration/architecture changes.
- Commit on a dedicated branch prefixed with `codex/`.
- Never push unless explicitly requested.
- Before release, run lock + lint + type-check + tests + build + artifact checks.

## Recursive Maintenance Rule
When this file or project conventions become outdated:
1. Update `AGENTS.md` first.
2. Align implementation and tests with updated guidance.
3. Align documentation to match implementation.
