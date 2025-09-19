from __future__ import annotations

from collections.abc import Callable
from importlib import import_module

from fastapi import FastAPI

try:
    from tortoise.models import Model
except Exception:  # pragma: no cover - only if tortoise missing in env
    class Model:  # type: ignore
        pass

from .settings import Settings


class AdminSite:
    """
    Minimal admin facade. Encapsulates admin mounting and optional model registration.
    Keeps fastapi-admin & Tortoise as internal details.
    """

    def __init__(self, title: str = "Admin") -> None:
        self.title = title
        self._mounted = False
        self._models: list[type[Model]] = []

    def mount(self, app: FastAPI, settings: Settings, path: str | None = None) -> None:
        mount_path = path or settings.admin_path
        try:
            from fastapi_admin.app import app as admin_app  # type: ignore  # noqa: PLC0415

            app.mount(mount_path, admin_app)
            self._mounted = True
        except Exception:
            placeholder = FastAPI(title=f"{self.title} placeholder")

            @placeholder.get("/")
            def _placeholder() -> dict[str, str]:
                return {"admin": "not-configured"}

            app.mount(mount_path, placeholder)
            self._mounted = True

    def register_model(self, model: type[Model]) -> None:
        self._models.append(model)
        # Note: fastapi-admin resource registration can be integrated here in future


def try_call_admin_hooks(app: FastAPI, settings: Settings) -> None:
    """
    If an installed app defines `admin.init_admin(app, settings)`, call it.
    Allows projects to wire AdminSite without exposing fastapi-admin directly.
    """
    for app_name in settings.installed_apps:
        try:
            module = import_module(f"{app_name}.admin")
        except ModuleNotFoundError:
            continue
        hook: Callable[[FastAPI, Settings], None] | None = getattr(module, "init_admin", None)
        if callable(hook):
            try:
                hook(app, settings)
            except Exception:
                continue


