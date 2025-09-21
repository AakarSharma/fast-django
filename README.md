<div align="center">

# fast-django

**Django-like Developer Experience on ASGI with FastAPI, Tortoise ORM, Aerich, and FastAPI-Admin**

[![PyPI version](https://badge.fury.io/py/fast-django-asgi.svg)](https://badge.fury.io/py/fast-django-asgi)
[![Python Support](https://img.shields.io/pypi/pyversions/fast-django-asgi.svg)](https://pypi.org/project/fast-django-asgi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/AakarSharma/fast-django/workflows/CI/badge.svg)](https://github.com/AakarSharma/fast-django/actions)
[![Documentation Status](https://github.com/AakarSharma/fast-django/workflows/Docs/badge.svg)](https://aakarsharma.github.io/fast-django/)

[Documentation](https://aakarsharma.github.io/fast-django/) • [Examples](https://aakarsharma.github.io/fast-django/examples/) • [API Reference](https://aakarsharma.github.io/fast-django/api/) • [Contributing](CONTRIBUTING.md)

</div>

## 🚀 What is fast-django?

fast-django brings the familiar Django development experience to modern ASGI applications, combining the power of FastAPI with Django's developer-friendly patterns. It provides a clean abstraction layer that makes building high-performance web APIs as intuitive as Django.

### ✨ Key Features

- 🏗️ **Django-style CLI** - Familiar `manage.py` commands for project management
- 🗄️ **Tortoise ORM** - Django-like ORM with async support and migrations
- 📊 **Admin Interface** - Auto-mounting admin UI with FastAPI-Admin
- ⚙️ **Pydantic Settings** - Type-safe configuration with environment variables
- 🛣️ **Auto-routing** - Automatic router discovery and inclusion
- 🔧 **Scaffolding** - Generate projects and apps with `startproject` and `startapp`
- 🚀 **FastAPI-powered** - Built on FastAPI for high performance and automatic API docs
- 🔄 **Aerich Migrations** - Database migrations with automatic discovery
- 🔔 **Signals** - Django-like request and ORM signals

## 🚀 Quick Start

### Installation

```bash
pip install fast-django-asgi
```

### Create Your First Project

```bash
# Create a new project
fast-django startproject myblog
cd myblog

# Create an app
fast-django startapp blog

# Set up the database
python manage.py makemigrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser --email admin@example.com

# Start the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see your app and `http://127.0.0.1:8000/docs` for automatic API documentation!

## 📖 Documentation

- **[Getting Started](https://aakarsharma.github.io/fast-django/getting-started/)** - Complete setup guide
- **[Core Concepts](https://aakarsharma.github.io/fast-django/routing/)** - Routing, ORM, Settings, Middleware, Signals, and more
- **[Examples](https://aakarsharma.github.io/fast-django/examples/)** - Real-world applications
- **[API Reference](https://aakarsharma.github.io/fast-django/api/)** - Complete API documentation

### Local Documentation

```bash
pip install "fast-django-asgi[docs]"
mkdocs serve
```

## 🎯 Why fast-django?

### Django Developers
If you love Django's developer experience but need the performance and modern features of FastAPI, fast-django is perfect for you. It provides:

- Familiar CLI commands (`manage.py runserver`, `makemigrations`, etc.)
- Django-style project structure and app organization
- Similar ORM patterns and database operations
- Admin interface that works like Django's admin

### FastAPI Developers
If you're already using FastAPI but want a more structured approach to building applications, fast-django offers:

- Project scaffolding and app organization
- Database migrations and ORM integration
- Admin interface out of the box
- Settings management with environment variables

### Modern Python Web Development
fast-django combines the best of both worlds:

- **Performance**: Built on FastAPI and ASGI
- **Developer Experience**: Django-like patterns and CLI
- **Type Safety**: Full Pydantic integration
- **Modern Stack**: Async/await, type hints, and modern Python features

## 🏗️ Architecture

fast-django provides a clean abstraction layer that combines:

- **FastAPI** for the web framework and API layer
- **Tortoise ORM** for database operations and models
- **Aerich** for database migrations
- **FastAPI-Admin** for the admin interface
- **Pydantic** for settings and data validation

## 📦 What's Included

- **Core Application Factory**: `create_app()` function for app initialization
- **Settings System**: Environment-based configuration with `FD_` prefix
- **ORM Integration**: Re-exported Tortoise ORM components
- **CLI Tools**: Complete command-line interface for project management
- **Admin System**: Pluggable admin interface with model registration
- **Scaffolding**: Templates for projects and apps
- **Middleware Support**: Easy middleware configuration
- **Auto-discovery**: Automatic app and model discovery

## 🛠️ Development

### Prerequisites

- Python 3.11+
- pip or your preferred package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/AakarSharma/fast-django.git
cd fast-django

# Install in development mode
pip install -e ".[dev,test,docs]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/fast_django --cov-report=html

# Run linting
ruff check . && ruff format --check .

# Run type checking
mypy src
```

### Building Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check . && mypy src`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📊 Project Status

- ✅ **Core Features**: Complete and stable
- ✅ **Documentation**: Comprehensive and up-to-date
- ✅ **Testing**: High test coverage with CI/CD
- ✅ **Type Safety**: Full type hints and mypy compliance
- 🔄 **Active Development**: Regular updates and improvements

## 🆘 Support

- 📚 **Documentation**: [https://aakarsharma.github.io/fast-django/](https://aakarsharma.github.io/fast-django/)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/AakarSharma/fast-django/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/AakarSharma/fast-django/discussions)
- 📧 **Contact**: [Create an issue](https://github.com/AakarSharma/fast-django/issues/new)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework for building APIs
- [Tortoise ORM](https://tortoise-orm.readthedocs.io/) - The async ORM
- [Aerich](https://github.com/tortoise/aerich) - Database migrations
- [FastAPI-Admin](https://github.com/fastapi-admin/fastapi-admin) - Admin interface
- [Django](https://www.djangoproject.com/) - Inspiration for developer experience

---

<div align="center">

**Made with ❤️ by the fast-django community**

[⭐ Star us on GitHub](https://github.com/AakarSharma/fast-django) • [🐛 Report a bug](https://github.com/AakarSharma/fast-django/issues) • [💡 Request a feature](https://github.com/AakarSharma/fast-django/issues)

</div>
