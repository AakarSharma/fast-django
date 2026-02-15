# Admin

Use the `AdminSite` facade to mount admin.

```python
from fast_django.admin import AdminSite
from fast_django import create_app, Settings

app = create_app(Settings())
AdminSite().mount(app, Settings())
```

## Access Control

Admin auth behavior follows Django-style flags from `auth_user`:

- `is_staff=True` is required for admin access
- `is_superuser=True` bypasses permission checks
- permissions can be granted directly or through groups

Create an admin user with:

```bash
python manage.py createsuperuser --username admin --email admin@example.com
```

## Built-in Auth Admin API (Fallback Admin App)

When `fastapi_admin` is unavailable, fast-django mounts a fallback admin app that includes auth management APIs under:

- `/admin/api/auth/users`
- `/admin/api/auth/groups`
- `/admin/api/auth/permissions`
- `/admin/api/auth/users/{user_id}/groups/{group_id}`
- `/admin/api/auth/users/{user_id}/permissions/{permission_id}`
- `/admin/api/auth/groups/{group_id}/permissions/{permission_id}`

These routes require an authenticated staff/superuser session.

## App-specific Admin Hook

In an installed app, define:

```python
from fastapi import FastAPI
from fast_django.admin import AdminSite
from fast_django.settings import Settings


def init_admin(app: FastAPI, settings: Settings) -> None:
    AdminSite(title="Admin").mount(app, settings)
```
