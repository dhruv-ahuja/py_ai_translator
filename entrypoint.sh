#!/bin/sh

FLAG=${1:-web}

echo "Starting application setup..."

PYTHONPATH=/app

echo "Running database migrations..."
uv run alembic upgrade head

if [ "$FLAG" = "web" ]; then
    echo "Starting web application..."
    uv run fastapi run --host 0.0.0.0 --port 8000 --proxy-headers --workers 4

elif [ "$FLAG" = "cli" ]; then
    echo "Starting CLI application..."
    shift # remove the first 'cli' argument
    uv run app/main.py "$@"
fi
