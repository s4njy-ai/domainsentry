"""
Cyber news feed endpoints for DomainSentry API.
"""
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.schemas.feed import NewsFeedItem, NewsFeedResponse
from app.services.feed_service import FeedService

router = APIRouter()


@router.get("/", response_model=NewsFeedResponse)
async def get_news_feeds(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    category: str = None,
):
    """
    Get aggregated cyber security news feeds.
    """
    service = FeedService(db)
    return await service.get_news_items(limit=limit, category=category)


@router.get("/refresh")
async def refresh_news_feeds(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh all news feeds in background.
    """
    service = FeedService(db)
    background_tasks.add_task(service.refresh_all_feeds)
    
    return {"message": "News feeds refresh started in background"}


@router.get("/sources")
async def get_feed_sources(
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of configured news feed sources.
    """
    service = FeedService(db)
    return {"sources": service.get_feed_sources()}