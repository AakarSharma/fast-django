# Settings

fast-django uses Pydantic Settings for configuration management, providing environment variable support with the `FD_` prefix and automatic `.env` file loading.

## Basic Settings

### Creating a Settings Class

```python
from fast_django.settings import Settings, OrmConfig

class MySettings(Settings):
    app_name: str = "myapp"
    debug: bool = False
    secret_key: str = "change-me"
    orm: OrmConfig = OrmConfig(models=["myapp.models", "aerich.models"])
```

### Using Settings

```python
from fast_django import create_app
from myapp.settings import MySettings

settings = MySettings()
app = create_app(settings)
```

## Configuration Options

### Application Settings

```python
class Settings(Settings):
    # Application name
    app_name: str = "fast-django app"

    # Debug mode
    debug: bool = False

    # Secret key for security
    secret_key: str = "change-me"

    # Base directory (defaults to current working directory)
    base_dir: Path = Field(default_factory=lambda: Path.cwd())

    # Admin interface settings
    admin_enabled: bool = True
    admin_path: str = "/admin"
```

### Database Configuration

```python
from fast_django.settings import Settings, OrmConfig

class Settings(Settings):
    orm: OrmConfig = OrmConfig(
        # Database connections
        connections={
            "default": "sqlite://db.sqlite3",
            "readonly": "sqlite://readonly.db",
        },

        # Model modules
        models=["myapp.models", "aerich.models"],

        # App-specific configuration
        apps={
            "models": {
                "models": ["myapp.models", "aerich.models"],
                "default_connection": "default",
            },
            "analytics": {
                "models": ["analytics.models"],
                "default_connection": "readonly",
            }
        }
    )
```

### App Configuration

```python
class Settings(Settings):
    # Installed apps (for auto-discovery)
    installed_apps: list[str] = ["myapp", "blog", "users"]

    # Middleware (dotted paths)
    middleware: list[str] = [
        "fastapi.middleware.cors.CORSMiddleware",
        "fastapi.middleware.gzip.GZipMiddleware",
    ]
```

## Environment Variables

### Basic Environment Variables

```bash
# .env file
FD_APP_NAME="My Awesome App"
FD_DEBUG=true
FD_SECRET_KEY="your-secret-key-here"
FD_ADMIN_ENABLED=true
FD_ADMIN_PATH="/admin"
```

### Database Environment Variables

```bash
# Database configuration
FD_ORM_CONNECTIONS_DEFAULT=sqlite://db.sqlite3
FD_ORM_CONNECTIONS_READONLY=postgres://user:pass@localhost/readonly

# Model modules
FD_ORM_MODELS_0=myapp.models
FD_ORM_MODELS_1=blog.models
FD_ORM_MODELS_2=aerich.models
```

### App Configuration Environment Variables

```bash
# Installed apps
FD_INSTALLED_APPS_0=myapp
FD_INSTALLED_APPS_1=blog
FD_INSTALLED_APPS_2=users

# Middleware
FD_MIDDLEWARE_0=fastapi.middleware.cors.CORSMiddleware
FD_MIDDLEWARE_1=fastapi.middleware.gzip.GZipMiddleware
```

## Advanced Configuration

### Custom Settings Classes

```python
from fast_django.settings import Settings, OrmConfig
from typing import List, Optional

class ProductionSettings(Settings):
    app_name: str = "Production App"
    debug: bool = False
    secret_key: str = "production-secret-key"

    # Production database
    orm: OrmConfig = OrmConfig(
        connections={
            "default": "postgres://user:pass@prod-db:5432/myapp",
        },
        models=["myapp.models", "aerich.models"]
    )

    # Production middleware
    middleware: List[str] = [
        "fastapi.middleware.cors.CORSMiddleware",
        "fastapi.middleware.gzip.GZipMiddleware",
        "myapp.middleware.SecurityMiddleware",
    ]

class DevelopmentSettings(Settings):
    app_name: str = "Development App"
    debug: bool = True
    secret_key: str = "dev-secret-key"

    # Development database
    orm: OrmConfig = OrmConfig(
        connections={
            "default": "sqlite://dev.db",
        },
        models=["myapp.models", "aerich.models"]
    )

class TestSettings(Settings):
    app_name: str = "Test App"
    debug: bool = True
    secret_key: str = "test-secret-key"

    # Test database
    orm: OrmConfig = OrmConfig(
        connections={
            "default": "sqlite://:memory:",
        },
        models=["myapp.models", "aerich.models"]
    )
```

### Environment-based Settings

