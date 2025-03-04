from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import Relationship, SQLModel, Field
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import JSONB

from digest.database.enums import ContentType

class ContentPiece(SQLModel, table=True):
    """Database model for content pieces."""
    

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        index=True,
    )
    title: str = Field(index=True)
    content: str
    content_type: ContentType = Field(default=ContentType.ARTICLE)
    url: Optional[str] = Field(default=None)
    author: Optional[str] = Field(default=None)
    published_at: Optional[datetime] = Field(default=None)
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    source_id: str = Field(foreign_key="source.id", index=True)
    metainfo: Dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    processed: bool = Field(default=False) 

    source: "Source" = Relationship(back_populates="content_pieces") # type: ignore