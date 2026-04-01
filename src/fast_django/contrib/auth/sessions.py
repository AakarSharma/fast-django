from __future__ import annotations

import hashlib
import hmac
import json
from base64 import urlsafe_b64decode, urlsafe_b64encode
from collections.abc import Awaitable, Callable, MutableMapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from typing import Any, Literal

from fastapi import Request, Response

from .models import AnonymousUser, Session, User


@dataclass(slots=True)
class SessionSettings:
    secret_key: str
    cookie_name: str
    max_age_seconds: int
    secure: bool
    httponly: bool
    samesite: Literal["lax", "strict", "none"]


def _sign(data: str, secret_key: str) -> str:
    digest = hmac.new(secret_key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest


def _encode_payload(payload: dict[str, Any], secret_key: str) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    encoded = urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")
    signature = _sign(encoded, secret_key)
    return f"{encoded}:{signature}"


def _decode_payload(value: str, secret_key: str) -> dict[str, Any] | None:
    if ":" not in value:
        return None
    encoded, signature = value.rsplit(":", 1)
    expected = _sign(encoded, secret_key)
    if not hmac.compare_digest(signature, expected):
        return None
    try:
        decoded = urlsafe_b64decode(encoded.encode("ascii")).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None
    try:
        payload = json.loads(decoded)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


async def create_user_session(user: User, settings: SessionSettings) -> str:
    expires_at = datetime.now(UTC) + timedelta(seconds=settings.max_age_seconds)
    session_key = token_urlsafe(30)[:40]
    payload = {
        "_auth_user_id": str(user.id),
        "_auth_user_backend": "fast_django.contrib.auth.backends.ModelBackend",
        "_auth_user_hash": hashlib.sha256(user.password.encode("utf-8")).hexdigest(),
    }
    encoded = _encode_payload(payload, settings.secret_key)
    await Session.create(session_key=session_key, session_data=encoded, expire_date=expires_at)
    return session_key


async def destroy_user_session(session_key: str | None) -> None:
    if not session_key:
        return
    await Session.filter(session_key=session_key).delete()


async def get_user_from_session(
    session_key: str | None, settings: SessionSettings
) -> User | AnonymousUser:
    user = await _resolve_user_from_session(session_key, settings)
    if user is None:
        return AnonymousUser()
    return user


async def _resolve_user_from_session(  # noqa: PLR0911
    session_key: str | None, settings: SessionSettings
) -> User | None:
    if not session_key:
        return None
    session = await Session.get_or_none(session_key=session_key)
    if session is None:
        return None
    now = datetime.utcnow() if session.expire_date.tzinfo is None else datetime.now(UTC)
    if session.expire_date <= now:
        await session.delete()
        return None

    payload = _decode_payload(session.session_data, settings.secret_key)
    if payload is None:
        return None

    user_id = payload.get("_auth_user_id")
    if isinstance(user_id, int):
        parsed_user_id = user_id
    elif isinstance(user_id, str) and user_id.isdigit():
        parsed_user_id = int(user_id)
    else:
        return None
    user = await User.get_or_none(id=parsed_user_id)
    if user is None or not user.is_active:
        return None

    expected_hash = hashlib.sha256(user.password.encode("utf-8")).hexdigest()
    if payload.get("_auth_user_hash") != expected_hash:
        return None

    return user


async def authenticate(username: str, password: str) -> User | None:
    user = await User.get_or_none(username=username)
    if user is None or not user.is_active:
        return None
    if not user.check_password(password):
        return None
    user.last_login = datetime.now(UTC)
    await user.save(update_fields=["last_login"])
    return user


async def login(response: Response, user: User, settings: SessionSettings) -> str:
    session_key = await create_user_session(user, settings)
    response.set_cookie(
        key=settings.cookie_name,
        value=session_key,
        max_age=settings.max_age_seconds,
        httponly=settings.httponly,
        secure=settings.secure,
        samesite=settings.samesite,
    )
    return session_key


async def logout(request: Request, response: Response, settings: SessionSettings) -> None:
    await destroy_user_session(request.cookies.get(settings.cookie_name))
    response.delete_cookie(settings.cookie_name)


class SessionAuthenticationMiddleware:
    def __init__(
        self,
        app: Callable[
            [
                MutableMapping[str, Any],
                Callable[[], Awaitable[MutableMapping[str, Any]]],
                Callable[[MutableMapping[str, Any]], Awaitable[None]],
            ],
            Awaitable[None],
        ],
        settings: SessionSettings,
    ) -> None:
        self.app = app
        self.settings = settings

    async def __call__(
        self,
        scope: MutableMapping[str, Any],
        receive: Callable[[], Awaitable[MutableMapping[str, Any]]],
        send: Callable[[MutableMapping[str, Any]], Awaitable[None]],
    ) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        headers = {k.decode("latin1"): v.decode("latin1") for k, v in scope.get("headers", [])}
        cookie_header = headers.get("cookie", "")
        session_key = None
        for cookie in cookie_header.split(";"):
            part = cookie.strip()
            if not part or "=" not in part:
                continue
            name, value = part.split("=", 1)
            if name == self.settings.cookie_name:
                session_key = value
                break

        user = await get_user_from_session(session_key, self.settings)
        state = scope.setdefault("state", {})
        state["user"] = user
        await self.app(scope, receive, send)


def get_request_user(request: Request) -> User | AnonymousUser:
    user = getattr(request.state, "user", None)
    if user is None:
        return AnonymousUser()
    if isinstance(user, User):
        return user
    return AnonymousUser()


__all__ = [
    "SessionAuthenticationMiddleware",
    "SessionSettings",
    "authenticate",
    "create_user_session",
    "destroy_user_session",
    "get_request_user",
    "get_user_from_session",
    "login",
    "logout",
]
