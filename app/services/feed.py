from app.repositories.app import CrawledDataRepository
from app.config.db import AsyncSession
from app.schemas.feed import RSSItem, RSSFeed


async def prepare_feed(async_session: AsyncSession):
    repository = CrawledDataRepository()
    feed_data = []

    crawled_data = await repository.list(async_session)

    for entry in crawled_data:
        title = entry.url.split("/")[-1]
        description = entry.content[:200]
        entry_data = RSSItem(title=title, description=description, link=entry.url, guid=entry.url)
        feed_data.append(entry_data)

    feed = RSSFeed(
        title="Dhuv's Crawled Data Feed", description="RSS feed of crawled content", link="/feed/", items=feed_data
    )
    return feed
