# Py AI Translator

## About

Py AI Translator is a multi-lingual translation tool that helps you translate web content using AI. The API flow works like this:

1. Crawl websites and extract their content
2. Translate the content to different languages (Spanish by default)
3. Save translations as markdown files
4. Serve translations via a FastAPI web API

Built with Python 3.13, FastAPI, and SQLAlchemy, it's perfect for:

- Quickly localizing documentation or blog posts
- Creating multilingual versions of web content
- Experimenting with AI-powered translation

It utilizes Google's Gemini Flash Lite 001 model, ensuring quality and speed for AI translations without burning a hole in the pocket.
It works well for small and medium documents and can become erratic for large documents.

Will add support for other models down the line.

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
