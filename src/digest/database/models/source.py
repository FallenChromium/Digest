from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from digest.database.models.content import ContentPiece
from digest.database.enums import SourceType, UpdateFrequency


class Source(SQLModel, table=True):
    """Database model for content sources."""
    

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        index=True
    )
    name: str = Field(index=True)
    source_type: SourceType
    parser_id: str = Field(index=True)
    update_frequency: UpdateFrequency = Field(default=UpdateFrequency.HOURLY)
    config: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_retrieved: Optional[datetime] = Field(default=None)

    # Relationships
    content_pieces: List["ContentPiece"] = Relationship(
        back_populates="source",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    feed_source_score: List["FeedSourceScore"] = Relationship(back_populates="source") # type: ignore
    trusted_by: List["TrustedSource"] = Relationship(back_populates="source") # type: ignore
