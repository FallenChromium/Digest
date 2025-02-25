from typing import Dict, List, Optional, Any
from datetime import datetime

from app.retrieval.models import SourceConfig, ContentPiece
from app.retrieval.parsers.base import ParserRegistry


class Source:
    """
    Source class represents a configured news source that can be fetched.
    It connects the source configuration with the appropriate parser.
    """
    
    def __init__(self, config: SourceConfig):
        """
        Initialize a source from its configuration.
        
        Args:
            config: The source configuration
        """
        self.config = config
        self._initialize_parser()
    
    def _initialize_parser(self) -> None:
        """Initialize the parser based on the source configuration."""
        parser_cls = ParserRegistry.get_parser(self.config.parser_id)
        self.parser = parser_cls(self.config.id, self.config.config)
    
    async def fetch(self) -> List[ContentPiece]:
        """
        Fetch content from the source.
        
        Returns:
            A list of ContentPiece objects
        """
        return await self.parser.fetch()
    
    async def test_connection(self) -> bool:
        """
        Test if the source is accessible.
        
        Returns:
            True if the connection is successful, False otherwise
        """
        return await self.parser.test_connection()
    
    def update_last_retrieved(self) -> None:
        """Update the last_retrieved timestamp in the source configuration."""
        self.config.last_retrieved = datetime.utcnow()
        self.config.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the source to a dictionary.
        
        Returns:
            A dictionary representation of the source
        """
        return self.config.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Source":
        """
        Create a source from a dictionary.
        
        Args:
            data: A dictionary representation of the source
            
        Returns:
            A Source instance
        """
        config = SourceConfig(**data)
        return cls(config) 