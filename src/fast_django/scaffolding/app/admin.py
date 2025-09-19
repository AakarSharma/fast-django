from __future__ import annotations

from fastapi import FastAPI

from fast_django.admin import AdminSite
from fast_django.settings import Settings


def init_admin(app: FastAPI, settings: Settings) -> None:
    site = AdminSite(title="Admin")
    site.mount(app, settings)


