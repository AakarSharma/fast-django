from __future__ import annotations

from fastapi import FastAPI

from .admin import try_call_admin_hooks
from .apps import include_app_routers
from .db import init_db
from .signals import SignalsMiddleware  # ensure signals module imports and middleware available
from .settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings()  # loads from env/.env
    app = FastAPI(title=app_settings.app_name)

    # Built-in signals middleware (emits request_started/request_finished/got_request_exception)
    app.add_middleware(SignalsMiddleware)

    # Middleware by dotted path
    for dotted in app_settings.middleware:
        module_path, cls_name = dotted.rsplit(".", 1)
        module = __import__(module_path, fromlist=[cls_name])
        middleware_cls = getattr(module, cls_name)
        app.add_middleware(middleware_cls)

    # DB
    init_db(app, app_settings)

    # Include routers from installed apps
    if app_settings.installed_apps:
        include_app_routers(app, app_settings.installed_apps)

    if app_settings.admin_enabled:
        try_call_admin_hooks(app, app_settings)

    return app


