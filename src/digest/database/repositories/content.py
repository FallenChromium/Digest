from typing import List, Optional
from uuid import UUID
from sqlalchemy import func, or_, text
from sqlmodel import Session, select
from sqlalchemy.dialects.postgresql import insert
import langdetect


from digest.database.enums import ContentType
from digest.database.models.content import ContentPiece


class ContentRepository:
    """Repository for managing content pieces in the database."""

    def __init__(self, session: Session):
        self.session = session

    def _detect_language(self, text: str) -> str:
        """Detect language of the text and convert to PostgreSQL text search configuration name."""
        try:
            lang_code = langdetect.detect(text)
            return ContentPiece.convert_language_code(lang_code)
        except:
            return 'simple'

    def _update_tsvectors(self, content_piece: ContentPiece):
        """Update tsvector columns based on content language."""
        if not content_piece.metainfo.get('language'):
            content_piece.language = self._detect_language(content_piece.content)
        
        # Update tsvectors using the appropriate language configuration
        self.session.execute(
            text("""
                UPDATE content_piece 
                SET 
                    title_tsv = to_tsvector(:lang::regconfig, :title),
                    content_tsv = to_tsvector(:lang::regconfig, :content)
                WHERE id = :id
            """),
            {
                'lang': content_piece.metainfo['language'],
                'title': content_piece.title,
                'content': content_piece.content,
                'id': content_piece.id
            }
        )

    def create(self, content_piece: ContentPiece) -> ContentPiece:
        """Create a new content piece."""
        metainfo = content_piece.metainfo or {}
        if 'language' not in metainfo:
            metainfo['language'] = self._detect_language(content_piece.content)
            content_piece.metainfo = metainfo
        
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

    def search(self, query: str, similarity_threshold: float = 0.3) -> List[ContentPiece]:
        """
        Search for content pieces using a combination of full-text search and trigram similarity.
        The search is performed across multiple languages and is typo-tolerant.
        """
        # Detect query language
        query_lang = self._detect_language(query)
        
        # Convert query to tsquery
        tsquery = func.plainto_tsquery(query_lang, query)
        
        # Build combined search query using both full-text search and trigram similarity
        results = self.session.query(
            ContentPiece,
            func.ts_rank(text('content_tsv'), tsquery).label('rank'),
            func.similarity(ContentPiece.content, query).label('content_sim'),
            func.similarity(ContentPiece.title, query).label('title_sim')
        ).filter(
            or_(
                # Match by full-text search
                text(f"content_tsv @@ plainto_tsquery('{query_lang}', :query)").bindparams(query=query),
                text(f"title_tsv @@ plainto_tsquery('{query_lang}', :query)").bindparams(query=query),
                # Match by trigram similarity
                func.word_similarity(ContentPiece.content, query) > similarity_threshold,
                func.word_similarity(ContentPiece.title, query) > similarity_threshold
            )
        ).all()
        
        # Sort results by combining FTS rank and trigram similarity
        sorted_results = sorted(
            results,
            key=lambda x: (x.rank * 0.4 + max(x.content_sim, x.title_sim) * 0.6),
            reverse=True
        )
        
        # Return unique content pieces in order of relevance
        seen = set()
        final_results = []
        for result in sorted_results:
            if result[0].id not in seen:
                seen.add(result[0].id)
                final_results.append(result[0])
        
        return final_results

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
        
        # TODO: should be moved to pipelines and ran by a task manager
        for piece in content_pieces:
            if not piece.metainfo:
                piece.metainfo = {}
            if 'language' not in piece.metainfo:
                piece.metainfo['language'] = self._detect_language(piece.content)
        
        # convert to dicts because we're using SQL-level statement
        content_dicts = [piece.model_dump() for piece in content_pieces]
        stmt = insert(ContentPiece).values(content_dicts).on_conflict_do_nothing(index_elements=['url'])
        result = self.session.execute(stmt)
        self.session.commit()
        
        # Get the number of affected rows
        return result.rowcount if hasattr(result, 'rowcount') else len(content_pieces)

    def get_latest_content_for_source(self, source_id: str, limit: int = 1) -> List[ContentPiece]:
        """Get the most recent content pieces for a source."""
        statement = select(ContentPiece).where(
            ContentPiece.source_id == source_id
        ).order_by(text('retrieved_at DESC')).limit(limit)
        
        return list(self.session.exec(statement))
    
    def get_all_paged(self, page: int = 1, page_size: int = 10) -> List[ContentPiece]:
        """Get all content pieces paged."""
        statement = select(ContentPiece).order_by(text('retrieved_at DESC')).offset((page - 1) * page_size).limit(page_size)
        return list(self.session.exec(statement))