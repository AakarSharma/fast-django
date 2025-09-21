from __future__ import annotations

from typing import Any, Callable, Iterable, List

import inspect


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
        self._receivers: List[Receiver] = []

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
                await result  # type: ignore[no-any-return]


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

    def __init__(self, app: Callable[..., Any]):
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Callable[..., Any], send: Callable[..., Any]) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        # Emit request_started best-effort
        try:
            await request_started.send(sender=self, scope=scope)
        except Exception:
            # Do not break the request because of receivers
            pass

        finished_emitted = {"v": False}

        async def send_wrapper(message: dict[str, Any]) -> None:
            mtype = message.get("type")
            if mtype == "http.response.start" and not finished_emitted["v"]:
                try:
                    await request_finished.send(sender=self, scope=scope, message=message)
                except Exception:
                    pass
                finally:
                    finished_emitted["v"] = True
            elif mtype == "http.response.body" and not finished_emitted["v"]:
                # Fallback: some stacks may not expose start; emit on first body
                try:
                    await request_finished.send(sender=self, scope=scope, message=message)
                except Exception:
                    pass
                finally:
                    finished_emitted["v"] = True
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:  # noqa: BLE001 - propagate after emitting
            try:
                await got_request_exception.send(sender=self, scope=scope, exception=exc)
            except Exception:
                pass
            raise


_patched = False
_orig_save: Callable[..., Any] | None = None
_orig_delete: Callable[..., Any] | None = None


def _is_created(instance: Any) -> bool:
    # Best-effort: before first save, `pk` is None in Tortoise
    try:
        pk = getattr(instance, "pk")
        return pk is None
    except Exception:
        return False


def _patch_tortoise_model_methods() -> None:
    global _patched, _orig_save, _orig_delete
    if _patched:
        return
    try:
        from tortoise.models import Model  # local import to avoid hard dependency at import time
    except Exception:
        return

    if getattr(Model.save, "__fast_django_patched__", False) is True:  # type: ignore[attr-defined]
        _patched = True
        return

    _orig_save = Model.save
    _orig_delete = Model.delete

    async def _fd_save(self: Any, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        created = _is_created(self)
        try:
            await pre_save.send(sender=self.__class__, instance=self, created=created)
        except Exception:
            pass
        result = await _orig_save(self, *args, **kwargs)  # type: ignore[misc]
        try:
            await post_save.send(sender=self.__class__, instance=self, created=created)
        except Exception:
            pass
        return result

    async def _fd_delete(self: Any, *args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        try:
            await pre_delete.send(sender=self.__class__, instance=self)
        except Exception:
            pass
        result = await _orig_delete(self, *args, **kwargs)  # type: ignore[misc]
        try:
            await post_delete.send(sender=self.__class__, instance=self)
        except Exception:
            pass
        return result

    setattr(_fd_save, "__fast_django_patched__", True)
    setattr(_fd_delete, "__fast_django_patched__", True)
    Model.save = _fd_save  # type: ignore[assignment]
    Model.delete = _fd_delete  # type: ignore[assignment]
    _patched = True


# Apply the ORM patches eagerly so signals work even without FastAPI app
_patch_tortoise_model_methods()


__all__ = [
    "AsyncSignal",
    "SignalsMiddleware",
    "request_started",
    "request_finished",
    "got_request_exception",
    "pre_save",
    "post_save",
    "pre_delete",
    "post_delete",
]


