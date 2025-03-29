#!/bin/sh

echo "Starting application setup..."

echo "Running database migrations..."
uv run alembic upgrade head

echo "Starting FastAPI application..."
uv run fastapi run --host 0.0.0.0 --port 8000 --proxy-headers --workers 4
