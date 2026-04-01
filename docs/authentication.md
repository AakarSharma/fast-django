# Authentication

fast-django now includes Django-style auth/session/admin data models and permission behavior.

## Django-Compatible Tables

fast-django creates the same core table names used by Django:

- `auth_user`
- `auth_group`
- `auth_permission`
- `auth_user_groups`
- `auth_user_user_permissions`
- `auth_group_permissions`
- `django_content_type`
- `django_session`
- `django_admin_log`

## Default Permission Generation

Use:

```bash
python manage.py syncpermissions
```

or run full migration flow:

```bash
python manage.py makemigrations
python manage.py migrate
```

`migrate` synchronizes content types and default model permissions (`add`, `change`, `delete`, `view`).

## Session Authentication

Session middleware is enabled by default (`Settings.auth_enabled=True`).

Cookie/session defaults:

- Cookie name: `sessionid`
- Age: `1209600` seconds (2 weeks)
- HttpOnly: enabled
- SameSite: `lax`

Authentication helpers:

```python
from fast_django import authenticate, login, logout, get_request_user
```

## Superuser Creation

Built-in Django-style auth user:

```bash
python manage.py createsuperuser --username admin --email admin@example.com
```

## Permission Checks

The built-in `User` model exposes Django-like permission checks:

- `await user.has_perm("auth.change_user")`
- `await user.has_module_perms("auth")`

Group and direct user permissions are both considered.
