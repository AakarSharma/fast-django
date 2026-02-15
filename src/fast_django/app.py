from __future__ import annotations

from fastapi import FastAPI

from .admin import AdminSite, try_call_admin_hooks
from .apps import include_app_routers
from .contrib.auth import SessionAuthenticationMiddleware, SessionSettings
from .db import init_db
from .settings import Settings
from .signals import SignalsMiddleware  # ensure signals module imports and middleware available


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings()  # loads from env/.env
    app = FastAPI(title=app_settings.app_name)

    # Built-in signals middleware (emits request_started/request_finished/got_request_exception)
    app.add_middleware(SignalsMiddleware)

    if app_settings.auth_enabled:
        app.add_middleware(
            SessionAuthenticationMiddleware,
            settings=SessionSettings(
                secret_key=app_settings.secret_key,
                cookie_name=app_settings.session_cookie_name,
                max_age_seconds=app_settings.session_age_seconds,
                secure=app_settings.session_cookie_secure,
                httponly=app_settings.session_cookie_httponly,
                samesite=app_settings.session_cookie_samesite,
            ),
        )

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
        hooks_called = try_call_admin_hooks(app, app_settings)
        if not hooks_called:
            AdminSite(title="Admin").mount(app, app_settings)

    return app
