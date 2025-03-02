from typing import Any, Dict, List

from pydantic import HttpUrl
from tchan import ChannelScraper

from digest.retrieval.models import ContentPiece, ContentType, SourceType
from digest.retrieval.parsers.base import BaseParser, ParserRegistry


@ParserRegistry.register
class TchanParser(BaseParser):
    parser_id = "tchan"
    name = "Telegram Channel Parser"
    description = "Parses content from public Telegram channels."
    supported_source_types = [SourceType.CUSTOM]

    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["channel_name", "limit"],
            "properties": {
                "channel_name": {"type": "string"},
                "limit": {"type": "integer", "description": "Number of posts to parse"},
            },
        }

    def validate_config(self) -> None:
        if "channel_name" not in self.config:
            raise ValueError("channel_name is required for tchan parser")
        if "limit" not in self.config:
            raise ValueError("limit is required for tchan parser")

    async def fetch(self) -> List[ContentPiece]:
        channel_name = self.config["channel_name"]
        limit = self.config["limit"]

        scraper = ChannelScraper()
        content_pieces = []
        for _, message in zip(range(limit), scraper.messages(channel_name)):
            if message.text is None:
                continue

            content_piece = ContentPiece(
                id=f"{self.source_id}{message.id}",
                title="",
                content=message.text,
                content_type=ContentType.POST,
                url=HttpUrl(f"https://t.me/{channel_name}/{message.id}"),
                author=message.author,
                published_at=message.created_at,
                source_id=self.source_id,
            )

            content_pieces.append(content_piece)

        return content_pieces

    async def test_connection(self) -> bool:
        channel_name = self.config["channel_name"]

        scraper = ChannelScraper()
        try:
            _ = scraper.info(channel_name)
            return True
        except:
            return False
