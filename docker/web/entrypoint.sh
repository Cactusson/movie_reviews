#!/bin/sh

cd src

echo "Collecting static files..."
python manage.py collectstatic --verbosity=3 --noinput

echo "Running migrations..."
python manage.py migrate --verbosity=3 --noinput

echo "Starting server..."
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application
