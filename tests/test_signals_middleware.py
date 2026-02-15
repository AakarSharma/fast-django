from __future__ import annotations

import anyio
import httpx
import pytest

from fast_django import Settings, create_app
from fast_django.signals import SignalsMiddleware, got_request_exception, request_finished


def test_non_http_passthrough() -> None:
    called = {"ok": False}

    async def asgi_app(scope, receive, send):  # type: ignore[no-redef]
        called["ok"] = True

    mw = SignalsMiddleware(asgi_app)

    async def run() -> None:
        scope = {"type": "websocket"}

        async def dummy_recv():
            return {}

        async def dummy_send(message):
            return None

        await mw(scope, dummy_recv, dummy_send)

    anyio.run(run)
    assert called["ok"] is True


def test_finished_receiver_exception_propagates() -> None:
    s = Settings()
    app = create_app(s)

    def r_finished(sender, **kw):  # type: ignore[no-redef]
        raise RuntimeError("receiver failure")

    request_finished.connect(r_finished)

    @app.get("/ok2")
    def ok2() -> dict[str, str]:
        return {"x": "1"}

    transport = httpx.ASGITransport(app=app)

    async def run() -> None:
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as client:
            with pytest.raises(RuntimeError, match="receiver failure"):
                await client.get("/ok2")

    try:
        anyio.run(run)
    finally:
        request_finished.disconnect(r_finished)


def test_error_receiver_exception_propagates() -> None:
    s = Settings()
    app = create_app(s)

    def r_error(sender, **kw):  # type: ignore[no-redef]
        raise RuntimeError("error receiver failure")

    got_request_exception.connect(r_error)

    @app.get("/bad")
    def bad() -> dict[str, str]:
        raise RuntimeError("boom")

    transport = httpx.ASGITransport(app=app)

    async def run() -> None:
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as client:
            with pytest.raises(RuntimeError, match="error receiver failure"):
                await client.get("/bad")

    try:
        anyio.run(run)
    finally:
        got_request_exception.disconnect(r_error)
