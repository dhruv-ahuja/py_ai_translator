from pydantic import BaseModel, Field


class CrawledDataCreate(BaseModel):
    url: str
    content: str = Field("")
    metadata: dict | None = Field(None)


class CrawledDataUpdate(BaseModel):
    id: int
    url: str | None
    content: str = Field("")
    metadata: dict | None = Field(None)


class AiTranslationOutputCreate(BaseModel):
    crawled_data_id: int
    language: str
    content: str = Field("")
    metadata: dict | None = Field(None)


class AiTranslationOutputUpdate(BaseModel):
    id: int
    crawled_data_id: int
    language: str = Field("")
    content: str = Field("")
    metadata: dict | None = Field(None)
