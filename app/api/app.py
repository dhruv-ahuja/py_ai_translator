from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app.config.db import AsyncSession, get_async_session_dependency
from app.schemas.app import TranslateRequestInput, TranslateResponse
from app.services.app import save_translated_content, get_or_crawl_url, get_crawled_data, get_or_translate_content

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
            "crawled_data_id": crawled_data.id,
            "content": translation_output.content,
            "metadata": {
                "translation_metadata": translation_output.ai_metadata,
                "crawled_metadata": crawled_data.crawled_metadata,
            },
        },
    )


@router.post("/translate")
async def translate(
    req_input: TranslateRequestInput, session: AsyncSession = Depends(get_async_session_dependency)
) -> TranslateResponse:
    """Translates content from a URL to a target language."""

    logger.debug("received translate request", input=req_input)
    url = req_input.url
    language = req_input.language

    try:
        crawled_data, _ = await get_or_crawl_url(url, session, req_input.cache)
        translated_content = await get_or_translate_content(crawled_data, session, language)

        title = req_input.title if req_input.title else crawled_data.title
        translation_output, output_file_path = await save_translated_content(
            crawled_data.id, title, translated_content, language, save_to_disk=req_input.save_to_disk
        )

        return TranslateResponse(
            success=True,
            error=None,
            data={
                "crawled_data_id": crawled_data.id,
                "metadata": {
                    "translation_metadata": translation_output.ai_metadata,
                    "crawled_metadata": crawled_data.crawled_metadata,
                },
                "content": translated_content,
            },
        )
    except ValueError as exc:
        logger.error("Translation failed", url=url, error=str(exc))
        return TranslateResponse(success=False, error={"message": str(exc)}, data=None)
