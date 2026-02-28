#!/bin/sh
set -e

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if needed..."
python manage.py create_superuser_if_none

echo "Loading initial data if needed..."
python manage.py load_initial_data

echo "Starting server..."
exec "$@"
