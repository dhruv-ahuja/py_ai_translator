from fastapi import APIRouter, Depends
from loguru import logger

from app.config.db import AsyncSession, get_async_session_dependency
from app.schemas.app import TranslateRequestInput, TranslateResponse
from app.services.app import crawl_single_url, translate_content, save_translated_content

router = APIRouter(prefix="/app")


@router.post("/translate")
async def translate(
    req_input: TranslateRequestInput, async_session: AsyncSession = Depends(get_async_session_dependency)
) -> TranslateResponse:
    """Translates content from a URL to a target language."""

    logger.debug("received translate request", input=req_input)
    url = req_input.url
    language = req_input.language

    crawled_data = await crawl_single_url(url, cache=req_input.cache)
    if not crawled_data or not crawled_data.content:
        logger.error("No content found for URL", url=url)
        return TranslateResponse(success=False, error={"message": "No content found for the given URL"}, data=None)

    translated_content = await translate_content(crawled_data, language)
    if not translated_content:
        logger.error(
            "Unable to translate content for URL", url=url, content_length=len(crawled_data.content), language=language
        )
        return TranslateResponse(success=False, error={"message": "Unable to translate for the given URL."}, data=None)

    title = req_input.title if req_input.title else crawled_data.title
    output_file_path = await save_translated_content(
        crawled_data.id, title, translated_content, language, save_to_disk=req_input.save_to_disk
    )
    logger.info(
        "Saved translated content",
        translation_id=crawled_data.id,
        url=url,
        save_to_disk=req_input.save_to_disk,
        output_file_path=output_file_path,
    )
    return TranslateResponse(
        success=True,
        error=None,
        data={
            "translation_id": crawled_data.id,
            "content": translated_content,
            "metadata": {"output_file_path": output_file_path, "crawled_metadata": crawled_data.crawled_metadata},
        },
    )
