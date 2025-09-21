# Admin

Use the AdminSite facade to mount admin without touching underlying libs.

```python
from fast_django.admin import AdminSite
from fast_django import create_app, Settings

app = create_app(Settings())
AdminSite().mount(app, Settings())
```

To customize per app, add `admin.py` in the app and define:

```python
from fastapi import FastAPI
from fast_django.admin import AdminSite
from fast_django.settings import Settings

def init_admin(app: FastAPI, settings: Settings) -> None:
    site = AdminSite(title="Admin")
    site.mount(app, settings)
```

Model registration will be added on top of AdminSite (resource mapping), keeping FastAPI-Admin and ORM internal.
