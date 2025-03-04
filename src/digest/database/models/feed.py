from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID
from sqlmodel import Field, Relationship, SQLModel


class SourceInclusion(str, Enum):
    """Enum for source inclusion in a feed."""
    INCLUDED = "included"
    EXCLUDED = "excluded"

class Feed(SQLModel, table=True):
    """Database model for user feeds with information goals."""
    

    id: UUID = Field(primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    user: "User" = Relationship(back_populates="feed") # type: ignore
    feed_source_score: List["FeedSourceScore"] = Relationship(back_populates="feed") # type: ignore
