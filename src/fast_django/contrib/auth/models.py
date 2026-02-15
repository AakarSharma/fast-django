from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from passlib.context import CryptContext
from tortoise import fields
from tortoise.fields.relational import ForeignKeyRelation, ManyToManyRelation
from tortoise.models import Model

_PASSWORD_CONTEXT = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class ContentType(Model):
    id = fields.IntField(pk=True)
    app_label = fields.CharField(max_length=100)
    model = fields.CharField(max_length=100)

    class Meta:
        table = "django_content_type"
        unique_together = (("app_label", "model"),)


class Permission(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    content_type: ForeignKeyRelation[ContentType] = fields.ForeignKeyField(
        "auth.ContentType", on_delete=fields.CASCADE
    )
    codename = fields.CharField(max_length=100)

    class Meta:
        table = "auth_permission"
        unique_together = (("content_type", "codename"),)


class Group(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=150, unique=True)
    permissions: ManyToManyRelation[Permission] = fields.ManyToManyField(
        "auth.Permission",
        through="auth_group_permissions",
        related_name="group_set",
    )

    class Meta:
        table = "auth_group"


class User(Model):
    id = fields.IntField(pk=True)
    password = fields.CharField(max_length=128)
    last_login = fields.DatetimeField(null=True)
    is_superuser = fields.BooleanField(default=False)
    username = fields.CharField(max_length=150, unique=True)
    first_name = fields.CharField(max_length=150, default="")
    last_name = fields.CharField(max_length=150, default="")
    email = fields.CharField(max_length=254, default="")
    is_staff = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    date_joined = fields.DatetimeField(default=lambda: datetime.now(UTC))
    groups: ManyToManyRelation[Group] = fields.ManyToManyField(
        "auth.Group",
        through="auth_user_groups",
        related_name="user_set",
    )
    user_permissions: ManyToManyRelation[Permission] = fields.ManyToManyField(
        "auth.Permission",
        through="auth_user_user_permissions",
        related_name="user_set",
    )

    class Meta:
        table = "auth_user"

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def set_password(self, raw_password: str) -> None:
        self.password = _PASSWORD_CONTEXT.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return bool(_PASSWORD_CONTEXT.verify(raw_password, self.password))

    async def get_user_permissions(self) -> set[str]:
        permissions = await self.user_permissions.all().prefetch_related("content_type")
        return {
            f"{permission.content_type.app_label}.{permission.codename}"
            for permission in permissions
            if permission.content_type is not None
        }

    async def get_group_permissions(self) -> set[str]:
        groups = await self.groups.all().prefetch_related("permissions__content_type")
        result: set[str] = set()
        for group in groups:
            for permission in await group.permissions.all().prefetch_related("content_type"):
                if permission.content_type is None:
                    continue
                result.add(f"{permission.content_type.app_label}.{permission.codename}")
        return result

    async def get_all_permissions(self) -> set[str]:
        if not self.is_active:
            return set()
        if self.is_superuser:
            permissions = await Permission.all().prefetch_related("content_type")
            return {
                f"{permission.content_type.app_label}.{permission.codename}"
                for permission in permissions
                if permission.content_type is not None
            }
        return (await self.get_user_permissions()) | (await self.get_group_permissions())

    async def has_perm(self, perm: str, obj: Any | None = None) -> bool:
        del obj
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        return perm in (await self.get_all_permissions())

    async def has_module_perms(self, app_label: str) -> bool:
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        return any(perm.startswith(f"{app_label}.") for perm in await self.get_all_permissions())


class Session(Model):
    session_key = fields.CharField(max_length=40, pk=True)
    session_data = fields.TextField()
    expire_date = fields.DatetimeField(index=True)

    class Meta:
        table = "django_session"


class AnonymousUser:
    is_authenticated = False
    is_anonymous = True
    is_active = False
    is_staff = False
    is_superuser = False
    username = ""

    async def has_perm(self, perm: str, obj: Any | None = None) -> bool:
        del perm, obj
        return False

    async def has_module_perms(self, app_label: str) -> bool:
        del app_label
        return False


__all__ = [
    "AnonymousUser",
    "ContentType",
    "Group",
    "Permission",
    "Session",
    "User",
]
