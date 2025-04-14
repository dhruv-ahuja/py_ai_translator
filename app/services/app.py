from pathlib import Path

from app.config.app_settings import settings
from app.config.db import AsyncSession, get_async_session
from app.config.logger import logger
from app.config.models import AiTranslationOutput, CrawledData
from app.repositories.app import AiTranslationOutputRepository, CrawledDataRepository
from app.schemas.app import AiTranslationOutputCreate, CrawledDataCreate
from app.utils.ai import create_agent, get_agent_prompt
from app.utils.crawler import crawl_url


S = AsyncSession


async def get_crawled_data(id: int, session: S) -> CrawledData | None:
    repository = CrawledDataRepository()
    return await repository.get(id, session)


async def get_crawled_data_by_url(url: str, session: S) -> CrawledData | None:
    """Get crawled data for the given URL, if it exists and is not older than the specified number of days."""

    repository = CrawledDataRepository()
    filters = {"url": url}
    return await repository.get_by_filter(session, **filters)


async def crawl_single_url(url: str, session: S, cache: bool = True) -> CrawledData | None:
    """Crawls a URL and saves its content and metadata to the database."""

    result = await crawl_url(url, cache)
    if not result:
        return None
    content = result.markdown
    if not content:
        return None

    repository = CrawledDataRepository()
    content = content.fit_markdown if content.fit_markdown else content

    logger.debug("Extracted markdown content from URL\n", url=url, content=str(content))
    logger.debug("Crawled URL metadata", url=url, metadata=result.metadata)

    crawled_data = CrawledDataCreate(url=url, content=content, metadata=result.metadata)
    crawled_data_record = await repository.add(crawled_data, session)

    await session.flush()
    await session.refresh(crawled_data_record)

    return crawled_data_record


async def translate_content(crawled_data: CrawledData, language: str = "Spanish") -> str:
    prompt = get_agent_prompt(crawled_data.content, language)
    agent = create_agent(system_prompt=prompt)
    result = await agent.run(prompt)
    logger.debug("Usage stats for agent", usage=result.usage())
    return result.data


async def get_or_crawl_url(
    url: str,
    session: S,
    cache: bool = True,
) -> tuple[CrawledData, bool]:
    """Get existing crawled data or crawl fresh if not found.
    Returns tuple of (crawled_data, is_fresh_crawl)"""

    # Check for existing crawled data
    crawled_data = await get_crawled_data_by_url(url, session)
    if crawled_data:
        logger.info("Found existing crawled data", id=crawled_data.id, url=url)
        return crawled_data, False

    # If not found, crawl fresh
    crawled_data = await crawl_single_url(url, session, cache)
    if not crawled_data:
        raise ValueError(f"Failed to crawl URL: {url}")

    await session.commit()
    return crawled_data, True


async def get_or_translate_content(crawled_data: CrawledData, session: S, language: str = "Spanish") -> str:
    """Get existing translation or translate fresh if not found."""

    await session.refresh(crawled_data)

    translation_output = await crawled_data.awaitable_attrs.translation_output
    if not translation_output:
        return await translate_content(crawled_data, language)

    logger.info("Found existing translation", id=translation_output.id)
    return translation_output.content


async def save_translated_content(
    crawled_data_id: int, file_name: str, content: str, language: str = "Spanish", save_to_disk: bool = True
) -> tuple[AiTranslationOutput, Path | None]:
    output_file_path = None
    if save_to_disk:
        output_folder = Path(settings.general.output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
        output_file_path = output_folder.joinpath(f"{file_name}.md")

        logger.debug("Saving translated content to file", output_file_path=output_file_path)

        with open(output_file_path, "w") as f:
            # remove markdown codeblock marker
            content = content.replace("```markdown", "").replace("```md", "").replace("```", "")
            f.write(content)
            f.write("\n--------------------------------------\n")

    repository = AiTranslationOutputRepository()
    async with get_async_session() as session:
        translated_data = AiTranslationOutputCreate(
            crawled_data_id=crawled_data_id,
            language=language,
            content=content,
            metadata={"output_file_path": str(output_file_path)},
        )
        translation_output = await repository.add(translated_data, session)

    logger.debug("Translated content saved successfully", output_file_path=output_file_path)
    return translation_output, output_file_path
