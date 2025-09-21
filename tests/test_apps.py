from __future__ import annotations

from fastapi import FastAPI

from fast_django.apps import include_app_routers


def test_include_app_routers_imports_template() -> None:
    app = FastAPI()
    include_app_routers(app, ["fast_django.scaffolding.project.project_name"])
    assert any(getattr(r, "path", "") == "/healthz" for r in app.routes)
