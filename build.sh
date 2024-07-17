#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install --no-cache-dir -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Start the application server
exec "$@"
