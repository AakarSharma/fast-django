from __future__ import annotations

from datetime import UTC, datetime

from tortoise import fields
from tortoise.fields.relational import ForeignKeyNullableRelation, ForeignKeyRelation
from tortoise.models import Model

from fast_django.contrib.auth.models import ContentType, User


class LogEntry(Model):
    id = fields.IntField(pk=True)
    action_time = fields.DatetimeField(default=lambda: datetime.now(UTC))
    user: ForeignKeyRelation[User] = fields.ForeignKeyField("auth.User", on_delete=fields.CASCADE)
    content_type: ForeignKeyNullableRelation[ContentType] = fields.ForeignKeyField(
        "auth.ContentType", on_delete=fields.SET_NULL, null=True
    )
    object_id = fields.TextField(null=True)
    object_repr = fields.CharField(max_length=200)
    action_flag = fields.SmallIntField()
    change_message = fields.TextField()

    class Meta:
        table = "django_admin_log"


__all__ = ["LogEntry"]
