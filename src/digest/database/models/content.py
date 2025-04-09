from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, validator
from sqlmodel import Relationship, SQLModel, Field, Column
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlmodel import Index, text, UniqueConstraint, DDL
from sqlalchemy import event, Column as SQLAlchemyColumn, Table
from sqlalchemy.ext.declarative import declared_attr
from pgvector.sqlalchemy import Vector
from digest.database.enums import ContentType
import numpy as np

# Create trigram extension if not exists

# Add this mapping after imports, before the class
LANGDETECT_TO_POSTGRES_MAP: Dict[str, str] = {
    # Germanic
    'en': 'english',
    'de': 'german',
    'nl': 'dutch',
    'da': 'danish',
    'sv': 'swedish',
    'no': 'norwegian',
    # Romance
    'es': 'spanish',
    'fr': 'french',
    'it': 'italian',
    'pt': 'portuguese',
    'ro': 'romanian',
    'ca': 'catalan',
    # Slavic
    'ru': 'russian',
    'sr': 'serbian',
    # Other Indo-European
    'el': 'greek',
    'hi': 'hindi',
    'lt': 'lithuanian',
    'ga': 'irish',
    'hy': 'armenian',
    'yi': 'yiddish',
    # Uralic
    'fi': 'finnish',
    'hu': 'hungarian',
    # Others
    'eu': 'basque',
    'id': 'indonesian',
    'ta': 'tamil',
    'tr': 'turkish',
    'ar': 'arabic',
    'ne': 'nepali'
}

class ContentPiece(SQLModel, table=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    __tablename__ = 'content_piece'
    """Database model for content pieces."""
    __table_args__ = (
        UniqueConstraint('url', name='uq_content_url'),
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
    embedding: Optional[list[float]] = Field(sa_column=Column(Vector(768), nullable=True, default=None))

    # Generated columns for full-text search
    title_tsv: Optional[str] = Field(
        sa_column=SQLAlchemyColumn(
            TSVECTOR,
            nullable=False
        ),
        exclude=True  # Exclude from model serialization
    )
    content_tsv: Optional[str] = Field(
        sa_column=SQLAlchemyColumn(
            TSVECTOR,
            nullable=False
        ),
        exclude=True  # Exclude from model serialization
    )

    @field_serializer("embedding")
    def serialize_embedding(self, embedding: np.ndarray):
        if embedding is not None:
            if isinstance(embedding, np.ndarray):
                return embedding.tolist()
            elif isinstance(embedding, list):
                return embedding
        return None
    
    source: "Source" = Relationship(back_populates="content_pieces") # type: ignore

    @staticmethod
    def convert_language_code(lang_code: str) -> str:
        return LANGDETECT_TO_POSTGRES_MAP.get(lang_code, 'simple')


event.listen(
    SQLModel.metadata,
    'before_create',
    DDL('CREATE EXTENSION IF NOT EXISTS vector;')
)
event.listen(
    SQLModel.metadata,
    'before_create',
    DDL('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
)

# Create trigger function and trigger after table creation
@event.listens_for(Table, 'after_create')
def create_triggers(target, connection, **kw):
    if target.name == 'content_piece':
        connection.execute(text('''
        CREATE OR REPLACE FUNCTION content_piece_tsvector_trigger() RETURNS trigger AS $$
        DECLARE
            lang regconfig;
        BEGIN
            -- Try to use the language from metainfo, fallback to 'simple' if not supported
            BEGIN
                lang := COALESCE(NEW.metainfo->>'language', 'simple')::regconfig;
            EXCEPTION WHEN undefined_object THEN
                lang := 'simple'::regconfig;
            END;

            NEW.title_tsv := to_tsvector(lang, NEW.title);
            NEW.content_tsv := to_tsvector(lang, NEW.content);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER content_piece_tsvector_update
            BEFORE INSERT OR UPDATE ON content_piece
            FOR EACH ROW
            EXECUTE FUNCTION content_piece_tsvector_trigger();

        CREATE INDEX ix_content_piece_title_tsv ON content_piece USING gin(title_tsv);
        CREATE INDEX ix_content_piece_content_tsv ON content_piece USING gin(content_tsv);
        '''))
