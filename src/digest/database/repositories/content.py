from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from sqlalchemy.dialects.postgresql import insert

from digest.database.enums import ContentType
from digest.database.models.content import ContentPiece


class ContentRepository:
    """Repository for managing content pieces in the database."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, content_piece: ContentPiece) -> ContentPiece:
        """Create a new content piece."""
        self.session.add(content_piece)
        self.session.commit()
        self.session.refresh(content_piece)
        return content_piece

    def get_by_id(self, content_id: UUID) -> Optional[ContentPiece]:
        """Get a content piece by ID."""
        return self.session.get(ContentPiece, content_id)

    def get_by_source(self, source_id: UUID) -> List[ContentPiece]:
        """Get all content pieces for a source."""
        statement = select(ContentPiece).where(ContentPiece.source_id == source_id)
        return list(self.session.exec(statement))

    def get_by_type(self, content_type: ContentType) -> List[ContentPiece]:
        """Get all content pieces of a specific type."""
        statement = select(ContentPiece).where(ContentPiece.content_type == content_type)
        return list(self.session.exec(statement))

    def update(self, content_piece: ContentPiece) -> ContentPiece:
        """Update a content piece."""
        self.session.add(content_piece)
        self.session.commit()
        self.session.refresh(content_piece)
        return content_piece

    def delete(self, content_id: UUID) -> bool:
        """Delete a content piece."""
        content_piece = self.get_by_id(content_id)
        if not content_piece:
            return False
        
        self.session.delete(content_piece)
        self.session.commit()
        return True

    def get_unprocessed(self) -> List[ContentPiece]:
        """Get all unprocessed content pieces."""
        statement = select(ContentPiece).where(ContentPiece.processed == False)
        return list(self.session.exec(statement))

    def mark_as_processed(self, content_id: UUID) -> bool:
        """Mark a content piece as processed."""
        content_piece = self.get_by_id(content_id)
        if not content_piece:
            return False
        
        content_piece.processed = True
        self.session.add(content_piece)
        self.session.commit()
        return True

    def bulk_insert(self, content_pieces: List[ContentPiece]) -> int:
        """
        Efficiently inserts multiple content pieces, skipping those with duplicate URLs.
        Returns the number of new pieces inserted.
        """
        if not content_pieces:
            return 0
        
        # convert to dicts because we're using SQL-level statement
        content_dicts = [piece.model_dump() for piece in content_pieces]
        stmt = insert(ContentPiece).values(content_dicts).on_conflict_do_nothing(index_elements=['url'])
        result = self.session.execute(stmt)
        self.session.commit()
        
        return result.rowcount

    def get_latest_content_for_source(self, source_id: str, limit: int = 1) -> List[ContentPiece]:
        """Get the most recent content pieces for a source."""
        statement = select(ContentPiece).where(
            ContentPiece.source_id == source_id
        ).order_by(ContentPiece.retrieved_at.desc()).limit(limit)
        
        return list(self.session.exec(statement).all()) 