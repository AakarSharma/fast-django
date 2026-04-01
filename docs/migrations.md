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
- App migrations live under `<app>/migrations/`.
- Built-in auth/admin migrations live under `.fast_django/migrations/auth/`.
- You can target built-in auth migrations explicitly via `--app auth`.
- If you run app-scoped generation (`makemigrations --app <name>`), use the matching scoped upgrade
  (`migrate --app <name>`) for that workflow.
