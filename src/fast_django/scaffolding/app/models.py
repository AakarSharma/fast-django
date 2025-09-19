from __future__ import annotations

from tortoise import fields
from tortoise.models import Model


class Example(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)


