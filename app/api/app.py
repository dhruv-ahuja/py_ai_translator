from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app.config.db import AsyncSession, get_async_session_dependency
from app.config.models import AiTranslationOutput
from app.schemas.app import TranslateRequestInput, TranslateResponse
from app.services.app import (
    crawl_single_url,
    translate_content,
    save_translated_content,
    get_crawled_data_by_url,
    get_crawled_data,
)

router = APIRouter(prefix="/app")


@router.get("/translate")
async def get_translation(
    id: int, async_session: AsyncSession = Depends(get_async_session_dependency)
) -> TranslateResponse:
    crawled_data = await get_crawled_data(id, async_session)
    if not crawled_data:
        raise HTTPException(
            status_code=404,
            detail="Crawled data not found",
        )

    translation_output = await crawled_data.awaitable_attrs.translation_output
    if not translation_output:
        raise HTTPException(
            status_code=404,
            detail="Translation output not found",
        )

    return TranslateResponse(
        success=True,
        error=None,
        data={
            "translation_id": translation_output.id,
            "content": translation_output.content,
            "metadata": {
                "translation_metadata": translation_output.ai_metadata,
                "crawled_metadata": crawled_data.crawled_metadata,
            },
        },
    )


@router.post("/translate")
async def translate(
    req_input: TranslateRequestInput, async_session: AsyncSession = Depends(get_async_session_dependency)
) -> TranslateResponse:
    """Translates content from a URL to a target language."""

    logger.debug("received translate request", input=req_input)
    url = req_input.url
    language = req_input.language
    fresh_crawl = False

    # TODO: move all conditional logic to service layer
    crawled_data = await get_crawled_data_by_url(url, async_session)
    if not crawled_data:
        crawled_data = await crawl_single_url(url, cache=req_input.cache)
        fresh_crawl = True
    else:
        logger.info("found existing crawled data", id=crawled_data.id, url=url)

    if not crawled_data or not crawled_data.content:
        logger.error("No content found for URL", url=url)
        return TranslateResponse(success=False, error={"message": "No content found for the given URL"}, data=None)

    if not fresh_crawl:
        translation_output: AiTranslationOutput | None = await crawled_data.awaitable_attrs.translation_output
        if translation_output:
            logger.info("Found existing translation output", id=translation_output.id, url=url)
            translated_content = translation_output.content
            return TranslateResponse(
                success=True,
                error=None,
                data={
                    "translation_id": crawled_data.id,
                    "content": translated_content,
                    "metadata": {
                        "translation_metadata": translation_output.ai_metadata,
                        "crawled_metadata": crawled_data.crawled_metadata,
                    },
                },
            )

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
            "metadata": {
                "translation_metadata": translation_output.ai_metadata,
                "crawled_metadata": crawled_data.crawled_metadata,
            },
            "content": translated_content,
        },
    )
