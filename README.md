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

To run the app in CLI mode:

```bash
uv run --env-file .env app/main.py
```

To run the app server:

```bash
uv run --env-file .env fastapi dev --port 8002
```

The API server will be accessible at `http://localhost:8002`, with API docs at `http://localhost:8002/docs`

## Docker Usage

To run the app in CLI mode:

```bash
docker run --env-file .env.deploy --network app-network --rm dhruvahuja/py_ai_translator_cli 'https://www.example.com'
```

To run the app server:

```bash
docker compose up -d
```

The API server will be accessible at `http://localhost:8002`, with API docs at `http://localhost:8002/docs`
