#!/bin/sh
set -e

# If arguments were passed (e.g. "celery …"), run them directly
if [ "$#" -gt 0 ]; then
	exec "$@"
fi

echo "==> Running migrations…"
python manage.py migrate --noinput

echo "==> Collecting static files…"
rm -rf /app/staticfiles/*
python manage.py collectstatic --noinput --clear

echo "==> Starting Daphne (ASGI)…"
exec daphne -b 0.0.0.0 -p 8000 boundless.asgi:application
