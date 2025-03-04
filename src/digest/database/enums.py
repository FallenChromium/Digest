
from enum import Enum


class ContentType(str, Enum):
    """Types of content that can be retrieved."""
    ARTICLE = "article"
    POST = "post"
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    FILE = "file"
    OTHER = "other"

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
