from pathlib import Path

from app.config.app_settings import settings
from app.config.db import AsyncSession, get_async_session
from app.config.logger import logger
from app.config.models import CrawledData
from app.repositories.app import AiTranslationOutputRepository, CrawledDataRepository
from app.schemas.app import AiTranslationOutputCreate, CrawledDataCreate
from app.utils.ai import create_agent, get_agent_prompt
from app.utils.crawler import crawl_url


S = AsyncSession


async def crawl_single_url(url: str, cache: bool = True) -> CrawledData | None:
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

    async with get_async_session() as session:
        crawled_data = CrawledDataCreate(url=url, content=content, metadata=result.metadata)
        crawled_data_record = await repository.add(crawled_data, session)

    async with get_async_session() as session:
        count = await repository.count(session)
        logger.info("number of crawled data records", count=count)
    return crawled_data_record


async def translate_content(crawled_data: CrawledData, language: str = "Spanish") -> str:
    prompt = get_agent_prompt(crawled_data.content, language)
    agent = create_agent(system_prompt=prompt)
    result = await agent.run(prompt)
    logger.debug("Usage stats for agent", usage=result.usage())
    return result.data


async def save_translated_content(
    crawled_data_id: int, file_name: str, content: str, language: str = "Spanish", save_to_disk: bool = True
) -> None:
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
        translated_data = AiTranslationOutputCreate(crawled_data_id=crawled_data_id, language=language, content=content)
        await repository.add(translated_data, session)

    logger.debug("Translated content saved successfully", output_file_path=output_file_path)
