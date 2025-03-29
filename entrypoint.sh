#!/bin/sh

echo "Starting application setup..."

echo "Running database migrations..."
alembic upgrade head

echo "Setting up crawl4ai"
crawl4ai setup

echo "Starting FastAPI application..."
fastapi run --host 0.0.0.0 --port 8000 --proxy-headers --workers 4
