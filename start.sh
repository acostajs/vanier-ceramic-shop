#!/usr/bin/env bash
set -o errexit

echo "==> Compiling translation messages..."
python manage.py compilemessages

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate --no-input

echo "==> Starting Gunicorn server..."
exec gunicorn main.wsgi:application --bind 0.0.0.0:7860
