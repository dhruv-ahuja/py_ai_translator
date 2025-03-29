from datetime import datetime
from app.repositories.app import CrawledDataRepository
from app.config.db import AsyncSession
from app.schemas.feed import AtomItem, AtomFeed


async def prepare_feed(async_session: AsyncSession):
    repository = CrawledDataRepository()
    feed_entries = []

    crawled_data = await repository.list(async_session)
    now = datetime.utcnow()

    for entry in crawled_data:
        title = entry.url.split("/")[-1]
        summary = entry.content[:200]

        url = f"https://feed.dhruvahuja.me/files/markdown/{title}.md"
        entry_data = AtomItem(title=title, summary=summary, link=url, id=url, updated=now, content=entry.content)
        feed_entries.append(entry_data)

    feed = AtomFeed(
        title="Dhuv's Crawled Data Feed",
        subtitle="Atom feed of crawled content",
        link="/feed/",
        id="https://feed.dhruvahuja.me/feed/",
        updated=now,
        entries=feed_entries,
    )
    return feed
