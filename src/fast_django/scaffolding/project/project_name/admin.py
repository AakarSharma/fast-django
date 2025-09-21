from __future__ import annotations

from importlib import import_module

from fastapi import FastAPI

from fast_django.settings import Settings


def init_admin(app: FastAPI, settings: Settings) -> None:
    try:
        module = import_module("fastapi_admin.app")
        app.mount(settings.admin_path, module.app)
    except Exception:
        # Fallback: mount a placeholder app to avoid hard dependency in tests
        placeholder = FastAPI()

        @placeholder.get("/")
        def _placeholder() -> dict[str, str]:
            return {"admin": "not-configured"}

        app.mount(settings.admin_path, placeholder)
