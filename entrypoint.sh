#!/bin/bash
set -e

echo "Running migrations..."
flask db migrate -m "Auto migration for schedule update" || true
flask db upgrade

echo "Creating/Updating admin user..."
python create_admin.py

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5001 --workers 4 --access-logfile - --error-logfile - wsgi:app
