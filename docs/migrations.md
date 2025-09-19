# Migrations

- Use `python manage.py makemigrations` to generate migrations.
- Auto-discovers all app folders with a `models.py` file and writes `orm_config.py`.
- For per-app migrations, use `--app <app_name>`; migration files are stored under `<app_name>/migrations/`.

Commands:

```
python manage.py makemigrations          # all apps with models.py
python manage.py makemigrations --app blog
python manage.py migrate
```

Notes:
- The generated `orm_config.py` exposes `ORM` consumed by Aerich.
- You can customize `ORM` later for multi-database setups.
