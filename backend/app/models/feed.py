"""
Feed models for DomainSentry.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class NewsFeedItem(Base):
    """
    News feed item model for cyber security news aggregation.
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