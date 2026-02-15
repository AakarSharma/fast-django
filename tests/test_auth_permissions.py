from __future__ import annotations

import anyio

from fast_django import Settings, create_app
from fast_django.contrib.auth.models import Group, Permission, User
from fast_django.contrib.auth.permissions import sync_content_types_and_permissions
from fast_django.orm import Tortoise


async def _exercise_permissions() -> None:
    settings = Settings()
    settings.orm.connections = {"default": "sqlite://:memory:"}
    app = create_app(settings)
    await app.router.startup()
    await Tortoise.generate_schemas(safe=True)
    await sync_content_types_and_permissions()

    permission_codenames = set(
        await Permission.filter(content_type__app_label="auth", content_type__model="user").values_list(
            "codename", flat=True
        )
    )
    assert {"add_user", "change_user", "delete_user", "view_user"}.issubset(permission_codenames)

    can_view_user = await Permission.get(
        content_type__app_label="auth", content_type__model="user", codename="view_user"
    )

    group = await Group.create(name="editors")
    await group.permissions.add(can_view_user)

    user = User(username="alice", email="alice@example.com", is_staff=False, is_superuser=False)
    user.set_password("secret")
    await user.save()
    await user.groups.add(group)

    assert await user.has_perm("auth.view_user") is True
    assert await user.has_module_perms("auth") is True

    user.is_active = False
    await user.save(update_fields=["is_active"])
    assert await user.has_perm("auth.view_user") is False

    await app.router.shutdown()


def test_permissions_sync_and_user_group_resolution() -> None:
    anyio.run(_exercise_permissions)
