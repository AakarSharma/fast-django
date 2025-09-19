# CLI API Reference

This page provides detailed API documentation for fast-django's command-line interface.

## Main CLI App

### `app`

```python
app = typer.Typer(help="fast-django CLI")
```

Main Typer CLI application instance.

## Commands

### `startproject`

```python
@app.command()
def startproject(name: str) -> None
```

Creates a new fast-django project.

**Parameters:**
- `name` (str): Project name.

**What it creates:**
- Project directory structure
- `manage.py` script
- `asgi.py` ASGI application
- `settings.py` configuration
- `orm_config.py` database config
- `aerich.ini` migration config

**Example:**
```bash
fast-django startproject myapp
```

### `startapp`

```python
@app.command()
def startapp(name: str) -> None
```

Creates a new app within the current project.

**Parameters:**
- `name` (str): App name.

**What it creates:**
- App directory structure
- `models.py` for database models
- `routes.py` for API routes
- `views.py` for view functions
- `admin.py` for admin config
- `migrations/` directory

**Example:**
```bash
fast-django startapp blog
```

### `runserver`

```python
@app.command()
def runserver(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True
) -> None
```

Starts the development server.

**Parameters:**
- `host` (str): Host to bind to. Default: "127.0.0.1"
- `port` (int): Port to bind to. Default: 8000
- `reload` (bool): Enable auto-reload. Default: True

**Example:**
```bash
fast-django runserver --host 0.0.0.0 --port 8080
```

### `makemigrations`

```python
@app.command()
def makemigrations(
    app_name: str | None = typer.Option(None, help="Limit migrations to given app directory")
) -> None
```

Creates database migrations.

**Parameters:**
- `app_name` (str, optional): Specific app to migrate.

**Features:**
- Auto-discovers apps with `models.py`
- Generates `orm_config.py` if missing
- Creates migration files in app directories
- Uses Aerich for migration generation

**Example:**
```bash
fast-django makemigrations
fast-django makemigrations --app blog
```

### `migrate`

```python
@app.command()
def migrate() -> None
```

Applies pending database migrations.

**What it does:**
- Applies all pending migrations
- Updates database schema
- Uses Aerich for execution

**Example:**
```bash
fast-django migrate
```

### `shell`

```python
@app.command()
def shell() -> None
```

Opens an interactive Python shell.

**Features:**
- Uses IPython if available
- Pre-loads project context
- Useful for debugging

**Example:**
```bash
fast-django shell
```

### `createsuperuser`

```python
@app.command()
def createsuperuser(
    email: str = typer.Option(...),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    models: str | None = typer.Option(None, help="Dotted path to app models module")
) -> None
```

Creates a superuser account.

**Parameters:**
- `email` (str): Email address (required).
- `password` (str): Password (prompted if not provided).
- `models` (str, optional): Models module path.

**Auto-discovery:**
- Finds User models in project
- Searches for `User` class in app models
- Uses `FD_APP_MODELS` environment variable

**Example:**
```bash
fast-django createsuperuser --email admin@example.com
```

## Utility Functions

### `_write_aerich_ini`

```python
def _write_aerich_ini(location: Path) -> None
```

Writes Aerich configuration file.

**Parameters:**
- `location` (Path): Directory for migrations.

### `copy_tree`

```python
def copy_tree(src: Path, dst: Path) -> None
```

Copies directory tree recursively.

**Parameters:**
- `src` (Path): Source directory.
- `dst` (Path): Destination directory.

## Environment Variables

### `FD_TEST_MODE`

```bash
FD_TEST_MODE=1
```

Enables test mode for CLI commands.

### `FD_APP_MODELS`

```bash
FD_APP_MODELS=myapp.models
```

Specifies models module for createsuperuser.

### `PYTEST_CURRENT_TEST`

```bash
PYTEST_CURRENT_TEST=test_function
```

Automatically detected for test mode.

## Error Handling

### Common Exceptions

#### `typer.Exit(1)`

Raised when:
- Directory already exists
- Project directory not found
- Invalid configuration

#### `subprocess.CalledProcessError`

Raised when:
- External command fails
- Database connection error
- Migration errors

## Examples

### Complete Project Setup

```bash
# Create project
fast-django startproject myblog
cd myblog

# Create apps
fast-django startapp blog
fast-django startapp users

# Database setup
fast-django makemigrations
fast-django migrate

# Create superuser
fast-django createsuperuser --email admin@example.com

# Start development
fast-django runserver
```

### Development Workflow

```bash
# Make model changes
# Edit models.py files

# Create migrations
fast-django makemigrations --app blog

# Apply migrations
fast-django migrate

# Test in shell
fast-django shell

# Run server
fast-django runserver --reload
```

### Production Commands

```bash
# Disable reload for production
fast-django runserver --no-reload --host 0.0.0.0 --port 80

# Create migrations for specific app
fast-django makemigrations --app users

# Apply all migrations
fast-django migrate
```

## Troubleshooting

### Common Issues

1. **"Directory already exists"**
   - Choose different name
   - Remove existing directory

2. **"Run inside a project directory"**
   - Ensure `pyproject.toml` exists
   - Run from project root

3. **"No User model found"**
   - Create User model in app
   - Set `FD_APP_MODELS` environment variable

4. **"Migration errors"**
   - Check model imports
   - Verify `orm_config.py` is up to date
   - Try recreating migrations

### Debug Commands

```bash
# Show help
fast-django --help
fast-django runserver --help

# Check project structure
ls -la
cat pyproject.toml

# Verify database config
cat orm_config.py
cat aerich.ini
```
