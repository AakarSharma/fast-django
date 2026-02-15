from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from fast_django.cli.main import app

runner = CliRunner()


def test_startproject_exists(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        Path("mysite").mkdir()
        res = runner.invoke(app, ["startproject", "mysite"])  # type: ignore[list-item]
        assert res.exit_code != 0


def test_startapp_exists(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        Path("myapp").mkdir()
        res = runner.invoke(app, ["startapp", "myapp"])  # type: ignore[list-item]
        assert res.exit_code != 0


def test_makemigrations_requires_pyproject(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        res = runner.invoke(app, ["makemigrations"])  # type: ignore[list-item]
        assert res.exit_code != 0
        assert "Run inside a project" in res.output


def test_makemigrations_calls_aerich(tmp_path: Path, monkeypatch: Any) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], check: bool = False) -> None:  # type: ignore[no-untyped-def]
        assert check is True
        calls.append(cmd)

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        Path("pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
        Path("blog").mkdir()
        Path("blog/models.py").write_text("\n", encoding="utf-8")
        monkeypatch.setattr("subprocess.run", fake_run)
        res = runner.invoke(app, ["makemigrations"])  # type: ignore[list-item]
        assert res.exit_code == 0
        assert any("init-db" in cmd for cmd in calls)
        assert any(cmd[-2:] == ["migrate", "--no-input"] for cmd in calls)


def test_migrate_calls_upgrade(tmp_path: Path, monkeypatch: Any) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], check: bool = False) -> None:  # type: ignore[no-untyped-def]
        assert check is True
        calls.append(cmd)

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        Path("pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
        Path("blog/migrations/blog").mkdir(parents=True)
        Path("blog/models.py").write_text("\n", encoding="utf-8")
        monkeypatch.setattr("subprocess.run", fake_run)
        res = runner.invoke(app, ["migrate", "--app", "blog"])  # type: ignore[list-item]
        assert res.exit_code == 0
        assert calls and calls[0][-1] == "upgrade"


def test_shell_invokes_ipython(tmp_path: Path, monkeypatch: Any) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], check: bool = False) -> None:  # type: ignore[no-untyped-def]
        assert check is True
        calls.append(cmd)

    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        monkeypatch.setattr("subprocess.run", fake_run)
        res = runner.invoke(app, ["shell"])  # type: ignore[list-item]
        assert res.exit_code == 0
        assert calls and calls[0][0] == "ipython"


def test_runserver_fallback_app_target(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        os.environ["FD_TEST_MODE"] = "1"
        res = runner.invoke(app, ["runserver"])  # type: ignore[list-item]
        assert res.exit_code == 0


def test_createsuperuser_no_user_model(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        res = runner.invoke(
            app, ["createsuperuser", "--email", "a@example.com", "--password", "x"]
        )  # type: ignore[list-item]
        assert res.exit_code != 0
