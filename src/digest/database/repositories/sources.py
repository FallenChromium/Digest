from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from digest.database.models.source import Source
from digest.database.enums import SourceType


class SourceRepository:
    """Repository for managing sources in the database."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, source: Source) -> Source:
        """Create a new source."""
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source

    def get_by_id(self, source_id: UUID) -> Optional[Source]:
        """Get a source by ID."""
        return self.session.get(Source, source_id)

    def get_by_name(self, name: str) -> Optional[Source]:
        """Get a source by name."""
        statement = select(Source).where(Source.name == name)
        return self.session.exec(statement).first()

    def get_by_type(self, source_type: SourceType) -> List[Source]:
        """Get sources by type."""
        statement = select(Source).where(Source.source_type == source_type)
        return list(self.session.exec(statement))

    def get_enabled(self) -> List[Source]:
        """Get all enabled sources."""
        statement = select(Source).where(Source.enabled == True)
        return list(self.session.exec(statement))

    def get_all(self) -> List[Source]:
        """Get all sources."""
        statement = select(Source)
        return list(self.session.exec(statement))

    def update(self, source: Source) -> Source:
        """Update a source."""
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source

    def delete(self, source_id: UUID) -> bool:
        """Delete a source."""
        source = self.get_by_id(source_id)
        if not source:
            return False
        
        self.session.delete(source)
        self.session.commit()
        return True

    def update_last_retrieved(self, source_id: UUID) -> bool:
        """Update the last_retrieved timestamp of a source."""
        source = self.get_by_id(source_id)
        if not source:
            return False
        
        source.last_retrieved = datetime.utcnow()
        self.session.add(source)
        self.session.commit()
        return True 