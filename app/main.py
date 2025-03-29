import asyncio
import time

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import logfire

from app.config.logger import logger
from app.services.app import crawl_single_url, translate_content, save_translated_content
from app.config.app_settings import settings
from app.api import feed


# TODO: move this and future instrumentation logic to config module
if settings.logfire.enable:
    logfire.configure(token=settings.logfire.token.get_secret_value())
    logfire.instrument_openai()

    # sleep to avoid interrupting user input when logfire emits startup log
    logger.debug("enabled Logfire telemetry")
    time.sleep(2)


async def sample_conversion():
    url = input("Enter URL to crawl: ").strip()
    name = input("Enter name for output file (leave empty for page title): ").strip()
    caching = input("Enable caching? (Y/n): ").strip().lower()
    caching = False
    cache = True if caching == "" or caching == "y" else False

    crawled_data = await crawl_single_url(url, cache)
    if not crawled_data or not crawled_data.content:
        logger.error("No content found for URL, exiting...", url=url)
        return

    translated_content = await translate_content(crawled_data)
    await save_translated_content(crawled_data.id, name, translated_content)
    logger.info("Translation completed successfully", url=url, name=name)


app = FastAPI(default_response_class=ORJSONResponse)
app.include_router(feed.router)


@app.get("/")
def healthcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    asyncio.run(sample_conversion())
