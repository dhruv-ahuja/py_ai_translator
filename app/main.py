import asyncio
import time

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import logfire

from app.config.logger import logger
from app.services.app import crawl_single_url, translate_content, save_translated_content
from app.config.app_settings import settings
from app.api import feed, app as app_api


# TODO: move this and future instrumentation logic to config module
if settings.logfire.enable:
    logfire.configure(token=settings.logfire.token.get_secret_value())
    logfire.instrument_openai()

    # sleep to avoid interrupting user input when logfire emits startup log
    logger.debug("enabled Logfire telemetry")
    time.sleep(2)


async def translate():
    url = input("Enter URL to crawl: ").strip()
    name = input("Enter name for output file (leave empty for page title): ").strip()
    caching = input("Enable caching? (Y/n): ").strip().lower()
    cache = True if caching == "" or caching == "y" else False

    crawled_data = await crawl_single_url(url, cache)
    if not crawled_data or not crawled_data.content:
        logger.error("No content found for URL, exiting...", url=url)
        return

    # generate name if not explicitly passed
    name = name if name else crawled_data.title
    translated_content = await translate_content(crawled_data)
    await save_translated_content(crawled_data.id, name, translated_content)
    logger.info("Translation completed successfully", url=url, name=name)


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
    asyncio.run(translate())
