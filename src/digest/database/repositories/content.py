from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import func, or_, text, literal
from sqlmodel import Session, cast, select
from sqlalchemy.dialects.postgresql import insert, REGCONFIG
import langdetect
from dataclasses import dataclass


from digest.database.enums import ContentType
from digest.database.models.content import ContentPiece


@dataclass
class SearchResult:
    id: str
    title: str
    content: str
    rank: Optional[float] = None
    similarity: Optional[float] = None
    snippet: Optional[str] = None
    query_plan: Optional[Dict[str, Any]] = None


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
            return 'english'

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

    # TODO: refactor benchmarking into another module
    def get_query_plan(self, stmt, analyze: bool = True) -> Dict[str, Any]:
        """Get the query plan for a given SQL statement using EXPLAIN ANALYZE.

        Returns a dictionary containing:
        - query_plan: The raw query plan
        - index_usage: List of indices used
        - scan_type: Type of scan (seq, index, bitmap, etc.)
        - total_cost: Estimated total cost
        - actual_time: Actual execution time (if analyze=True)
        """
        engine = self.session.get_bind()
        compiled = stmt.compile(
            dialect=engine.dialect,
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled)

        # Get both plain EXPLAIN and EXPLAIN ANALYZE
        explain_cmd = "EXPLAIN (FORMAT JSON) " + sql
        explain_analyze_cmd = "EXPLAIN (ANALYZE, FORMAT JSON) " + sql if analyze else None

        result = self.session.execute(text(explain_cmd)).scalar()
        if not result:
            return {
                'query_plan': {},
                'index_usage': [],
                'scan_type': 'unknown',
                'total_cost': 0,
                'actual_time': None,
                'rows': 0,
                'raw_plan': None
            }

        plan_data = result[0].get('Plan', {})

        if explain_analyze_cmd:
            analyze_result = self.session.execute(text(explain_analyze_cmd)).scalar()
            analyze_data = analyze_result[0].get('Plan', {}) if analyze_result else {}
        else:
            analyze_data = {}

        # Extract relevant information
        index_scans = []
        def extract_index_info(node):
            if 'Index Name' in node:
                index_scans.append({
                    'index_name': node['Index Name'],
                    'scan_type': node['Node Type'],
                    'index_cond': node.get('Index Cond', None)
                })
            if 'Plans' in node:
                for subplan in node['Plans']:
                    extract_index_info(subplan)

        extract_index_info(plan_data)

        return {
            'query_plan': plan_data,
            'index_usage': index_scans,
            'scan_type': plan_data.get('Node Type', 'unknown'),
            'total_cost': plan_data.get('Total Cost', 0),
            'actual_time': analyze_data.get('Actual Total Time', None) if analyze else None,
            'rows': analyze_data.get('Actual Rows', plan_data.get('Plan Rows', 0)) if analyze else plan_data.get('Plan Rows', 0),
            'raw_plan': result
        }

    def _generate_snippet(self, content: str, query: str, query_lang: str) -> str:
        """Generate a snippet from content highlighting the query matches."""
        casted_lang = cast(literal(query_lang), type_=REGCONFIG)
        tsquery = func.plainto_tsquery(casted_lang, query)
        result = self.session.scalar(
            select(
                func.ts_headline(
                    casted_lang,
                    content,
                    tsquery,
                    'MaxWords=50, MinWords=15'
                )
            )
        )
        return result or content[:200] + "..."  # Fallback to first 200 chars if no matches

    def search(self, query: str, similarity_threshold: float = 0.3, include_plan: bool = False) -> List[SearchResult]:
        """
        Search for content pieces using a combination of full-text search and trigram similarity.
        The search is performed across multiple languages and is typo-tolerant.
        """
        # Detect query language
        query_lang = self._detect_language(query)

        # Convert query to tsquery
        tsquery = func.plainto_tsquery(cast(literal(query_lang), type_=REGCONFIG), query)

        # Build combined search query using both full-text search and trigram similarity
        stmt = select(
            ContentPiece,
            func.ts_rank(text('content_tsv'), tsquery).label('rank'),
            func.similarity(ContentPiece.content, query).label('content_sim'),
            func.similarity(ContentPiece.title, query).label('title_sim')
        ).where(
            or_(
                # Match by full-text search
                text(f"content_tsv @@ plainto_tsquery('{query_lang}', :query)").bindparams(query=query),
                text(f"title_tsv @@ plainto_tsquery('{query_lang}', :query)").bindparams(query=query),
                # Match by trigram similarity
                func.word_similarity(ContentPiece.content, query) > similarity_threshold,
                func.word_similarity(ContentPiece.title, query) > similarity_threshold
            )
        )

        # Get query plan if requested
        plan = self.get_query_plan(stmt) if include_plan else None

        # Execute query
        results = self.session.execute(stmt).all()

        # Sort results by combining FTS rank and trigram similarity
        # TODO: dynamic weighing?
        sorted_results = sorted(
            results,
            key=lambda x: (x[1] * 0.4 + max(x[2], x[3]) * 0.6),
            reverse=True
        )

        # Return unique content pieces in order of relevance
        seen = set()
        final_results = []
        for result in sorted_results:
            if result[0].id not in seen:
                seen.add(result[0].id)
                snippet = self._generate_snippet(result[0].content, query, query_lang)
                final_results.append(SearchResult(
                    id=str(result[0].id),
                    title=result[0].title,
                    content=result[0].content,
                    rank=float(result[1]),
                    similarity=max(float(result[2]), float(result[3])),
                    snippet=snippet,
                    query_plan=plan
                ))

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

        # Get initial count
        initial_count = self.session.scalar(select(func.count()).select_from(ContentPiece)) or 0

        # Convert to dicts because we're using SQL-level statement
        content_dicts = [piece.model_dump() for piece in content_pieces]
        stmt = insert(ContentPiece).values(content_dicts).on_conflict_do_nothing(index_elements=['url'])
        self.session.execute(stmt)
        self.session.commit()

        # Get final count and return the difference
        final_count = self.session.scalar(select(func.count()).select_from(ContentPiece)) or 0
        return final_count - initial_count

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

    def search_fts_only(self, query: str, include_plan: bool = False) -> List[SearchResult]:
        """Full-text search only using tsvector."""
        query_lang = self._detect_language(query)
        # TODO: fix later
        casted_lang = cast(literal(query_lang), type_=REGCONFIG)
        tsquery = func.plainto_tsquery(casted_lang, query)

        # Build the query
        stmt = select(
            ContentPiece,
            func.ts_rank(text('content_tsv'), tsquery).label('rank'),
            func.ts_headline(
                casted_lang,
                ContentPiece.content,
                tsquery,
                'MaxWords=50, MinWords=15'
            ).label('snippet')
        ).where(
            or_(
                ContentPiece.content_tsv.op('@@')(tsquery),
                ContentPiece.title_tsv.op('@@')(tsquery)
            )
        ).params(query=query)

        # Get query plan if requested
        plan = self.get_query_plan(stmt) if include_plan else None

        # Execute query
        results = self.session.execute(stmt).all()

        return [
            SearchResult(
                id=str(r[0].id),
                title=r[0].title,
                content=r[0].content,
                rank=float(r[1]),
                snippet=r[2],
                query_plan=plan
            ) for r in results
        ]

    def search_trigram_only(self, query: str, similarity_threshold: float = 0.3, include_plan: bool = False) -> List[SearchResult]:
        """Trigram similarity search only."""
        query_lang = self._detect_language(query)
        # Build the query using word_similarity for trigram matching
        stmt = select(
            ContentPiece,
            func.word_similarity(ContentPiece.content, query).label('content_sim'),
            func.word_similarity(ContentPiece.title, query).label('title_sim')
        ).where(
            or_(
                func.word_similarity(ContentPiece.content, query) > similarity_threshold,
                func.word_similarity(ContentPiece.title, query) > similarity_threshold
            )
        )

        # Get query plan if requested
        plan = self.get_query_plan(stmt) if include_plan else None

        # Execute query
        results = self.session.execute(stmt).all()

        return [
            SearchResult(
                id=str(r[0].id),
                title=r[0].title,
                content=r[0].content,
                rank=float(r[1]),
                snippet=self._generate_snippet(r[0].content, query, query_lang),
                query_plan=plan
            ) for r in results
        ]

    def search_no_index(self, query: str, include_plan: bool = False) -> List[SearchResult]:
        """Search without using any indices (forced sequential scan)."""
        query_lang = self._detect_language(query)

        # Explicitly disable index scans
        stmt = text("""
            SET enable_indexscan = off;
            SET enable_bitmapscan = off;
            SET enable_seqscan = on;
        """)
        self.session.execute(stmt)

        try:
            stmt = select(ContentPiece).where(
                or_(
                    text("content ILIKE :query").bindparams(query=f"%{query}%"),
                    text("title ILIKE :query").bindparams(query=f"%{query}%")
                )
            )

            plan = self.get_query_plan(stmt) if include_plan else None

            # Execute query
            results = self.session.execute(stmt).all()

            return [
                SearchResult(
                    id=str(r[0].id),
                    title=r[0].title,
                    content=r[0].content,
                    snippet=self._generate_snippet(r[0].content, query, query_lang),
                    query_plan=plan
                ) for r in results
            ]
        finally:
            # Reset index settings
            reset_stmt = text("""
                SET enable_indexscan = on;
                SET enable_bitmapscan = on;
                SET enable_seqscan = on;
            """)
            self.session.execute(reset_stmt)
