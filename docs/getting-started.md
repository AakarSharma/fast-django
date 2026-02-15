# Getting Started

This guide walks through your first fast-django project.

## Installation

```bash
uv tool install fast-django
```

For repository development:

```bash
uv sync --all-extras
```

## Create a Project

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

## Create an App

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

## Add App to Settings

```python
class Settings(Settings):
    app_name: str = "mysite"
    debug: bool = True
    orm: OrmConfig = OrmConfig(models=["mysite.models", "blog.models", "aerich.models"])
    installed_apps: list[str] = ["mysite", "blog"]
```

## Migrations

```bash
python manage.py makemigrations
python manage.py makemigrations --app blog
python manage.py migrate
```

Migrations are generated per app and stored under each app's `migrations/` directory.

## Run Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/docs`.

## Admin

```python
class Settings(Settings):
    admin_enabled: bool = True
    admin_path: str = "/admin"
```

Visit `http://127.0.0.1:8000/admin`.
