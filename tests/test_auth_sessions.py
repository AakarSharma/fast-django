from __future__ import annotations

import anyio
import httpx
from fastapi import Request

from fast_django import Settings, create_app
from fast_django.contrib.auth.models import User
from fast_django.contrib.auth.permissions import sync_content_types_and_permissions
from fast_django.contrib.auth.sessions import SessionSettings, create_user_session, get_request_user
from fast_django.orm import Tortoise


async def _exercise_session_auth() -> None:
    settings = Settings()
    settings.orm.connections = {"default": "sqlite://:memory:"}
    app = create_app(settings)

    @app.get("/whoami")
    async def whoami(request: Request) -> dict[str, object]:
        user = get_request_user(request)
        return {
            "authenticated": bool(getattr(user, "is_authenticated", False)),
            "username": getattr(user, "username", ""),
        }

    await app.router.startup()
    await Tortoise.generate_schemas(safe=True)
    await sync_content_types_and_permissions()

    user = User(username="session_user", email="s@example.com", is_staff=True)
    user.set_password("pw")
    await user.save()

    session_settings = SessionSettings(
        secret_key=settings.secret_key,
        cookie_name=settings.session_cookie_name,
        max_age_seconds=settings.session_age_seconds,
        secure=settings.session_cookie_secure,
        httponly=settings.session_cookie_httponly,
        samesite=settings.session_cookie_samesite,
    )
    session_key = await create_user_session(user, session_settings)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        anonymous = await client.get("/whoami")
        assert anonymous.status_code == httpx.codes.OK
        assert anonymous.json()["authenticated"] is False

        authenticated = await client.get(
            "/whoami", cookies={settings.session_cookie_name: session_key}
        )
        assert authenticated.status_code == httpx.codes.OK
        assert authenticated.json() == {"authenticated": True, "username": "session_user"}

    await app.router.shutdown()


def test_session_middleware_authenticates_request_user() -> None:
    anyio.run(_exercise_session_auth)
