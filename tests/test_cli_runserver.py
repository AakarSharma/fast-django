from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from fast_django.cli.main import app

runner = CliRunner()


def test_runserver_infer_module(tmp_path: Path) -> None:
    proj = tmp_path / "mysite"
    (proj).mkdir()
    (proj / "asgi.py").write_text("app=None\n", encoding="utf-8")
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        os.environ["FD_TEST_MODE"] = "1"
        res = runner.invoke(app, ["runserver", "--port", "9999", "--host", "127.0.0.1"])  # type: ignore[list-item]
        # Since uvicorn won't start here, command should still return 0 (we don't check)
        assert res.exit_code == 0
