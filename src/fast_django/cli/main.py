from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import typer
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist

from fast_django.utils import discover_models_modules

app = typer.Typer(help="fast-django CLI")

_AERICH_CONFIG_DIR = Path(".fast_django") / "aerich"


def copy_tree(src: Path, dst: Path) -> None:
    if not dst.exists():
        dst.mkdir(parents=True)
    for root, _dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        target_root = dst / rel
        target_root.mkdir(parents=True, exist_ok=True)
        for f in files:
            shutil.copy2(Path(root) / f, target_root / f)


def _run_command(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        typer.echo(f"Command failed ({exc.returncode}): {' '.join(cmd)}", err=True)
        raise typer.Exit(1) from exc


def _ensure_project_context() -> None:
    if not (Path("manage.py").exists() or Path("pyproject.toml").exists()):
        typer.echo("Run inside a project directory.", err=True)
        raise typer.Exit(1)


def _discover_target_apps(limit_app: str | None) -> list[str]:
    if limit_app is not None:
        app_dir = Path(limit_app)
        if not app_dir.is_dir() or not (app_dir / "models.py").exists():
            typer.echo(f"App {limit_app!r} was not found or has no models.py", err=True)
            raise typer.Exit(1)
        return [limit_app]

    modules = discover_models_modules(Path.cwd())
    apps = [module.split(".", 1)[0] for module in modules if module != "aerich.models"]
    if not apps:
        typer.echo("No apps with models.py were discovered.", err=True)
        raise typer.Exit(1)
    return sorted(set(apps))


def _write_orm_config(apps: list[str]) -> None:
    lines = [
        "ORM = {",
        "    'connections': {'default': 'sqlite://db.sqlite3'},",
        "    'apps': {",
    ]
    for app_name in apps:
        lines.append(
            "        "
            + repr(app_name)
            + ": {'models': ["
            + repr(f"{app_name}.models")
            + ", 'aerich.models'], 'default_connection': 'default'},"
        )
    lines.extend(["    }", "}"])
    Path("orm_config.py").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _aerich_config_path(app_name: str) -> Path:
    return _AERICH_CONFIG_DIR / f"{app_name}.toml"


def _ensure_aerich_config(app_name: str) -> Path:
    _AERICH_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_path = _aerich_config_path(app_name)
    config_path.write_text(
        "\n".join(
            [
                "[tool.aerich]",
                'tortoise_orm = "orm_config.ORM"',
                f'location = "{app_name}/migrations"',
                'src_folder = "."',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return config_path


def _ensure_app_migrations_package(app_name: str) -> None:
    migrations_dir = Path(app_name) / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    init_file = migrations_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("\n", encoding="utf-8")


def _aerich_state_dir(app_name: str) -> Path:
    return Path(app_name) / "migrations" / app_name



def _aerich_invocation() -> list[str]:
    aerich_bin = shutil.which("aerich")
    if aerich_bin is not None:
        return [aerich_bin]
    return [sys.executable, "-m", "aerich.cli"]


def _run_aerich(config_path: Path, app_name: str, args: list[str]) -> None:
    _run_command([*_aerich_invocation(), "-c", str(config_path), "--app", app_name, *args])


@app.command()
def startproject(name: str) -> None:
    base = Path.cwd() / name
    if base.exists():
        typer.echo(f"Directory {name} already exists", err=True)
        raise typer.Exit(1)

    template = Path(__file__).parent.parent / "scaffolding" / "project"
    copy_tree(template, base)

    (base / "project_name").rename(base / name)

    pattern = re.compile(r"project_name")
    for path in base.rglob("*.py"):
        content = path.read_text(encoding="utf-8")
        new_content = pattern.sub(name, content)
        path.write_text(new_content, encoding="utf-8")

    (base / "orm_config.py").write_text(
        (
            "ORM = {\n"
            "    'connections': {'default': 'sqlite://db.sqlite3'},\n"
            f"    'apps': {{{name!r}: {{'models': [{name!r} + '.models', 'aerich.models'], 'default_connection': 'default'}}}}\n"
            "}\n"
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
    _ensure_app_migrations_package(name)
    typer.echo(f"Created app {name}")


@app.command()
def runserver(host: str = "127.0.0.1", port: int = 8000, reload: bool = True) -> None:
    asgi_target = None
    cwd = Path.cwd()
    for candidate in cwd.iterdir():
        if candidate.is_dir() and (candidate / "asgi.py").exists():
            asgi_target = f"{candidate.name}.asgi:app"
            break
    if asgi_target is None:
        asgi_target = "app:app"
    cmd = ["uvicorn", asgi_target, "--host", host, "--port", str(port)]
    if reload:
        cmd.append("--reload")
    if os.getenv("FD_TEST_MODE") == "1" or os.getenv("PYTEST_CURRENT_TEST"):
        typer.echo("runserver (test mode): " + " ".join(cmd))
        raise typer.Exit(0)
    _run_command(cmd)


@app.command()
def makemigrations(
    app: str | None = typer.Option(
        None, "--app", "--app-name", help="Limit migrations to a specific app"
    ),
) -> None:
    _ensure_project_context()
    apps = _discover_target_apps(app)
    _write_orm_config(apps)

    for app_name in apps:
        _ensure_app_migrations_package(app_name)
        config_path = _ensure_aerich_config(app_name)
        if not _aerich_state_dir(app_name).exists():
            _run_aerich(config_path, app_name, ["init-db"])
        _run_aerich(config_path, app_name, ["migrate", "--no-input"])


@app.command()
def migrate(
    app: str | None = typer.Option(
        None, "--app", "--app-name", help="Limit migration upgrade to a specific app"
    ),
) -> None:
    _ensure_project_context()
    apps = _discover_target_apps(app)
    for app_name in apps:
        config_path = _ensure_aerich_config(app_name)
        if not _aerich_state_dir(app_name).exists():
            typer.echo(
                f"Migration state not initialized for app {app_name!r}. Run makemigrations first.",
                err=True,
            )
            raise typer.Exit(1)
        _run_aerich(config_path, app_name, ["upgrade"])


@app.command()
def shell() -> None:
    _run_command(["ipython"])


@app.command()
def createsuperuser(
    email: str = typer.Option(...),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    models: str | None = typer.Option(
        None, help="Dotted path to app models module (e.g. myapp.models)"
    ),
) -> None:
    """Create a superuser in the first discoverable User model."""
    target_model = None
    cwd = Path.cwd()
    env_models = models or os.getenv("FD_APP_MODELS")
    if env_models:
        try:
            module = __import__(env_models, fromlist=["User"])
        except ModuleNotFoundError as exc:
            if exc.name != env_models:
                raise
        else:
            target_model = getattr(module, "User", None)

    candidate_name = None
    for candidate in cwd.iterdir():
        if candidate.is_dir() and (candidate / "models.py").exists():
            module_path = f"{candidate.name}.models"
            try:
                module = __import__(module_path, fromlist=["User"])
            except ModuleNotFoundError as exc:
                if exc.name != module_path:
                    raise
                continue
            target_model = getattr(module, "User", None)
            if target_model is not None:
                candidate_name = candidate.name
                break

    if target_model is None:
        typer.echo("No User model found in current project.", err=True)
        raise typer.Exit(1)

    from tortoise import Tortoise, run_async  # noqa: PLC0415

    models_module = env_models or (f"{candidate_name}.models" if candidate_name else None)

    async def _create() -> None:
        await Tortoise.init(
            config={
                "connections": {"default": "sqlite://db.sqlite3"},
                "apps": {
                    "models": {
                        "models": [models_module or "app.models", "aerich.models"],
                        "default_connection": "default",
                    }
                },
            }
        )
        pwd = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)
        try:
            await target_model.get(email=email)
            typer.echo("User already exists", err=True)
        except DoesNotExist:
            await target_model.create(email=email, is_active=True, password=pwd, is_superuser=True)
            typer.echo("Superuser created")

        if getattr(Tortoise, "_inited", False):
            await Tortoise.close_connections()

    run_async(_create())
