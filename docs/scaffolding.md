# Scaffolding

fast-django provides Django-style scaffolding via `startproject` and `startapp`.

## Project Scaffolding

```bash
fast-django startproject myproject
```

Generated structure:

```text
myproject/
├── manage.py
├── orm_config.py
└── myproject/
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    ├── models.py
    └── admin.py
```

## App Scaffolding

```bash
fast-django startapp myapp
```

Generated structure:

```text
myapp/
├── __init__.py
├── models.py
├── routes.py
├── views.py
├── admin.py
└── migrations/
    └── __init__.py
```

## Migration Layout

- `makemigrations` discovers app modules with `models.py`.
- Aerich config files are created under `.fast_django/aerich/`.
- Migration files are kept in app-local `migrations/` directories.

## Template Paths

- Project templates: `src/fast_django/scaffolding/project/`
- App templates: `src/fast_django/scaffolding/app/`
