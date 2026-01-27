"""
Feed schemas for DomainSentry API.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class NewsFeedItemBase(BaseModel):
    """Base schema for news feed item."""
    title: str
    link: str
    description: str
    source: str
    published_at: datetime
    author: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class NewsFeedItemCreate(NewsFeedItemBase):
    """Schema for creating a news feed item."""
    pass


class NewsFeedItemInDB(NewsFeedItemBase):
    """Schema for news feed item in database."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NewsFeedItem(NewsFeedItemInDB):
    """Schema for news feed item response."""
    pass


class NewsFeedResponse(BaseModel):
    """Schema for news feed response."""
    items: List[NewsFeedItem]
    total: int
    sources: List[str]
    updated_at: datetime


class NewsFeedRefreshResponse(BaseModel):
    """Schema for news feed refresh response."""
    message: str
    processed_feeds: int
    new_items: int
    errors: List[str]