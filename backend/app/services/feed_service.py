"""
Cyber news feed service for DomainSentry.
"""
import asyncio
import datetime
import feedparser
import httpx
import uuid
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.feed import NewsFeedItem as NewsFeedItemModel
from app.schemas.feed import NewsFeedItemCreate, NewsFeedResponse


class FeedService:
    """
    Service for managing cyber security news feeds.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.feed_urls = settings.RSS_FEEDS
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def get_news_items(self, limit: int = 50, category: Optional[str] = None) -> NewsFeedResponse:
        """
        Get aggregated news feed items.
        """
        query = select(NewsFeedItemModel).order_by(NewsFeedItemModel.published_at.desc()).limit(limit)
        
        if category:
            # Filter by category/tag if provided
            # This is simplified - in reality you'd have a proper tag system
            query = query.where(NewsFeedItemModel.description.contains(category) |
                               NewsFeedItemModel.title.contains(category))
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        # Get unique sources
        sources = list(set([item.source for item in items]))
        
        return NewsFeedResponse(
            items=items,
            total=len(items),
            sources=sources,
            updated_at=datetime.utcnow()
        )
    
    async def refresh_all_feeds(self) -> dict:
        """
        Refresh all configured news feeds.
        """
        processed_feeds = 0
        new_items = 0
        errors = []
        
        for feed_url in self.feed_urls:
            try:
                feed_items = await self._fetch_feed(feed_url)
                new_count = await self._save_feed_items(feed_items, feed_url)
                new_items += new_count
                processed_feeds += 1
            except Exception as e:
                errors.append(f"Error processing {feed_url}: {str(e)}")
        
        return {
            "processed_feeds": processed_feeds,
            "new_items": new_items,
            "errors": errors
        }
    
    async def _fetch_feed(self, feed_url: str) -> List[dict]:
        """
        Fetch and parse a single RSS feed.
        """
        try:
            response = await self.http_client.get(feed_url)
            response.raise_for_status()
            
            feed_content = response.text
            parsed_feed = feedparser.parse(feed_content)
            
            items = []
            for entry in parsed_feed.entries:
                # Extract publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                
                # Extract categories/tags
                categories = []
                if hasattr(entry, 'tags'):
                    categories = [tag.term for tag in entry.tags]
                
                # Extract author
                author = getattr(entry, 'author', 'Unknown')
                
                items.append({
                    'title': getattr(entry, 'title', ''),
                    'link': getattr(entry, 'link', ''),
                    'description': getattr(entry, 'summary', ''),
                    'published_at': pub_date or datetime.utcnow(),
                    'author': author,
                    'categories': categories,
                    'tags': categories  # Same as categories for simplicity
                })
            
            return items
        except Exception as e:
            print(f"Error fetching feed {feed_url}: {str(e)}")
            raise
    
    async def _save_feed_items(self, feed_items: List[dict], feed_source: str) -> int:
        """
        Save feed items to database, avoiding duplicates.
        """
        new_items_count = 0
        
        for item_data in feed_items:
            # Check if item already exists (using link as unique identifier)
            existing_query = select(NewsFeedItemModel).where(
                NewsFeedItemModel.link == item_data['link']
            )
            result = await self.db.execute(existing_query)
            existing_item = result.scalar_one_or_none()
            
            if not existing_item:
                # Create new feed item
                feed_item = NewsFeedItemModel(
                    id=uuid.uuid4(),
                    title=item_data['title'],
                    link=item_data['link'],
                    description=item_data['description'],
                    source=urlparse(feed_source).netloc,
                    published_at=item_data['published_at'],
                    author=item_data['author'],
                    categories=item_data['categories'],
                    tags=item_data['tags'],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                self.db.add(feed_item)
                new_items_count += 1
        
        if new_items_count > 0:
            await self.db.commit()
        
        return new_items_count
    
    def get_feed_sources(self) -> List[str]:
        """
        Get list of configured feed sources.
        """
        return self.feed_urls
    
    async def close(self):
        """
        Close HTTP client.
        """
        await self.http_client.aclose()


# Create a simple model for news feed items since I haven't defined it yet
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class NewsFeedItem(Base):
    """
    News feed item model.
    """
    __tablename__ = "news_feed_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    link = Column(String(1000), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    source = Column(String(255), nullable=False)
    published_at = Column(DateTime, nullable=True)
    author = Column(String(255), nullable=True)
    categories = Column(String, nullable=True)  # Storing as JSON string for simplicity
    tags = Column(String, nullable=True)  # Storing as JSON string for simplicity
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<NewsFeedItem(id={self.id}, title={self.title}, source={self.source})>"