# Core API Reference

This page provides detailed API documentation for fast-django's core components.

## Application Factory

### `create_app`

```python
def create_app(settings: Settings | None = None) -> FastAPI
```

Creates and configures a FastAPI application with fast-django features.

**Parameters:**
- `settings` (Settings, optional): Configuration settings. If None, uses default Settings.

**Returns:**
- `FastAPI`: Configured FastAPI application instance.

**Example:**
```python
from fast_django import create_app, Settings

# Using default settings
app = create_app()

# Using custom settings
settings = Settings(app_name="My App", debug=True)
app = create_app(settings)
```

### Built-ins

`create_app` automatically adds `fast_django.signals.SignalsMiddleware` to emit request lifecycle signals. Custom middleware listed in `Settings.middleware` is applied after this built-in middleware.

## Settings

### `Settings`

```python
class Settings(BaseSettings):
    app_name: str = "fast-django app"
    debug: bool = False
    secret_key: str = "change-me"
    base_dir: Path = Field(default_factory=lambda: Path.cwd())
    admin_enabled: bool = True
    admin_path: str = "/admin"
    orm: OrmConfig = Field(default_factory=OrmConfig)
    installed_apps: list[str] = Field(default_factory=list)
    middleware: list[str] = Field(default_factory=list)
```

Base settings class using Pydantic Settings.

**Fields:**
- `app_name` (str): Application name for FastAPI title.
- `debug` (bool): Debug mode flag.
- `secret_key` (str): Secret key for security.
- `base_dir` (Path): Base directory path.
- `admin_enabled` (bool): Enable admin interface.
- `admin_path` (str): Admin interface mount path.
- `orm` (OrmConfig): Database configuration.
- `installed_apps` (list[str]): List of installed app names.
- `middleware` (list[str]): List of middleware dotted paths.

### `OrmConfig`

```python
class OrmConfig(BaseModel):
    models: list[str] = Field(default_factory=lambda: ["aerich.models"])
    connections: dict[str, str] = Field(default_factory=lambda: {"default": "sqlite://db.sqlite3"})
    apps: dict[str, dict[str, Any]] = Field(default_factory=dict)
```

Database configuration for Tortoise ORM.

**Fields:**
- `models` (list[str]): List of model module paths.
- `connections` (dict[str, str]): Database connection URLs.
- `apps` (dict[str, dict[str, Any]]): App-specific ORM configuration.

## Database

### `init_db`

```python
def init_db(app: FastAPI, settings: Settings) -> None
```

Initializes database connections and ORM.

**Parameters:**
- `app` (FastAPI): FastAPI application instance.
- `settings` (Settings): Application settings.

### `build_tortoise_config`

```python
def build_tortoise_config(settings: Settings) -> dict[str, Any]
```

Builds Tortoise ORM configuration from settings.

**Parameters:**
- `settings` (Settings): Application settings.

**Returns:**
- `dict[str, Any]`: Tortoise ORM configuration dictionary.

## Apps

### `include_app_routers`

```python
def include_app_routers(app: FastAPI, app_names: list[str]) -> None
```

Automatically includes routers from installed apps.

**Parameters:**
- `app` (FastAPI): FastAPI application instance.
- `app_names` (list[str]): List of app names to include.

**Discovery Order:**
1. `{app_name}.urls`
2. `{app_name}.routes`
3. `{app_name}.api`
4. `{app_name}.views`

## Admin

### `AdminSite`

```python
class AdminSite:
    def __init__(self, title: str = "Admin") -> None
    def mount(self, app: FastAPI, settings: Settings, path: Optional[str] = None) -> None
    def register_model(self, model: Type[Model]) -> None
```

Admin interface facade for mounting and model registration.

**Methods:**
- `__init__(title)`: Initialize admin site with title.
- `mount(app, settings, path)`: Mount admin interface to FastAPI app.
- `register_model(model)`: Register a model for admin interface.

### `try_call_admin_hooks`

```python
def try_call_admin_hooks(app: FastAPI, settings: Settings) -> None
```

Calls admin initialization hooks from installed apps.

**Parameters:**
- `app` (FastAPI): FastAPI application instance.
- `settings` (Settings): Application settings.

**Hook Function:**
```python
def init_admin(app: FastAPI, settings: Settings) -> None:
    # Your admin configuration
    pass
```

## Utilities

### `discover_models_modules`

```python
def discover_models_modules(start_dir: Path | None = None) -> list[str]
```

Discovers model modules in a directory.

**Parameters:**
- `start_dir` (Path, optional): Directory to search. Defaults to current directory.

**Returns:**
- `list[str]`: List of discovered model module paths.

**Example:**
```python
from fast_django.utils import discover_models_modules

# Discover models in current directory
models = discover_models_modules()
# Returns: ['app1.models', 'app2.models', 'aerich.models']

# Discover models in specific directory
models = discover_models_modules(Path('/path/to/project'))
```
