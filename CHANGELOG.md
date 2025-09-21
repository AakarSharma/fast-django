# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Django-like signals system:
  - Request lifecycle signals via built-in `SignalsMiddleware`
  - ORM signals (`pre_save`, `post_save`, `pre_delete`, `post_delete`) by patching Tortoise `Model`
- New docs page: Signals, added to navigation
- Tests for request and ORM signals

### Added
- Comprehensive documentation with examples and API reference
- Enhanced README with badges and clear project overview
- Detailed contributing guidelines and code of conduct
- Multiple example applications (Blog, E-commerce, Real-time Chat)

### Changed
- Improved project structure and organization
- Enhanced documentation with better navigation
- Updated mkdocs configuration with modern theme features

## [0.1.0] - 2025-01-27

### Added
- Initial release of fast-django
- Core application factory (`create_app`)
- Settings system with Pydantic
- Tortoise ORM integration
- CLI commands (`startproject`, `startapp`, `runserver`, `makemigrations`, `migrate`, `shell`, `createsuperuser`)
- Admin interface with FastAPI-Admin
- Scaffolding system for projects and apps
- Middleware support
- Auto-discovery for apps and models
- Database migrations with Aerich
- Environment variable configuration
- Type hints and mypy support
- Comprehensive test suite
- Documentation with MkDocs

### Features
- **Application Factory**: `create_app()` function for app initialization
- **Settings Management**: Pydantic-based settings with `FD_` prefix
- **ORM Integration**: Re-exported Tortoise ORM components
- **CLI Tools**: Complete command-line interface
- **Admin System**: Pluggable admin interface
- **Scaffolding**: Project and app generation templates
- **Middleware**: Easy middleware configuration
- **Auto-discovery**: Automatic app and model discovery
- **Migrations**: Database migration management
- **Documentation**: Comprehensive guides and API reference

### Technical Details
- Python 3.11+ support
- FastAPI 0.115+ integration
- Tortoise ORM 0.20+ for database operations
- Aerich 0.7.2+ for migrations
- FastAPI-Admin 1.0.4+ for admin interface
- Typer 0.12.3+ for CLI
- Pydantic 2.5+ for settings and validation
- Uvicorn for ASGI server
- Ruff for linting and formatting
- MyPy for type checking
- Pytest for testing

## [0.0.1] - 2025-01-01

### Added
- Initial project setup
- Basic project structure
- Core dependencies
- Development tooling