```python
import os
from fast_django.settings import Settings, OrmConfig

def get_settings():
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return ProductionSettings()
    elif env == "test":
        return TestSettings()
    else:
        return DevelopmentSettings()

# Usage
settings = get_settings()
app = create_app(settings)
```

### Custom Field Types

```python
from fast_django.settings import Settings
from typing import List, Dict, Any
from pathlib import Path

class MySettings(Settings):
    # Custom list field
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]

    # Custom dict field
    cache_config: Dict[str, Any] = {
        "backend": "redis",
        "host": "localhost",
        "port": 6379,
    }

    # Custom path field
    static_files_dir: Path = Path("static")

    # Custom validation
    def model_post_init(self, __context: Any) -> None:
        if self.debug and self.secret_key == "change-me":
            raise ValueError("Must set a secure secret key in production")
```

## Database Configuration

### Multiple Databases

```python
class Settings(Settings):
    orm: OrmConfig = OrmConfig(
        connections={
            "default": "postgres://user:pass@localhost/main",
            "analytics": "postgres://user:pass@localhost/analytics",
            "cache": "redis://localhost:6379/0",
        },
        apps={
            "models": {
                "models": ["myapp.models", "aerich.models"],
                "default_connection": "default",
            },
            "analytics": {
                "models": ["analytics.models"],
                "default_connection": "analytics",
            },
            "cache": {
                "models": ["cache.models"],
                "default_connection": "cache",
            }
        }
    )
```

### Database URL Examples

```python
# SQLite
"sqlite://db.sqlite3"
"sqlite://:memory:"

# PostgreSQL
"postgres://user:password@localhost:5432/dbname"
"postgres://user:password@localhost:5432/dbname?sslmode=require"

# MySQL
"mysql://user:password@localhost:3306/dbname"

# Redis
"redis://localhost:6379/0"
"redis://user:password@localhost:6379/0"
```

## Middleware Configuration

### Built-in Middleware

```python
class Settings(Settings):
    middleware: List[str] = [
        # CORS middleware
        "fastapi.middleware.cors.CORSMiddleware",

        # GZip compression
        "fastapi.middleware.gzip.GZipMiddleware",

        # Trusted host middleware
        "fastapi.middleware.trustedhost.TrustedHostMiddleware",

        # HTTPS redirect (production)
        "fastapi.middleware.httpsredirect.HTTPSRedirectMiddleware",
    ]
```

### Custom Middleware

```python
# myapp/middleware.py
from fastapi import Request, Response
import time

class TimingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = time.time() - start_time
                message["headers"].append([b"x-process-time", str(process_time).encode()])
            await send(message)

        await self.app(scope, receive, send_wrapper)

# In settings.py
class Settings(Settings):
    middleware: List[str] = [
        "myapp.middleware.TimingMiddleware",
    ]
```

## Validation and Error Handling

### Custom Validation

```python
from fast_django.settings import Settings
from pydantic import validator

class Settings(Settings):
    app_name: str = "myapp"
    debug: bool = False
    secret_key: str = "change-me"

    @validator('secret_key')
    def validate_secret_key(cls, v, values):
        if not values.get('debug') and v == "change-me":
            raise ValueError("Must set a secure secret key in production")
        return v

    @validator('app_name')
    def validate_app_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("App name cannot be empty")
        return v.strip()
```

### Settings Validation

```python
from fast_django.settings import Settings

try:
    settings = Settings()
    print("Settings loaded successfully")
except ValidationError as e:
    print(f"Settings validation failed: {e}")
```

## Best Practices

1. **Use environment variables** for configuration that changes between environments
2. **Set secure defaults** for production settings
3. **Validate sensitive settings** like secret keys
4. **Use different settings classes** for different environments
5. **Document your settings** with clear field descriptions
6. **Use type hints** for better IDE support and validation
7. **Keep secrets out of code** - use environment variables or secret management
8. **Test your settings** with different environment configurations

## Troubleshooting

### Common Issues

1. **"Settings validation failed"**
   - Check that all required fields have values
   - Verify environment variable names use `FD_` prefix
   - Check for type mismatches

2. **"Database connection failed"**
   - Verify database URL format
   - Check that database server is running
   - Verify credentials and permissions

3. **"Module not found"**
   - Check that model modules are correctly specified
   - Verify import paths are correct
   - Ensure modules are in Python path

### Debugging Settings

```python
# Print all settings
settings = Settings()
print(settings.dict())

# Print specific setting
print(f"Debug mode: {settings.debug}")
print(f"Database URL: {settings.orm.connections['default']}")
```
