from __future__ import annotations

from collections.abc import Callable
from importlib import import_module

from fastapi import FastAPI

try:
    from tortoise.models import Model
except ImportError:  # pragma: no cover - only if tortoise missing in env

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
            module = import_module("fastapi_admin.app")
        except ModuleNotFoundError:
            placeholder = FastAPI(title=f"{self.title} placeholder")

            @placeholder.get("/")
            def _placeholder() -> dict[str, str]:
                return {"admin": "not-configured"}

            app.mount(mount_path, placeholder)
            self._mounted = True
            return

        app.mount(mount_path, module.app)
        self._mounted = True

    def register_model(self, model: type[Model]) -> None:
        self._models.append(model)


def try_call_admin_hooks(app: FastAPI, settings: Settings) -> None:
    """
    If an installed app defines `admin.init_admin(app, settings)`, call it.
    Allows projects to wire AdminSite without exposing fastapi-admin directly.
    """
    for app_name in settings.installed_apps:
        try:
            module = import_module(f"{app_name}.admin")
        except ModuleNotFoundError as exc:
            if exc.name != f"{app_name}.admin":
                raise
            continue
        hook: Callable[[FastAPI, Settings], None] | None = getattr(module, "init_admin", None)
        if callable(hook):
            hook(app, settings)
