from __future__ import annotations

import types
from typing import Any

import pytest
from fastapi import FastAPI

from fast_django.admin import try_call_admin_hooks
from fast_django.scaffolding.project.project_name.admin import init_admin as template_init_admin
from fast_django.settings import Settings


def test_admin_template_init_mounts() -> None:
    app = FastAPI()
    s = Settings()
    s.admin_path = "/admin"
    template_init_admin(app, s)
    assert any(getattr(r, "path", "").startswith("/admin") for r in app.routes)


def test_try_call_admin_hooks_calls_hook(monkeypatch: Any) -> None:
    called: dict[str, bool] = {"x": False}
    mod = types.ModuleType("dummyapp.admin")

    def _hook(app: FastAPI, settings: Settings) -> None:
        called["x"] = True

    mod.init_admin = _hook  # type: ignore[attr-defined]
    monkeypatch.setitem(__import__("sys").modules, "dummyapp.admin", mod)
    s = Settings()
    s.installed_apps = ["dummyapp"]
    app = FastAPI()
    try_call_admin_hooks(app, s)
    assert called["x"] is True


def test_try_call_admin_hooks_propagates_hook_error(monkeypatch: Any) -> None:
    mod = types.ModuleType("dummyapp.admin")

    def _hook(app: FastAPI, settings: Settings) -> None:
        raise RuntimeError("hook boom")

    mod.init_admin = _hook  # type: ignore[attr-defined]
    monkeypatch.setitem(__import__("sys").modules, "dummyapp.admin", mod)
    s = Settings()
    s.installed_apps = ["dummyapp"]
    with pytest.raises(RuntimeError, match="hook boom"):
        try_call_admin_hooks(FastAPI(), s)
