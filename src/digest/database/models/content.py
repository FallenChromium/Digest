from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import Relationship, SQLModel, Field
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Index, text, UniqueConstraint, DDL

from digest.database.enums import ContentType

class ContentPiece(SQLModel, table=True):
    """Database model for content pieces."""
    __table_args__ = (
        UniqueConstraint('url', name='uq_content_url'),
        # TODO: ts_vector index for keyword search if we'll deem it necessary
        Index(
            'ix_content_piece_trigram',
            text('title gin_trgm_ops'),
            text('content gin_trgm_ops'),
            postgresql_using='gin'
        ),
        {'extend_existing': True}
    )

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

# Create trigger for automatic search vector updates
search_vector_trigger = DDL('''
    CREATE TRIGGER content_piece_search_vector_update
        BEFORE INSERT OR UPDATE
        ON contentpiece
        FOR EACH ROW
        EXECUTE FUNCTION
        tsvector_update_trigger(
            search_vector, 'pg_catalog.english',
            title, content
        );
''')

# Create trigram extension if not exists
create_extension_trigger = DDL('''
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
''')