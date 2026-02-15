from __future__ import annotations

from fast_django.contrib.auth.password_validation import validate_password


def test_validate_password_warns_for_common_short_numeric_password() -> None:
    warnings = validate_password("123456", username="admin", email="admin@example.com")
    assert "This password is too short. It must contain at least 8 characters." in warnings
    assert "This password is entirely numeric." in warnings
    assert "This password is too common." in warnings


def test_validate_password_accepts_strong_password() -> None:
    warnings = validate_password("A-very-strong-password-42", username="admin", email="admin@example.com")
    assert warnings == []
