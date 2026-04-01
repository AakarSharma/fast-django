from __future__ import annotations

import anyio
from fastapi import FastAPI

from fast_django.contrib.auth.models import AnonymousUser, User
from fast_django.db import build_tortoise_config, init_db
from fast_django.settings import Settings


def test_build_tortoise_config_prefers_apps_mapping() -> None:
    settings = Settings()
    settings.orm.apps = {"models": {"models": ["a.b"], "default_connection": "default"}}
    config = build_tortoise_config(settings)
    assert config["apps"] == settings.orm.apps


def test_anonymous_user_permission_methods() -> None:
    anon = AnonymousUser()

    async def run() -> None:
        assert await anon.has_perm("auth.view_user") is False
        assert await anon.has_module_perms("auth") is False

    anyio.run(run)


def test_user_property_flags() -> None:
    user = User(username="u", email="e", is_active=True)
    assert user.is_authenticated is True
    assert user.is_anonymous is False


def test_init_db_can_sync_permissions_on_startup(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    called = {"init": False, "sync": False, "close": False}

    class DummyTortoise:
        @staticmethod
        async def init(config):  # type: ignore[no-untyped-def]
            called["init"] = True

        @staticmethod
        async def close_connections() -> None:
            called["close"] = True

    async def fake_sync() -> None:
        called["sync"] = True

    monkeypatch.setattr("fast_django.db.Tortoise", DummyTortoise)
    monkeypatch.setattr("fast_django.db.sync_content_types_and_permissions", fake_sync)

    settings = Settings()
    settings.auth_sync_permissions_on_startup = True
    app = FastAPI()
    init_db(app, settings)

    async def run() -> None:
        await app.router.startup()
        await app.router.shutdown()

    anyio.run(run)
    assert called == {"init": True, "sync": True, "close": True}
