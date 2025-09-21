from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from fast_django.cli.main import app as cli
from fast_django.orm import Model, fields
from fast_django.routers import APIRouter, FastAPI


def test_reexports() -> None:
    class Example(Model):
        id = fields.IntField(pk=True)

    router = APIRouter()
    api = FastAPI()
    assert router and api


def test_startapp_scaffold_files(tmp_path: Path) -> None:
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        res = runner.invoke(cli, ["startapp", "shop"])  # type: ignore[list-item]
        assert res.exit_code == 0
        assert (Path("shop") / "models.py").exists()
        assert (Path("shop") / "views.py").exists()
        assert (Path("shop") / "routes.py").exists()
        assert (Path("shop") / "migrations" / "__init__.py").exists()
