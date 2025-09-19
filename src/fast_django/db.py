from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from tortoise import Tortoise

from .settings import Settings


def build_tortoise_config(settings: Settings) -> dict[str, Any]:
    if settings.orm.apps:
        return {
            "connections": settings.orm.connections,
            "apps": settings.orm.apps,
        }

    # default app config - users can extend via settings
    return {
        "connections": settings.orm.connections,
        "apps": {
            "models": {
                "models": settings.orm.models,
                "default_connection": "default",
            }
        },
    }


def init_db(app: FastAPI, settings: Settings) -> None:
    config = build_tortoise_config(settings)

    @app.on_event("startup")
    async def init_orm() -> None:
        await Tortoise.init(config=config)

    @app.on_event("shutdown")
    async def close_orm() -> None:
        await Tortoise.close_connections()


