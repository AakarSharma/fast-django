# Getting Started

This guide will walk you through setting up your first fast-django project and understanding the core concepts.

## Installation

Install fast-django using pip:

```bash
pip install fast-django-asgi
```

For development with documentation support:

```bash
pip install "fast-django[docs]"
```

## Creating Your First Project

### 1. Start a New Project

```bash
fast-django startproject mysite
cd mysite
```

This creates a new project with the following structure:

```
mysite/
├── manage.py              # Django-style management script
├── orm_config.py          # Auto-generated ORM configuration
├── aerich.ini            # Aerich migration configuration
└── mysite/               # Project package
    ├── __init__.py
    ├── asgi.py           # ASGI application entry point
    ├── settings.py       # Project settings
    ├── urls.py           # Main URL routing
    ├── models.py         # Project-level models
    └── admin.py          # Admin configuration
```

### 2. Understanding the Project Structure

#### `manage.py`
The main entry point for CLI commands, similar to Django's manage.py:

```python
#!/usr/bin/env python3
from fast_django.cli.main import app

if __name__ == "__main__":
    app()
```

#### `settings.py`
Your project's configuration file:

```python
from fast_django.settings import Settings, OrmConfig

class Settings(Settings):
    app_name: str = "mysite"
    debug: bool = True
    orm: OrmConfig = OrmConfig(models=["mysite.models", "aerich.models"])
    installed_apps: list[str] = ["mysite"]
```

#### `asgi.py`
The ASGI application entry point:

```python
from mysite.settings import Settings
from fast_django import create_app

settings = Settings()
app = create_app(settings)
```

### 3. Running the Development Server

```bash
python manage.py runserver
```

This starts the development server on `http://127.0.0.1:8000` with auto-reload enabled.

Visit `http://127.0.0.1:8000/docs` to see the automatic API documentation.

## Creating Your First App

### 1. Generate an App

```bash
fast-django startapp blog
```

This creates a new app with the following structure:

```
blog/
├── __init__.py
├── models.py      # App models
├── urls.py        # API routes (primary)
├── views.py       # View functions
├── admin.py       # Admin configuration
└── migrations/    # Database migrations
    └── __init__.py
```

### 2. Add the App to Settings

Update `mysite/settings.py`:

```python
class Settings(Settings):
    app_name: str = "mysite"
    debug: bool = True
    orm: OrmConfig = OrmConfig(
        models=["mysite.models", "blog.models", "aerich.models"]
    )
    installed_apps: list[str] = ["mysite", "blog"]
```

### 3. Define Models

In `blog/models.py`:

```python
from fast_django.orm import Model, fields

class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
```

### 4. Create API Routes

In `blog/routes.py`:

```python
from fast_django.routers import APIRouter
from .models import Post

router = APIRouter()

@router.get("/posts")
async def list_posts():
    posts = await Post.all()
    return [{"id": post.id, "title": post.title} for post in posts]

@router.post("/posts")
async def create_post(title: str, content: str):
    post = await Post.create(title=title, content=content)
    return {"id": post.id, "title": post.title}
```

## Database Management

### Migrations

fast-django uses Aerich for database migrations with automatic discovery:

```bash
# Create migrations for all apps
python manage.py makemigrations

# Create migrations for a specific app
python manage.py makemigrations --app blog

# Apply migrations
python manage.py migrate
```

### Database Configuration

Configure your database in `settings.py`:

```python
class Settings(Settings):
    orm: OrmConfig = OrmConfig(
        connections={
            "default": "sqlite://db.sqlite3",  # SQLite
            # "default": "postgres://user:pass@localhost/db",  # PostgreSQL
            # "default": "mysql://user:pass@localhost/db",     # MySQL
        },
        models=["mysite.models", "blog.models", "aerich.models"]
    )
```

## Admin Interface

The admin interface is automatically mounted when enabled in settings:

```python
class Settings(Settings):
    admin_enabled: bool = True
    admin_path: str = "/admin"
```

Access the admin at `http://127.0.0.1:8000/admin`.

### Custom Admin Configuration

Create `blog/admin.py`:

```python
from fastapi import FastAPI
from fast_django.admin import AdminSite
from fast_django.settings import Settings

def init_admin(app: FastAPI, settings: Settings) -> None:
    site = AdminSite(title="Blog Admin")
    site.mount(app, settings)
    # Register models here when model registration is implemented
```

## Environment Configuration

fast-django supports environment variables with the `FD_` prefix:

```bash
# .env file
FD_DEBUG=true
FD_APP_NAME="My Awesome App"
FD_SECRET_KEY="your-secret-key-here"
FD_ADMIN_ENABLED=true
```

## Next Steps

- Learn about [ORM and Models](orm.md)
- Explore [Routing and Views](routing.md)
- Set up [Middleware](middleware.md)
- Configure [Settings](settings.md)
- Check out [Examples](examples.md)
