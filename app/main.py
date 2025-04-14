import asyncio
import time

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import logfire

from app.config.db import get_async_session
from app.config.logger import logger
from app.services.app import save_translated_content, get_or_crawl_url, get_or_translate_content
from app.config.app_settings import settings
from app.api import feed, app as app_api


# TODO: move this and future instrumentation logic to config module
if settings.logfire.enable:
    logfire.configure(token=settings.logfire.token.get_secret_value())
    logfire.instrument_openai()

    # sleep to avoid interrupting user input when logfire emits startup log
    logger.debug("enabled Logfire telemetry")
    time.sleep(2)


async def translate(url: str, name: str = "", cache: bool = True):
    """CLI translation handler using common service logic"""
    try:
        async with get_async_session() as session:
            crawled_data, _ = await get_or_crawl_url(url, session, cache)
            translated_content = await get_or_translate_content(crawled_data, session)

            name = name if name else crawled_data.title
            await save_translated_content(crawled_data.id, name, translated_content)
            logger.info("Translation completed", url=url)
    except ValueError as exc:
        logger.error("Translation failed", url=url, error=str(exc))
        raise


# TODO: clean up the main module
app = FastAPI(default_response_class=ORJSONResponse)
app.include_router(feed.router)
app.include_router(app_api.router)


@app.exception_handler(500)
async def internal_server_error(request, exc: Exception):
    """generic 500 error handler"""
    logger.error("Internal Server Error", path=request.url.path, method=request.method, body=request.body, exc_info=exc)
    return ORJSONResponse(
        status_code=500,
        content={"detail": "Unexpected error occurred"},
    )


@app.get("/")
def healthcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str, help="URL to crawl")
    parser.add_argument("--name", type=str, help="Name for output file (leave empty for page title)", default="")
    parser.add_argument("--cache", action="store_true", help="Enable caching")

    args = parser.parse_args()
    asyncio.run(translate(args.url, args.name, args.cache))
