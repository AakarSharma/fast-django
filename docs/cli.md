# CLI

fast-django provides a command-line interface with Django-style `manage.py` commands.

## Available Commands

### Project Management

#### `startproject <name>`
Creates a new fast-django project.

```bash
fast-django startproject mysite
```

What it creates:
- Project directory structure
- `manage.py` script
- `asgi.py` ASGI application entry point
- `settings.py` with base configuration
- `orm_config.py` for database configuration

#### `startapp <name>`
Creates a new app.

```bash
fast-django startapp blog
```

What it creates:
- App directory structure
- `models.py` for database models
- `urls.py` for API routes
- `views.py` for view functions
- `admin.py` for admin configuration
- `migrations/` package for database migrations

### Development Server

#### `runserver [options]`
Starts the development server with auto-reload.

```bash
python manage.py runserver
python manage.py runserver --host 0.0.0.0 --port 8080
python manage.py runserver --no-reload
```

Options:
- `--host`: Host to bind to (default: `127.0.0.1`)
- `--port`: Port to bind to (default: `8000`)
- `--reload` / `--no-reload`

### Database Management

#### `makemigrations [--app <app_name>]`
Creates database migrations for model changes.

```bash
python manage.py makemigrations
python manage.py makemigrations --app blog
```

Features:
- Auto-discovers apps with `models.py`
- Regenerates `orm_config.py` for discovered apps
- Uses app-scoped Aerich configs under `.fast_django/aerich/`
- Writes migration files under app-local `migrations/` directories

#### `migrate [--app <app_name>]`
Applies pending database migrations.

```bash
python manage.py migrate
python manage.py migrate --app blog
```

### User Management

#### `createsuperuser`
Creates a superuser account for admin access.

```bash
python manage.py createsuperuser --email admin@example.com --password secret123
```

Options:
- `--email`: required
- `--password`: prompted if not provided
- `--models`: optional dotted models module

### Development Tools

#### `shell`
Opens IPython.

```bash
python manage.py shell
```

## Using `fast-django` directly

```bash
fast-django startproject mysite
fast-django startapp blog
fast-django runserver
```

## Environment Variables

- `FD_TEST_MODE=1`: test mode for non-blocking `runserver`
- `FD_APP_MODELS`: models module override for `createsuperuser`
- `PYTEST_CURRENT_TEST`: auto-detected test mode

## Troubleshooting

1. `Run inside a project directory`
- Ensure the command runs from a directory containing `pyproject.toml` or `manage.py`.

2. `Migration state not initialized`
- Run `python manage.py makemigrations` first for the app.

3. Admin route unavailable
- Ensure `admin_enabled=True`
- Ensure `fastapi-admin` is installed

## Help

```bash
python manage.py --help
python manage.py runserver --help
python manage.py makemigrations --help
```
