from pydantic import BaseModel, Field


class CrawlerDataCreate(BaseModel):
    url: str
    content: str = Field("")
    metadata: dict | None = Field(None)

    def get_crawled_page_title(self) -> str:
        formatted_url = self.url.replace("https://", "").replace("www.", "")
        if self.metadata is None:
            return formatted_url

        # opengraph titles are better as they are meant for social media and are concise
        # shorten the given title if it is too long
        opengraph_title = self.metadata.get("og:title")
        given_title = self.metadata.get("title")
        given_title = (given_title[:50] + "..." if len(given_title) > 50 else given_title) if given_title else None

        # use opengraph title if available, otherwise use given title, falling back to formatted url if
        # no title is available
        title = opengraph_title if opengraph_title else given_title
        title = title if title else formatted_url
        return title


class CrawlerDataUpdate(BaseModel):
    id: int
    url: str | None
    content: str = Field("")
    metadata: dict | None = Field(None)


class AiTranslationOutputCreate(BaseModel):
    crawler_data_id: int
    language: str
    content: str = Field("")
    metadata: dict | None = Field(None)


class AiTranslationOutputUpdate(BaseModel):
    id: int
    crawler_data_id: int
    language: str = Field("")
    content: str = Field("")
    metadata: dict | None = Field(None)
