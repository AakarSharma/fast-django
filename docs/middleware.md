# Middleware

- Add dotted middleware paths in `Settings.middleware`.
- They will be added in order during app creation.

```python
from fast_django.settings import Settings

class My(Settings):
    middleware = [
        "fastapi.middleware.cors.CORSMiddleware",
        "fastapi.middleware.gzip.GZipMiddleware",
    ]
```
