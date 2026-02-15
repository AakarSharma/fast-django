from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OrmConfig(BaseModel):
    models: list[str] = Field(
        default_factory=lambda: [
            "fast_django.contrib.auth.models",
            "fast_django.contrib.admin.models",
            "aerich.models",
        ]
    )
    connections: dict[str, Any] = Field(default_factory=lambda: {"default": "sqlite://db.sqlite3"})
    apps: dict[str, dict[str, Any]] = Field(default_factory=dict)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FD_", env_file=(".env",), case_sensitive=False)

    app_name: str = "fast-django app"
    debug: bool = False
    secret_key: str = "change-me"

    base_dir: Path = Field(default_factory=Path.cwd)
    auth_enabled: bool = True
    auth_sync_permissions_on_startup: bool = False
    session_cookie_name: str = "sessionid"
    session_cookie_secure: bool = False
    session_cookie_httponly: bool = True
    session_cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    session_age_seconds: int = 1209600
    admin_enabled: bool = True
    admin_path: str = "/admin"

    orm: OrmConfig = Field(default_factory=OrmConfig)
    installed_apps: list[str] = Field(default_factory=list)
    middleware: list[str] = Field(default_factory=list)

    # Backward-compat alias for earlier APIs/tests
    @property
    def tortoise(self) -> OrmConfig:  # pragma: no cover - compat shim
        return self.orm
