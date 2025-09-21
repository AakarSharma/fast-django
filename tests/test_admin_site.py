from __future__ import annotations

import types
from typing import Any

from fastapi import FastAPI

from fast_django.admin import AdminSite
from fast_django.orm import Model, fields
from fast_django.settings import Settings


def test_admin_site_mount_success() -> None:
    app = FastAPI()
    site = AdminSite(title="X")
    site.mount(app, Settings(), path="/admin")
    assert any(getattr(r, "path", "").startswith("/admin") for r in app.routes)


def test_admin_site_mount_placeholder(monkeypatch: Any) -> None:
    # Force failure to import fastapi_admin.app
    dummy = types.ModuleType("fastapi_admin")
    monkeypatch.setitem(__import__("sys").modules, "fastapi_admin", dummy)

    app = FastAPI()
    site = AdminSite(title="Y")
    site.mount(app, Settings(), path="/adm")
    # placeholder mounted
    assert any(getattr(r, "path", "").startswith("/adm") for r in app.routes)


def test_admin_site_register_model() -> None:
    class M(Model):
        id = fields.IntField(pk=True)

    AdminSite().register_model(M)
