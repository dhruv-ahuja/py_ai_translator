import asyncio
import time
from pathlib import Path

import logfire
from app.config.logger import logger

from app.ai import create_agent, generate_language_prompt
from app.crawler import crawl_url
from app.config.app_settings import settings


if settings.logfire.enable:
    logfire.configure(token=settings.logfire.token.get_secret_value())
    logfire.instrument_openai()

    # sleep to avoid interrupting user input when logfire emits startup log
    logger.debug("enabled Logfire telemetry")
    time.sleep(2)


async def sample_conversion():
    url = input("Enter URL to crawl: ").strip()
    name = input("Enter name for output file (leave empty for page title): ").strip()
    cache = input("Enable cache? (Y/n): ").strip().lower()
    if cache == "" or cache == "y":
        cache = True
    else:
        cache = False

    result = await crawl_url(url, cache)
    content = result.markdown

    if not content:
        logger.error("No content found for URL, exiting...", url=url)
        return

    # TODO: clean up this logic as much as possible
    if not name:
        opengraph_title = result.metadata.get("og:title")
        title = result.metadata.get("title")
        title = (title[:100] + "..." if len(title) > 100 else title) if title else None
        sanitized_url = url.replace("https://", "").replace("www.", "")

        name = opengraph_title if opengraph_title else title
        name = name if name else sanitized_url

    content = content.fit_markdown if content.fit_markdown else content
    logger.debug("Extracted markdown content from URL\n", url=url, content=str(content))

    prompt = generate_language_prompt("Spanish", content)
    agent = create_agent(system_prompt=prompt)

    user_prompt = f"""
    Convert the following Markdown content into a bilingual document. Translate each paragraph into Spanish and place the original English paragraph below it. Also, translate headings into Spanish and keep the original English headings below them.
    
    {content}
    """
    translation_result = await agent.run(user_prompt)
    logger.debug("Usage stats for agent", usage=translation_result.usage())

    output_folder = Path(settings.general.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file_path = output_folder.joinpath(f"{name}.md")

    with open(output_file_path, "w") as f:
        data = translation_result.data
        # remove markdown codeblock marker
        data = data.replace("```markdown", "").replace("```", "")
        f.write(data)

    logger.debug("Crawled URL metadata", url=url, metadata=result.metadata)
    logger.info("Translated content saved successfully", output_file_path=output_file_path)


if __name__ == "__main__":
    asyncio.run(sample_conversion())
