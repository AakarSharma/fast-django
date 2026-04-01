from __future__ import annotations

_COMMON_PASSWORDS = {
    "123456",
    "12345678",
    "123456789",
    "admin",
    "administrator",
    "password",
    "qwerty",
    "letmein",
    "welcome",
    "django",
    "fastdjango",
}
_MIN_PASSWORD_LENGTH = 8


def validate_password(
    password: str,
    *,
    username: str | None = None,
    email: str | None = None,
) -> list[str]:
    warnings: list[str] = []

    if len(password) < _MIN_PASSWORD_LENGTH:
        warnings.append(
            f"This password is too short. It must contain at least {_MIN_PASSWORD_LENGTH} characters."
        )

    if password.isdigit():
        warnings.append("This password is entirely numeric.")

    normalized_password = password.strip().lower()
    if normalized_password in _COMMON_PASSWORDS:
        warnings.append("This password is too common.")

    if username:
        normalized_username = username.strip().lower()
        if normalized_username and normalized_username in normalized_password:
            warnings.append("This password is too similar to the username.")

    if email:
        local = email.split("@", 1)[0].strip().lower()
        if local and local in normalized_password:
            warnings.append("This password is too similar to the email address.")

    return warnings


__all__ = ["validate_password"]
