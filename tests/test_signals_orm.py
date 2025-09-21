from __future__ import annotations

import anyio

from fast_django import Settings, create_app
from fast_django.orm import Tortoise
from fast_django.scaffolding.project.project_name.models import User
from fast_django.signals import post_delete, post_save, pre_delete, pre_save


async def _exercise_orm() -> None:
    # Ensure app bootstraps ORM
    s = Settings()
    s.installed_apps = ["fast_django.scaffolding.project.project_name"]
    s.orm.models = [
        "fast_django.scaffolding.project.project_name.models",
        "aerich.models",
    ]
    app = create_app(s)
    # Trigger startup to init ORM and create tables
    await app.router.startup()
    await Tortoise.generate_schemas()

    events: list[str] = []

    def on_pre_save(sender, **kwargs):
        if kwargs.get("created"):
            events.append("pre_create")
        else:
            events.append("pre_update")

    def on_post_save(sender, **kwargs):
        if kwargs.get("created"):
            events.append("post_create")
        else:
            events.append("post_update")

    def on_pre_delete(sender, **kwargs):
        events.append("pre_delete")

    def on_post_delete(sender, **kwargs):
        events.append("post_delete")

    pre_save.connect(on_pre_save)
    post_save.connect(on_post_save)
    pre_delete.connect(on_pre_delete)
    post_delete.connect(on_post_delete)

    # Create
    u = User(email="a@example.com")
    await u.save()
    assert "pre_create" in events and "post_create" in events

    events.clear()
    # Update
    u.is_active = False
    await u.save()
    assert "pre_update" in events and "post_update" in events

    events.clear()
    # Delete
    await u.delete()
    assert "pre_delete" in events and "post_delete" in events

    # Cleanly shutdown
    await app.router.shutdown()


def test_orm_signals() -> None:
    anyio.run(_exercise_orm)
