from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Iterable, MutableMapping
from contextlib import suppress
from typing import Any, cast

from tortoise.models import Model

Receiver = Callable[..., Any]


class AsyncSignal:
    """
    Minimal async-friendly signal implementation (Django-like).

    - Receivers can be async or sync callables.
    - `send()` awaits async receivers and invokes sync receivers directly.
    - Exceptions from receivers are not swallowed by default; callers may catch.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._receivers: list[Receiver] = []

    def connect(self, receiver: Receiver) -> None:
        if receiver not in self._receivers:
            self._receivers.append(receiver)

    def disconnect(self, receiver: Receiver) -> None:
        if receiver in self._receivers:
            self._receivers.remove(receiver)

    def receivers(self) -> Iterable[Receiver]:
        return tuple(self._receivers)

    async def send(self, sender: object | None = None, **kwargs: Any) -> None:
        for receiver in list(self._receivers):
            result = receiver(sender, **kwargs)
            if inspect.isawaitable(result):
                await result


# Request lifecycle signals
request_started = AsyncSignal("request_started")
request_finished = AsyncSignal("request_finished")
got_request_exception = AsyncSignal("got_request_exception")


# ORM lifecycle signals
pre_save = AsyncSignal("pre_save")
post_save = AsyncSignal("post_save")
pre_delete = AsyncSignal("pre_delete")
post_delete = AsyncSignal("post_delete")


class SignalsMiddleware:
    """
    ASGI middleware that emits request lifecycle signals.

    - request_started before handing to downstream
    - got_request_exception if downstream raises
    - request_finished when response starts
    """

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
    ):
        self.app = app

    async def __call__(
        self,
        scope: MutableMapping[str, Any],
        receive: Callable[[], Awaitable[MutableMapping[str, Any]]],
        send: Callable[[MutableMapping[str, Any]], Awaitable[None]],
    ) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        # Emit request_started best-effort
        with suppress(Exception):
            await request_started.send(sender=self, scope=scope)

        finished_emitted = {"v": False}

        async def send_wrapper(message: MutableMapping[str, Any]) -> None:
            mtype = message.get("type")
            if mtype == "http.response.start" and not finished_emitted["v"]:
                with suppress(Exception):
                    await request_finished.send(sender=self, scope=scope, message=message)
                finished_emitted["v"] = True
            elif mtype == "http.response.body" and not finished_emitted["v"]:
                # Fallback: some stacks may not expose start; emit on first body
                with suppress(Exception):
                    await request_finished.send(sender=self, scope=scope, message=message)
                finished_emitted["v"] = True
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            with suppress(Exception):
                await got_request_exception.send(sender=self, scope=scope, exception=exc)
            raise


def _is_created(instance: Any) -> bool:
    # Best-effort: before first save, `pk` is None in Tortoise
    try:
        pk = instance.pk
        return pk is None
    except Exception:
        return False


def _patch_tortoise_model_methods() -> None:
    if getattr(Model.save, "__fast_django_patched__", False) is True:
        return

    orig_save = Model.save
    orig_delete = Model.delete

    async def _fd_save(self: Any, *args: Any, **kwargs: Any) -> None:
        created = _is_created(self)
        with suppress(Exception):
            await pre_save.send(sender=self.__class__, instance=self, created=created)
        await orig_save(self, *args, **kwargs)
        with suppress(Exception):
            await post_save.send(sender=self.__class__, instance=self, created=created)

    async def _fd_delete(self: Any, *args: Any, **kwargs: Any) -> None:
        with suppress(Exception):
            await pre_delete.send(sender=self.__class__, instance=self)
        await orig_delete(self, *args, **kwargs)
        with suppress(Exception):
            await post_delete.send(sender=self.__class__, instance=self)

    cast(Any, _fd_save).__fast_django_patched__ = True
    cast(Any, _fd_delete).__fast_django_patched__ = True
    cast(Any, Model).save = _fd_save
    cast(Any, Model).delete = _fd_delete


# Apply the ORM patches eagerly so signals work even without FastAPI app
_patch_tortoise_model_methods()


__all__ = [
    "AsyncSignal",
    "SignalsMiddleware",
    "got_request_exception",
    "post_delete",
    "post_save",
    "pre_delete",
    "pre_save",
    "request_finished",
    "request_started",
]
