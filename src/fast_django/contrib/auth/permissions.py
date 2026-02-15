from __future__ import annotations

from collections.abc import Iterable

from tortoise import Tortoise
from tortoise.models import Model

from .models import ContentType, Permission

_DEFAULT_PERMISSION_ACTIONS = ("add", "change", "delete", "view")


def _model_identity(model: type[Model]) -> tuple[str, str]:
    module_parts = model.__module__.split(".")
    app_label = module_parts[-2] if len(module_parts) > 1 else module_parts[0]
    if model.__module__.startswith("fast_django.contrib.auth"):
        app_label = "auth"
    elif model.__module__.startswith("fast_django.contrib.admin"):
        app_label = "admin"
    model_name = model.__name__.lower()
    return app_label, model_name


def _iter_models() -> Iterable[type[Model]]:
    for app_models in Tortoise.apps.values():
        for model in app_models.values():
            if getattr(model._meta, "abstract", False):
                continue
            yield model


async def sync_content_types_and_permissions() -> None:
    for model in _iter_models():
        app_label, model_name = _model_identity(model)
        content_type, _ = await ContentType.get_or_create(app_label=app_label, model=model_name)

        for action in _DEFAULT_PERMISSION_ACTIONS:
            codename = f"{action}_{model_name}"
            name = f"Can {action} {model_name}"
            await Permission.get_or_create(
                content_type=content_type,
                codename=codename,
                defaults={"name": name},
            )


__all__ = ["sync_content_types_and_permissions"]
