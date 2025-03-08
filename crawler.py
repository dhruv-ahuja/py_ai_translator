from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    CrawlResult,
    DefaultMarkdownGenerator,
    PruningContentFilter,
    CacheMode,
    BrowserConfig,
)

browser_config = BrowserConfig(
    headless=True,  # 'True' for automated runs
    verbose=True,
    # use_managed_browser=True,  # Enables persistent browser strategy
    browser_type="chromium",
    # user_data_dir="/path/to/my-chrome-profile"
)
config = CrawlerRunConfig(
    # magic=True,
    # user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    word_count_threshold=10,  # Minimum words per content block
    exclude_external_links=True,  # Remove external links
    remove_overlay_elements=True,  # Remove popups/modals
    excluded_tags=["form", "header"],
    # Cache control
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.6), options={"ignore_links": True}
    ),
)


async def crawl_url(url: str) -> CrawlResult:
    async with AsyncWebCrawler() as crawler:
        result: CrawlResult = await crawler.arun(url=url, config=config, browser_config=browser_config)
        if result.success:
            print(result.markdown.fit_markdown)
        else:
            print(result.error_message)

        return result
