import asyncio

from digest.retrieval.parsers.base import ParserRegistry
from digest.retrieval.sources.base import Source
from digest.retrieval.sources.repository import repository as source_repository


class TaskManager:
    parser_tasks = {}

    async def _start_parser(self, source: Source):
        try:
            print(f"Parser {source.config.id} started")
            source_id = source.config.id
            parser_id = source.config.parser_id
            parser_config = source.config.config

            # TODO: timeout_sec = source.config.update_frequency
            timeout_sec = 10

            parser_cls = ParserRegistry.get_parser(parser_id)
            parser = parser_cls(source_id, parser_config)

            while True:
                content_pieces, _ = await asyncio.gather(parser.fetch(), asyncio.sleep(timeout_sec))
                print(f"Parser {source.config.id} got {len(content_pieces)} content pieces")
        except asyncio.CancelledError as e:
            print(f"Parser {source.config.id} stopped")
            raise e

    def start_all_parsers(self):
        for source in source_repository.get_all():
            try:
                self.parser_tasks[source.config.id] = asyncio.create_task(self._start_parser(source))
            except Exception as e:
                print(e)

    def start_parser(self, source_id: str):
        source = source_repository.get(source_id)
        if not source:
            raise ValueError(f"Source with ID '{source_id}' does not exists")

        try:
            self.parser_tasks[source.config.id] = asyncio.create_task(self._start_parser(source))
        except Exception as e:
            print(e)

    def stop_parser(self, source_id: str):
        self.parser_tasks[source_id].cancel()
        del self.parser_tasks[source_id]


task_manager = TaskManager()
