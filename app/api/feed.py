from fastapi import APIRouter, Depends, Response
from loguru import logger

from app.config.db import AsyncSession, get_async_session_dependency
from app.services.feed import prepare_feed

router = APIRouter(prefix="/feed")


@router.get("/", response_class=Response)
async def get_feed(async_session: AsyncSession = Depends(get_async_session_dependency)):
    feed = await prepare_feed(async_session)
    xml_feed = feed.to_xml()

    logger.debug("created XML feed", xml_feed=xml_feed)
    return Response(
        content=xml_feed,
        media_type="application/rss+xml; charset=utf-8",
        headers={"Cache-Control": "no-cache", "Content-Type": "application/rss+xml; charset=utf-8"},
    )
