from __future__ import annotations

from importlib import import_module

from fastapi import APIRouter, FastAPI


def include_app_routers(app: FastAPI, app_names: list[str]) -> None:
    for name in app_names:
        for mod in ("urls", "routes", "api", "views"):
            try:
                module = import_module(f"{name}.{mod}")
            except ModuleNotFoundError:
                continue
            router = getattr(module, "router", None)
            if isinstance(router, APIRouter):
                app.include_router(router)
                break


