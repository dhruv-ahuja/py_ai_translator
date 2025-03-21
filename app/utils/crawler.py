from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    CrawlResult,
    DefaultMarkdownGenerator,
    PruningContentFilter,
    CacheMode,
    BrowserConfig,
)
from app.config.logger import logger


browser_config = BrowserConfig(
    headless=True,  # 'True' for automated runs
    verbose=True,
    use_managed_browser=True,  # Enables persistent browser strategy
    browser_type="chromium",
)
config = CrawlerRunConfig(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.52 Safari/537.36",
    word_count_threshold=10,  # Minimum words per content block
    exclude_external_links=False,
    remove_overlay_elements=True,  # Remove popups/modals
    excluded_tags=["form", "header"],
    # Cache control
    cache_mode=CacheMode.ENABLED,
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.6), options={"ignore_links": False}
    ),
)


async def crawl_url(url: str, cache: bool = True) -> CrawlResult | None:
    async with AsyncWebCrawler() as crawler:
        if not cache:
            config.cache_mode = CacheMode.DISABLED
        result: CrawlResult = await crawler.arun(url=url, config=config, browser_config=browser_config)
        if not result.success:
            logger.error("error crawling URL", url=url, error=result.error_message)
            return None

        return result
