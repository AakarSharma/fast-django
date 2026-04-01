from __future__ import annotations

from datetime import UTC, datetime, timedelta

import anyio
from fastapi import Request, Response

from fast_django import Settings, create_app
from fast_django.contrib.auth.models import Session, User
from fast_django.contrib.auth.sessions import (
    SessionAuthenticationMiddleware,
    SessionSettings,
    _decode_payload,
    _encode_payload,
    authenticate,
    create_user_session,
    destroy_user_session,
    get_request_user,
    get_user_from_session,
    login,
    logout,
)
from fast_django.orm import Tortoise


async def _exercise_session_helpers() -> None:
    settings = Settings()
    settings.orm.connections = {"default": "sqlite://:memory:"}
    app = create_app(settings)
    await app.router.startup()
    await Tortoise.generate_schemas(safe=True)

    session_settings = SessionSettings(
        secret_key=settings.secret_key,
        cookie_name=settings.session_cookie_name,
        max_age_seconds=settings.session_age_seconds,
        secure=settings.session_cookie_secure,
        httponly=settings.session_cookie_httponly,
        samesite=settings.session_cookie_samesite,
    )

    user = User(username="helper", email="h@example.com", is_active=True)
    user.set_password("pw")
    await user.save()

    assert _decode_payload("invalid", settings.secret_key) is None
    encoded = _encode_payload({"k": "v"}, settings.secret_key)
    assert _decode_payload(encoded + "x", settings.secret_key) is None
    assert _decode_payload(
        _encode_payload({"k": "v"}, settings.secret_key), settings.secret_key
    ) == {"k": "v"}

    key = await create_user_session(user, session_settings)
    resolved = await get_user_from_session(key, session_settings)
    assert isinstance(resolved, User)
    assert resolved.username == "helper"

    unknown = await get_user_from_session("does-not-exist", session_settings)
    assert unknown.is_authenticated is False

    broken = await Session.create(
        session_key="broken",
        session_data=_encode_payload({"_auth_user_id": "NaN"}, settings.secret_key),
        expire_date=datetime.now(UTC) + timedelta(hours=1),
    )
    broken_user = await get_user_from_session(broken.session_key, session_settings)
    assert broken_user.is_authenticated is False

    assert await authenticate("helper", "bad") is None
    ok_user = await authenticate("helper", "pw")
    assert isinstance(ok_user, User)

    response = Response()
    login_key = await login(response, user, session_settings)
    assert login_key

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [
                (b"cookie", f"{settings.session_cookie_name}={login_key}".encode("latin1"))
            ],
        }
    )
    await logout(request, response, session_settings)
    assert await Session.get_or_none(session_key=login_key) is None

    await destroy_user_session(None)

    await app.router.shutdown()


def test_session_helpers_and_auth_flow() -> None:
    anyio.run(_exercise_session_helpers)


def test_get_request_user_returns_anonymous_for_invalid_state() -> None:
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
    assert get_request_user(request).is_anonymous is True
    request.scope["state"] = {}
    request.scope["state"]["user"] = object()
    assert get_request_user(request).is_anonymous is True


def test_session_auth_middleware_non_http_passthrough() -> None:
    called = {"v": False}

    async def app(scope, receive, send):  # type: ignore[no-untyped-def]
        called["v"] = True

    middleware = SessionAuthenticationMiddleware(
        app,
        SessionSettings(
            secret_key="x",
            cookie_name="sessionid",
            max_age_seconds=60,
            secure=False,
            httponly=True,
            samesite="lax",
        ),
    )

    async def run() -> None:
        async def recv():
            return {}

        async def send(msg):
            return None

        await middleware({"type": "websocket"}, recv, send)

    anyio.run(run)
    assert called["v"] is True
