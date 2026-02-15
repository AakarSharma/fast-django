from __future__ import annotations

import asyncio
import subprocess
import types
from pathlib import Path
from typing import Any, ClassVar

import pytest
import typer
from typer.testing import CliRunner

from fast_django.cli import main as cli_main

runner = CliRunner()


def test_run_command_raises_typer_exit_on_subprocess_error(monkeypatch: Any) -> None:
    def _fail(cmd: list[str], check: bool = True) -> None:  # type: ignore[no-untyped-def]
        raise subprocess.CalledProcessError(2, cmd)

    monkeypatch.setattr(cli_main.subprocess, "run", _fail)
    with pytest.raises(typer.Exit):
        cli_main._run_command(["x"])


def test_discover_target_apps_alias_and_missing(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        assert cli_main._discover_target_apps("auth") == ["auth"]
        with pytest.raises(typer.Exit):
            cli_main._discover_target_apps("missing")


def test_load_orm_config_module_missing_and_bad_spec(tmp_path: Path, monkeypatch: Any) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        with pytest.raises(typer.Exit):
            cli_main._load_orm_config_module()

        Path("orm_config.py").write_text("ORM = {}\n", encoding="utf-8")
        monkeypatch.setattr(
            cli_main.importlib.util, "spec_from_file_location", lambda *a, **k: None
        )
        with pytest.raises(typer.Exit):
            cli_main._load_orm_config_module()


def test_syncpermissions_command_calls_internal_sync(tmp_path: Path, monkeypatch: Any) -> None:
    called = {"v": False}

    def _sync() -> None:
        called["v"] = True

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        Path("pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
        monkeypatch.setattr(cli_main, "_sync_permissions_from_orm_config", _sync)
        res = runner.invoke(cli_main.app, ["syncpermissions"])  # type: ignore[list-item]
        assert res.exit_code == 0
        assert called["v"] is True


def test_migrate_calls_sync_permissions_when_global(monkeypatch: Any, tmp_path: Path) -> None:
    calls: list[tuple[str, ...]] = []
    sync_called = {"v": False}

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        Path("pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
        monkeypatch.setattr(cli_main, "_discover_target_apps", lambda app: ["blog"])
        monkeypatch.setattr(cli_main, "_ensure_aerich_config", lambda app_name: Path("x.toml"))
        monkeypatch.setattr(cli_main, "_aerich_state_dir", lambda app_name: Path("."))
        monkeypatch.setattr(
            cli_main, "_run_aerich", lambda config, app_name, args: calls.append(tuple(args))
        )
        monkeypatch.setattr(
            cli_main,
            "_sync_permissions_from_orm_config",
            lambda: sync_called.__setitem__("v", True),
        )
        res = runner.invoke(cli_main.app, ["migrate"])  # type: ignore[list-item]
        assert res.exit_code == 0
        assert ("upgrade",) in calls
        assert sync_called["v"] is True


class _DummyUser:
    existing: ClassVar[bool] = False
    saved_usernames: ClassVar[list[str]] = []

    def __init__(
        self,
        username: str,
        email: str,
        is_active: bool,
        is_staff: bool,
        is_superuser: bool,
    ) -> None:
        self.username = username
        self.email = email
        self.is_active = is_active
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.password = ""

    @classmethod
    async def get_or_none(cls, username: str):  # type: ignore[no-untyped-def]
        return object() if cls.existing else None

    def set_password(self, raw: str) -> None:
        self.password = "hashed-" + raw

    async def save(self) -> None:
        _DummyUser.saved_usernames.append(self.username)


class _DummyTortoise:
    _inited = True

    @staticmethod
    async def init(config: dict[str, Any]) -> None:
        return None

    @staticmethod
    async def close_connections() -> None:
        return None


def test_createsuperuser_builtin_branches(monkeypatch: Any, tmp_path: Path) -> None:
    def _run_sync(coro):  # type: ignore[no-untyped-def]
        return asyncio.run(coro)

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        Path("orm_config.py").write_text("ORM = {}\n", encoding="utf-8")
        monkeypatch.setattr(cli_main, "User", _DummyUser)
        monkeypatch.setattr(
            cli_main,
            "_load_orm_config_module",
            lambda: types.SimpleNamespace(ORM={"connections": {}, "apps": {}}),
        )
        monkeypatch.setattr("tortoise.Tortoise", _DummyTortoise)
        monkeypatch.setattr("tortoise.run_async", _run_sync)

        _DummyUser.existing = False
        created = runner.invoke(
            cli_main.app,
            [
                "createsuperuser",
                "--username",
                "rootuser",
                "--email",
                "ops-team@example.com",
                "--password",
                "sTr0ng!pass",
            ],
        )  # type: ignore[list-item]
        assert created.exit_code == 0
        assert "Superuser created" in created.output
        assert "rootuser" in _DummyUser.saved_usernames

        _DummyUser.existing = True
        exists = runner.invoke(
            cli_main.app,
            [
                "createsuperuser",
                "--username",
                "rootuser",
                "--email",
                "ops-team@example.com",
                "--password",
                "sTr0ng!pass",
            ],
        )  # type: ignore[list-item]
        assert exists.exit_code == 0
        assert "User already exists" in exists.output


def test_createsuperuser_requires_username_when_not_custom(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        res = runner.invoke(
            cli_main.app, ["createsuperuser", "--password", "strong-password-1"], input="\n"
        )  # type: ignore[list-item]
        assert res.exit_code != 0
        assert "--username is required" in res.output


def test_createsuperuser_custom_missing_module(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        res = runner.invoke(
            cli_main.app,
            [
                "createsuperuser",
                "--models",
                "missing.models",
                "--password",
                "x",
                "--email",
                "x@y.com",
            ],
        )  # type: ignore[list-item]
        assert res.exit_code != 0
        assert "No User model found" in res.output


def test_createsuperuser_blocks_on_password_warning_without_bypass(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        cli_main,
        "validate_password",
        lambda password, username=None, email=None: ["This password is too short."],
    )
    monkeypatch.setattr(cli_main.typer, "confirm", lambda *args, **kwargs: False)

    res = runner.invoke(
        cli_main.app,
        ["createsuperuser", "--username", "admin", "--email", "a@example.com", "--password", "123"],
    )  # type: ignore[list-item]
    assert res.exit_code != 0
    assert "Password validation warnings" in res.output


def test_createsuperuser_allows_password_warning_with_bypass(
    monkeypatch: Any, tmp_path: Path
) -> None:
    def _run_sync(coro):  # type: ignore[no-untyped-def]
        return asyncio.run(coro)

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        Path("orm_config.py").write_text("ORM = {}\n", encoding="utf-8")
        monkeypatch.setattr(cli_main, "User", _DummyUser)
        monkeypatch.setattr(
            cli_main,
            "_load_orm_config_module",
            lambda: types.SimpleNamespace(ORM={"connections": {}, "apps": {}}),
        )
        monkeypatch.setattr("tortoise.Tortoise", _DummyTortoise)
        monkeypatch.setattr("tortoise.run_async", _run_sync)
        monkeypatch.setattr(
            cli_main,
            "validate_password",
            lambda password, username=None, email=None: ["This password is too short."],
        )
        monkeypatch.setattr(cli_main.typer, "confirm", lambda *args, **kwargs: True)

        _DummyUser.existing = False
        res = runner.invoke(
            cli_main.app,
            [
                "createsuperuser",
                "--username",
                "admin2",
                "--email",
                "b@example.com",
                "--password",
                "123",
            ],
        )  # type: ignore[list-item]
        assert res.exit_code == 0
        assert "Superuser created" in res.output
