# CLI

fast-django provides a comprehensive command-line interface that mirrors Django's `manage.py` commands while adding modern ASGI-specific functionality.

## Available Commands

### Project Management

#### `startproject <name>`
Creates a new fast-django project with the specified name.

```bash
fast-django startproject mysite
```

**What it creates:**
- Project directory structure
- `manage.py` script
- `asgi.py` ASGI application entry point
- `settings.py` with basic configuration
- `orm_config.py` for database configuration
- `aerich.ini` for migration management

#### `startapp <name>`
Creates a new app within the current project.

```bash
fast-django startapp blog
```

**What it creates:**
- App directory structure
- `models.py` for database models
- `urls.py` for API routes
- `views.py` for view functions
- `admin.py` for admin configuration
- `migrations/` directory for database migrations

### Development Server

#### `runserver [options]`
Starts the development server with auto-reload.

```bash
# Basic usage
python manage.py runserver

# Custom host and port
python manage.py runserver --host 0.0.0.0 --port 8080

# Disable auto-reload
python manage.py runserver --no-reload
```

**Options:**
- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to bind to (default: 8000)
- `--reload`: Enable auto-reload (default: True)
- `--no-reload`: Disable auto-reload

### Database Management

#### `makemigrations [--app <app_name>]`
Creates database migrations for model changes.

```bash
# Create migrations for all apps
python manage.py makemigrations

# Create migrations for specific app
python manage.py makemigrations --app blog
```

**Features:**
- Auto-discovers apps with `models.py` files
- Generates `orm_config.py` if it doesn't exist
- Creates migration files in app-specific `migrations/` directories
- Uses Aerich for migration generation

#### `migrate`
Applies pending database migrations.

```bash
python manage.py migrate
```

**What it does:**
- Applies all pending migrations
- Updates database schema
- Uses Aerich for migration execution

### User Management

#### `createsuperuser`
Creates a superuser account for admin access.

```bash
python manage.py createsuperuser --email admin@example.com --password secret123
```

**Options:**
- `--email`: Email address for the superuser (required)
- `--password`: Password for the superuser (prompted if not provided)
- `--models`: Specify models module path (optional)

**Auto-discovery:**
- Automatically finds User models in your project
- Searches for `User` class in app models
- Uses environment variable `FD_APP_MODELS` if set

### Development Tools

#### `shell`
Opens an interactive Python shell with your project context.

```bash
python manage.py shell
```

**Features:**
- Uses IPython if available
- Pre-loads your project models and settings
- Useful for debugging and data exploration

## Command Line Interface

### Using `fast-django` directly

You can run commands directly with the `fast-django` command:

```bash
fast-django startproject mysite
fast-django startapp blog
fast-django runserver
```

### Using `manage.py`

The traditional Django-style approach:

```bash
python manage.py startproject mysite
python manage.py startapp blog
python manage.py runserver
```

## Environment Variables

Several commands respect environment variables:

- `FD_TEST_MODE=1`: Enables test mode (useful for CI/CD)
- `FD_APP_MODELS`: Specifies the models module for createsuperuser
- `PYTEST_CURRENT_TEST`: Automatically detected for test mode

## Examples

### Complete Project Setup

```bash
# Create project
fast-django startproject myblog
cd myblog

# Create blog app
fast-django startapp blog

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser --email admin@example.com

# Start development server
python manage.py runserver
```

### Development Workflow

```bash
# Make model changes in blog/models.py
# Then create migrations
python manage.py makemigrations --app blog

# Apply migrations
python manage.py migrate

# Test in shell
python manage.py shell

# Run server
python manage.py runserver
```

## Troubleshooting

### Common Issues

1. **"Run inside a project directory"**
   - Make sure you're in a directory with `pyproject.toml`
   - Run commands from the project root

2. **Migration errors**
   - Check that your models are properly imported
   - Ensure `orm_config.py` is up to date
   - Try recreating migrations with `--app` flag

3. **Admin not accessible**
   - Ensure `admin_enabled=True` in settings
   - Check that `fastapi-admin` is installed
   - Verify admin path configuration

### Getting Help

```bash
# Show help for any command
python manage.py --help
python manage.py runserver --help
python manage.py makemigrations --help
```
