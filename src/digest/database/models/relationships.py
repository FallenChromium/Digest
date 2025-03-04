from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlmodel import Field, Relationship, SQLModel

from digest.database.models.feed import Feed
from digest.database.models.source import Source
from digest.database.models.user import User

class FeedSourceScore(SQLModel, table=True):
    __tablename__ = "feed_source_score" # type: ignore
    """Database model for source inclusion/exclusion rules in feeds."""

    feed_id: UUID = Field(foreign_key="feed.id", primary_key=True)
    source_id: str = Field(foreign_key="source.id", primary_key=True)
    rating: int = Field(default=5, ge=0, le=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    feed: Feed = Relationship(back_populates="feed_source_score")
    source: Source = Relationship(back_populates="feed_source_score")



class TrustedSource(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    source_id: str = Field(foreign_key="source.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(default=None)
    user: User = Relationship(back_populates="trusted_sources")
    source: Source = Relationship(back_populates="trusted_by")
