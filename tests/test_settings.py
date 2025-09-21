from __future__ import annotations

from fast_django.settings import Settings


def test_settings_default() -> None:
    s = Settings()
    assert s.app_name
    assert s.tortoise.connections["default"].startswith("sqlite")
