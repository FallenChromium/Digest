from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl


class ContentType(str, Enum):
    """Types of content that can be retrieved."""
    ARTICLE = "article"
    POST = "post"
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    FILE = "file"
    OTHER = "other"


class ContentPiece(BaseModel):
    """Base model for any piece of content retrieved from a source."""
    id: str = Field(..., description="Unique identifier for the content piece")
    title: str = Field(..., description="Title of the content")
    content: str = Field(..., description="Raw content text")
    content_type: ContentType = Field(default=ContentType.ARTICLE)
    url: Optional[HttpUrl] = Field(None, description="Original URL of the content if available")
    author: Optional[str] = Field(None, description="Author of the content")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    source_id: str = Field(..., description="ID of the source this content came from")
    metadata: Dict[str, Union[str, int, float, bool, List, Dict]] = Field(
        default_factory=dict, 
        description="Additional metadata specific to the content type"
    )
    processed: bool = Field(default=False, description="Whether the content has been processed")
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "article-123",
                "title": "Breaking News: Important Event", 
                "content": "This is the full content of the article...",
                "content_type": "article",
                "url": "https://example.com/article/123",
                "author": "John Doe",
                "published_at": "2023-04-01T12:00:00Z",
                "source_id": "nytimes-rss",
                "metadata": {
                    "categories": ["politics", "world"],
                    "read_time_minutes": 5
                }
            }
        }
    }


class SourceType(str, Enum):
    """Types of news sources that can be configured."""
    RSS = "rss"
    WEBPAGE = "webpage"
    FILE_FOLDER = "file_folder"
    CUSTOM = "custom"


class UpdateFrequency(str, Enum):
    """Frequency options for source updates."""
    REALTIME = "realtime"  # For websocket or streaming sources
    MINUTES_5 = "5min"
    MINUTES_15 = "15min"
    MINUTES_30 = "30min"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MANUAL = "manual"


class SourceConfig(BaseModel):
    """Configuration for a news source."""
    id: str = Field(..., description="Unique identifier for the source")
    name: str = Field(..., description="User-friendly name for the source")
    source_type: SourceType = Field(..., description="Type of the source")
    parser_id: str = Field(..., description="ID of the parser to use with this source")
    update_frequency: UpdateFrequency = Field(default=UpdateFrequency.HOURLY)
    config: Dict[str, Union[str, int, float, bool, List, Dict]] = Field(
        default_factory=dict,
        description="Parser-specific configuration"
    )
    tags: List[str] = Field(default_factory=list, description="User-defined tags for categorization")
    enabled: bool = Field(default=True, description="Whether this source is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_retrieved: Optional[datetime] = Field(None, description="When content was last retrieved")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "nytimes-rss",
                "name": "New York Times - World News",
                "source_type": "rss",
                "parser_id": "rss",
                "update_frequency": "hourly",
                "config": {
                    "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
                },
                "tags": ["news", "world", "trusted"],
                "enabled": True
            }
        } 
    }