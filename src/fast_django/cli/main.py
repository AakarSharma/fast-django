from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import typer
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist

from fast_django.contrib.auth import sync_content_types_and_permissions, validate_password
from fast_django.contrib.auth.models import User
from fast_django.utils import discover_models_modules

app = typer.Typer(help="fast-django CLI")

_AERICH_CONFIG_DIR = Path(".fast_django") / "aerich"
_BUILTIN_AUTH_APP = "auth"
_BUILTIN_AUTH_ALIAS = "auth"
_BUILTIN_AUTH_MODELS = [
    "fast_django.contrib.auth.models",
    "fast_django.contrib.admin.models",
    "aerich.models",
]


def copy_tree(src: Path, dst: Path) -> None:
    if not dst.exists():
        dst.mkdir(parents=True)
    for root, _dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        target_root = dst / rel
        target_root.mkdir(parents=True, exist_ok=True)
        for name in files:
            shutil.copy2(Path(root) / name, target_root / name)


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


def _normalize_app_name(app_name: str) -> str:
    return _BUILTIN_AUTH_APP if app_name == _BUILTIN_AUTH_ALIAS else app_name


def _is_builtin_auth_app(app_name: str) -> bool:
    return _normalize_app_name(app_name) == _BUILTIN_AUTH_APP


def _discover_target_apps(limit_app: str | None) -> list[str]:
    if limit_app is not None:
        app_name = _normalize_app_name(limit_app)
        if _is_builtin_auth_app(app_name):
            return [_BUILTIN_AUTH_APP]
        app_dir = Path(app_name)
        if not app_dir.is_dir() or not (app_dir / "models.py").exists():
            typer.echo(f"App {limit_app!r} was not found or has no models.py", err=True)
            raise typer.Exit(1)
        return [app_name]

    modules = discover_models_modules(Path.cwd())
    apps = sorted({module.split(".", 1)[0] for module in modules if module != "aerich.models"})
    if _BUILTIN_AUTH_APP not in apps:
        apps.append(_BUILTIN_AUTH_APP)
    return apps


def _models_for_app(app_name: str) -> list[str]:
    if _is_builtin_auth_app(app_name):
        return _BUILTIN_AUTH_MODELS
    return [f"{app_name}.models", "aerich.models"]


def _orm_config_text(apps: list[str]) -> str:
    lines = [
        "ORM = {",
        "    'connections': {'default': 'sqlite://db.sqlite3'},",
        "    'apps': {",
    ]
    for app_name in apps:
        lines.append(
            "        "
            + repr(app_name)
            + ": {'models': "
            + repr(_models_for_app(app_name))
            + ", 'default_connection': 'default'},"
        )
    lines.extend(["    }", "}"])
    return "\n".join(lines) + "\n"


def _write_orm_config(apps: list[str], path: Path | None = None) -> None:
    target = path or Path("orm_config.py")
    target.write_text(_orm_config_text(apps), encoding="utf-8")


def _migration_location(app_name: str) -> Path:
    if _is_builtin_auth_app(app_name):
        return Path(".fast_django") / "migrations" / _BUILTIN_AUTH_ALIAS
    return Path(app_name) / "migrations"


def _aerich_config_path(app_name: str) -> Path:
    normalized = _normalize_app_name(app_name)
    return _AERICH_CONFIG_DIR / f"{normalized}.toml"


