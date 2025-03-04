from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

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