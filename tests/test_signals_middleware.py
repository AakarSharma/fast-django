from __future__ import annotations

import anyio
import httpx

from fast_django import Settings, create_app
from fast_django.signals import request_finished, request_started, got_request_exception


def test_non_http_passthrough() -> None:
    called = {"ok": False}

    async def asgi_app(scope, receive, send):  # type: ignore[no-redef]
        called["ok"] = True

    # Wrap with middleware directly
    from fast_django.signals import SignalsMiddleware

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


def test_finished_receiver_exception_and_app_exception() -> None:
    s = Settings()
    app = create_app(s)

    # Receiver that raises on finished to exercise internal except
    def r_finished(sender, **kw):  # type: ignore[no-redef]
        raise RuntimeError("receiver failure")

    # Receiver that raises on got_request_exception
    def r_error(sender, **kw):  # type: ignore[no-redef]
        raise RuntimeError("error receiver failure")

    request_finished.connect(r_finished)
    got_request_exception.connect(r_error)

    @app.get("/ok2")
    def ok2() -> dict[str, str]:
        return {"x": "1"}

    @app.get("/bad")
    def bad() -> dict[str, str]:
        raise RuntimeError("boom")

    transport = httpx.ASGITransport(app=app)
    async def run() -> None:
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as client:
            resp = await client.get("/ok2")
            assert resp.status_code == 200
            try:
                await client.get("/bad")
            except Exception:
                pass

    try:
        anyio.run(run)
    finally:
        # cleanup to avoid leaking receivers across tests
        request_finished.disconnect(r_finished)
        got_request_exception.disconnect(r_error)