def _ensure_aerich_config(app_name: str) -> Path:
    normalized = _normalize_app_name(app_name)
    _AERICH_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_path = _aerich_config_path(normalized)
    location = _migration_location(normalized)
    config_path.write_text(
        "\n".join(
            [
                "[tool.aerich]",
                'tortoise_orm = "orm_config.ORM"',
                f'location = "{location.as_posix()}"',
                'src_folder = "."',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return config_path


def _ensure_app_migrations_package(app_name: str) -> None:
    normalized = _normalize_app_name(app_name)
    location = _migration_location(normalized)
    location.mkdir(parents=True, exist_ok=True)
    init_file = location / "__init__.py"
    if not init_file.exists():
        init_file.write_text("\n", encoding="utf-8")


def _aerich_state_dir(app_name: str) -> Path:
    normalized = _normalize_app_name(app_name)
    return _migration_location(normalized) / normalized


def _aerich_invocation() -> list[str]:
    aerich_bin = shutil.which("aerich")
    if aerich_bin is not None:
        return [aerich_bin]
    return [sys.executable, "-m", "aerich.cli"]


def _run_aerich(config_path: Path, app_name: str, args: list[str]) -> None:
    normalized = _normalize_app_name(app_name)
    _run_command([*_aerich_invocation(), "-c", str(config_path), "--app", normalized, *args])


def _load_orm_config_module() -> ModuleType:
    config_path = Path("orm_config.py")
    if not config_path.exists():
        typer.echo("Missing orm_config.py. Run makemigrations first.", err=True)
        raise typer.Exit(1)
    spec = importlib.util.spec_from_file_location("fast_django_orm_config", config_path)
    if spec is None or spec.loader is None:
        typer.echo("Unable to load orm_config.py", err=True)
        raise typer.Exit(1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sync_permissions_from_orm_config() -> None:
    module = _load_orm_config_module()
    orm_config = module.ORM

    from tortoise import Tortoise, run_async  # noqa: PLC0415

    async def _sync() -> None:
        await Tortoise.init(config=orm_config)
        await sync_content_types_and_permissions()
        await Tortoise.close_connections()

    run_async(_sync())


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

    _write_orm_config([name, _BUILTIN_AUTH_APP], base / "orm_config.py")

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
    _write_orm_config(apps)
    for app_name in apps:
        config_path = _ensure_aerich_config(app_name)
        if not _aerich_state_dir(app_name).exists():
            typer.echo(
                f"Migration state not initialized for app {app_name!r}. Run makemigrations first.",
                err=True,
            )
            raise typer.Exit(1)
        _run_aerich(config_path, app_name, ["upgrade"])

    if app is None or _is_builtin_auth_app(app):
        _sync_permissions_from_orm_config()


@app.command()
def syncpermissions() -> None:
    """Create default content types and model permissions."""
    _ensure_project_context()
    _sync_permissions_from_orm_config()


@app.command()
def shell() -> None:
    _run_command(["ipython"])


@app.command()
def createsuperuser(
    username: str | None = typer.Option(None),
    email: str = typer.Option(""),
    password: str = typer.Option("", prompt=True, hide_input=True, confirmation_prompt=True),
    models: str | None = typer.Option(
        None, help="Dotted path to app models module (e.g. myapp.models)"
    ),
) -> None:
    """Create a Django-style superuser in the built-in auth model by default."""

    if models is not None:
        _create_superuser_custom_model(models=models, email=email, password=password)
        return

    if username is None or username == "":
        username = typer.prompt("Username", default="", show_default=False).strip()
        if not username:
            typer.echo("--username is required for the built-in auth user model.", err=True)
            raise typer.Exit(1)

    warnings = validate_password(password, username=username, email=email)
    if warnings:
        typer.echo("Password validation warnings:", err=True)
        for warning in warnings:
            typer.echo(f" - {warning}", err=True)
        if not typer.confirm("Bypass password validation and create superuser anyway?", default=False):
            raise typer.Exit(1)

    from tortoise import Tortoise, run_async  # noqa: PLC0415

    async def _create() -> None:
        module = _load_orm_config_module()
        orm_config = module.ORM
        await Tortoise.init(config=orm_config)

        existing = await User.get_or_none(username=username)
        if existing is not None:
            typer.echo("User already exists", err=True)
            await Tortoise.close_connections()
            return

        user = User(
            username=username,
            email=email,
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        user.set_password(password)
        await user.save()
        typer.echo("Superuser created")
        await Tortoise.close_connections()

    run_async(_create())


def _create_superuser_custom_model(models: str, email: str, password: str) -> None:
    target_model = None
    try:
        module = __import__(models, fromlist=["User"])
    except ModuleNotFoundError as exc:
        root_module = models.split(".", 1)[0]
        if exc.name not in {models, root_module}:
            raise
    else:
        target_model = getattr(module, "User", None)

    if target_model is None:
        typer.echo("No User model found for the supplied --models module.", err=True)
        raise typer.Exit(1)

    from tortoise import Tortoise, run_async  # noqa: PLC0415

    async def _create() -> None:
        await Tortoise.init(
            config={
                "connections": {"default": "sqlite://db.sqlite3"},
                "apps": {
                    "models": {
                        "models": [models, "aerich.models"],
                        "default_connection": "default",
                    }
                },
            }
        )
        pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto").hash(password)
        try:
            await target_model.get(email=email)
            typer.echo("User already exists", err=True)
        except DoesNotExist:
            await target_model.create(email=email, is_active=True, password=pwd, is_superuser=True)
            typer.echo("Superuser created")

        if Tortoise._inited:
            await Tortoise.close_connections()

    run_async(_create())
