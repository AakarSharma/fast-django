from __future__ import annotations

from pydantic import Field

from fast_django.settings import OrmConfig, Settings as BaseSettings


class Settings(BaseSettings):
    app_name: str = "project_name"
    debug: bool = True
    orm: OrmConfig = OrmConfig(
        models=[
            "fast_django.contrib.auth.models",
            "fast_django.contrib.admin.models",
            "project_name.models",
            "aerich.models",
        ]
    )
    installed_apps: list[str] = Field(default_factory=lambda: ["project_name"])
