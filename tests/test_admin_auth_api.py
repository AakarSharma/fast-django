from __future__ import annotations

import anyio
import httpx

from fast_django import Settings, create_app
from fast_django.contrib.auth.models import Group, Permission, User
from fast_django.contrib.auth.permissions import sync_content_types_and_permissions
from fast_django.contrib.auth.sessions import SessionSettings, create_user_session
from fast_django.orm import Tortoise


async def _exercise_admin_auth_api() -> None:
    settings = Settings()
    settings.orm.connections = {"default": "sqlite://:memory:"}
    settings.installed_apps = ["fast_django.scaffolding.project.project_name"]

    app = create_app(settings)
    await app.router.startup()
    await Tortoise.generate_schemas(safe=True)
    await sync_content_types_and_permissions()

    superuser = User(
        username="admin",
        email="admin@example.com",
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )
    superuser.set_password("secret")
    await superuser.save()

    normal_user = User(username="bob", email="bob@example.com", is_active=True)
    normal_user.set_password("secret")
    await normal_user.save()
    staff_user = User(username="staff", email="staff@example.com", is_active=True, is_staff=False)
    staff_user.set_password("secret")
    await staff_user.save()

    group = await Group.create(name="managers")
    permission = await Permission.get(
        content_type__app_label="auth", content_type__model="user", codename="change_user"
    )

    session_settings = SessionSettings(
        secret_key=settings.secret_key,
        cookie_name=settings.session_cookie_name,
        max_age_seconds=settings.session_age_seconds,
        secure=settings.session_cookie_secure,
        httponly=settings.session_cookie_httponly,
        samesite=settings.session_cookie_samesite,
    )
    session_key = await create_user_session(superuser, session_settings)
    staff_session_key = await create_user_session(staff_user, session_settings)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        unauthorized = await client.get("/admin/api/auth/users")
        assert unauthorized.status_code == httpx.codes.UNAUTHORIZED

        users = await client.get(
            "/admin/api/auth/users", cookies={settings.session_cookie_name: session_key}
        )
        assert users.status_code == httpx.codes.OK
        assert any(item["username"] == "admin" for item in users.json())

        groups = await client.get(
            "/admin/api/auth/groups", cookies={settings.session_cookie_name: session_key}
        )
        assert groups.status_code == httpx.codes.OK
        assert any(item["name"] == "managers" for item in groups.json())

        permissions = await client.get(
            "/admin/api/auth/permissions", cookies={settings.session_cookie_name: session_key}
        )
        assert permissions.status_code == httpx.codes.OK
        assert any(item["codename"] == "change_user" for item in permissions.json())

        forbidden = await client.get(
            "/admin/api/auth/groups", cookies={settings.session_cookie_name: staff_session_key}
        )
        assert forbidden.status_code == httpx.codes.FORBIDDEN

        assign_group = await client.post(
            f"/admin/api/auth/users/{normal_user.id}/groups/{group.id}",
            cookies={settings.session_cookie_name: session_key},
        )
        assert assign_group.status_code == httpx.codes.OK

        assign_user_permission = await client.post(
            f"/admin/api/auth/users/{normal_user.id}/permissions/{permission.id}",
            cookies={settings.session_cookie_name: session_key},
        )
        assert assign_user_permission.status_code == httpx.codes.OK

        assign_group_permission = await client.post(
            f"/admin/api/auth/groups/{group.id}/permissions/{permission.id}",
            cookies={settings.session_cookie_name: session_key},
        )
        assert assign_group_permission.status_code == httpx.codes.OK

        missing_user = await client.post(
            "/admin/api/auth/users/999999/groups/999999",
            cookies={settings.session_cookie_name: session_key},
        )
        assert missing_user.status_code == httpx.codes.NOT_FOUND

        missing_permission = await client.post(
            f"/admin/api/auth/groups/{group.id}/permissions/999999",
            cookies={settings.session_cookie_name: session_key},
        )
        assert missing_permission.status_code == httpx.codes.NOT_FOUND

    await app.router.shutdown()


def test_admin_auth_management_api() -> None:
    anyio.run(_exercise_admin_auth_api)
