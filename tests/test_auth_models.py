from __future__ import annotations

import anyio

from fast_django import Settings, create_app
from fast_django.contrib.admin.models import LogEntry
from fast_django.contrib.auth.models import ContentType, Group, Permission, Session, User
from fast_django.contrib.auth.permissions import sync_content_types_and_permissions
from fast_django.orm import Tortoise


async def _create_auth_schema() -> set[str]:
    settings = Settings()
    settings.orm.connections = {"default": "sqlite://:memory:"}
    app = create_app(settings)
    await app.router.startup()
    await Tortoise.generate_schemas(safe=True)
    await sync_content_types_and_permissions()

    conn = Tortoise.get_connection("default")
    rows = await conn.execute_query_dict("SELECT name FROM sqlite_master WHERE type='table'")
    await app.router.shutdown()
    return {str(row["name"]) for row in rows}


def test_django_compatible_auth_table_names() -> None:
    tables = anyio.run(_create_auth_schema)
    assert "auth_user" in tables
    assert "auth_group" in tables
    assert "auth_permission" in tables
    assert "auth_group_permissions" in tables
    assert "auth_user_groups" in tables
    assert "auth_user_user_permissions" in tables
    assert "django_content_type" in tables
    assert "django_session" in tables
    assert "django_admin_log" in tables


def test_model_meta_table_names() -> None:
    assert User._meta.db_table == "auth_user"
    assert Group._meta.db_table == "auth_group"
    assert Permission._meta.db_table == "auth_permission"
    assert ContentType._meta.db_table == "django_content_type"
    assert Session._meta.db_table == "django_session"
    assert LogEntry._meta.db_table == "django_admin_log"
