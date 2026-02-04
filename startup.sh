#!/bin/bash

# Azure startup script - runs migrations and starts gunicorn

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn server..."
gunicorn smart_campus.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
