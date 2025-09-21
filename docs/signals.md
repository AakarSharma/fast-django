# Signals

fast-django includes Django-like signals for request lifecycle and ORM events.

## Request signals

Dispatched by built-in `SignalsMiddleware` (enabled by default via `create_app`):

- `request_started(sender, scope)`
- `request_finished(sender, scope, message)`
- `got_request_exception(sender, scope, exception)`

Receivers can be sync or async.

Example:

```python
from fast_django.signals import request_started, request_finished

async def on_started(sender, scope, **_):
    ...

def on_finished(sender, scope, message, **_):
    ...

request_started.connect(on_started)
request_finished.connect(on_finished)
```

## ORM signals

Patched onto Tortoise `Model.save()` / `Model.delete()` at import time:

- `pre_save(sender, instance, created)`
- `post_save(sender, instance, created)`
- `pre_delete(sender, instance)`
- `post_delete(sender, instance)`

`created` is inferred by checking if `instance.pk` is `None` before save.

Example:

```python
from fast_django.signals import post_save

async def on_post_save(sender, instance, created, **_):
    if created:
        print("created:", instance)

post_save.connect(on_post_save)
```

## Notes

- Custom middleware in `Settings.middleware` is added after the built-in `SignalsMiddleware`.
- Receivers should be lightweight; offload heavy work to background tasks.
