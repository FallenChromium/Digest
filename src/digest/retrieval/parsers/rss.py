import asyncio
import datetime
import hashlib
import uuid
from typing import Any, Dict, List, Optional

import requests
import feedparser
from pydantic import HttpUrl, ValidationError

from digest.retrieval.models import ContentPiece, ContentType, SourceType
from digest.retrieval.parsers.base import BaseParser, ParserRegistry


@ParserRegistry.register
class RssParser(BaseParser):
    """Parser for RSS and Atom feeds."""
    
    parser_id = "rss"
    name = "RSS/Atom Feed Parser"
    description = "Parses content from RSS and Atom feeds."
    supported_source_types = [SourceType.RSS]
    
    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        """Configuration schema for RSS parser."""
        return {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {
                    "type": "string",
                    "format": "uri",
                    "description": "URL of the RSS or Atom feed"
                },
                "headers": {
                    "type": "object",
                    "description": "HTTP headers to send with the request",
                    "additionalProperties": {
                        "type": "string"
                    }
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout for HTTP requests in seconds",
                    "default": 30
                }
            }
        }
    
    def validate_config(self) -> None:
        """Validate the RSS parser configuration."""
        if "url" not in self.config:
            raise ValueError("URL is required for RSS parser")
        
        try:
            HttpUrl(self.config["url"])
        except ValidationError:
            raise ValueError(f"Invalid URL: {self.config['url']}")
    
    async def fetch(self) -> List[ContentPiece]:
        """Fetch and parse the RSS feed."""
        url = self.config["url"]
        headers = self.config.get("headers", {})
        timeout = self.config.get("timeout", 30)
        
        # Use asyncio to run the HTTP request in a thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.get(url, headers=headers, timeout=timeout)
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch RSS feed: HTTP {response.status_code}")
        
        # Parse the feed
        feed = feedparser.parse(response.text)
        
        # Convert feed entries to ContentPiece objects
        content_pieces = []
        for entry in feed.entries:
            # Create a unique ID based on the entry ID or link
            entry_id = entry.get("id", entry.get("link", ""))
            if not entry_id:
                entry_id = str(uuid.uuid4())
            else:
                # Create a stable hash from the entry ID
                entry_id = hashlib.md5(entry_id.encode()).hexdigest()
            
            # Extract the publication date
            published_at = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published_at = datetime.datetime(*entry.published_parsed[:6])
            
            # Extract content
            content = ""
            if hasattr(entry, "content") and entry.content:
                content = entry.content[0].value
            elif hasattr(entry, "summary") and entry.summary:
                content = entry.summary
            elif hasattr(entry, "description") and entry.description:
                content = entry.description
            
            # Create the ContentPiece
            content_piece = ContentPiece(
                id=f"{self.source_id}:{entry_id}",
                title=entry.get("title", "Untitled"),
                content=content,
                content_type=ContentType.ARTICLE,
                url=entry.get("link"),
                author=entry.get("author"),
                published_at=published_at,
                source_id=self.source_id,
                metadata={
                    "feed_title": feed.feed.get("title", ""),
                    "categories": [tag.term for tag in entry.get("tags", [])] if hasattr(entry, "tags") else []
                }
            )
            
            content_pieces.append(content_piece)
        
        return content_pieces
    
    async def test_connection(self) -> bool:
        """Test if the RSS feed is accessible."""
        try:
            url = self.config["url"]
            headers = self.config.get("headers", {})
            timeout = self.config.get("timeout", 30)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.head(url, headers=headers, timeout=timeout)
            )
            
            return response.status_code == 200
        except Exception:
            return False 