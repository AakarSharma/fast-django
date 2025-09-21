from __future__ import annotations

import anyio
import httpx

from fast_django import Settings, create_app


async def _request_healthz() -> None:
    s = Settings()
    s.installed_apps = ["fast_django.scaffolding.project.project_name"]  # use template module
    app = create_app(s)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/healthz")
        assert resp.status_code == httpx.codes.OK
        assert resp.json()["status"] == "ok"


def test_app_healthz_route() -> None:
    anyio.run(_request_healthz)
