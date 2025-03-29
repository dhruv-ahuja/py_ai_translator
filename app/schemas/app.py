from typing import Annotated, TypedDict
from pydantic import AfterValidator, AnyHttpUrl, BaseModel, Field


# check whether string is valid URL then convert it back to string for usage in the app
UrlString = Annotated[str, AfterValidator(lambda v: str(AnyHttpUrl(v)))]


# Service-DB Interface schemas
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


# Base API schemas
class ErrorResponseSchema(TypedDict):
    message: str


class BaseResponse(BaseModel):
    success: bool
    error: ErrorResponseSchema | None = Field(None)
    # TODO: add typeddict post-model creation validation
    data: dict | None = Field(None)


# API schemas


class TranslateRequestInput(BaseModel):
    url: UrlString = Field(...)
    language: str = Field("Spanish", description="Target language to translate to. Default: Spanish")
    save_to_disk: bool = Field(True, description="Save translated content to disk. Default: True")
    title: str | None = Field(
        None,
        description="Title of the content to be saved to disk. Automatically computed if not passed when saving file.",
    )
    cache: bool = Field(True, description="Allow crawler to cache the page. Default: True")


# NOTE: Experimental kinda "pattern", also avoiding creating more modules than needed right now
class _TranslateResponseData(TypedDict):
    translation_id: int | None
    content: str
    metadata: dict | None = Field(None)


class TranslateResponse(BaseResponse):
    data: _TranslateResponseData
