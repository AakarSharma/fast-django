from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from tortoise import Tortoise

from .contrib.auth import sync_content_types_and_permissions
from .settings import Settings


def build_tortoise_config(settings: Settings) -> dict[str, Any]:
    if settings.orm.apps:
        return {
            "connections": settings.orm.connections,
            "apps": settings.orm.apps,
        }

    apps: dict[str, dict[str, Any]] = {}
    for model_module in settings.orm.models:
        if model_module.startswith("fast_django.contrib.auth") or model_module.startswith(
            "fast_django.contrib.admin"
        ):
            app_label = "auth"
        else:
            app_label = model_module.split(".", 1)[0]

        app_config = apps.setdefault(
            app_label, {"models": [], "default_connection": "default"}
        )
        if model_module not in app_config["models"]:
            app_config["models"].append(model_module)

    return {"connections": settings.orm.connections, "apps": apps}


def init_db(app: FastAPI, settings: Settings) -> None:
    config = build_tortoise_config(settings)

    @app.on_event("startup")
    async def init_orm() -> None:
        await Tortoise.init(config=config)
        if settings.auth_enabled and settings.auth_sync_permissions_on_startup:
            await sync_content_types_and_permissions()

    @app.on_event("shutdown")
    async def close_orm() -> None:
        await Tortoise.close_connections()
