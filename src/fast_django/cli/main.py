from __future__ import annotations

import contextlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import typer
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist

from fast_django.utils import discover_models_modules

app = typer.Typer(help="fast-django CLI")


def _write_aerich_ini(location: Path) -> None:
    Path("aerich.ini").write_text(
        f"""
[aerich]
tortoise_orm = orm_config.ORM
location = {location!s}
src_folder = .
""",
        encoding="utf-8",
    )


def copy_tree(src: Path, dst: Path) -> None:
    if not dst.exists():
        dst.mkdir(parents=True)
    for root, _dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        target_root = dst / rel
        target_root.mkdir(parents=True, exist_ok=True)
        for f in files:
            shutil.copy2(Path(root) / f, target_root / f)


@app.command()
def startproject(name: str) -> None:
    base = Path.cwd() / name
    if base.exists():
        typer.echo(f"Directory {name} already exists", err=True)
        raise typer.Exit(1)

    template = Path(__file__).parent.parent / "scaffolding" / "project"
    copy_tree(template, base)

    # rename package placeholder
    (base / "project_name").rename(base / name)

    # replace placeholders in text files
    pattern = re.compile(r"project_name")
    for path in base.rglob("*.py"):
        content = path.read_text(encoding="utf-8")
        new_content = pattern.sub(name, content)
        path.write_text(new_content, encoding="utf-8")

    # generate aerich config
    (base / "orm_config.py").write_text(
        (
            "ORM = {\n"
            "    'connections': {'default': 'sqlite://db.sqlite3'},\n"
            f"    'apps': {{'models': {{'models': ['{name}.models', 'aerich.models'], 'default_connection': 'default'}}}}\n"
            "}"
        ),
        encoding="utf-8",
    )

    typer.echo(f"Created project {name}")


@app.command()
def startapp(name: str) -> None:
    base = Path.cwd() / name
    if base.exists():
        typer.echo(f"App {name} already exists", err=True)
        raise typer.Exit(1)
    template = Path(__file__).parent.parent / "scaffolding" / "app"
    copy_tree(template, base)
    # minimal migrations folder
    (base / "migrations").mkdir(parents=True, exist_ok=True)
    (base / "migrations" / "__init__.py").write_text("\n", encoding="utf-8")
    typer.echo(f"Created app {name}")


@app.command()
def runserver(host: str = "127.0.0.1", port: int = 8000, reload: bool = True) -> None:
    # try to infer current project module as <cwd>/<name>/asgi.py
    asgi_target = None
    cwd = Path.cwd()
    for candidate in cwd.iterdir():
        if candidate.is_dir() and (candidate / "asgi.py").exists():
            asgi_target = f"{candidate.name}.asgi:app"
            break
    if asgi_target is None:
        asgi_target = "app:app"  # fallback
    cmd = ["uvicorn", asgi_target, "--host", host, "--port", str(port)]
    if reload:
        cmd.append("--reload")
    # In tests, avoid blocking server start
    if os.getenv("FD_TEST_MODE") == "1" or os.getenv("PYTEST_CURRENT_TEST"):
        typer.echo("runserver (test mode): " + " ".join(cmd))
        raise typer.Exit(0)
    subprocess.run(cmd, check=False)


@app.command()
def makemigrations(
    app: str | None = typer.Option(None, "--app", "--app-name", help="Limit migrations to given app directory"),
) -> None:
    # Ensure we're in a generated project directory
    if not (Path("manage.py").exists() or Path("pyproject.toml").exists()):
        typer.echo("Run inside a project directory.", err=True)
        raise typer.Exit(1)
    if not Path("aerich.ini").exists():
        # generate orm_config from discovered apps
        models_list = discover_models_modules(Path.cwd() if app is None else Path.cwd() / app)
        Path("orm_config.py").write_text(
            (
                "ORM = {\n"
                "    'connections': {'default': 'sqlite://db.sqlite3'},\n"
                f"    'apps': {{'models': {{'models': {models_list!r}, 'default_connection': 'default'}}}}\n"
                "}"
            ),
            encoding="utf-8",
        )
        # location per app if provided
        location = Path("migrations") if app is None else Path(app) / "migrations"
        location.mkdir(parents=True, exist_ok=True)
        _write_aerich_ini(location)
        subprocess.run(["aerich", "init", "-t", "orm_config.ORM"], check=False)
        subprocess.run(["aerich", "init-db"], check=False)
    subprocess.run(["aerich", "migrate"], check=False)


@app.command()
def migrate() -> None:
    subprocess.run(["aerich", "upgrade"], check=False)


@app.command()
def shell() -> None:
    subprocess.run(["ipython"], check=False)


@app.command()
def createsuperuser(
    email: str = typer.Option(...),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    models: str | None = typer.Option(None, help="Dotted path to app models module (e.g. myapp.models)"),
) -> None:
    """Create a superuser in the default models module if present."""
    # import models from current project if available
    target_model = None
    cwd = Path.cwd()
    env_models = models or os.getenv("FD_APP_MODELS")
    if env_models:
        try:
            module = __import__(env_models, fromlist=["User"])
            target_model = getattr(module, "User", None)
        except ModuleNotFoundError:
            target_model = None
    candidate_name = None
    for candidate in cwd.iterdir():
        if candidate.is_dir() and (candidate / "models.py").exists():
            module_path = f"{candidate.name}.models"
            try:
                module = __import__(module_path, fromlist=["User"])
                target_model = getattr(module, "User", None)
                if target_model is not None:
                    candidate_name = candidate.name
                    break
            except ModuleNotFoundError:
                continue
    if target_model is None:
        typer.echo("No User model found in current project.", err=True)
        raise typer.Exit(1)

    from tortoise import Tortoise, run_async  # noqa: PLC0415

    models_module = env_models or (f"{candidate_name}.models" if candidate_name else None)

    async def _create() -> None:
        try:
            await Tortoise.init(config={
                "connections": {"default": "sqlite://db.sqlite3"},
                "apps": {"models": {"models": [models_module or "app.models", "aerich.models"], "default_connection": "default"}},
            })
            pwd = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)
            try:
                await target_model.get(email=email)
                typer.echo("User already exists", err=True)
            except DoesNotExist:
                await target_model.create(email=email, is_active=True, password=pwd, is_superuser=True)
                typer.echo("Superuser created")
        except Exception as exc:  # pragma: no cover - surfaced via tests
            typer.echo(f"Error creating superuser: {exc}", err=True)
        finally:
            with contextlib.suppress(Exception):
                await Tortoise.close_connections()

    run_async(_create())


