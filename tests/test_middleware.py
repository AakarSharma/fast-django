from __future__ import annotations

import anyio
import httpx

from fast_django import Settings, create_app


async def _request_with_gzip() -> None:
    s = Settings()
    s.middleware = ["fastapi.middleware.gzip.GZipMiddleware"]
    app = create_app(s)

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"pong": "ok"}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ping")
        assert resp.status_code == httpx.codes.OK


def test_middleware_add() -> None:
    anyio.run(_request_with_gzip)
