#!/usr/bin/env bash
set -euo pipefail

TMP_DIR=$(mktemp -d)
pushd "$TMP_DIR" >/dev/null

fast-django startproject demo
cd demo
fast-django startapp blog

python manage.py makemigrations --app blog
python manage.py migrate

FD_TEST_MODE=1 python manage.py runserver --no-reload

popd >/dev/null
rm -rf "$TMP_DIR"
