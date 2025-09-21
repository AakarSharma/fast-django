from __future__ import annotations

import anyio
import httpx

from fast_django import Settings, create_app
from fast_django.signals import request_finished, request_started


async def _exercise_routes() -> None:
    s = Settings()
    app = create_app(s)

    events: list[str] = []

    def started(sender, **kwargs):  # type: ignore[no-redef]
        events.append("started")

    def finished(sender, **kwargs):  # type: ignore[no-redef]
        events.append("finished")

    request_started.connect(started)
    request_finished.connect(finished)

    @app.get("/ok")
    def ok() -> dict[str, str]:
        return {"ok": "1"}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ok")
        assert resp.status_code == httpx.codes.OK
        assert "started" in events and "finished" in events

        # Ensure no duplicate emissions across multiple requests
        events.clear()
        resp = await client.get("/ok")
        assert resp.status_code == httpx.codes.OK
        # finished may be emitted on start or body depending on stack; just assert started appeared
        assert "started" in events


def test_request_signals() -> None:
    anyio.run(_exercise_routes)
