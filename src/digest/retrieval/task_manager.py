import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from digest.retrieval.parsers.base import BaseParser, ParserRegistry
from digest.database.models.source import Source
from digest.database.repositories.sources import SourceRepository
from digest.database.repositories.content import ContentRepository
from digest.database.session import get_long_session

class TaskManager:
    def __init__(self, source_repository: SourceRepository, content_repository: ContentRepository):
        self.source_repository = source_repository
        self.content_repository = content_repository
        self.parser_tasks: Dict[str, asyncio.Task] = {}

    async def _fetch_content(self, parser: BaseParser):
        content_pieces = await parser.fetch()
        source = self.source_repository.get_by_id(parser.source_id)
        if not source:
            raise ValueError(f"Source with ID '{parser.source_id}' does not exist")
        if content_pieces:
            # Efficiently insert new content pieces, skipping duplicates
            new_pieces = self.content_repository.bulk_insert(content_pieces)
            print(f"Parser for {source.name} got {len(content_pieces)} content pieces, {new_pieces} new pieces inserted")
        current_time = datetime.utcnow()
        source.last_retrieved = current_time
        self.source_repository.update(source)
    async def _start_parser(self, source: Source):
        try:
            print(f"Parser for {source.name} activated")
            parser_cls = ParserRegistry.get_parser(source.parser_id)
            parser = parser_cls(source.id, source.config)
            update_frequency = source.update_frequency

            while True:
                try:
                    current_time = datetime.utcnow()
                    last_fetch = source.last_retrieved

                    if last_fetch and (current_time - last_fetch).total_seconds() < update_frequency:
                        await asyncio.sleep(30)
                        continue

                    await self._fetch_content(parser)
                    await asyncio.sleep(update_frequency)

                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    print(f"Error in parser loop for {source.name}: {str(e)}")
                    await asyncio.sleep(60)  # Wait before retrying after error

        except asyncio.CancelledError:
            print(f"Parser for {source.name} stopped")
            raise
        except Exception as e:
            print(f"Fatal error in parser for {source.name}: {str(e)}")
            raise e

    def start_all_parsers(self):
        """Start all parsers as background tasks"""
        for source in self.source_repository.get_all():
            if source.id not in self.parser_tasks:
                self.parser_tasks[source.id] = asyncio.create_task(
                    self._start_parser(source)
                )

    async def stop_all_parsers(self):
        """Gracefully stop all parsers"""
        for task in self.parser_tasks.values():
            task.cancel()
        await asyncio.gather(*self.parser_tasks.values(), return_exceptions=True)
        self.parser_tasks.clear()

    def start_parser(self, source_id: str):
        source = self.source_repository.get_by_id(source_id)
        if not source:
            raise ValueError(f"Source with ID '{source_id}' does not exist")

        try:
            self.parser_tasks[source.id] = asyncio.create_task(self._start_parser(source))
        except Exception as e:
            print(f"Error starting parser for source {source_id}: {str(e)}")

    def stop_parser(self, source_id: str):
        if source_id in self.parser_tasks:
            self.parser_tasks[source_id].cancel()
            del self.parser_tasks[source_id]

    def one_off_fetch(self, source_id: str):
        source = self.source_repository.get_by_id(source_id)
        if not source:
            raise ValueError(f"Source with ID '{source_id}' does not exist")
        parser = ParserRegistry.get_parser(source.parser_id)
        return asyncio.create_task(self._fetch_content(parser(source.id, source.config)))

# Initialize repositories with a long-lived session
session = get_long_session()
task_manager = TaskManager(
    source_repository=SourceRepository(session),
    content_repository=ContentRepository(session)
)
