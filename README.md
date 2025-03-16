# Py AI Translator

## Setup

The app uses the latest Python 3.13

Install dependencies using:

```bash
uv sync
```

Copy `.env.example` as `.env` and set appropiate values

Run DB migrations:

```bash
uv run --env-file .env alembic upgrade head
```

## Usage

Run the app using:

```bash
uv run --env-file .env app/main.py
```
