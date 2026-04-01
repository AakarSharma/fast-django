# CLI

fast-django provides Django-style management commands.

## Core Commands

### `startproject <name>`
Creates a new project.

### `startapp <name>`
Creates a new app with app-local `migrations/`.

### `runserver`
Runs Uvicorn with Django-like defaults.

## Migrations

### `makemigrations [--app <app_name>]`
Generates migrations for discovered apps.

- App migrations are app-local: `<app>/migrations/`
- Built-in auth/admin migrations are managed under `.fast_django/migrations/auth/`

### `migrate [--app <app_name>]`
Applies migrations.

- Full migrate also syncs content types and default permissions.

### `syncpermissions`
Explicitly syncs content types and default model permissions.

## User Management

### `createsuperuser`
Creates a built-in auth superuser.

```bash
python manage.py createsuperuser --username admin --email admin@example.com
```

Behavior:

- prompts for password + confirmation
- validates password strength (short/common/numeric/similar checks)
- warns before creation if validation fails, with explicit bypass confirmation
- sets `is_staff=True` and `is_superuser=True`

Optional custom model flow:

```bash
python manage.py createsuperuser --models myapp.models --email admin@example.com
```

## Release Workflow

For maintainers, run the full uv-based release pipeline:

```bash
./scripts/release.sh
./scripts/release.sh patch   # or minor / major
```
