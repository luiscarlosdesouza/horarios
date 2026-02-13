#!/bin/bash
set -e

echo "Running migrations..."

if [ -d "migrations" ]; then
    flask db upgrade
    echo "Creating/Updating admin user..."
    python create_admin.py
else
    echo "Migrations directory not found. Skipping upgrade and admin creation."
fi

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5001 --workers 4 --access-logfile - --error-logfile - wsgi:app
