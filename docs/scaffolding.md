# Scaffolding

fast-django provides a comprehensive scaffolding system that generates project and app structures, similar to Django's `startproject` and `startapp` commands.

## Project Scaffolding

### Creating a New Project

```bash
fast-django startproject myproject
```

This command creates a complete project structure with all necessary files:

```
myproject/
├── manage.py              # CLI entry point
├── orm_config.py          # Database configuration
├── aerich.ini            # Migration configuration
└── myproject/            # Project package
    ├── __init__.py
    ├── asgi.py           # ASGI application
    ├── settings.py       # Project settings
    ├── urls.py           # Main routing
    ├── models.py         # Project models
    └── admin.py          # Admin configuration
```

### Generated Files

#### `manage.py`
The main CLI entry point:

```python
#!/usr/bin/env python3
from fast_django.cli.main import app

if __name__ == "__main__":
    app()
```

#### `asgi.py`
ASGI application entry point:

```python
from myproject.settings import Settings
from fast_django import create_app

settings = Settings()
app = create_app(settings)
```

#### `settings.py`
Project configuration:

```python
from fast_django.settings import Settings, OrmConfig

class Settings(Settings):
    app_name: str = "myproject"
    debug: bool = True
    orm: OrmConfig = OrmConfig(models=["myproject.models", "aerich.models"])
    installed_apps: list[str] = ["myproject"]
```

#### `urls.py`
Main routing configuration:

```python
from fast_django.routers import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Welcome to MyProject"}

@router.get("/health")
def health():
    return {"status": "healthy"}
```

#### `models.py`
Project-level models:

```python
from fast_django.orm import Model, fields

class Example(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
```

#### `admin.py`
Admin configuration:

```python
from fastapi import FastAPI
from fast_django.admin import AdminSite
from fast_django.settings import Settings

def init_admin(app: FastAPI, settings: Settings) -> None:
    site = AdminSite(title="Admin")
    site.mount(app, settings)
```

## App Scaffolding

### Creating a New App

```bash
fast-django startapp myapp
```

This creates an app structure within your project:

```
myapp/
├── __init__.py
├── models.py         # App models
├── routes.py         # API routes
├── views.py          # View functions
├── admin.py          # Admin configuration
└── migrations/       # Database migrations
    └── __init__.py
```

### Generated App Files

#### `models.py`
App models template:

```python
from fast_django.orm import Model, fields

class Example(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
```

#### `routes.py`
API routes template:

```python
from fast_django.routers import APIRouter

router = APIRouter()

@router.get("/")
def index():
    return {"message": "Hello from myapp"}
```

#### `views.py`
View functions template:

```python
from fast_django.routers import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}
```

#### `admin.py`
Admin configuration template:

```python
from fastapi import FastAPI
from fast_django.admin import AdminSite
from fast_django.settings import Settings

def init_admin(app: FastAPI, settings: Settings) -> None:
    site = AdminSite(title="MyApp Admin")
    site.mount(app, settings)
```

## Customizing Scaffolding

### Project Templates

You can customize the project scaffolding by modifying the templates in `src/fast_django/scaffolding/project/`:

```
scaffolding/
└── project/
    ├── manage.py
    └── project_name/
        ├── __init__.py
        ├── asgi.py
        ├── settings.py
        ├── urls.py
        ├── models.py
        └── admin.py
```

### App Templates

App templates are located in `src/fast_django/scaffolding/app/`:

```
scaffolding/
└── app/
    ├── __init__.py
    ├── models.py
    ├── routes.py
    ├── views.py
    └── admin.py
```

### Template Variables

Templates use `project_name` as a placeholder that gets replaced with the actual project name:

```python
# In template files
class Settings(Settings):
    app_name: str = "project_name"

# After generation
class Settings(Settings):
    app_name: str = "myproject"
```

## Advanced Usage

### Custom Project Structure

You can create custom project templates by:

1. Copying the default templates
2. Modifying the structure
3. Updating the CLI command to use your templates

```python
# Custom startproject command
@app.command()
def startproject_custom(name: str) -> None:
    base = Path.cwd() / name
    if base.exists():
        typer.echo(f"Directory {name} already exists", err=True)
        raise typer.Exit(1)

    # Use custom template directory
    template = Path(__file__).parent.parent / "custom_scaffolding" / "project"
    copy_tree(template, base)

    # Replace placeholders
    pattern = re.compile(r"project_name")
    for path in base.rglob("*.py"):
        content = path.read_text(encoding="utf-8")
        new_content = pattern.sub(name, content)
        path.write_text(new_content, encoding="utf-8")
```

### Custom App Structure

Similarly, you can create custom app templates:

```python
@app.command()
def startapp_custom(name: str) -> None:
    base = Path.cwd() / name
    if base.exists():
        typer.echo(f"App {name} already exists", err=True)
        raise typer.Exit(1)

    # Use custom app template
    template = Path(__file__).parent.parent / "custom_scaffolding" / "app"
    copy_tree(template, base)
```

## Integration with Settings

### Auto-Discovery

When you create an app, you need to add it to your project's `installed_apps`:

```python
# In myproject/settings.py
class Settings(Settings):
    installed_apps: list[str] = ["myproject", "myapp"]
    orm: OrmConfig = OrmConfig(
        models=["myproject.models", "myapp.models", "aerich.models"]
    )
```

### Database Configuration

The scaffolding system automatically generates `orm_config.py` for database configuration:

```python
# Generated orm_config.py
ORM = {
    'connections': {'default': 'sqlite://db.sqlite3'},
    'apps': {
        'models': {
            'models': ['myproject.models', 'myapp.models', 'aerich.models'],
            'default_connection': 'default'
        }
    }
}
```

## Best Practices

1. **Use descriptive names** for projects and apps
2. **Follow naming conventions** (lowercase, underscores)
3. **Add apps to installed_apps** after creation
4. **Update ORM models** list when adding new apps
5. **Customize templates** for your organization's needs
6. **Version control** your custom templates
7. **Document** any custom scaffolding modifications

## Troubleshooting

### Common Issues

1. **"Directory already exists"**
   - Choose a different name or remove the existing directory
   - Check for hidden files that might prevent creation

2. **"Permission denied"**
   - Ensure you have write permissions in the target directory
   - Run with appropriate user permissions

3. **"Template not found"**
   - Verify the scaffolding templates exist
   - Check the fast-django installation

4. **"Import errors after generation"**
   - Ensure all dependencies are installed
   - Check that the project structure is correct

### Debugging

```bash
# Check if fast-django is properly installed
pip show fast-django

# Verify CLI commands work
fast-django --help

# Check template files exist
ls -la $(python -c "import fast_django; print(fast_django.__file__)")/../scaffolding/
```

## Examples

### Complete Project Setup

```bash
# Create project
fast-django startproject myblog
cd myblog

# Create apps
fast-django startapp blog
fast-django startapp users
fast-django startapp comments

# Update settings
# Edit myblog/settings.py to include new apps

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Custom App Template

Create a custom app template with additional files:

```
custom_scaffolding/
└── app/
    ├── __init__.py
    ├── models.py
    ├── routes.py
    ├── views.py
    ├── admin.py
    ├── serializers.py    # Custom file
    ├── permissions.py    # Custom file
    └── tests.py          # Custom file
```

This allows you to generate apps with your organization's standard structure and files.
