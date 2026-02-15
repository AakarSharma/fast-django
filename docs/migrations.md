# Migrations

- Use `python manage.py makemigrations` to generate migrations.
- Models are auto-discovered from app folders that contain `models.py`.
- Migrations are generated per app and stored under each app directory.

Commands:

```bash
python manage.py makemigrations          # all apps with models.py
python manage.py makemigrations --app blog
python manage.py migrate
python manage.py migrate --app blog
```

Notes:
- `orm_config.py` is regenerated from discovered apps and exposed as `ORM` for Aerich.
- fast-django writes app-scoped Aerich config files under `.fast_django/aerich/`.
- Aerich state and migration files are stored under `<app>/migrations/` (with Aerich app namespace folders inside that directory).
