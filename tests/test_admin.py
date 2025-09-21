from __future__ import annotations

import types
from typing import Any

from fastapi import FastAPI

from fast_django.admin import try_call_admin_hooks
from fast_django.scaffolding.project.project_name.admin import init_admin as template_init_admin
from fast_django.settings import Settings


def test_admin_template_init_mounts() -> None:
    app = FastAPI()
    s = Settings()
    s.admin_path = "/admin"
    template_init_admin(app, s)
    # Mounted apps are in routes as Mount
    assert any(getattr(r, "path", "").startswith("/admin") for r in app.routes)


def test_try_call_admin_hooks_calls_hook(monkeypatch: Any) -> None:
    called: dict[str, bool] = {"x": False}
    mod = types.ModuleType("dummyapp.admin")

    def _hook(app: FastAPI, settings: Settings) -> None:
        called["x"] = True

    mod.init_admin = _hook  # type: ignore[attr-defined]
    # register module
    monkeypatch.setitem(__import__("sys").modules, "dummyapp.admin", mod)
    s = Settings()
    s.installed_apps = ["dummyapp"]
    app = FastAPI()
    try_call_admin_hooks(app, s)
    assert called["x"] is True
