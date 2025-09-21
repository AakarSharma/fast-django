from __future__ import annotations

import anyio

from fast_django.signals import AsyncSignal


def test_async_signal_connect_disconnect_and_sync_receiver() -> None:
    sig = AsyncSignal("x")
    seen: list[int] = []

    def r(sender, **kw):  # type: ignore[no-redef]
        seen.append(1)

    sig.connect(r)

    async def run() -> None:
        await sig.send(sender=None)

    anyio.run(run)
    assert seen == [1]

    sig.disconnect(r)

    async def run2() -> None:
        await sig.send(sender=None)

    anyio.run(run2)
    assert seen == [1]


def test_async_signal_async_receiver() -> None:
    sig = AsyncSignal("y")
    seen: list[str] = []

    async def r(sender, **kw):  # type: ignore[no-redef]
        seen.append("ok")

    sig.connect(r)

    async def run() -> None:
        await sig.send(sender=None)

    anyio.run(run)
    assert seen == ["ok"]
