# Getting Started

This tutorial walks through a full Django-like flow in fast-django: project scaffolding, app creation,
app-local migrations, auth/session tables, superuser creation, and admin startup.

## 1. Install

```bash
uv tool install fast-django
```

For local package development:

```bash
uv sync --all-extras
```

## 2. Create a Project

```bash
fast-django startproject mysite
cd mysite
```

Generated structure:

```text
mysite/
├── manage.py
├── orm_config.py
└── mysite/
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    ├── models.py
    └── admin.py
```

## 3. Create an App

```bash
fast-django startapp blog
```

Generated structure:

```text
blog/
├── __init__.py
├── models.py
├── urls.py
├── views.py
├── admin.py
└── migrations/
    └── __init__.py
```

## 4. Register the App in Settings

Edit `mysite/settings.py`:

```python
class Settings(Settings):
    app_name: str = "mysite"
    debug: bool = True
    orm: OrmConfig = OrmConfig(
        models=[
            "fast_django.contrib.auth.models",
            "fast_django.contrib.admin.models",
            "mysite.models",
            "blog.models",
            "aerich.models",
        ]
    )
    installed_apps: list[str] = ["mysite", "blog"]
```

## 5. Create and Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

Behavior:

- app migrations are stored under `<app>/migrations/`
- built-in auth/admin migrations are stored under `.fast_django/migrations/auth/`
- default permissions (`add`, `change`, `delete`, `view`) are synced on `migrate`

For scoped workflows, pair commands by app:

```bash
python manage.py makemigrations --app blog
python manage.py migrate --app blog
```

You can resync permissions explicitly:

```bash
python manage.py syncpermissions
```

## 6. Create a Superuser

```bash
python manage.py createsuperuser --username admin --email admin@example.com
```

The command prompts for password and confirmation. Weak passwords trigger warnings, with an explicit bypass prompt.
Created superusers are marked `is_staff=True` and `is_superuser=True`.

## 7. Run the Server

```bash
python manage.py runserver
```

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/admin`

## 8. Validate Django-Compatible Auth Tables

After migrations, expected tables include:

- `auth_user`
- `auth_group`
- `auth_permission`
- `auth_user_groups`
- `auth_user_user_permissions`
- `auth_group_permissions`
- `django_content_type`
- `django_session`
- `django_admin_log`
