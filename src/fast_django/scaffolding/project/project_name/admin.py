from __future__ import annotations

from importlib import import_module

from fastapi import FastAPI

from fast_django.settings import Settings


def init_admin(app: FastAPI, settings: Settings) -> None:
    try:
        module = import_module("fastapi_admin.app")
    except ModuleNotFoundError:
        placeholder = FastAPI()

        @placeholder.get("/")
        def _placeholder() -> dict[str, str]:
            return {"admin": "not-configured"}

        app.mount(settings.admin_path, placeholder)
        return

    app.mount(settings.admin_path, module.app)
