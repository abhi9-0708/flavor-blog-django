#!/bin/sh
set -e

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if needed..."
python manage.py create_superuser_if_none

echo "Starting server..."
exec "$@"
