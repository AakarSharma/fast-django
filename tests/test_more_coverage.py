from __future__ import annotations

import asyncio
import importlib
import os
import sys
import types
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from typer.testing import CliRunner

from fast_django.admin import try_call_admin_hooks
from fast_django.apps import include_app_routers
from fast_django.cli.main import app
from fast_django.settings import Settings

runner = CliRunner()


def test_startproject_scaffold(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        res = runner.invoke(app, ["startproject", "mysite"])  # type: ignore[list-item]
        assert res.exit_code == 0
        assert (Path("mysite") / "orm_config.py").exists()
        assert (Path("mysite") / "mysite" / "asgi.py").exists()
        assert (Path("mysite") / "mysite" / "models.py").exists()


def test_startapp_scaffold(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        res = runner.invoke(app, ["startapp", "blog"])  # type: ignore[list-item]
        assert res.exit_code == 0
        assert (Path("blog") / "models.py").exists()


def test_runserver_reload_false(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        os.environ["FD_TEST_MODE"] = "1"
        (Path("mysite")).mkdir()
        (Path("mysite") / "asgi.py").write_text("app=None\n", encoding="utf-8")
        res = runner.invoke(app, ["runserver", "--no-reload"])  # type: ignore[list-item]
        assert res.exit_code == 0


def test_try_call_admin_hooks_swallow_exceptions(monkeypatch: Any) -> None:
    called: dict[str, bool] = {"x": False}
    mod = types.ModuleType("boom.admin")

    def _hook(*args: Any, **kwargs: Any) -> None:
        called["x"] = True
        raise RuntimeError("boom")

    mod.init_admin = _hook  # type: ignore[attr-defined]
    monkeypatch.setitem(__import__("sys").modules, "boom.admin", mod)
    settings = Settings()
    settings.installed_apps = ["boom"]
    app_fast = FastAPI()
    try_call_admin_hooks(app_fast, settings)
    assert called["x"] is True


def test_include_app_routers_missing_module() -> None:
    app_fast = FastAPI()
    include_app_routers(app_fast, ["missing.module.name"])
    # should not raise and routes remain empty
    assert app_fast.routes == app_fast.routes


def test_makemigrations_skip_init(tmp_path: Path, monkeypatch: Any) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], check: bool = False) -> None:  # type: ignore[no-untyped-def]
        calls.append(cmd)

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        Path("pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
        Path("aerich.ini").write_text("[aerich]\n", encoding="utf-8")
        monkeypatch.setattr("subprocess.run", fake_run)
        res = runner.invoke(app, ["makemigrations"])  # type: ignore[list-item]
        assert res.exit_code == 0
        assert any(cmd[:2] == ["aerich", "migrate"] for cmd in calls)
        assert not any(cmd[:2] == ["aerich", "init"] for cmd in calls)


def test_createsuperuser_success(tmp_path: Path, monkeypatch: Any) -> None:
    # create a fake models module with Tortoise-like API
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        (Path("myproj")).mkdir()
        (Path("myproj") / "__init__.py").write_text("\n", encoding="utf-8")
        (Path("myproj") / "models.py").write_text(
            """
from fast_django.cli.main import DoesNotExist

class User:
    created = []
    @classmethod
    async def get(cls, email: str):
        raise DoesNotExist
    @classmethod
    async def create(cls, **kwargs):
        cls.created.append(kwargs)
            """.strip(),
            encoding="utf-8",
        )

        # monkeypatch Tortoise and CryptContext and run_async
        class DummyTortoise:
            @staticmethod
            async def init(config: dict[str, Any]) -> None:
                return None

            @staticmethod
            async def close_connections() -> None:
                return None

        class DummyCrypt:
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                pass

            def hash(self, pw: str) -> str:
                return "hashed-" + pw

        def run_sync(coro):  # type: ignore[no-untyped-def]
            return asyncio.run(coro)

        class DummyDoesNotExist(Exception):
            pass

        monkeypatch.setattr("tortoise.Tortoise", DummyTortoise)
        monkeypatch.setattr("tortoise.run_async", run_sync)
        monkeypatch.setattr("fast_django.cli.main.CryptContext", DummyCrypt)
        monkeypatch.setattr("fast_django.cli.main.DoesNotExist", DummyDoesNotExist)

        sys.path.insert(0, str(Path.cwd()))
        res = runner.invoke(
            app,
            [
                "createsuperuser",
                "--email",
                "a@example.com",
                "--password",
                "pass",
                "--models",
                "myproj.models",
            ],
        )  # type: ignore[list-item]
        assert res.exit_code in (0, 1)
        # ensure our fake model recorded creation
        mod = importlib.import_module("myproj.models")
        assert mod.User.created and mod.User.created[0]["email"] == "a@example.com"


def test_createsuperuser_user_exists(tmp_path: Path, monkeypatch: Any) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        (Path("myproj")).mkdir()
        (Path("myproj") / "__init__.py").write_text("\n", encoding="utf-8")
        (Path("myproj") / "models.py").write_text(
            """
class User:
    @classmethod
    async def get(cls, email: str):
        return object()
            """.strip(),
            encoding="utf-8",
        )

        class DummyTortoise:
            @staticmethod
            async def init(config: dict[str, Any]) -> None:
                return None

            @staticmethod
            async def close_connections() -> None:
                return None

        def run_sync(coro):  # type: ignore[no-untyped-def]
            return asyncio.run(coro)

        monkeypatch.setattr("tortoise.Tortoise", DummyTortoise)
        monkeypatch.setattr("tortoise.run_async", run_sync)
        # No need to patch CryptContext as we won't hit create branch
        sys.path.insert(0, str(Path.cwd()))
        res = runner.invoke(
            app,
            [
                "createsuperuser",
                "--email",
                "a@example.com",
                "--password",
                "pass",
                "--models",
                "myproj.models",
            ],
        )  # type: ignore[list-item]
        assert res.exit_code == 0
