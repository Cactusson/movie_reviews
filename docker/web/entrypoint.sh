#!/bin/sh

echo "Running migrations..."
python src/manage.py migrate

echo "Starting server..."
python src/manage.py runserver 0.0.0.0:8000
