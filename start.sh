#!/bin/sh
set -eu

PORT="${PORT:-8000}"
SQLITE_PATH="${SQLITE_PATH:-/app/data/db.sqlite3}"

mkdir -p /app/data /app/staticfiles
mkdir -p "$(dirname "$SQLITE_PATH")"

export SQLITE_PATH

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_demo_data

exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-120}"
