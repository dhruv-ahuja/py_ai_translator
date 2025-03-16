import datetime as dt

from sqlalchemy import ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB


class Base(DeclarativeBase):
    pass


class CrawlerData(Base):
    __tablename__ = "crawler_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str | None] = mapped_column(String, nullable=False, default="")
    # attribute name 'metadata' is reserved by sqlalchemy
    crawler_metadata: Mapped[dict | None] = mapped_column(JSONB, name="metadata", nullable=True)
    created_date: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_date: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    translation_output: Mapped["AiTranslationOutput"] = relationship(
        "AiTranslationOutput", back_populates="crawler_data"
    )

    def __repr__(self) -> str:
        content = self.content[:50] + "..." if isinstance(self.content, str) else self.content
        return f"CrawlerData(id={self.id}, url={self.url}, markdown={content}, metadata={self.crawler_metadata}, created_date={self.created_date}, updated_date={self.updated_date})"

    @property
    def metadata_column(self) -> str:
        return "crawler_metadata"


class AiTranslationOutput(Base):
    __tablename__ = "ai_translation_output_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    crawler_data_id: Mapped[int] = mapped_column(ForeignKey("crawler_data.id"))
    language: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False, default="")
    # attribute name 'metadata' is reserved by sqlalchemy
    ai_metadata: Mapped[dict | None] = mapped_column(JSONB, name="metadata", nullable=True)
    created_date: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_date: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    crawler_data: Mapped["CrawlerData"] = relationship("CrawlerData", back_populates="translation_output")

    def __repr__(self) -> str:
        content = self.content[:50] + "..." if isinstance(self.content, str) else self.content
        return f"AiTranslationOutput(id={self.id}, crawler_data_id={self.crawler_data_id}, markdown={content}, metadata={self.ai_metadata}, created_date={self.created_date}, updated_date={self.updated_date})"

    @property
    def metadata_column(self) -> str:
        return "ai_metadata"
