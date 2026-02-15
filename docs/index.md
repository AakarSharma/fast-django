# fast-django

**Django-like Developer Experience on ASGI with FastAPI, Tortoise ORM, Aerich, and FastAPI-Admin.**

fast-django brings the familiar Django development experience to modern ASGI applications, combining the power of FastAPI with Django's developer-friendly patterns.

## Quick Start

```bash
uv tool install fast-django
fast-django startproject mysite
cd mysite
python manage.py runserver
```

## Key Features

- 🚀 **FastAPI-powered**: Built on FastAPI for high performance and automatic API documentation
- 🗄️ **Tortoise ORM**: Django-like ORM with async support
- 🔧 **Django-style CLI**: Familiar `manage.py` commands for project management
- 📊 **Admin Interface**: Auto-mounting admin interface with FastAPI-Admin
- 🏗️ **Scaffolding**: Generate projects and apps with `startproject` and `startapp`
- 🔄 **Migrations**: Aerich-powered database migrations
- ⚙️ **Settings Management**: Pydantic-based settings with environment variable support
- 🛣️ **Auto-routing**: Automatic router discovery and inclusion

## Architecture

fast-django provides a clean abstraction layer that combines:

- **FastAPI** for the web framework and API layer
- **Tortoise ORM** for database operations and models
- **Aerich** for database migrations
- **FastAPI-Admin** for the admin interface
- **Pydantic** for settings and data validation

## What's Included

- **Core Application Factory**: `create_app()` function for app initialization
- **Settings System**: Environment-based configuration with `FD_` prefix
- **ORM Integration**: Re-exported Tortoise ORM components
- **CLI Tools**: Complete command-line interface for project management
- **Admin System**: Pluggable admin interface with model registration
- **Scaffolding**: Templates for projects and apps
- **Middleware Support**: Easy middleware configuration
- **Auto-discovery**: Automatic app and model discovery

## Getting Started

1. [Installation & Setup](getting-started.md)
2. [Project Structure](getting-started.md#project-structure)
3. [Creating Your First App](getting-started.md#creating-your-first-app)
4. [Database & Models](orm.md)
5. [API Routes](routing.md)
6. [Admin Interface](admin.md)

## Examples

Check out our [examples](examples.md) to see fast-django in action, including a complete blog application.
