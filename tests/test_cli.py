from __future__ import annotations

import shutil
from pathlib import Path

from typer.testing import CliRunner

from fast_django.cli.main import app

runner = CliRunner()


def test_startproject_tmp(tmp_path: Path) -> None:
    # Note: keep tmp dir isolated; no need to capture cwd
    try:
        # run inside tmp
        os_cwd = tmp_path
        (os_cwd).mkdir(parents=True, exist_ok=True)
        with runner.isolated_filesystem(temp_dir=str(os_cwd)):
            result = runner.invoke(app, ["startproject", "mysite"])  # type: ignore[list-item]
            assert result.exit_code == 0, result.output
            assert (Path("mysite") / "manage.py").exists()
            assert (Path("mysite") / "mysite" / "asgi.py").exists()
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
