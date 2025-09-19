from __future__ import annotations

from fastapi import FastAPI

from fast_django.settings import Settings


def init_admin(app: FastAPI, settings: Settings) -> None:
    try:
        from fastapi_admin.app import app as admin_app  # type: ignore  # noqa: PLC0415

        app.mount(settings.admin_path, admin_app)
    except Exception:
        # Fallback: mount a placeholder app to avoid hard dependency in tests
        placeholder = FastAPI()
        @placeholder.get("/")
        def _placeholder() -> dict[str, str]:
            return {"admin": "not-configured"}
        app.mount(settings.admin_path, placeholder)


